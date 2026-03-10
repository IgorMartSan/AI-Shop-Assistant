from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict


class CoilSegmentDefectSchema(BaseModel):
    id: Optional[int] = None
    coil_segment_id: int
    defect_class_id: int
    confidence: Optional[float] = None
    center_x_px: float
    center_y_px: float
    width_px: float
    height_px: float
    defect_image_path: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CoilSegmentDefectUpdateSchema(BaseModel):
    coil_segment_id: Optional[int] = None
    defect_class_id: Optional[int] = None
    confidence: Optional[float] = None
    center_x_px: Optional[float] = None
    center_y_px: Optional[float] = None
    width_px: Optional[float] = None
    height_px: Optional[float] = None
    defect_image_path: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
