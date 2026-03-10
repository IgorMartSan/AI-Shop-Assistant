from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class CoilSegmentBorderCreateSchema(BaseModel):
    coil_segment_id: int
    pair_idx: Optional[int] = None
    x1_px: float
    y1_px: float
    x2_px: float
    y2_px: float

    model_config = ConfigDict(from_attributes=True)


class CoilSegmentBorderUpdateSchema(BaseModel):
    coil_segment_id: Optional[int] = None
    pair_idx: Optional[int] = None
    x1_px: Optional[float] = None
    y1_px: Optional[float] = None
    x2_px: Optional[float] = None
    y2_px: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class CoilSegmentBorderOutSchema(BaseModel):
    id: int
    coil_segment_id: int
    pair_idx: Optional[int] = None
    x1_px: float
    y1_px: float
    x2_px: float
    y2_px: float
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
