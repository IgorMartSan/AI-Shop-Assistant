from __future__ import annotations

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from db.database import get_db
from repositories.coil_segment_border_repository import CoilSegmentBorderRepository
from repositories.coil_segment_repository import CoilSegmentRepository
from schemas.coil_segment_border_schemas import (
    CoilSegmentBorderCreateSchema,
    CoilSegmentBorderOutSchema,
    CoilSegmentBorderUpdateSchema,
)
from use_cases.coil_segment_border_use_cases import CoilSegmentBorderUseCases
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

router = APIRouter(prefix="/coil-segment-borders", tags=["CoilSegmentBorders"])


@router.post(
    "",
    response_model=CoilSegmentBorderOutSchema,
    status_code=201,
    summary="Create segment border",
    description="Create a new coil segment border.",
    response_description="Segment border created.",
)
def create_border(
    payload: CoilSegmentBorderCreateSchema,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_modify_access(current_data)
    repo = CoilSegmentBorderRepository(db_session)
    segment_repo = CoilSegmentRepository(db_session)
    return CoilSegmentBorderUseCases.create(payload=payload, repository=repo, segment_repository=segment_repo)


@router.get(
    "",
    response_model=list[CoilSegmentBorderOutSchema],
    summary="List segment borders",
    description="List coil segment borders with optional filtering.",
    response_description="List of segment borders.",
)
def list_borders(
    coil_segment_id: int | None = Query(default=None),
    skip: int = 0,
    limit: int = 100,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_view_access(current_data)
    repo = CoilSegmentBorderRepository(db_session)
    return CoilSegmentBorderUseCases.list(repository=repo, coil_segment_id=coil_segment_id, skip=skip, limit=limit)


@router.get(
    "/{border_id}",
    response_model=CoilSegmentBorderOutSchema,
    summary="Get segment border",
    description="Get a coil segment border by ID.",
    response_description="Segment border details.",
)
def get_border(
    border_id: int,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_view_access(current_data)
    repo = CoilSegmentBorderRepository(db_session)
    return CoilSegmentBorderUseCases.get_by_id(border_id=border_id, repository=repo)


@router.patch(
    "/{border_id}",
    response_model=CoilSegmentBorderOutSchema,
    summary="Update segment border",
    description="Update a coil segment border by ID.",
    response_description="Segment border updated.",
)
def update_border(
    border_id: int,
    payload: CoilSegmentBorderUpdateSchema,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_modify_access(current_data)
    repo = CoilSegmentBorderRepository(db_session)
    segment_repo = CoilSegmentRepository(db_session)
    return CoilSegmentBorderUseCases.update(
        border_id=border_id, payload=payload, repository=repo, segment_repository=segment_repo
    )


@router.delete(
    "/{border_id}",
    status_code=204,
    summary="Delete segment border",
    description="Delete a coil segment border by ID.",
    response_description="Segment border deleted.",
)
def delete_border(
    border_id: int,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_modify_access(current_data)
    repo = CoilSegmentBorderRepository(db_session)
    CoilSegmentBorderUseCases.delete(border_id=border_id, repository=repo)
    return None
