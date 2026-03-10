from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class CoilSegmentAnnotatorSegCreateSchema(BaseModel):
    coil_segment_id: int
    model_id: int
    mask_url: str
    scale: Optional[float] = None
    infer_metadata: Optional[dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class CoilSegmentAnnotatorSegUpdateSchema(BaseModel):
    coil_segment_id: Optional[int] = None
    model_id: Optional[int] = None
    mask_url: Optional[str] = None
    scale: Optional[float] = None
    infer_metadata: Optional[dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class CoilSegmentAnnotatorSegOutSchema(BaseModel):
    id: int
    coil_segment_id: int
    model_id: int
    mask_url: str
    scale: Optional[float] = None
    infer_metadata: Optional[dict[str, Any]] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
