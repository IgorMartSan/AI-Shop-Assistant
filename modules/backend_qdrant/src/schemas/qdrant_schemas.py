from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class QdrantSearchRequest(BaseModel):
    collection_name: str = Field(
        ...,
        min_length=1,
        description="Nome da collection no Qdrant onde a busca vetorial sera executada.",
        examples=["products_embedding_test"],
    )
    query_vector: list[float] = Field(
        ...,
        min_length=1,
        description="Vetor de embedding usado como consulta de similaridade.",
        examples=[[0.12, -0.45, 0.91, 0.07]],
    )
    limit: int = Field(
        default=3,
        ge=1,
        le=100,
        description="Quantidade maxima de pontos retornados na busca.",
        examples=[5],
    )
    with_payload: bool = Field(
        default=True,
        description="Define se os metadados de cada ponto devem ser incluidos na resposta.",
        examples=[True],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "collection_name": "products_embedding_test",
                "query_vector": [0.12, -0.45, 0.91, 0.07],
                "limit": 5,
                "with_payload": True,
            }
        }
    }


class QdrantSearchResponse(BaseModel):
    """Resultado da busca vetorial."""

    result: list[dict[str, Any]]


class QdrantCollectionInfo(BaseModel):
    name: str = Field(
        ...,
        description="Nome da collection cadastrada no Qdrant.",
        examples=["products_embedding_test"],
    )


class QdrantListCollectionsResponse(BaseModel):
    result: list[QdrantCollectionInfo]


class PointPayload(BaseModel):
    """Payload genérico para pontos Qdrant"""

    pass


class QdrantPoint(BaseModel):
    id: str | int = Field(..., description="ID unico do ponto.", examples=[101])
    vector: list[float] = Field(
        ...,
        min_length=1,
        description="Vetor de embedding armazenado no Qdrant.",
        examples=[[0.12, -0.45, 0.91, 0.07]],
    )
    payload: Optional[dict[str, Any]] = Field(
        default=None,
        description="Dados adicionais associados ao ponto, como nome, SKU ou categoria.",
        examples=[{"name": "Notebook Dell", "category": "informatica"}],
    )


class QdrantCreatePointRequest(BaseModel):
    collection_name: str = Field(
        ...,
        min_length=1,
        description="Nome da collection onde os pontos serao inseridos.",
        examples=["products_embedding_test"],
    )
    points: list[QdrantPoint] = Field(
        ...,
        min_length=1,
        description="Lista de pontos a serem criados ou sobrescritos.",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "collection_name": "products_embedding_test",
                "points": [
                    {
                        "id": 101,
                        "vector": [0.12, -0.45, 0.91, 0.07],
                        "payload": {
                            "name": "Notebook Dell",
                            "category": "informatica",
                        },
                    }
                ],
            }
        }
    }


class QdrantCreatePointResponse(BaseModel):
    operation_id: int
    status: str


class QdrantGetPointRequest(BaseModel):
    collection_name: str = Field(
        ...,
        min_length=1,
        description="Nome da collection onde o ponto esta armazenado.",
    )
    point_id: str | int = Field(..., description="Identificador unico do ponto.")


class QdrantGetPointResponse(BaseModel):
    result: Optional[dict[str, Any]]


class QdrantUpdatePointRequest(BaseModel):
    collection_name: str = Field(
        ...,
        min_length=1,
        description="Nome da collection onde o ponto sera atualizado.",
    )
    point_id: str | int = Field(..., description="Identificador unico do ponto.")
    vector: Optional[list[float]] = Field(
        default=None,
        min_length=1,
        description="Novo vetor de embedding do ponto. Opcional se apenas o payload for atualizado.",
        examples=[[0.14, -0.41, 0.88, 0.11]],
    )
    payload: Optional[dict[str, Any]] = Field(
        default=None,
        description="Novo payload parcial ou completo do ponto.",
        examples=[{"name": "Notebook Dell G15", "stock": 12}],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "collection_name": "products_embedding_test",
                "point_id": 101,
                "vector": [0.14, -0.41, 0.88, 0.11],
                "payload": {"name": "Notebook Dell G15", "stock": 12},
            }
        }
    }


class QdrantUpdatePointResponse(BaseModel):
    operation_id: int
    status: str


class QdrantDeletePointRequest(BaseModel):
    collection_name: str = Field(
        ...,
        min_length=1,
        description="Nome da collection de origem do ponto.",
    )
    point_id: str | int = Field(..., description="Identificador unico do ponto.")


class QdrantDeletePointResponse(BaseModel):
    operation_id: int
    status: str


class QdrantBatchDeleteRequest(BaseModel):
    collection_name: str = Field(
        ...,
        min_length=1,
        description="Nome da collection de onde os pontos serao removidos.",
        examples=["products_embedding_test"],
    )
    point_ids: list[str | int] = Field(
        ...,
        min_length=1,
        description="Lista de IDs dos pontos a serem removidos.",
        examples=[[101, 102, 103]],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "collection_name": "products_embedding_test",
                "point_ids": [101, 102, 103],
            }
        }
    }


class QdrantBatchDeleteResponse(BaseModel):
    operation_id: int
    status: str


class QdrantListPointsRequest(BaseModel):
    collection_name: str = Field(
        ...,
        min_length=1,
        description="Nome da collection que sera listada.",
    )
    limit: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Quantidade maxima de pontos retornados por pagina.",
        examples=[100],
    )
    offset: Optional[int] = Field(
        default=None,
        ge=0,
        description="Offset numerico para paginacao da listagem.",
        examples=[0],
    )
    with_payload: bool = Field(
        default=True,
        description="Inclui o payload de cada ponto na resposta.",
        examples=[True],
    )
    with_vector: bool = Field(
        default=False,
        description="Inclui o vetor armazenado de cada ponto na resposta.",
        examples=[False],
    )


class QdrantListPointsResponse(BaseModel):
    result: list[dict[str, Any]]
    next_page_offset: Optional[int]


class QdrantListAllPointsResponse(BaseModel):
    result: list[dict[str, Any]]
    total: int
