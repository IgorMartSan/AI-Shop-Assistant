from __future__ import annotations

from typing import Optional

from sqlalchemy import String, cast, or_
from sqlalchemy.orm import Session

from db.model import User as UserModel
from utils.enums import UserTypeEnum


class UserRepository:
    def __init__(self, db_session: Session):
        self._db = db_session

    def create(self, user: UserModel) -> UserModel:
        self._db.add(user)
        self._db.commit()
        self._db.refresh(user)
        return user

    def get_by_id(self, user_id: int) -> Optional[UserModel]:
        return self._db.query(UserModel).filter(UserModel.id == user_id).first()

    def get_by_username(self, username: str) -> Optional[UserModel]:
        return self._db.query(UserModel).filter(UserModel.username == username).first()

    def get_by_email(self, email: str) -> Optional[UserModel]:
        return self._db.query(UserModel).filter(UserModel.email == email).first()

    def list(
        self,
        skip: int = 0,
        limit: int = 100,
        q: Optional[str] = None,
        username: Optional[str] = None,
        email: Optional[str] = None,
        user_type: Optional[UserTypeEnum] = None,
        is_active: Optional[bool] = None,
    ) -> list[UserModel]:
        query = self._db.query(UserModel)
        if q:
            pattern = f"%{q}%"
            query = query.filter(
                or_(
                    UserModel.username.ilike(pattern),
                    UserModel.email.ilike(pattern),
                    cast(UserModel.user_type, String).ilike(pattern),
                    cast(UserModel.id, String).ilike(pattern),
                    cast(UserModel.is_active, String).ilike(pattern),
                )
            )
        if username:
            query = query.filter(UserModel.username.ilike(f"%{username}%"))
        if email:
            query = query.filter(UserModel.email.ilike(f"%{email}%"))
        if user_type:
            query = query.filter(UserModel.user_type == user_type)
        if is_active is not None:
            query = query.filter(UserModel.is_active == is_active)
        return query.offset(skip).limit(limit).all()

    def update(self, user: UserModel) -> UserModel:
        self._db.commit()
        self._db.refresh(user)
        return user

    def delete(self, user: UserModel) -> None:
        self._db.delete(user)
        self._db.commit()
