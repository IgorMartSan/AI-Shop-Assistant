from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import HTTPException

from db.model import CoilSegment as CoilSegmentModel
from repositories.coil_segment_repository import CoilSegmentRepository
from schemas.coil_segment_schemas import (
    CoilSegmentCreateSchema,
    CoilSegmentUpdateSchema,
)


class CoilSegmentUseCases:
    @staticmethod
    def add_coil_segment(payload: CoilSegmentCreateSchema, repository: CoilSegmentRepository) -> CoilSegmentModel:
        segment_model = CoilSegmentModel(**payload.model_dump())
        return repository.create(segment_model)

    @staticmethod
    def remove_coil_segment_by_id(segment_id: int, repository: CoilSegmentRepository) -> None:
        segment = repository.get_by_id(segment_id)
        if not segment:
            raise HTTPException(status_code=404, detail="Coil segment not found")
        repository.delete(segment)

    @staticmethod
    def update_coil_segment_by_id(
        segment_id: int, payload: CoilSegmentUpdateSchema, repository: CoilSegmentRepository
    ) -> CoilSegmentModel:
        segment = repository.get_by_id(segment_id)
        if not segment:
            raise HTTPException(status_code=404, detail="Coil segment not found")
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(segment, key, value)
        return repository.update(segment)

    @staticmethod
    def list_coil_segments(
        repository: CoilSegmentRepository,
        skip: int = 0,
        limit: int = 100,
        coil_id: Optional[int] = None,
        cam_id: Optional[int] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        position_start_min: Optional[float] = None,
        position_start_max: Optional[float] = None,
    ) -> list[CoilSegmentModel]:
        return repository.list(
            skip=skip,
            limit=limit,
            coil_id=coil_id,
            cam_id=cam_id,
            date_from=date_from,
            date_to=date_to,
            position_start_min=position_start_min,
            position_start_max=position_start_max,
        )

    @staticmethod
    def get_coil_segment_by_id(segment_id: int, repository: CoilSegmentRepository) -> CoilSegmentModel:
        segment = repository.get_by_id(segment_id)
        if not segment:
            raise HTTPException(status_code=404, detail="Coil segment not found")
        return segment

    @staticmethod
    def get_fragments_with_bboxes(coil_id: int, cam_id: int, repository: CoilSegmentRepository):
        return repository.list_with_bboxes(coil_id=coil_id, cam_id=cam_id)

    @staticmethod
    def get_coil_segment_with_bboxes(segment_id: int, repository: CoilSegmentRepository):
        segment = repository.get_with_bboxes(segment_id)
        if not segment:
            raise HTTPException(status_code=404, detail="Coil segment not found")
        return segment

    @staticmethod
    def get_image_path_by_fragment_and_type(segment_id: int, image_type: str, repository: CoilSegmentRepository) -> str:
        segment = repository.get_by_id(segment_id)
        if not segment:
            raise HTTPException(status_code=404, detail=f"Segmento com ID {segment_id} não encontrado.")
        if image_type == "original":
            image_path = segment.original_image_path
        elif image_type == "medium":
            image_path = segment.medium_image_path
        elif image_type == "mini":
            image_path = segment.mini_image_path
        else:
            raise HTTPException(status_code=400, detail="Tipo de imagem inválido. Use 'original', 'medium' ou 'mini'.")
        if not image_path:
            raise HTTPException(status_code=404, detail="Caminho da imagem não encontrado para o tipo especificado.")
        return image_path

    @staticmethod
    def get_image_segmentation_path(segment_id: int, repository: CoilSegmentRepository):
        segment = repository.get_by_id(segment_id)
        if not segment:
            raise HTTPException(status_code=404, detail=f"Segmento com ID {segment_id} não encontrado.")
        image_path = segment.original_image_path
        if not image_path:
            raise HTTPException(status_code=404, detail="Caminho da imagem não encontrado para o tipo especificado.")
        return image_path, segment
