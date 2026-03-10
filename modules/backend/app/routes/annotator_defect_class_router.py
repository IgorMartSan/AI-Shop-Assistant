from __future__ import annotations

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from db.database import get_db
from repositories.annotator_defect_class_repository import AnnotatorDefectClassRepository
from repositories.annotator_repository import AnnotatorRepository
from schemas.annotator_defect_class_schemas import (
    AnnotatorDefectClassCreateSchema,
    AnnotatorDefectClassOutSchema,
    AnnotatorDefectClassUpdateSchema,
)
from use_cases.annotator_defect_class_use_cases import AnnotatorDefectClassUseCases
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

router = APIRouter(prefix="/annotator-defect-classes", tags=["AnnotatorDefectClasses"])


@router.post(
    "",
    response_model=AnnotatorDefectClassOutSchema,
    status_code=201,
    summary="Create defect class",
    description="Create a new defect class for an annotator.",
    response_description="Defect class created.",
)
def create_model_class(
    payload: AnnotatorDefectClassCreateSchema,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_modify_access(current_data)
    repo = AnnotatorDefectClassRepository(db_session)
    annotator_repo = AnnotatorRepository(db_session)
    return AnnotatorDefectClassUseCases.create(
        payload=payload, repository=repo, annotator_repository=annotator_repo
    )


@router.get(
    "",
    response_model=list[AnnotatorDefectClassOutSchema],
    summary="List defect classes",
    description="List defect classes with optional filtering.",
    response_description="List of defect classes.",
)
def list_model_classes(
    model_id: int | None = Query(default=None),
    skip: int = 0,
    limit: int = 100,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_view_access(current_data)
    repo = AnnotatorDefectClassRepository(db_session)
    return AnnotatorDefectClassUseCases.list(repository=repo, model_id=model_id, skip=skip, limit=limit)


@router.get(
    "/{class_id}",
    response_model=AnnotatorDefectClassOutSchema,
    summary="Get defect class",
    description="Get a defect class by ID.",
    response_description="Defect class details.",
)
def get_model_class(
    class_id: int,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_view_access(current_data)
    repo = AnnotatorDefectClassRepository(db_session)
    return AnnotatorDefectClassUseCases.get_by_id(class_id=class_id, repository=repo)


@router.patch(
    "/{class_id}",
    response_model=AnnotatorDefectClassOutSchema,
    summary="Update defect class",
    description="Update a defect class by ID.",
    response_description="Defect class updated.",
)
def update_model_class(
    class_id: int,
    payload: AnnotatorDefectClassUpdateSchema,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_modify_access(current_data)
    repo = AnnotatorDefectClassRepository(db_session)
    annotator_repo = AnnotatorRepository(db_session)
    return AnnotatorDefectClassUseCases.update(
        class_id=class_id,
        payload=payload,
        repository=repo,
        annotator_repository=annotator_repo,
    )


@router.delete(
    "/{class_id}",
    status_code=204,
    summary="Delete defect class",
    description="Delete a defect class by ID.",
    response_description="Defect class deleted.",
)
def delete_model_class(
    class_id: int,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_modify_access(current_data)
    repo = AnnotatorDefectClassRepository(db_session)
    AnnotatorDefectClassUseCases.delete(class_id=class_id, repository=repo)
    return None
