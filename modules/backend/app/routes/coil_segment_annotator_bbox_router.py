from __future__ import annotations

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from db.database import get_db
from repositories.annotator_defect_class_repository import AnnotatorDefectClassRepository
from repositories.annotator_repository import AnnotatorRepository
from repositories.coil_segment_annotator_bbox_repository import CoilSegmentAnnotatorBBoxRepository
from repositories.coil_segment_repository import CoilSegmentRepository
from schemas.coil_segment_annotator_bbox_schemas import (
    CoilSegmentAnnotatorBBoxCreateSchema,
    CoilSegmentAnnotatorBBoxOutSchema,
    CoilSegmentAnnotatorBBoxUpdateSchema,
)
from use_cases.coil_segment_annotator_bbox_use_cases import CoilSegmentAnnotatorBBoxUseCases
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

router = APIRouter(prefix="/bboxes", tags=["BBoxes"])


@router.post(
    "",
    response_model=CoilSegmentAnnotatorBBoxOutSchema,
    status_code=201,
    summary="Create bounding box",
    description="Create a new bounding box for a coil segment.",
    response_description="Bounding box created.",
)
def create_bbox(
    payload: CoilSegmentAnnotatorBBoxCreateSchema,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_modify_access(current_data)
    repo = CoilSegmentAnnotatorBBoxRepository(db_session)
    segment_repo = CoilSegmentRepository(db_session)
    annotator_repo = AnnotatorRepository(db_session)
    class_repo = AnnotatorDefectClassRepository(db_session)
    return CoilSegmentAnnotatorBBoxUseCases.create(
        payload=payload,
        repository=repo,
        segment_repository=segment_repo,
        annotator_repository=annotator_repo,
        model_class_repository=class_repo,
    )


@router.get(
    "",
    response_model=list[CoilSegmentAnnotatorBBoxOutSchema],
    summary="List bounding boxes",
    description="List bounding boxes with optional filtering.",
    response_description="List of bounding boxes.",
)
def list_bboxes(
    coil_segment_id: int | None = Query(default=None),
    model_id: int | None = Query(default=None),
    model_class_id: int | None = Query(default=None),
    confidence_min: float | None = Query(default=None),
    skip: int = 0,
    limit: int = 100,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_view_access(current_data)
    repo = CoilSegmentAnnotatorBBoxRepository(db_session)
    return CoilSegmentAnnotatorBBoxUseCases.list(
        repository=repo,
        coil_segment_id=coil_segment_id,
        model_id=model_id,
        model_class_id=model_class_id,
        confidence_min=confidence_min,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{bbox_id}",
    response_model=CoilSegmentAnnotatorBBoxOutSchema,
    summary="Get bounding box",
    description="Get a bounding box by ID.",
    response_description="Bounding box details.",
)
def get_bbox(
    bbox_id: int,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_view_access(current_data)
    repo = CoilSegmentAnnotatorBBoxRepository(db_session)
    return CoilSegmentAnnotatorBBoxUseCases.get_by_id(bbox_id=bbox_id, repository=repo)


@router.patch(
    "/{bbox_id}",
    response_model=CoilSegmentAnnotatorBBoxOutSchema,
    summary="Update bounding box",
    description="Update a bounding box by ID.",
    response_description="Bounding box updated.",
)
def update_bbox(
    bbox_id: int,
    payload: CoilSegmentAnnotatorBBoxUpdateSchema,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_modify_access(current_data)
    repo = CoilSegmentAnnotatorBBoxRepository(db_session)
    segment_repo = CoilSegmentRepository(db_session)
    annotator_repo = AnnotatorRepository(db_session)
    class_repo = AnnotatorDefectClassRepository(db_session)
    return CoilSegmentAnnotatorBBoxUseCases.update(
        bbox_id=bbox_id,
        payload=payload,
        repository=repo,
        segment_repository=segment_repo,
        annotator_repository=annotator_repo,
        model_class_repository=class_repo,
    )


@router.delete(
    "/{bbox_id}",
    status_code=204,
    summary="Delete bounding box",
    description="Delete a bounding box by ID.",
    response_description="Bounding box deleted.",
)
def delete_bbox(
    bbox_id: int,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_modify_access(current_data)
    repo = CoilSegmentAnnotatorBBoxRepository(db_session)
    CoilSegmentAnnotatorBBoxUseCases.delete(bbox_id=bbox_id, repository=repo)
    return None
