from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict


class DefectClassSchema(BaseModel):
    id: Optional[int] = None
    model_id: Optional[int] = None
    name: str
    color: Optional[str] = None
    pixel: Optional[int] = None
    comment: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class DefectClassUpdateSchema(BaseModel):
    model_id: Optional[int] = None
    name: Optional[str] = None
    color: Optional[str] = None
    pixel: Optional[int] = None
    comment: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
