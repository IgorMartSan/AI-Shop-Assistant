from __future__ import annotations

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from db.database import get_db
from repositories.annotator_repository import AnnotatorRepository
from repositories.coil_segment_annotator_seg_repository import CoilSegmentAnnotatorSegRepository
from repositories.coil_segment_repository import CoilSegmentRepository
from schemas.coil_segment_annotator_seg_schemas import (
    CoilSegmentAnnotatorSegCreateSchema,
    CoilSegmentAnnotatorSegOutSchema,
    CoilSegmentAnnotatorSegUpdateSchema,
)
from use_cases.coil_segment_annotator_seg_use_cases import CoilSegmentAnnotatorSegUseCases
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

router = APIRouter(prefix="/segmentations", tags=["Segmentations"])


@router.post(
    "",
    response_model=CoilSegmentAnnotatorSegOutSchema,
    status_code=201,
    summary="Create segmentation",
    description="Create a new segmentation for a coil segment.",
    response_description="Segmentation created.",
)
def create_segmentation(
    payload: CoilSegmentAnnotatorSegCreateSchema,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_modify_access(current_data)
    repo = CoilSegmentAnnotatorSegRepository(db_session)
    segment_repo = CoilSegmentRepository(db_session)
    annotator_repo = AnnotatorRepository(db_session)
    return CoilSegmentAnnotatorSegUseCases.create(
        payload=payload,
        repository=repo,
        segment_repository=segment_repo,
        annotator_repository=annotator_repo,
    )


@router.get(
    "",
    response_model=list[CoilSegmentAnnotatorSegOutSchema],
    summary="List segmentations",
    description="List segmentations with optional filtering.",
    response_description="List of segmentations.",
)
def list_segmentations(
    coil_segment_id: int | None = Query(default=None),
    model_id: int | None = Query(default=None),
    skip: int = 0,
    limit: int = 100,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_view_access(current_data)
    repo = CoilSegmentAnnotatorSegRepository(db_session)
    return CoilSegmentAnnotatorSegUseCases.list(
        repository=repo,
        coil_segment_id=coil_segment_id,
        model_id=model_id,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{segmentation_id}",
    response_model=CoilSegmentAnnotatorSegOutSchema,
    summary="Get segmentation",
    description="Get a segmentation by ID.",
    response_description="Segmentation details.",
)
def get_segmentation(
    segmentation_id: int,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_view_access(current_data)
    repo = CoilSegmentAnnotatorSegRepository(db_session)
    return CoilSegmentAnnotatorSegUseCases.get_by_id(segmentation_id=segmentation_id, repository=repo)


@router.patch(
    "/{segmentation_id}",
    response_model=CoilSegmentAnnotatorSegOutSchema,
    summary="Update segmentation",
    description="Update a segmentation by ID.",
    response_description="Segmentation updated.",
)
def update_segmentation(
    segmentation_id: int,
    payload: CoilSegmentAnnotatorSegUpdateSchema,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_modify_access(current_data)
    repo = CoilSegmentAnnotatorSegRepository(db_session)
    segment_repo = CoilSegmentRepository(db_session)
    annotator_repo = AnnotatorRepository(db_session)
    return CoilSegmentAnnotatorSegUseCases.update(
        segmentation_id=segmentation_id,
        payload=payload,
        repository=repo,
        segment_repository=segment_repo,
        annotator_repository=annotator_repo,
    )


@router.delete(
    "/{segmentation_id}",
    status_code=204,
    summary="Delete segmentation",
    description="Delete a segmentation by ID.",
    response_description="Segmentation deleted.",
)
def delete_segmentation(
    segmentation_id: int,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_modify_access(current_data)
    repo = CoilSegmentAnnotatorSegRepository(db_session)
    CoilSegmentAnnotatorSegUseCases.delete(segmentation_id=segmentation_id, repository=repo)
    return None
