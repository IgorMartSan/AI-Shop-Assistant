from __future__ import annotations

from fastapi import HTTPException

from db.model import CoilSegmentAnnotatorBBox as CoilSegmentAnnotatorBBoxModel
from repositories.coil_segment_annotator_bbox_repository import CoilSegmentAnnotatorBBoxRepository
from repositories.coil_segment_repository import CoilSegmentRepository
from repositories.annotator_repository import AnnotatorRepository
from repositories.annotator_defect_class_repository import AnnotatorDefectClassRepository
from schemas.coil_segment_annotator_bbox_schemas import (
    CoilSegmentAnnotatorBBoxCreateSchema,
    CoilSegmentAnnotatorBBoxUpdateSchema,
)


class CoilSegmentAnnotatorBBoxUseCases:
    @staticmethod
    def create(
        payload: CoilSegmentAnnotatorBBoxCreateSchema,
        repository: CoilSegmentAnnotatorBBoxRepository,
        segment_repository: CoilSegmentRepository,
        annotator_repository: AnnotatorRepository,
        model_class_repository: AnnotatorDefectClassRepository,
    ) -> CoilSegmentAnnotatorBBoxModel:
        if not segment_repository.get_by_id(payload.coil_segment_id):
            raise HTTPException(status_code=404, detail="Coil segment not found")
        if not annotator_repository.get_by_id(payload.model_id):
            raise HTTPException(status_code=404, detail="Annotator not found")
        if not model_class_repository.get_by_id(payload.model_class_id):
            raise HTTPException(status_code=404, detail="Annotator defect class not found")
        bbox = CoilSegmentAnnotatorBBoxModel(**payload.model_dump())
        return repository.create(bbox)

    @staticmethod
    def list(
        repository: CoilSegmentAnnotatorBBoxRepository,
        coil_segment_id: int | None,
        model_id: int | None,
        model_class_id: int | None,
        confidence_min: float | None,
        skip: int = 0,
        limit: int = 100,
    ):
        return repository.list(
            coil_segment_id=coil_segment_id,
            model_id=model_id,
            model_class_id=model_class_id,
            confidence_min=confidence_min,
            skip=skip,
            limit=limit,
        )

    @staticmethod
    def get_by_id(bbox_id: int, repository: CoilSegmentAnnotatorBBoxRepository) -> CoilSegmentAnnotatorBBoxModel:
        bbox = repository.get_by_id(bbox_id)
        if not bbox:
            raise HTTPException(status_code=404, detail="BBox not found")
        return bbox

    @staticmethod
    def update(
        bbox_id: int,
        payload: CoilSegmentAnnotatorBBoxUpdateSchema,
        repository: CoilSegmentAnnotatorBBoxRepository,
        segment_repository: CoilSegmentRepository,
        annotator_repository: AnnotatorRepository,
        model_class_repository: AnnotatorDefectClassRepository,
    ) -> CoilSegmentAnnotatorBBoxModel:
        bbox = repository.get_by_id(bbox_id)
        if not bbox:
            raise HTTPException(status_code=404, detail="BBox not found")
        if payload.coil_segment_id is not None:
            if not segment_repository.get_by_id(payload.coil_segment_id):
                raise HTTPException(status_code=404, detail="Coil segment not found")
            bbox.coil_segment_id = payload.coil_segment_id
        if payload.model_id is not None:
            if not annotator_repository.get_by_id(payload.model_id):
                raise HTTPException(status_code=404, detail="Annotator not found")
            bbox.model_id = payload.model_id
        if payload.model_class_id is not None:
            if not model_class_repository.get_by_id(payload.model_class_id):
                raise HTTPException(status_code=404, detail="Annotator defect class not found")
            bbox.model_class_id = payload.model_class_id
        for key, value in payload.model_dump(exclude_unset=True).items():
            if key in {"coil_segment_id", "model_id", "model_class_id"}:
                continue
            setattr(bbox, key, value)
        return repository.update(bbox)

    @staticmethod
    def delete(bbox_id: int, repository: CoilSegmentAnnotatorBBoxRepository) -> None:
        bbox = repository.get_by_id(bbox_id)
        if not bbox:
            raise HTTPException(status_code=404, detail="BBox not found")
        repository.delete(bbox)
