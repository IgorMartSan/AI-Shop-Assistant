from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class CamCreateSchema(BaseModel):
    name: str
    comment: Optional[str] = None
    metadata_cam: Optional[dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class CamUpdateSchema(BaseModel):
    name: Optional[str] = None
    comment: Optional[str] = None
    metadata_cam: Optional[dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class CamOutSchema(BaseModel):
    id: int
    name: str
    comment: Optional[str] = None
    metadata_cam: Optional[dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class CamConfigSchema(BaseModel):
    config: dict[str, Any]

    model_config = ConfigDict(from_attributes=True)
