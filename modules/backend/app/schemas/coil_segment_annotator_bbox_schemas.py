from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, model_validator


class CoilSegmentAnnotatorBBoxCreateSchema(BaseModel):
    coil_segment_id: int
    model_id: int
    model_class_id: int
    confidence: Optional[float] = None
    x_px: Optional[float] = None
    y_px: Optional[float] = None
    width_px: float
    height_px: float
    bbox_metadata: Optional[dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="after")
    def validate_position(self):
        has_xy = self.x_px is not None and self.y_px is not None
        if not has_xy:
            raise ValueError("bbox must contain (x_px, y_px)")
        return self


class CoilSegmentAnnotatorBBoxUpdateSchema(BaseModel):
    coil_segment_id: Optional[int] = None
    model_id: Optional[int] = None
    model_class_id: Optional[int] = None
    confidence: Optional[float] = None
    x_px: Optional[float] = None
    y_px: Optional[float] = None
    width_px: Optional[float] = None
    height_px: Optional[float] = None
    bbox_metadata: Optional[dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class CoilSegmentAnnotatorBBoxOutSchema(BaseModel):
    id: int
    coil_segment_id: int
    model_id: int
    model_class_id: int
    confidence: Optional[float] = None
    x_px: Optional[float] = None
    y_px: Optional[float] = None
    width_px: float
    height_px: float
    bbox_metadata: Optional[dict[str, Any]] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
