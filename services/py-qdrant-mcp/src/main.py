from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from qdrant_client import QdrantClient
from qdrant_client.http import models

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY") or None
DEFAULT_COLLECTION = os.getenv("QDRANT_COLLECTION", "products")
DEFAULT_VECTOR_NAME = os.getenv("QDRANT_VECTOR_NAME") or None

mcp = FastMCP("qdrant-mcp")

client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
)


def _build_filter(
    category: str | None = None,
    brand: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    in_stock_only: bool = False,
) -> models.Filter | None:
    must: list[models.FieldCondition] = []

    if category:
        must.append(
            models.FieldCondition(
                key="category",
                match=models.MatchValue(value=category),
            )
        )

    if brand:
        must.append(
            models.FieldCondition(
                key="brand",
                match=models.MatchValue(value=brand),
            )
        )

    if min_price is not None or max_price is not None:
        must.append(
            models.FieldCondition(
                key="price",
                range=models.Range(
                    gte=min_price,
                    lte=max_price,
                ),
            )
        )

    if in_stock_only:
        must.append(
            models.FieldCondition(
                key="stock",
                range=models.Range(gt=0),
            )
        )

    if not must:
        return None

    return models.Filter(must=must)


@mcp.tool()
def collection_info(collection_name: str = DEFAULT_COLLECTION) -> dict[str, Any]:
    """
    Retorna metadados básicos da collection do Qdrant.
    Use quando precisar inspecionar a collection antes de buscar.
    """
    info = client.get_collection(collection_name=collection_name)

    config = getattr(info, "config", None)
    points_count = getattr(info, "points_count", None)
    vectors_count = getattr(info, "vectors_count", None)

    return {
        "collection_name": collection_name,
        "points_count": points_count,
        "vectors_count": vectors_count,
        "config": str(config) if config is not None else None,
    }


@mcp.tool()
def search_by_vector(
    vector: list[float],
    collection_name: str = DEFAULT_COLLECTION,
    limit: int = 5,
    category: str | None = None,
    brand: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    in_stock_only: bool = False,
    with_payload: bool = True,
) -> list[dict[str, Any]]:
    """
    Busca itens parecidos no Qdrant usando um vetor já gerado por outro serviço.
    Ideal quando seu sistema já possui um embedder separado.
    """
    query_filter = _build_filter(
        category=category,
        brand=brand,
        min_price=min_price,
        max_price=max_price,
        in_stock_only=in_stock_only,
    )

    kwargs: dict[str, Any] = {
        "collection_name": collection_name,
        "query": vector,
        "query_filter": query_filter,
        "limit": limit,
        "with_payload": with_payload,
    }

    if DEFAULT_VECTOR_NAME:
        kwargs["using"] = DEFAULT_VECTOR_NAME

    result = client.query_points(**kwargs)

    return [
        {
            "id": point.id,
            "score": point.score,
            "payload": point.payload,
        }
        for point in result.points
    ]


@mcp.tool()
def search_by_id(
    point_id: str | int,
    collection_name: str = DEFAULT_COLLECTION,
    limit: int = 5,
    with_payload: bool = True,
) -> list[dict[str, Any]]:
    """
    Busca itens similares a partir do ID de um ponto já existente no Qdrant.
    Útil para recomendação do tipo 'itens parecidos com este produto'.
    """
    result = client.query_points(
        collection_name=collection_name,
        query=point_id,
        limit=limit,
        with_payload=with_payload,
    )

    return [
        {
            "id": point.id,
            "score": point.score,
            "payload": point.payload,
        }
        for point in result.points
    ]


@mcp.tool()
def search_text_fastembed(
    text: str,
    collection_name: str = DEFAULT_COLLECTION,
    limit: int = 5,
    category: str | None = None,
    brand: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    in_stock_only: bool = False,
    with_payload: bool = True,
) -> list[dict[str, Any]]:
    """
    Busca semântica por texto usando embedding local via FastEmbed no cliente Qdrant.
    Use só se você optar por instalar qdrant-client com suporte a fastembed.
    """
    query_filter = _build_filter(
        category=category,
        brand=brand,
        min_price=min_price,
        max_price=max_price,
        in_stock_only=in_stock_only,
    )

    result = client.query(
        collection_name=collection_name,
        query_text=text,
        query_filter=query_filter,
        limit=limit,
    )

    # Em algumas versões/helpers, query() pode devolver objetos levemente diferentes.
    # Este bloco tenta padronizar a saída.
    normalized: list[dict[str, Any]] = []

    for item in result:
        normalized.append(
            {
                "id": getattr(item, "id", None),
                "score": getattr(item, "score", None),
                "payload": getattr(item, "payload", None),
            }
        )

    return normalized


if __name__ == "__main__":
    mcp.run()