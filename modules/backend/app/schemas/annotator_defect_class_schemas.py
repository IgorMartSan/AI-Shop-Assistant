from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict


class AnnotatorDefectClassCreateSchema(BaseModel):
    model_id: int
    name: str
    color_r: Optional[int] = None
    color_g: Optional[int] = None
    color_b: Optional[int] = None
    pixel: int
    comment: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AnnotatorDefectClassUpdateSchema(BaseModel):
    model_id: Optional[int] = None
    name: Optional[str] = None
    color_r: Optional[int] = None
    color_g: Optional[int] = None
    color_b: Optional[int] = None
    pixel: Optional[int] = None
    comment: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AnnotatorDefectClassOutSchema(BaseModel):
    id: int
    model_id: int
    name: str
    color_r: Optional[int] = None
    color_g: Optional[int] = None
    color_b: Optional[int] = None
    pixel: int
    comment: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
