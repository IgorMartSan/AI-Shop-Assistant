from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class CoilCreateSchema(BaseModel):
    name: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    metadata_coil: Optional[dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class CoilUpdateSchema(BaseModel):
    name: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    metadata_coil: Optional[dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class CoilOutSchema(BaseModel):
    id: int
    name: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    metadata_coil: Optional[dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class CoilCameraCountSchema(BaseModel):
    cam_id: int
    cam_name: str
    frames: int

    model_config = ConfigDict(from_attributes=True)


class CoilWithCamerasSchema(CoilOutSchema):
    cameras: list[CoilCameraCountSchema] = []


class CoilNavigationSchema(BaseModel):
    selected_coil: Optional[CoilOutSchema] = None
    previous_coil: Optional[CoilOutSchema] = None
    next_coil: Optional[CoilOutSchema] = None

    model_config = ConfigDict(from_attributes=True)


class PaginatedCoilsSchema(BaseModel):
    coils: list[CoilWithCamerasSchema]
    page: int
    per_page: int
    total_count: int
    total_pages: int

    model_config = ConfigDict(from_attributes=True)
