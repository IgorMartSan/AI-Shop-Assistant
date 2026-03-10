from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class CoilSegmentCreateSchema(BaseModel):
    data: Optional[datetime] = None
    coil_id: int
    cam_id: int
    line_position_start: float
    line_position_end: float
    original_image_path: Optional[str] = None
    distance_per_px_axis_x: Optional[float] = None
    distance_per_px_axis_y: Optional[float] = None
    width_image_px: Optional[int] = None
    height_image_px: Optional[int] = None
    medium_image_path: Optional[str] = None
    medium_image_scale: Optional[float] = None
    mini_image_path: Optional[str] = None
    mini_image_scale: Optional[float] = None
    metadata_segment: Optional[dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class CoilSegmentUpdateSchema(BaseModel):
    data: Optional[datetime] = None
    coil_id: Optional[int] = None
    cam_id: Optional[int] = None
    line_position_start: Optional[float] = None
    line_position_end: Optional[float] = None
    original_image_path: Optional[str] = None
    distance_per_px_axis_x: Optional[float] = None
    distance_per_px_axis_y: Optional[float] = None
    width_image_px: Optional[int] = None
    height_image_px: Optional[int] = None
    medium_image_path: Optional[str] = None
    medium_image_scale: Optional[float] = None
    mini_image_path: Optional[str] = None
    mini_image_scale: Optional[float] = None
    metadata_segment: Optional[dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class CoilSegmentOutSchema(BaseModel):
    id: int
    data: Optional[datetime] = None
    coil_id: int
    cam_id: int
    line_position_start: float
    line_position_end: float
    original_image_path: Optional[str] = None
    distance_per_px_axis_x: Optional[float] = None
    distance_per_px_axis_y: Optional[float] = None
    width_image_px: Optional[int] = None
    height_image_px: Optional[int] = None
    medium_image_path: Optional[str] = None
    medium_image_scale: Optional[float] = None
    mini_image_path: Optional[str] = None
    mini_image_scale: Optional[float] = None
    metadata_segment: Optional[dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class AnnotatorDefectClassRefSchema(BaseModel):
    id: int
    model_id: int
    name: str
    color_r: Optional[int] = None
    color_g: Optional[int] = None
    color_b: Optional[int] = None
    pixel: int
    comment: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CoilSegmentAnnotatorBBoxSchema(BaseModel):
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
    model_class: Optional[AnnotatorDefectClassRefSchema] = None

    model_config = ConfigDict(from_attributes=True)


class CoilSegmentSchemaWithDefects(BaseModel):
    id: int
    data: Optional[datetime] = None
    coil_id: int
    cam_id: int
    line_position_start: float
    line_position_end: float
    original_image_path: Optional[str] = None
    distance_per_px_axis_x: Optional[float] = None
    distance_per_px_axis_y: Optional[float] = None
    width_image_px: Optional[int] = None
    height_image_px: Optional[int] = None
    medium_image_path: Optional[str] = None
    medium_image_scale: Optional[float] = None
    mini_image_path: Optional[str] = None
    mini_image_scale: Optional[float] = None
    metadata_segment: Optional[dict[str, Any]] = None
    defects: list[CoilSegmentAnnotatorBBoxSchema] = Field(
        default_factory=list, validation_alias="defects_bbox"
    )

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class CoilSegmentSchemaWithDefectsWithDefectsCount(CoilSegmentSchemaWithDefects):
    defects_count: int = 0


class CoilSegmentSchemaWithDefectsMiniMedium(CoilSegmentSchemaWithDefectsWithDefectsCount):
    defects_mini_scale: list[CoilSegmentAnnotatorBBoxSchema] = Field(default_factory=list)


class ImageSegmentationRequest(BaseModel):
    id: int
    tipo: str
    allowed_defect_ids: list[int] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class IngestCamSchema(BaseModel):
    name: str
    comment: Optional[str] = None
    metadata_cam: Optional[dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class IngestCoilSegmentSchema(BaseModel):
    data: Optional[datetime] = None
    line_position_start: float
    line_position_end: float
    original_image_path: Optional[str] = None
    distance_per_px_axis_x: Optional[float] = None
    distance_per_px_axis_y: Optional[float] = None
    width_image_px: Optional[int] = None
    height_image_px: Optional[int] = None
    medium_image_path: Optional[str] = None
    medium_image_scale: Optional[float] = None
    mini_image_path: Optional[str] = None
    mini_image_scale: Optional[float] = None
    metadata_segment: Optional[dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class IngestAnnotatorClassSchema(BaseModel):
    name: str
    pixel: int
    color_r: Optional[int] = None
    color_g: Optional[int] = None
    color_b: Optional[int] = None
    comment: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class IngestAnnotatorSchema(BaseModel):
    name: str
    comment: Optional[str] = None
    model_metadata: Optional[dict[str, Any]] = None
    classes: list[IngestAnnotatorClassSchema] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class IngestBBoxSchema(BaseModel):
    model_name: str
    class_name: str
    confidence: Optional[float] = None
    x_px: Optional[float] = None
    y_px: Optional[float] = None
    width_px: float
    height_px: float
    bbox_metadata: Optional[dict[str, Any]] = None
    class_pixel: Optional[int] = None
    class_color_r: Optional[int] = None
    class_color_g: Optional[int] = None
    class_color_b: Optional[int] = None
    class_comment: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="after")
    def validate_position(self):
        has_xy = self.x_px is not None and self.y_px is not None
        if not has_xy:
            raise ValueError("bbox must contain (x_px, y_px)")
        return self


class IngestSegmentationSchema(BaseModel):
    model_name: str
    mask_url: str
    scale: Optional[float] = None
    infer_metadata: Optional[dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class CoilSegmentIngestRequest(BaseModel):
    coil_id: int
    cam: IngestCamSchema
    segment: IngestCoilSegmentSchema
    annotators: list[IngestAnnotatorSchema] = Field(default_factory=list)
    bboxes: list[IngestBBoxSchema] = Field(default_factory=list)
    segmentations: list[IngestSegmentationSchema] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
