from __future__ import annotations

from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from db.database import get_db
from repositories.user_repository import UserRepository
from schemas.user_schemas import (
    UserCreateRequestSchema,
    UserOutSchema,
    UserUpdateRequestSchema,
    UserTokenResponseSchema,
    ChangePasswordRequestSchema,
)
from use_cases.user_use_cases import UserUseCases
from utils.enums import UserTypeEnum
from utils.auth import AuthUtils


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


def _require_admin_only(current_data: dict) -> None:
    user_type = current_data.get("user_type")
    if isinstance(user_type, UserTypeEnum):
        user_type = user_type.value
    if user_type != UserTypeEnum.ADMIN.value:
        raise HTTPException(status_code=403, detail="Forbidden")

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "",
    response_model=UserOutSchema,
    status_code=201,
    summary="Create user",
    description="Create a new user (admin only).",
    response_description="User created.",
)
def create_user(
    user: UserCreateRequestSchema,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_modify_access(current_data)
    repository = UserRepository(db_session)
    return UserUseCases.create(request_schema=user, repository=repository)


@router.get(
    "",
    response_model=list[UserOutSchema],
    summary="List users",
    description="List users with optional filters.",
    response_description="List of users.",
)
def list_users(
    skip: int = 0,
    limit: int = 100,
    q: str | None = Query(default=None),
    username: str | None = Query(default=None),
    email: str | None = Query(default=None),
    user_type: UserTypeEnum | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_view_access(current_data)
    repository = UserRepository(db_session)
    return UserUseCases.list(
        repository=repository,
        skip=skip,
        limit=limit,
        q=q,
        username=username,
        email=email,
        user_type=user_type,
        is_active=is_active,
    )


@router.get(
    "/{user_id}",
    response_model=UserOutSchema,
    summary="Get user",
    description="Get a user by ID.",
    response_description="User details.",
)
def get_user(
    user_id: int,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_view_access(current_data)
    repository = UserRepository(db_session)
    return UserUseCases.get_by_id(user_id=user_id, repository=repository)


@router.patch(
    "/{user_id}",
    response_model=UserOutSchema,
    summary="Update user",
    description="Update a user by ID.",
    response_description="User updated.",
)
def update_user(
    user_id: int,
    payload: UserUpdateRequestSchema,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_modify_access(current_data)
    repository = UserRepository(db_session)
    return UserUseCases.update(user_id=user_id, payload=payload, repository=repository)


@router.delete(
    "/{user_id}",
    status_code=204,
    summary="Delete user",
    description="Delete a user by ID.",
    response_description="User deleted.",
)
def delete_user(
    user_id: int,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_modify_access(current_data)
    repository = UserRepository(db_session)
    UserUseCases.delete(user_id=user_id, repository=repository)
    return None


auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post(
    "/token",
    response_model=UserTokenResponseSchema,
    summary="Login",
    description="Authenticate a user and return an access token.",
    response_description="Access token issued.",
)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db_session: Session = Depends(get_db)):
    repository = UserRepository(db_session)
    token = UserUseCases.login(form_data.username, form_data.password, repository=repository)
    return token


@auth_router.post(
    "/create_user",
    response_model=UserOutSchema,
    status_code=201,
    summary="Create user (legacy)",
    description="Legacy endpoint to create a new user.",
    response_description="User created.",
)
def create_user_legacy(
    user: UserCreateRequestSchema,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_modify_access(current_data)
    repository = UserRepository(db_session)
    return UserUseCases.create(request_schema=user, repository=repository)


@auth_router.post(
    "/change_password",
    status_code=204,
    summary="Change password",
    description="Change user password with current credentials.",
    response_description="Password updated.",
)
def change_password(
    payload: ChangePasswordRequestSchema,
    db_session: Session = Depends(get_db),
):
    repository = UserRepository(db_session)
    UserUseCases.change_password(payload=payload, repository=repository)
    return None
