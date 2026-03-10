from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class RequestGetImageSegmentationRemoveDefectsSchema(BaseModel):
    id: Optional[int] = Field(default=None)
    type: str = Field(default="medium")
    remove_defect_ids: list[int] = Field(default_factory=list)
    model_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class RequestGetImageSegmentationAllowedDefectsSchema(BaseModel):
    id: Optional[int] = Field(default=None)
    type: str = Field(default="medium")
    allowed_defect_ids: list[int] = Field(default_factory=list)
    model_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class SegmentationModelOutSchema(BaseModel):
    model_id: int
    model_name: str

    model_config = ConfigDict(from_attributes=True)
