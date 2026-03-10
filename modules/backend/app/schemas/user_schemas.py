from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from utils.enums import UserTypeEnum


class UserBaseSchema(BaseModel):
    username: str
    email: EmailStr
    is_active: bool = True
    user_type: UserTypeEnum = UserTypeEnum.USER

    model_config = ConfigDict(from_attributes=True)


class UserCreateRequestSchema(BaseModel):
    username: str
    email: EmailStr
    password: str
    user_type: UserTypeEnum = UserTypeEnum.USER
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)


class UserUpdateRequestSchema(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    user_type: Optional[UserTypeEnum] = None
    is_active: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)


class ChangePasswordRequestSchema(BaseModel):
    username: str
    current_password: str
    new_password: str

    model_config = ConfigDict(from_attributes=True)


class UserOutSchema(UserBaseSchema):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class UserLoginRequestSchema(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: str

    model_config = ConfigDict(from_attributes=True)


class UserTokenResponseSchema(BaseModel):
    access_token: str
    token_type: str = Field(default="bearer")

    model_config = ConfigDict(from_attributes=True)
