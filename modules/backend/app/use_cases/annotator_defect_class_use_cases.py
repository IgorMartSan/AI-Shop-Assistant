from __future__ import annotations

from fastapi import HTTPException

from db.model import AnnotatorDefectClass as AnnotatorDefectClassModel
from repositories.annotator_defect_class_repository import AnnotatorDefectClassRepository
from repositories.annotator_repository import AnnotatorRepository
from schemas.annotator_defect_class_schemas import (
    AnnotatorDefectClassCreateSchema,
    AnnotatorDefectClassUpdateSchema,
)


class AnnotatorDefectClassUseCases:
    @staticmethod
    def create(
        payload: AnnotatorDefectClassCreateSchema,
        repository: AnnotatorDefectClassRepository,
        annotator_repository: AnnotatorRepository,
    ) -> AnnotatorDefectClassModel:
        annotator = annotator_repository.get_by_id(payload.model_id)
        if not annotator:
            raise HTTPException(status_code=404, detail="Annotator not found")
        model_class = AnnotatorDefectClassModel(**payload.model_dump())
        return repository.create(model_class)

    @staticmethod
    def list(repository: AnnotatorDefectClassRepository, model_id: int | None, skip: int = 0, limit: int = 100):
        return repository.list(model_id=model_id, skip=skip, limit=limit)

    @staticmethod
    def get_by_id(class_id: int, repository: AnnotatorDefectClassRepository) -> AnnotatorDefectClassModel:
        model_class = repository.get_by_id(class_id)
        if not model_class:
            raise HTTPException(status_code=404, detail="Annotator defect class not found")
        return model_class

    @staticmethod
    def update(
        class_id: int,
        payload: AnnotatorDefectClassUpdateSchema,
        repository: AnnotatorDefectClassRepository,
        annotator_repository: AnnotatorRepository,
    ) -> AnnotatorDefectClassModel:
        model_class = repository.get_by_id(class_id)
        if not model_class:
            raise HTTPException(status_code=404, detail="Annotator defect class not found")
        if payload.model_id is not None:
            annotator = annotator_repository.get_by_id(payload.model_id)
            if not annotator:
                raise HTTPException(status_code=404, detail="Annotator not found")
            model_class.model_id = payload.model_id
        for key, value in payload.model_dump(exclude_unset=True).items():
            if key == "model_id":
                continue
            setattr(model_class, key, value)
        return repository.update(model_class)

    @staticmethod
    def delete(class_id: int, repository: AnnotatorDefectClassRepository) -> None:
        model_class = repository.get_by_id(class_id)
        if not model_class:
            raise HTTPException(status_code=404, detail="Annotator defect class not found")
        repository.delete(model_class)
