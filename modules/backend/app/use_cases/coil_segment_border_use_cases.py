from __future__ import annotations

from fastapi import HTTPException

from db.model import CoilSegmentBorder as CoilSegmentBorderModel
from repositories.coil_segment_border_repository import CoilSegmentBorderRepository
from repositories.coil_segment_repository import CoilSegmentRepository
from schemas.coil_segment_border_schemas import (
    CoilSegmentBorderCreateSchema,
    CoilSegmentBorderUpdateSchema,
)


class CoilSegmentBorderUseCases:
    @staticmethod
    def create(
        payload: CoilSegmentBorderCreateSchema,
        repository: CoilSegmentBorderRepository,
        segment_repository: CoilSegmentRepository,
    ) -> CoilSegmentBorderModel:
        segment = segment_repository.get_by_id(payload.coil_segment_id)
        if not segment:
            raise HTTPException(status_code=404, detail="Coil segment not found")
        border = CoilSegmentBorderModel(**payload.model_dump())
        return repository.create(border)

    @staticmethod
    def list(repository: CoilSegmentBorderRepository, coil_segment_id: int | None, skip: int = 0, limit: int = 100):
        return repository.list(coil_segment_id=coil_segment_id, skip=skip, limit=limit)

    @staticmethod
    def get_by_id(border_id: int, repository: CoilSegmentBorderRepository) -> CoilSegmentBorderModel:
        border = repository.get_by_id(border_id)
        if not border:
            raise HTTPException(status_code=404, detail="Coil segment border not found")
        return border

    @staticmethod
    def update(
        border_id: int,
        payload: CoilSegmentBorderUpdateSchema,
        repository: CoilSegmentBorderRepository,
        segment_repository: CoilSegmentRepository,
    ) -> CoilSegmentBorderModel:
        border = repository.get_by_id(border_id)
        if not border:
            raise HTTPException(status_code=404, detail="Coil segment border not found")
        if payload.coil_segment_id is not None:
            segment = segment_repository.get_by_id(payload.coil_segment_id)
            if not segment:
                raise HTTPException(status_code=404, detail="Coil segment not found")
            border.coil_segment_id = payload.coil_segment_id
        for key, value in payload.model_dump(exclude_unset=True).items():
            if key == "coil_segment_id":
                continue
            setattr(border, key, value)
        return repository.update(border)

    @staticmethod
    def delete(border_id: int, repository: CoilSegmentBorderRepository) -> None:
        border = repository.get_by_id(border_id)
        if not border:
            raise HTTPException(status_code=404, detail="Coil segment border not found")
        repository.delete(border)
