from __future__ import annotations

from infra.embedding_client import EmbeddingClient
from infra.environment import Environment
from infra.qdrant_client import QdrantClient


PRODUCTS = [
    {
        "id": 1,
        "name": "Notebook Gamer Nitro 16",
        "description": (
            "Notebook com processador Intel Core i7, 16 GB de RAM, SSD de 1 TB "
            "e placa RTX 4060. Ideal para jogos pesados, edicao de video e modelagem 3D."
        ),
    },
    {
        "id": 2,
        "name": "Smartphone Galaxy Vision",
        "description": (
            "Celular com camera tripla de 108 MP, tela AMOLED de 6.7 polegadas, "
            "bateria de longa duracao e suporte a 5G."
        ),
    },
    {
        "id": 3,
        "name": "Fone Bluetooth Sound Max",
        "description": (
            "Fone sem fio com cancelamento de ruido, som grave reforcado, "
            "microfone para chamadas e autonomia de 30 horas."
        ),
    },
    {
        "id": 4,
        "name": "Cafeteira Expresso Barista Pro",
        "description": (
            "Cafeteira automatica com moedor integrado, vaporizador de leite e "
            "programas para espresso, cappuccino e latte."
        ),
    },
]


def normalize_embedding(payload: list[float] | list[list[float]]) -> list[float]:
    if payload and isinstance(payload[0], list):
        return payload[0]
    return payload  # type: ignore[return-value]


def main() -> None:
    env = Environment()
    embedding_client = EmbeddingClient(base_url=env.EMBEDDING_API_BASE_URL)
    qdrant_client = QdrantClient(base_url=env.QDRANT_URL)

    first_embedding = normalize_embedding(embedding_client.embed(PRODUCTS[0]["description"]))
    qdrant_client.recreate_collection(
        collection_name=env.QDRANT_COLLECTION_NAME,
        vector_size=len(first_embedding),
    )

    points = [
        {
            "id": product["id"],
            "vector": normalize_embedding(embedding_client.embed(product["description"])),
            "payload": {
                "name": product["name"],
                "description": product["description"],
            },
        }
        for product in PRODUCTS
    ]

    qdrant_client.upsert_points(env.QDRANT_COLLECTION_NAME, points)

    print(f"Collection: {env.QDRANT_COLLECTION_NAME}")
    print(f"Produtos inseridos: {len(points)}")
    for product in PRODUCTS:
        print(f"- {product['id']}: {product['name']}")


if __name__ == "__main__":
    main()
