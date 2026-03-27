from __future__ import annotations

from infra.embedding_client import EmbeddingClient
from infra.environment import Environment
from infra.qdrant_client import QdrantClient


SEARCH_TEXT = "caffe"


def normalize_embedding(payload: list[float] | list[list[float]]) -> list[float]:
    if payload and isinstance(payload[0], list):
        return payload[0]
    return payload  # type: ignore[return-value]


def main() -> None:
    env = Environment()
    embedding_client = EmbeddingClient(base_url=env.EMBEDDING_API_BASE_URL)
    qdrant_client = QdrantClient(base_url=env.QDRANT_URL)

    query_vector = normalize_embedding(embedding_client.embed(SEARCH_TEXT))
    results = qdrant_client.search(
        collection_name=env.QDRANT_COLLECTION_NAME,
        query_vector=query_vector,
        limit=3,
    )

    print(f"Busca: {SEARCH_TEXT}")
    print(f"Collection: {env.QDRANT_COLLECTION_NAME}")
    print("Resultados:")
    for item in results:
        payload = item.get("payload", {})
        score = item.get("score", 0.0)
        print(
            f"- score={score:.4f} | "
            f"produto={payload.get('name')} | "
            f"descricao={payload.get('description')}"
        )


if __name__ == "__main__":
    main()
