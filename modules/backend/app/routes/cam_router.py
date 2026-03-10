from __future__ import annotations

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from db.database import get_db
from repositories.cam_repository import CamRepository
from schemas.cam_schemas import CamCreateSchema, CamOutSchema, CamUpdateSchema, CamConfigSchema
from use_cases.cam_use_cases import CamUseCases
from utils.auth import AuthUtils
from utils.enums import UserTypeEnum


def _require_view_access(current_data: dict) -> None:
    user_type = current_data.get("user_type")
    if isinstance(user_type, UserTypeEnum):
        user_type = user_type.value
    if user_type not in {UserTypeEnum.ADMIN.value, UserTypeEnum.SUPERUSER.value, UserTypeEnum.USER.value}:
        raise HTTPException(status_code=403, detail="Forbidden")


def _require_modify_access(current_data: dict) -> None:
    user_type = current_data.get("user_type")
    if isinstance(user_type, UserTypeEnum):
        user_type = user_type.value
    if user_type not in {UserTypeEnum.ADMIN.value, UserTypeEnum.SUPERUSER.value}:
        raise HTTPException(status_code=403, detail="Forbidden")


def _require_admin_access(current_data: dict) -> None:
    user_type = current_data.get("user_type")
    if isinstance(user_type, UserTypeEnum):
        user_type = user_type.value
    if user_type != UserTypeEnum.ADMIN.value:
        raise HTTPException(status_code=403, detail="Forbidden")

router = APIRouter(prefix="/cams", tags=["Cams"])


@router.post(
    "",
    response_model=CamOutSchema,
    status_code=201,
    summary="Create camera",
    description="Create a new camera.",
    response_description="Camera created.",
)
def create_cam(
    payload: CamCreateSchema,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_modify_access(current_data)
    repository = CamRepository(db_session)
    return CamUseCases.add_cam(payload=payload, repository=repository)


@router.get(
    "",
    response_model=list[CamOutSchema],
    summary="List cameras",
    description="List cameras with optional filtering.",
    response_description="List of cameras.",
)
def list_cams(
    skip: int = 0,
    limit: int = 100,
    name: str | None = Query(default=None),
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_view_access(current_data)
    repository = CamRepository(db_session)
    return CamUseCases.list_cams(repository=repository, skip=skip, limit=limit, name=name)


@router.get(
    "/{cam_id}",
    response_model=CamOutSchema,
    summary="Get camera",
    description="Get a camera by ID.",
    response_description="Camera details.",
)
def get_cam(
    cam_id: int,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_view_access(current_data)
    repository = CamRepository(db_session)
    return CamUseCases.get_cam_by_id(cam_id=cam_id, repository=repository)


@router.patch(
    "/{cam_id}",
    response_model=CamOutSchema,
    summary="Update camera",
    description="Update a camera by ID.",
    response_description="Camera updated.",
)
def update_cam(
    cam_id: int,
    payload: CamUpdateSchema,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_modify_access(current_data)
    repository = CamRepository(db_session)
    return CamUseCases.update_cam_by_id(cam_id=cam_id, cam_data=payload, repository=repository)


@router.get(
    "/{cam_id}/config",
    response_model=CamConfigSchema,
    summary="Get camera config",
    description="Get camera config stored in metadata_cam.config.",
    response_description="Camera config.",
)
def get_cam_config(
    cam_id: int,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_admin_access(current_data)
    repository = CamRepository(db_session)
    return CamUseCases.get_cam_config(cam_id=cam_id, repository=repository)


@router.patch(
    "/{cam_id}/config",
    response_model=CamConfigSchema,
    summary="Update camera config",
    description="Update camera config stored in metadata_cam.config.",
    response_description="Camera config updated.",
)
def update_cam_config(
    cam_id: int,
    payload: CamConfigSchema,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_admin_access(current_data)
    repository = CamRepository(db_session)
    return CamUseCases.update_cam_config(cam_id=cam_id, cam_data=payload, repository=repository)


@router.get(
    "/by-name/{cam_name}/config",
    response_model=CamConfigSchema,
    summary="Get camera config by name",
    description="Get camera config stored in metadata_cam.config using camera name.",
    response_description="Camera config.",
)
def get_cam_config_by_name(
    cam_name: str,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_admin_access(current_data)
    repository = CamRepository(db_session)
    return CamUseCases.get_cam_config_by_name(name=cam_name, repository=repository)


@router.patch(
    "/by-name/{cam_name}/config",
    response_model=CamConfigSchema,
    summary="Update camera config by name",
    description="Update camera config stored in metadata_cam.config using camera name.",
    response_description="Camera config updated.",
)
def update_cam_config_by_name(
    cam_name: str,
    payload: CamConfigSchema,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_admin_access(current_data)
    repository = CamRepository(db_session)
    return CamUseCases.update_cam_config_by_name(name=cam_name, cam_data=payload, repository=repository)


@router.delete(
    "/{cam_id}",
    status_code=204,
    summary="Delete camera",
    description="Delete a camera by ID.",
    response_description="Camera deleted.",
)
def delete_cam(
    cam_id: int,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_modify_access(current_data)
    repository = CamRepository(db_session)
    CamUseCases.remove_cam_by_id(cam_id=cam_id, repository=repository)
    return None


legacy_router = APIRouter(prefix="/cam", tags=["Cam-legacy"])


@legacy_router.post(
    "/add",
    response_model=CamOutSchema,
    status_code=201,
    summary="Create camera (legacy)",
    description="Legacy endpoint to create a new camera.",
    response_description="Camera created.",
)
def add_cam_legacy(
    payload: CamCreateSchema,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_modify_access(current_data)
    repository = CamRepository(db_session)
    return CamUseCases.add_cam(payload=payload, repository=repository)


@legacy_router.get(
    "/list",
    response_model=list[CamOutSchema],
    summary="List cameras (legacy)",
    description="Legacy endpoint to list cameras.",
    response_description="List of cameras.",
)
def list_cam_legacy(
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_view_access(current_data)
    repository = CamRepository(db_session)
    return CamUseCases.list_cams(repository=repository)


@legacy_router.get(
    "/get/{cam_id}",
    response_model=CamOutSchema,
    summary="Get camera (legacy)",
    description="Legacy endpoint to get a camera by ID.",
    response_description="Camera details.",
)
def get_cam_legacy(
    cam_id: int,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_view_access(current_data)
    repository = CamRepository(db_session)
    return CamUseCases.get_cam_by_id(cam_id=cam_id, repository=repository)


@legacy_router.put(
    "/update/{cam_id}",
    response_model=CamOutSchema,
    summary="Update camera (legacy)",
    description="Legacy endpoint to update a camera by ID.",
    response_description="Camera updated.",
)
def update_cam_legacy(
    cam_id: int,
    payload: CamUpdateSchema,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_modify_access(current_data)
    repository = CamRepository(db_session)
    return CamUseCases.update_cam_by_id(cam_id=cam_id, cam_data=payload, repository=repository)


@legacy_router.delete(
    "/remove/{cam_id}",
    status_code=204,
    summary="Delete camera (legacy)",
    description="Legacy endpoint to delete a camera by ID.",
    response_description="Camera deleted.",
)
def delete_cam_legacy(
    cam_id: int,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_modify_access(current_data)
    repository = CamRepository(db_session)
    CamUseCases.remove_cam_by_id(cam_id=cam_id, repository=repository)
    return None
