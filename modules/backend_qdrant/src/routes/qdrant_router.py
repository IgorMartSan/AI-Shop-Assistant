from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Path, Query

from repositories.qdrant_repository import QdrantRepositoryError
from schemas.qdrant_schemas import (
    QdrantBatchDeleteRequest,
    QdrantBatchDeleteResponse,
    QdrantCreatePointRequest,
    QdrantCreatePointResponse,
    QdrantDeletePointRequest,
    QdrantDeletePointResponse,
    QdrantGetPointRequest,
    QdrantGetPointResponse,
    QdrantListAllPointsResponse,
    QdrantListCollectionsResponse,
    QdrantListPointsRequest,
    QdrantListPointsResponse,
    QdrantSearchRequest,
    QdrantSearchResponse,
    QdrantUpdatePointRequest,
    QdrantUpdatePointResponse,
)
from use_cases.qdrant_use_cases import QdrantUseCases

router = APIRouter(prefix="/qdrant", tags=["Qdrant"])
logger = logging.getLogger(__name__)

ERROR_RESPONSES = {
    422: {
        "description": "Erro de validacao nos parametros enviados para a rota.",
    },
    502: {
        "description": "Falha de comunicacao entre a API e o Qdrant.",
    },
}


@router.get(
    "/collections",
    response_model=QdrantListCollectionsResponse,
    summary="Listar collections",
    description="Retorna todas as collections disponiveis na instancia do Qdrant.",
    response_description="Lista de collections cadastradas no Qdrant.",
    responses=ERROR_RESPONSES,
)
def list_collections():
    try:
        result = QdrantUseCases.list_collections()
        return {"result": result}
    except QdrantRepositoryError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post(
    "/search",
    response_model=QdrantSearchResponse,
    summary="Buscar vetores similares",
    description=(
        "Executa uma busca por similaridade vetorial em uma collection do Qdrant "
        "e retorna os pontos mais proximos do vetor informado."
    ),
    response_description="Lista de pontos similares retornados pelo Qdrant.",
    responses=ERROR_RESPONSES,
)
def search_qdrant(payload: QdrantSearchRequest):
    try:
        result = QdrantUseCases.search(payload)
        return {"result": result}
    except QdrantRepositoryError as exc:
        logger.exception(
            "Qdrant search failed | collection_name=%s | limit=%s",
            payload.collection_name,
            payload.limit,
        )
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.put(
    "/points",
    response_model=QdrantCreatePointResponse,
    summary="Criar ou sobrescrever pontos",
    description=(
        "Insere pontos em uma collection do Qdrant. Se um ID ja existir, "
        "o ponto correspondente pode ser sobrescrito conforme o comportamento do Qdrant."
    ),
    response_description="Resultado da operacao de escrita dos pontos.",
    responses=ERROR_RESPONSES,
)
def create_points(payload: QdrantCreatePointRequest):
    try:
        result = QdrantUseCases.create_points(payload)
        return result
    except QdrantRepositoryError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get(
    "/points/{collection_name}/{point_id}",
    response_model=QdrantGetPointResponse,
    summary="Consultar um ponto por ID",
    description="Recupera um ponto especifico de uma collection a partir do ID informado.",
    response_description="Dados do ponto encontrado, quando existir.",
    responses=ERROR_RESPONSES,
)
def get_point(
    collection_name: str = Path(
        ...,
        description="Nome da collection onde o ponto esta armazenado.",
        examples=["products_embedding_test"],
    ),
    point_id: str = Path(
        ...,
        description="ID do ponto que sera consultado.",
        examples=["101"],
    ),
):
    try:
        request = QdrantGetPointRequest(
            collection_name=collection_name, point_id=point_id
        )
        result = QdrantUseCases.get_point(request)
        return {"result": result}
    except QdrantRepositoryError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.patch(
    "/points/{collection_name}/{point_id}",
    response_model=QdrantUpdatePointResponse,
    summary="Atualizar um ponto",
    description=(
        "Atualiza o vetor, o payload ou ambos em um ponto existente. "
        "Os valores de `collection_name` e `point_id` do corpo sao ignorados e substituidos "
        "pelos parametros da URL."
    ),
    response_description="Resultado da operacao de atualizacao.",
    responses=ERROR_RESPONSES,
)
def update_point(
    collection_name: str = Path(
        ...,
        description="Nome da collection onde o ponto sera atualizado.",
        examples=["products_embedding_test"],
    ),
    point_id: str = Path(
        ...,
        description="ID do ponto que sera atualizado.",
        examples=["101"],
    ),
    payload: QdrantUpdatePointRequest = ...,
):
    try:
        # Override the path parameters
        payload.collection_name = collection_name
        payload.point_id = point_id
        result = QdrantUseCases.update_point(payload)
        return result
    except QdrantRepositoryError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.delete(
    "/points/{collection_name}/{point_id}",
    response_model=QdrantDeletePointResponse,
    summary="Excluir um ponto",
    description="Remove um ponto especifico de uma collection do Qdrant pelo ID.",
    response_description="Resultado da operacao de exclusao.",
    responses=ERROR_RESPONSES,
)
def delete_point(
    collection_name: str = Path(
        ...,
        description="Nome da collection de origem do ponto.",
        examples=["products_embedding_test"],
    ),
    point_id: str = Path(
        ...,
        description="ID do ponto que sera removido.",
        examples=["101"],
    ),
):
    try:
        request = QdrantDeletePointRequest(
            collection_name=collection_name, point_id=point_id
        )
        result = QdrantUseCases.delete_point(request)
        return result
    except QdrantRepositoryError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post(
    "/points/delete",
    response_model=QdrantBatchDeleteResponse,
    summary="Excluir varios pontos",
    description="Remove varios pontos de uma collection em uma unica requisicao.",
    response_description="Resultado da operacao de exclusao em lote.",
    responses=ERROR_RESPONSES,
)
def delete_points(payload: QdrantBatchDeleteRequest):
    try:
        result = QdrantUseCases.delete_points(payload)
        return result
    except QdrantRepositoryError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get(
    "/collections/{collection_name}/points",
    response_model=QdrantListPointsResponse,
    summary="Listar pontos com paginacao",
    description=(
        "Lista os pontos armazenados em uma collection especifica com suporte "
        "a paginacao por `offset`."
    ),
    response_description="Lista paginada de pontos da collection informada.",
    responses=ERROR_RESPONSES,
)
def list_collection_points(
    collection_name: str = Path(
        ...,
        description="Nome da collection que sera listada.",
        examples=["products_embedding_test"],
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=1000,
        description="Quantidade maxima de pontos retornados por pagina.",
        examples=[100],
    ),
    offset: int | None = Query(
        default=None,
        ge=0,
        description="Offset de paginacao para continuar a leitura da collection.",
        examples=[0],
    ),
    with_payload: bool = Query(
        default=True,
        description="Define se o payload de cada ponto deve ser retornado.",
    ),
    with_vector: bool = Query(
        default=False,
        description="Define se os vetores armazenados devem ser retornados.",
    ),
):
    try:
        request = QdrantListPointsRequest(
            collection_name=collection_name,
            limit=limit,
            offset=offset,
            with_payload=with_payload,
            with_vector=with_vector,
        )
        result = QdrantUseCases.list_points(request)
        return result
    except QdrantRepositoryError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get(
    "/points/{collection_name}",
    response_model=QdrantListAllPointsResponse,
    summary="Listar todos os pontos da collection",
    description=(
        "Busca todos os pontos de uma collection, percorrendo internamente todas "
        "as paginas retornadas pelo Qdrant."
    ),
    response_description="Lista completa de pontos da collection.",
    responses=ERROR_RESPONSES,
)
def list_all_points(
    collection_name: str = Path(
        ...,
        description="Nome da collection que sera listada.",
        examples=["products_embedding_test"],
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=1000,
        description="Quantidade de pontos buscados por lote interno ate completar a collection.",
        examples=[100],
    ),
    with_payload: bool = Query(
        default=True,
        description="Define se o payload de cada ponto deve ser retornado.",
    ),
    with_vector: bool = Query(
        default=False,
        description="Define se os vetores armazenados devem ser retornados.",
    ),
):
    try:
        request = QdrantListPointsRequest(
            collection_name=collection_name,
            limit=limit,
            offset=None,
            with_payload=with_payload,
            with_vector=with_vector,
        )
        result = QdrantUseCases.list_all_points(request)
        return result
    except QdrantRepositoryError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
