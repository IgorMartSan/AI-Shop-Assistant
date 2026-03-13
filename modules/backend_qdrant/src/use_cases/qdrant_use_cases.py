from __future__ import annotations

from typing import Optional

from repositories.qdrant_repository import QdrantRepository
from schemas.qdrant_schemas import (
    QdrantBatchDeleteRequest,
    QdrantCreatePointRequest,
    QdrantDeletePointRequest,
    QdrantGetPointRequest,
    QdrantListPointsRequest,
    QdrantListPointsPageRequest,
    QdrantSearchRequest,
    QdrantUpdatePointRequest,
)


class QdrantUseCases:
    @staticmethod
    def list_collections():
        repository = QdrantRepository()
        return repository.list_collections()

    @staticmethod
    def search(request_data: QdrantSearchRequest):
        repository = QdrantRepository()
        return repository.search(
            collection_name=request_data.collection_name,
            query_vector=request_data.query_vector,
            limit=request_data.limit,
            with_payload=request_data.with_payload,
        )

    @staticmethod
    def create_points(request_data: QdrantCreatePointRequest):
        repository = QdrantRepository()
        points = [
            {
                "id": point.id,
                "vector": point.vector,
                "payload": point.payload,
            }
            for point in request_data.points
        ]
        return repository.create_points(
            collection_name=request_data.collection_name,
            points=points,
        )

    @staticmethod
    def get_point(request_data: QdrantGetPointRequest):
        repository = QdrantRepository()
        return repository.get_point(
            collection_name=request_data.collection_name,
            point_id=request_data.point_id,
        )

    @staticmethod
    def update_point(request_data: QdrantUpdatePointRequest):
        repository = QdrantRepository()
        return repository.update_point(
            collection_name=request_data.collection_name,
            point_id=request_data.point_id,
            vector=request_data.vector,
            payload=request_data.payload,
        )

    @staticmethod
    def delete_point(request_data: QdrantDeletePointRequest):
        repository = QdrantRepository()
        return repository.delete_point(
            collection_name=request_data.collection_name,
            point_id=request_data.point_id,
        )

    @staticmethod
    def delete_points(request_data: QdrantBatchDeleteRequest):
        repository = QdrantRepository()
        return repository.delete_points(
            collection_name=request_data.collection_name,
            point_ids=request_data.point_ids,
        )

    @staticmethod
    def list_points(request_data: QdrantListPointsRequest):
        repository = QdrantRepository()
        return repository.list_points(
            collection_name=request_data.collection_name,
            limit=request_data.limit,
            offset=request_data.offset,
            with_payload=request_data.with_payload,
            with_vector=request_data.with_vector,
        )

    @staticmethod
    def list_all_points(request_data: QdrantListPointsRequest):
        repository = QdrantRepository()
        return repository.list_all_points(
            collection_name=request_data.collection_name,
            batch_limit=request_data.limit,
            with_payload=request_data.with_payload,
            with_vector=request_data.with_vector,
        )

    @staticmethod
    def list_points_page(request_data: QdrantListPointsPageRequest):
        repository = QdrantRepository()
        return repository.list_points_page(
            collection_name=request_data.collection_name,
            page=request_data.page,
            limit=request_data.limit,
            with_payload=request_data.with_payload,
            with_vector=request_data.with_vector,
            query=request_data.query,
        )
