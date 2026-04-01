import logging
import os
import time
from datetime import datetime, timezone
from typing import Iterable

from dotenv import load_dotenv
from config.logger import setup_logger
from infra.redis import ChatBufferRepository, RedisConnection
from infra.mongo.connection import MongoConnection
from infra.mongo.longtermrepository import LongTermRepository
from infra.mongo.shorttermrepository import ShortTermRepository


load_dotenv()

setup_logger(
    container_name="py-message-collector-service",
    log_dir=os.getenv("LOG_DIR", os.path.join(os.getcwd(), "system_log")),
    show_log=True,
    error_mode="full",
)

logger = logging.getLogger(__name__)


def build_mongo_uri() -> str:
    host = os.getenv("MONGO_HOST", "localhost")
    port = int(os.getenv("MONGO_PORT", 27017))
    return f"mongodb://{host}:{port}"


def build_client_id(platform: str, user_id: str) -> str:
    return f"{platform}:{user_id}"


def build_example_summary(messages: Iterable[str]) -> str:
    normalized_messages = [message.strip() for message in messages if message.strip()]

    if not normalized_messages:
        return "Resumo pendente: nenhuma mensagem valida recebida ainda."

    preview = " | ".join(normalized_messages[-5:])
    return (
        "Resumo de exemplo gerado sem LLM. "
        f"Ultimas mensagens recebidas: {preview}"
    )


def should_update_long_term(
    previous_count: int,
    current_count: int,
    threshold: int,
) -> bool:
    if threshold <= 0:
        return False

    return (previous_count // threshold) < (current_count // threshold)


def get_total_messages_seen(long_term_context: dict | None) -> int:
    if not long_term_context:
        return 0

    contexts = long_term_context.get("contexts", {})
    processing_state = contexts.get("processing_state", {})
    total_messages_seen = processing_state.get("total_messages_seen", 0)

    if isinstance(total_messages_seen, int):
        return total_messages_seen

    return 0


def main() -> None:
        platform = os.getenv("MESSAGE_PLATFORM", "redis_buffer")
        long_term_threshold = int(os.getenv("LONG_TERM_UPDATE_EVERY", 10))

        redis_conn = RedisConnection(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        db=int(os.getenv("REDIS_DB", 0)),
        )

        redis_repo_chatbuffer = ChatBufferRepository(redis_conn)

        mongo_conn = MongoConnection(
            uri=build_mongo_uri(),
            database_name=os.getenv("MONGO_DB", "chat_db"),
        )

        mongo_repo_longterm = LongTermRepository(mongo_conn)

        mongo_repo_shortterm = ShortTermRepository(mongo_conn)

        while True:
            items = redis_repo_chatbuffer.collect_ready(
                idle_seconds=10,
                batch_size=10,
                lock_ttl_seconds=240,
            )

            print(f"Coletados {len(items)} itens prontos para processamento")

            for item in items:
                user_id = item["user_id"]
                messages = item["messages"]
                lock_token = item["lock_token"]
                client_id = build_client_id(platform, user_id)

                try:
                    print(f"Processando user_id={user_id}: {messages}")

                    current_long_term_context = mongo_repo_longterm.get(client_id)
                    previous_message_count = get_total_messages_seen(
                        current_long_term_context
                    )

                    for message in messages:
                        mongo_repo_shortterm.save(
                            platform=platform,
                            user_id=user_id,
                            message=message,
                            role="user",
                            metadata={
                                "source": "redis_buffer",
                                "ingested_at": datetime.now(timezone.utc).isoformat(),
                            },
                        )

                    current_message_count = previous_message_count + len(messages)

                    mongo_repo_longterm.upsert_context(
                        client_id=client_id,
                        context_type="processing_state",
                        data={
                            "total_messages_seen": current_message_count,
                            "last_batch_size": len(messages),
                            "last_processed_at": datetime.now(timezone.utc),
                        },
                    )

                    if should_update_long_term(
                        previous_count=previous_message_count,
                        current_count=current_message_count,
                        threshold=long_term_threshold,
                    ):
                        recent_history = mongo_repo_shortterm.get_recent(
                            client_id=client_id,
                            limit=20,
                        )


                        long_term_payload = {
                            "text": build_example_summary(
                                item["content"] for item in recent_history
                            ),
                            "source": "example_without_llm",
                            "message_count_in_batch": len(messages),
                            "total_messages": current_message_count,
                            "recent_messages_for_prompt": [
                                item["content"] for item in recent_history[-10:]
                            ],
                            "last_message": messages[-1] if messages else "",
                            "updated_at": datetime.now(timezone.utc),
                        }

                        mongo_repo_longterm.upsert_context(
                            client_id=client_id,
                            context_type="summary",
                            data=long_term_payload,
                        )

                        logger.info(
                            "Contexto de longo prazo atualizado para user_id=%s com %s mensagens",
                            user_id,
                            current_message_count,
                        )

                    success = redis_repo_chatbuffer.ack_delete(user_id, lock_token)

                    if not success:
                        logger.warning(
                            "Não foi possível confirmar a deleção do user_id=%s",
                            user_id,
                        )
                    else:
                        logger.info(
                            "Mensagens persistidas no Mongo para user_id=%s",
                            user_id,
                        )

                except Exception:
                    logger.exception("Erro no processamento do user_id=%s", user_id)
                    redis_repo_chatbuffer.release_lock(user_id, lock_token)

            time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("Erro fatal na aplicação")
