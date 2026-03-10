from __future__ import annotations

from fastapi import HTTPException

from db.model import Annotator as AnnotatorModel
from repositories.annotator_repository import AnnotatorRepository
from schemas.annotator_schemas import AnnotatorCreateSchema, AnnotatorUpdateSchema


class AnnotatorUseCases:
    @staticmethod
    def create(payload: AnnotatorCreateSchema, repository: AnnotatorRepository) -> AnnotatorModel:
        existing = repository.get_by_name(payload.name)
        if existing:
            raise HTTPException(status_code=409, detail="Annotator name already registered")
        annotator = AnnotatorModel(**payload.model_dump())
        return repository.create(annotator)

    @staticmethod
    def list(repository: AnnotatorRepository, skip: int = 0, limit: int = 100, name: str | None = None) -> list[AnnotatorModel]:
        return repository.list(skip=skip, limit=limit, name=name)

    @staticmethod
    def get_by_id(annotator_id: int, repository: AnnotatorRepository) -> AnnotatorModel:
        annotator = repository.get_by_id(annotator_id)
        if not annotator:
            raise HTTPException(status_code=404, detail="Annotator not found")
        return annotator

    @staticmethod
    def update(annotator_id: int, payload: AnnotatorUpdateSchema, repository: AnnotatorRepository) -> AnnotatorModel:
        annotator = repository.get_by_id(annotator_id)
        if not annotator:
            raise HTTPException(status_code=404, detail="Annotator not found")
        if payload.name and payload.name != annotator.name:
            existing = repository.get_by_name(payload.name)
            if existing and existing.id != annotator_id:
                raise HTTPException(status_code=409, detail="Annotator name already registered")
            annotator.name = payload.name
        if payload.comment is not None:
            annotator.comment = payload.comment
        if payload.model_metadata is not None:
            annotator.model_metadata = payload.model_metadata
        return repository.update(annotator)

    @staticmethod
    def delete(annotator_id: int, repository: AnnotatorRepository) -> None:
        annotator = repository.get_by_id(annotator_id)
        if not annotator:
            raise HTTPException(status_code=404, detail="Annotator not found")
        repository.delete(annotator)
