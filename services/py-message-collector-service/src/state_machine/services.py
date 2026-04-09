from __future__ import annotations

import json
import logging
import os
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from urllib import error, request

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from .llm_context import LLM_CONTEXT

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class GraphDependencies:
    short_term_repository: Any
    long_term_repository: Any
    llm: ChatGroq
    long_term_threshold: int
    qdrant_api_base_url: str
    qdrant_products_collection: str
    qdrant_search_limit: int
    embedding_api_base_url: str
    llm_context: str


def build_client_id(platform: str, user_id: str) -> str:
    return f"{platform}:{user_id}"


def build_graph_dependencies(
    *,
    short_term_repository: Any,
    long_term_repository: Any,
    long_term_threshold: int,
) -> GraphDependencies:
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise RuntimeError("GROQ_API_KEY não configurada no .env")

    return GraphDependencies(
        short_term_repository=short_term_repository,
        long_term_repository=long_term_repository,
        llm=ChatGroq(
            api_key=groq_api_key,
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            temperature=0.2,
        ),
        long_term_threshold=long_term_threshold,
        qdrant_api_base_url=os.getenv("QDRANT_API_BASE_URL", "http://127.0.0.1:8000"),
        qdrant_products_collection=os.getenv(
            "QDRANT_PRODUCTS_COLLECTION",
            "products_embedding_test",
        ),
        qdrant_search_limit=int(os.getenv("QDRANT_SEARCH_LIMIT", 3)),
        embedding_api_base_url=os.getenv(
            "EMBEDDING_API_BASE_URL",
            "http://127.0.0.1:8080",
        ),
        llm_context=LLM_CONTEXT,
    )


def consolidate_messages(messages: list[str]) -> str:
    valid_messages = [message.strip() for message in messages if message.strip()]
    return "\n".join(valid_messages)


def save_and_load_short_term_memory(
    *,
    dependencies: GraphDependencies,
    platform: str,
    user_id: str,
    messages: list[str],
    consolidated_message: str,
) -> list[dict[str, str]]:
    ingested_at = datetime.now(timezone.utc).isoformat()

    for index, message in enumerate(messages):
        dependencies.short_term_repository.save(
            platform=platform,
            user_id=user_id,
            message=message,
            role="user",
            metadata={
                "source": "redis_buffer",
                "ingested_at": ingested_at,
                "message_index_in_batch": index,
                "batch_size": len(messages),
                "consolidated_message": consolidated_message,
            },
        )

    return dependencies.short_term_repository.get_recent(
        client_id=build_client_id(platform, user_id),
        limit=20,
    )


def load_long_term_memory(
    *,
    dependencies: GraphDependencies,
    client_id: str,
    short_term_memory: list[dict[str, str]],
    batch_size: int,
) -> dict[str, Any]:
    current_context = dependencies.long_term_repository.get(client_id) or {}
    previous_total = get_total_messages_seen(current_context)
    current_total = previous_total + batch_size

    dependencies.long_term_repository.upsert_context(
        client_id=client_id,
        context_type="processing_state",
        data={
            "total_messages_seen": current_total,
            "last_batch_size": batch_size,
            "last_processed_at": datetime.now(timezone.utc),
        },
    )

    if should_update_long_term(
        previous_count=previous_total,
        current_count=current_total,
        threshold=dependencies.long_term_threshold,
    ):
        contents = [item["content"] for item in short_term_memory if item.get("content")]
        dependencies.long_term_repository.upsert_context(
            client_id=client_id,
            context_type="summary",
            data={
                "text": build_example_summary(contents),
                "source": "simple_langgraph_pipeline",
                "message_count_in_batch": batch_size,
                "total_messages": current_total,
                "recent_messages_for_prompt": contents[-10:],
                "last_message": contents[-1] if contents else "",
                "updated_at": datetime.now(timezone.utc),
            },
        )

    return dependencies.long_term_repository.get(client_id) or {}


def decide_action(consolidated_message: str) -> str:
    keywords = {
        "produto",
        "produtos",
        "preco",
        "valor",
        "comprar",
        "catalogo",
        "estoque",
        "notebook",
        "celular",
        "smartphone",
        "monitor",
        "teclado",
        "mouse",
    }
    normalized = normalize_text(consolidated_message)

    for keyword in keywords:
        if keyword in normalized:
            return "search_products"

    return "respond_direct"


def search_products(
    *,
    dependencies: GraphDependencies,
    query: str,
) -> list[dict[str, Any]]:
    try:
        query_vector = generate_embedding(
            base_url=dependencies.embedding_api_base_url,
            text=query,
        )
        payload = post_json(
            url=f"{dependencies.qdrant_api_base_url.rstrip('/')}/qdrant/search",
            payload={
                "collection_name": dependencies.qdrant_products_collection,
                "query_vector": query_vector,
                "limit": dependencies.qdrant_search_limit,
                "with_payload": True,
            },
        )
    except Exception:
        logger.exception("Falha ao buscar produtos no Qdrant")
        return []

    result = payload.get("result", [])
    return result if isinstance(result, list) else []


def build_response(
    *,
    dependencies: GraphDependencies,
    platform: str,
    user_id: str,
    consolidated_message: str,
    short_term_memory: list[dict[str, str]],
    long_term_memory: dict[str, Any],
    product_results: list[dict[str, Any]],
) -> str:
    summary = (
        long_term_memory.get("contexts", {})
        .get("summary", {})
        .get("text", "Sem memória longa disponível.")
    )

    prompt = (
        f"Contexto de simulação da LLM:\n{dependencies.llm_context}\n\n"
        f"Mensagem consolidada do cliente:\n{consolidated_message}\n\n"
        f"Memória curta:\n{json.dumps(short_term_memory[-6:], ensure_ascii=False)}\n\n"
        f"Memória longa:\n{summary}\n\n"
        f"Produtos encontrados:\n{json.dumps(product_results, ensure_ascii=False)}"
    )

    response = dependencies.llm.invoke(
        [
            SystemMessage(content=dependencies.llm_context),
            HumanMessage(content=prompt),
        ]
    )

    final_response = response.content.strip()

    dependencies.short_term_repository.save(
        platform=platform,
        user_id=user_id,
        message=final_response,
        role="assistant",
        metadata={
            "source": "langgraph_pipeline",
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
    )

    return final_response


def build_example_summary(messages: list[str]) -> str:
    valid_messages = [message.strip() for message in messages if message.strip()]
    if not valid_messages:
        return "Resumo pendente: nenhuma mensagem valida recebida ainda."
    return "Resumo simples das ultimas mensagens: " + " | ".join(valid_messages[-5:])


def get_total_messages_seen(long_term_context: dict[str, Any] | None) -> int:
    if not long_term_context:
        return 0

    contexts = long_term_context.get("contexts", {})
    processing_state = contexts.get("processing_state", {})
    total_messages_seen = processing_state.get("total_messages_seen", 0)
    return total_messages_seen if isinstance(total_messages_seen, int) else 0


def should_update_long_term(
    previous_count: int,
    current_count: int,
    threshold: int,
) -> bool:
    if threshold <= 0:
        return False
    return (previous_count // threshold) < (current_count // threshold)


def normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    without_accents = "".join(
        char for char in normalized if not unicodedata.combining(char)
    )
    return without_accents.lower()


def generate_embedding(*, base_url: str, text: str) -> list[float]:
    payload = post_json(
        url=f"{base_url.rstrip('/')}/embed",
        payload={"inputs": text},
    )

    if isinstance(payload, list) and payload and isinstance(payload[0], list):
        return payload[0]
    if isinstance(payload, list):
        return payload

    raise RuntimeError("Embedding API retornou payload inválido")


def post_json(*, url: str, payload: dict[str, Any]) -> Any:
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url=url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=30.0) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"Erro HTTP em {url}: {exc.code} - {detail}") from exc
    except error.URLError as exc:
        raise RuntimeError(f"Erro de conexão em {url}: {exc}") from exc
