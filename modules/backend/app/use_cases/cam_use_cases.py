from __future__ import annotations

from fastapi import HTTPException

from db.model import Cam as CamModel
from repositories.cam_repository import CamRepository
from schemas.cam_schemas import CamCreateSchema, CamUpdateSchema, CamConfigSchema


class CamUseCases:
    @staticmethod
    def add_cam(payload: CamCreateSchema, repository: CamRepository) -> CamModel:
        existing = repository.get_by_name(payload.name)
        if existing:
            raise HTTPException(status_code=409, detail="Cam name already registered")
        cam_model = CamModel(**payload.model_dump())
        return repository.create(cam_model)

    @staticmethod
    def remove_cam_by_id(cam_id: int, repository: CamRepository) -> None:
        cam = repository.get_by_id(cam_id)
        if not cam:
            raise HTTPException(status_code=404, detail="Cam not found")
        repository.delete(cam)

    @staticmethod
    def update_cam_by_id(cam_id: int, cam_data: CamUpdateSchema, repository: CamRepository) -> CamModel:
        cam = repository.get_by_id(cam_id)
        if not cam:
            raise HTTPException(status_code=404, detail="Cam not found")
        if cam_data.name and cam_data.name != cam.name:
            existing = repository.get_by_name(cam_data.name)
            if existing and existing.id != cam_id:
                raise HTTPException(status_code=409, detail="Cam name already registered")
            cam.name = cam_data.name
        if cam_data.comment is not None:
            cam.comment = cam_data.comment
        if cam_data.metadata_cam is not None:
            cam.metadata_cam = cam_data.metadata_cam
        return repository.update(cam)

    @staticmethod
    def list_cams(repository: CamRepository, skip: int = 0, limit: int = 100, name: str | None = None) -> list[CamModel]:
        return repository.list(skip=skip, limit=limit, name=name)

    @staticmethod
    def get_cam_by_id(cam_id: int, repository: CamRepository) -> CamModel:
        cam = repository.get_by_id(cam_id)
        if not cam:
            raise HTTPException(status_code=404, detail="Cam not found")
        return cam

    @staticmethod
    def get_cam_by_name(name: str, repository: CamRepository) -> CamModel:
        cam = repository.get_by_name(name)
        if not cam:
            raise HTTPException(status_code=404, detail="Cam not found")
        return cam

    @staticmethod
    def get_cam_config(cam_id: int, repository: CamRepository) -> dict:
        cam = repository.get_by_id(cam_id)
        if not cam:
            raise HTTPException(status_code=404, detail="Cam not found")
        metadata = cam.metadata_cam if isinstance(cam.metadata_cam, dict) else {}
        config = metadata.get("config")
        if not isinstance(config, dict):
            config = {}
        return {"config": config}

    @staticmethod
    def get_cam_config_by_name(name: str, repository: CamRepository) -> dict:
        cam = repository.get_by_name(name)
        if not cam:
            raise HTTPException(status_code=404, detail="Cam not found")
        metadata = cam.metadata_cam if isinstance(cam.metadata_cam, dict) else {}
        config = metadata.get("config")
        if not isinstance(config, dict):
            config = {}
        return {"config": config}

    @staticmethod
    def update_cam_config(cam_id: int, cam_data: CamConfigSchema, repository: CamRepository) -> dict:
        cam = repository.get_by_id(cam_id)
        if not cam:
            raise HTTPException(status_code=404, detail="Cam not found")
        metadata = cam.metadata_cam if isinstance(cam.metadata_cam, dict) else {}
        metadata["config"] = cam_data.config
        cam.metadata_cam = metadata
        repository.update(cam)
        return {"config": cam_data.config}

    @staticmethod
    def update_cam_config_by_name(name: str, cam_data: CamConfigSchema, repository: CamRepository) -> dict:
        cam = repository.get_by_name(name)
        if not cam:
            raise HTTPException(status_code=404, detail="Cam not found")
        metadata = cam.metadata_cam if isinstance(cam.metadata_cam, dict) else {}
        metadata["config"] = cam_data.config
        cam.metadata_cam = metadata
        repository.update(cam)
        return {"config": cam_data.config}
