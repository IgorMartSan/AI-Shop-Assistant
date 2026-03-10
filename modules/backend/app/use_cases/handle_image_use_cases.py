from __future__ import annotations

from fastapi import HTTPException

from repositories.annotator_defect_class_repository import AnnotatorDefectClassRepository
from repositories.coil_segment_repository import CoilSegmentRepository


class HandleImageUseCases:
    @staticmethod
    def get_image_path_by_fragment_and_type(segment_id: int, image_type: str, segment_repo: CoilSegmentRepository) -> str:
        return HandleImageUseCases._get_image_path(segment_id, image_type, segment_repo)

    @staticmethod
    def _get_image_path(segment_id: int, image_type: str, segment_repo: CoilSegmentRepository) -> str:
        segment = segment_repo.get_by_id(segment_id)
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
    def get_segmentation_context(segment_id: int, segment_repo: CoilSegmentRepository):
        segment = segment_repo.get_by_id(segment_id)
        if not segment:
            raise HTTPException(status_code=404, detail=f"Segmento com ID {segment_id} não encontrado.")
        image_path = segment.original_image_path
        if not image_path:
            raise HTTPException(status_code=404, detail="Caminho da imagem não encontrado para o tipo especificado.")
        return image_path, segment

    @staticmethod
    def list_segmentation_classes(model_id: int | None, repo: AnnotatorDefectClassRepository):
        return repo.list(model_id=model_id)
