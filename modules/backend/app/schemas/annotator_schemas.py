from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class AnnotatorCreateSchema(BaseModel):
    name: str
    comment: Optional[str] = None
    model_metadata: Optional[dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class AnnotatorUpdateSchema(BaseModel):
    name: Optional[str] = None
    comment: Optional[str] = None
    model_metadata: Optional[dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class AnnotatorOutSchema(BaseModel):
    id: int
    name: str
    comment: Optional[str] = None
    model_metadata: Optional[dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)
