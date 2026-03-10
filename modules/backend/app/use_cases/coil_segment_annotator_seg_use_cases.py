from __future__ import annotations

from fastapi import HTTPException

from db.model import CoilSegmentAnnotatorSegmentation as CoilSegmentAnnotatorSegmentationModel
from repositories.coil_segment_annotator_seg_repository import CoilSegmentAnnotatorSegRepository
from repositories.coil_segment_repository import CoilSegmentRepository
from repositories.annotator_repository import AnnotatorRepository
from schemas.coil_segment_annotator_seg_schemas import (
    CoilSegmentAnnotatorSegCreateSchema,
    CoilSegmentAnnotatorSegUpdateSchema,
)


class CoilSegmentAnnotatorSegUseCases:
    @staticmethod
    def create(
        payload: CoilSegmentAnnotatorSegCreateSchema,
        repository: CoilSegmentAnnotatorSegRepository,
        segment_repository: CoilSegmentRepository,
        annotator_repository: AnnotatorRepository,
    ) -> CoilSegmentAnnotatorSegmentationModel:
        if not segment_repository.get_by_id(payload.coil_segment_id):
            raise HTTPException(status_code=404, detail="Coil segment not found")
        if not annotator_repository.get_by_id(payload.model_id):
            raise HTTPException(status_code=404, detail="Annotator not found")
        segmentation = CoilSegmentAnnotatorSegmentationModel(**payload.model_dump())
        return repository.create(segmentation)

    @staticmethod
    def list(repository: CoilSegmentAnnotatorSegRepository, coil_segment_id: int | None, model_id: int | None, skip: int = 0, limit: int = 100):
        return repository.list(coil_segment_id=coil_segment_id, model_id=model_id, skip=skip, limit=limit)

    @staticmethod
    def get_by_id(segmentation_id: int, repository: CoilSegmentAnnotatorSegRepository) -> CoilSegmentAnnotatorSegmentationModel:
        segmentation = repository.get_by_id(segmentation_id)
        if not segmentation:
            raise HTTPException(status_code=404, detail="Segmentation not found")
        return segmentation

    @staticmethod
    def update(
        segmentation_id: int,
        payload: CoilSegmentAnnotatorSegUpdateSchema,
        repository: CoilSegmentAnnotatorSegRepository,
        segment_repository: CoilSegmentRepository,
        annotator_repository: AnnotatorRepository,
    ) -> CoilSegmentAnnotatorSegmentationModel:
        segmentation = repository.get_by_id(segmentation_id)
        if not segmentation:
            raise HTTPException(status_code=404, detail="Segmentation not found")
        if payload.coil_segment_id is not None:
            if not segment_repository.get_by_id(payload.coil_segment_id):
                raise HTTPException(status_code=404, detail="Coil segment not found")
            segmentation.coil_segment_id = payload.coil_segment_id
        if payload.model_id is not None:
            if not annotator_repository.get_by_id(payload.model_id):
                raise HTTPException(status_code=404, detail="Annotator not found")
            segmentation.model_id = payload.model_id
        for key, value in payload.model_dump(exclude_unset=True).items():
            if key in {"coil_segment_id", "model_id"}:
                continue
            setattr(segmentation, key, value)
        return repository.update(segmentation)

    @staticmethod
    def delete(segmentation_id: int, repository: CoilSegmentAnnotatorSegRepository) -> None:
        segmentation = repository.get_by_id(segmentation_id)
        if not segmentation:
            raise HTTPException(status_code=404, detail="Segmentation not found")
        repository.delete(segmentation)
