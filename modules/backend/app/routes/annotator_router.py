from __future__ import annotations

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from db.database import get_db
from repositories.annotator_repository import AnnotatorRepository
from schemas.annotator_schemas import AnnotatorCreateSchema, AnnotatorOutSchema, AnnotatorUpdateSchema
from use_cases.annotator_use_cases import AnnotatorUseCases
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

router = APIRouter(prefix="/annotators", tags=["Annotators"])


@router.post(
    "",
    response_model=AnnotatorOutSchema,
    status_code=201,
    summary="Create annotator",
    description="Create a new annotator.",
    response_description="Annotator created.",
)
def create_annotator(
    payload: AnnotatorCreateSchema,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_modify_access(current_data)
    repo = AnnotatorRepository(db_session)
    return AnnotatorUseCases.create(payload=payload, repository=repo)


@router.get(
    "",
    response_model=list[AnnotatorOutSchema],
    summary="List annotators",
    description="List annotators with optional filtering.",
    response_description="List of annotators.",
)
def list_annotators(
    skip: int = 0,
    limit: int = 100,
    name: str | None = Query(default=None),
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_view_access(current_data)
    repo = AnnotatorRepository(db_session)
    return AnnotatorUseCases.list(repository=repo, skip=skip, limit=limit, name=name)


@router.get(
    "/{annotator_id}",
    response_model=AnnotatorOutSchema,
    summary="Get annotator",
    description="Get an annotator by ID.",
    response_description="Annotator details.",
)
def get_annotator(
    annotator_id: int,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_view_access(current_data)
    repo = AnnotatorRepository(db_session)
    return AnnotatorUseCases.get_by_id(annotator_id=annotator_id, repository=repo)


@router.patch(
    "/{annotator_id}",
    response_model=AnnotatorOutSchema,
    summary="Update annotator",
    description="Update an annotator by ID.",
    response_description="Annotator updated.",
)
def update_annotator(
    annotator_id: int,
    payload: AnnotatorUpdateSchema,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_modify_access(current_data)
    repo = AnnotatorRepository(db_session)
    return AnnotatorUseCases.update(annotator_id=annotator_id, payload=payload, repository=repo)


@router.delete(
    "/{annotator_id}",
    status_code=204,
    summary="Delete annotator",
    description="Delete an annotator by ID.",
    response_description="Annotator deleted.",
)
def delete_annotator(
    annotator_id: int,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_modify_access(current_data)
    repo = AnnotatorRepository(db_session)
    AnnotatorUseCases.delete(annotator_id=annotator_id, repository=repo)
    return None
