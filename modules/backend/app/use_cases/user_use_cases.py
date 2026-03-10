from __future__ import annotations

from typing import Optional

from fastapi import HTTPException

from db.model import User as UserModel
from repositories.user_repository import UserRepository
from schemas.user_schemas import (
    UserCreateRequestSchema,
    UserUpdateRequestSchema,
    ChangePasswordRequestSchema,
)
from utils.auth import AuthUtils


class UserUseCases:
    @staticmethod
    def create(request_schema: UserCreateRequestSchema, repository: UserRepository) -> UserModel:
        existing_username = repository.get_by_username(request_schema.username)
        if existing_username:
            raise HTTPException(status_code=409, detail="Username already registered")
        existing_email = repository.get_by_email(request_schema.email)
        if existing_email:
            raise HTTPException(status_code=409, detail="Email already registered")

        hashed_password = AuthUtils.get_password_hash(request_schema.password)
        new_user = UserModel(
            username=request_schema.username,
            email=request_schema.email,
            hashed_password=hashed_password,
            user_type=request_schema.user_type,
            is_active=request_schema.is_active,
        )
        return repository.create(new_user)

    @staticmethod
    def login(email_or_username: str, password: str, repository: UserRepository) -> dict:
        user = repository.get_by_email(email_or_username) or repository.get_by_username(email_or_username)
        if not user:
            raise HTTPException(status_code=404, detail="User/Email not found")
        if not user.is_active:
            raise HTTPException(status_code=401, detail="User account is not active. Please contact an administrator for approval.")
        if not AuthUtils.verify_password(password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Incorrect password")
        access_token = AuthUtils.create_access_token(data={"sub": user.username, "user_type": user.user_type})
        return {"access_token": access_token, "token_type": "bearer"}

    @staticmethod
    def list(
        repository: UserRepository,
        skip: int = 0,
        limit: int = 100,
        q: Optional[str] = None,
        username: Optional[str] = None,
        email: Optional[str] = None,
        user_type: Optional[UserTypeEnum] = None,
        is_active: Optional[bool] = None,
    ) -> list[UserModel]:
        return repository.list(
            skip=skip,
            limit=limit,
            q=q,
            username=username,
            email=email,
            user_type=user_type,
            is_active=is_active,
        )

    @staticmethod
    def get_by_id(user_id: int, repository: UserRepository) -> UserModel:
        user = repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    @staticmethod
    def update(user_id: int, payload: UserUpdateRequestSchema, repository: UserRepository) -> UserModel:
        user = repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if payload.username and payload.username != user.username:
            existing = repository.get_by_username(payload.username)
            if existing and existing.id != user_id:
                raise HTTPException(status_code=409, detail="Username already registered")
            user.username = payload.username
        if payload.email and payload.email != user.email:
            existing = repository.get_by_email(payload.email)
            if existing and existing.id != user_id:
                raise HTTPException(status_code=409, detail="Email already registered")
            user.email = payload.email
        if payload.password:
            user.hashed_password = AuthUtils.get_password_hash(payload.password)
        if payload.user_type is not None:
            user.user_type = payload.user_type
        if payload.is_active is not None:
            user.is_active = payload.is_active

        return repository.update(user)

    @staticmethod
    def change_password(payload: ChangePasswordRequestSchema, repository: UserRepository) -> None:
        user = repository.get_by_username(payload.username) or repository.get_by_email(payload.username)
        if not user:
            raise HTTPException(status_code=404, detail="User/Email not found")
        if not AuthUtils.verify_password(payload.current_password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Incorrect password")
        user.hashed_password = AuthUtils.get_password_hash(payload.new_password)
        repository.update(user)

    @staticmethod
    def delete(user_id: int, repository: UserRepository) -> None:
        user = repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        repository.delete(user)
