from __future__ import annotations

from io import BytesIO
import os

import numpy as np
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from PIL import Image, ImageDraw
from sqlalchemy.orm import Session

from db.database import get_db
from db.model import Annotator, CoilSegmentAnnotatorSegmentation
from repositories.annotator_defect_class_repository import AnnotatorDefectClassRepository
from repositories.coil_segment_repository import CoilSegmentRepository
from schemas.handle_image_schemas import (
    RequestGetImageSegmentationAllowedDefectsSchema,
    RequestGetImageSegmentationRemoveDefectsSchema,
    SegmentationModelOutSchema,
)
from use_cases.handle_image_use_cases import HandleImageUseCases
from utils.auth import AuthUtils
from utils.enums import UserTypeEnum


def _require_view_access(current_data: dict) -> None:
    user_type = current_data.get("user_type")
    if isinstance(user_type, UserTypeEnum):
        user_type = user_type.value
    if user_type not in {UserTypeEnum.ADMIN.value, UserTypeEnum.SUPERUSER.value, UserTypeEnum.USER.value}:
        raise HTTPException(status_code=403, detail="Forbidden")

router = APIRouter(prefix="/handle_image", tags=["HandleImage"])


def _class_rgb(defect) -> tuple[int, int, int] | None:
    if defect is None:
        return None
    if (
        getattr(defect, "color_r", None) is not None
        and getattr(defect, "color_g", None) is not None
        and getattr(defect, "color_b", None) is not None
    ):
        return int(defect.color_r), int(defect.color_g), int(defect.color_b)
    return None


@router.post(
    "/get_image_segmentation_rgb_resized_with_allowed_defects/",
    response_class=StreamingResponse,
    summary="Get segmentation image (allowed defects)",
    description="Return a resized segmentation image keeping only allowed defects.",
    response_description="PNG image stream.",
)
def get_image_segmentation_resized(
    request: RequestGetImageSegmentationAllowedDefectsSchema,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_view_access(current_data)
    segment_repo = CoilSegmentRepository(db_session)
    class_repo = AnnotatorDefectClassRepository(db_session)

    segment_id = request.id
    image_type = request.type
    allowed_defect_ids = request.allowed_defect_ids

    if image_type not in ["original", "medium", "mini"]:
        raise HTTPException(status_code=400, detail="Tipo de imagem inválido. Use 'original', 'medium' ou 'mini'.")

    image_path, segment = HandleImageUseCases.get_segmentation_context(segment_id, segment_repo)
    if not image_path or not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found.")

    if image_type == "mini":
        height = round(segment.height_image_px * segment.mini_image_scale)
        width = round(segment.width_image_px * segment.mini_image_scale)
    elif image_type == "medium":
        height = round(segment.height_image_px * segment.medium_image_scale)
        width = round(segment.width_image_px * segment.medium_image_scale)
    else:
        height = segment.height_image_px
        width = segment.width_image_px

    img = Image.open(image_path).convert("L")
    img_resized = img.resize((width, height), 2)
    gray_array = np.array(img_resized)

    list_segmentation_defects = HandleImageUseCases.list_segmentation_classes(request.model_id, class_repo)

    color_map: dict[int, tuple[int, int, int, int]] = {}
    for defect in list_segmentation_defects:
        if defect.pixel is None:
            continue
        rgb = _class_rgb(defect)
        if rgb is None:
            continue
        r, g, b = rgb
        if defect.id in allowed_defect_ids:
            alpha = 120
            color_map[defect.pixel] = (r, g, b, alpha)
        else:
            color_map[defect.pixel] = (0, 0, 0, 0)

    lookup_table = np.zeros((256, 4), dtype=np.uint8)
    for gray_value, (r, g, b, a) in color_map.items():
        if 0 <= gray_value <= 255:
            lookup_table[gray_value] = [r, g, b, a]

    rgba_array = lookup_table[gray_array]
    img_rgb = Image.fromarray(rgba_array, mode="RGBA")

    img_io = BytesIO()
    img_rgb.save(img_io, "PNG")
    img_io.seek(0)

    return StreamingResponse(img_io, media_type="image/png")


@router.get(
    "/{segment_id}/segmentation-models",
    response_model=list[SegmentationModelOutSchema],
    summary="List segmentation models for a segment",
    description="List distinct annotator models that have segmentation for the given segment.",
    response_description="List of segmentation models.",
)
def list_segmentation_models(
    segment_id: int,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_view_access(current_data)
    rows = (
        db_session.query(Annotator.id, Annotator.name)
        .join(
            CoilSegmentAnnotatorSegmentation,
            CoilSegmentAnnotatorSegmentation.model_id == Annotator.id,
        )
        .filter(CoilSegmentAnnotatorSegmentation.coil_segment_id == segment_id)
        .distinct()
        .order_by(Annotator.id)
        .all()
    )
    return [{"model_id": row[0], "model_name": row[1]} for row in rows]


@router.get(
    "/{segment_id}/segmentation/{model_id}/{image_type}",
    response_class=StreamingResponse,
    summary="Get segmentation image by model",
    description="Return a resized segmentation image for a given model. Options: original, medium, mini.",
    response_description="PNG image stream.",
)
def get_segmentation_image_by_model(
    segment_id: int,
    model_id: int,
    image_type: str,
    allowed_defect_ids: list[int] | None = Query(default=None),
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_view_access(current_data)
    segment_repo = CoilSegmentRepository(db_session)
    class_repo = AnnotatorDefectClassRepository(db_session)

    if image_type not in ["original", "medium", "mini"]:
        raise HTTPException(status_code=400, detail="Tipo de imagem inválido. Use 'original', 'medium' ou 'mini'.")

    segment = segment_repo.get_by_id(segment_id)
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found.")

    segmentation = (
        db_session.query(CoilSegmentAnnotatorSegmentation)
        .filter(
            CoilSegmentAnnotatorSegmentation.coil_segment_id == segment_id,
            CoilSegmentAnnotatorSegmentation.model_id == model_id,
        )
        .order_by(CoilSegmentAnnotatorSegmentation.created_at.desc(), CoilSegmentAnnotatorSegmentation.id.desc())
        .first()
    )
    if not segmentation or not segmentation.mask_url:
        raise HTTPException(status_code=404, detail="Segmentation not found.")

    image_path = segmentation.mask_url
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Segmentation mask not found.")

    if image_type == "mini":
        height = round(segment.height_image_px * segment.mini_image_scale)
        width = round(segment.width_image_px * segment.mini_image_scale)
    elif image_type == "medium":
        height = round(segment.height_image_px * segment.medium_image_scale)
        width = round(segment.width_image_px * segment.medium_image_scale)
    else:
        height = segment.height_image_px
        width = segment.width_image_px

    img = Image.open(image_path).convert("L")
    img_resized = img.resize((width, height), 2)
    gray_array = np.array(img_resized)

    list_segmentation_defects = HandleImageUseCases.list_segmentation_classes(model_id, class_repo)

    allowed_set = set(allowed_defect_ids) if allowed_defect_ids else None
    color_map: dict[int, tuple[int, int, int, int]] = {}
    for defect in list_segmentation_defects:
        if defect.pixel is None:
            continue
        rgb = _class_rgb(defect)
        if rgb is None:
            continue
        r, g, b = rgb
        if allowed_set is None or defect.id in allowed_set:
            alpha = 120
            color_map[defect.pixel] = (r, g, b, alpha)
        else:
            color_map[defect.pixel] = (0, 0, 0, 0)

    lookup_table = np.zeros((256, 4), dtype=np.uint8)
    for gray_value, (r, g, b, a) in color_map.items():
        if 0 <= gray_value <= 255:
            lookup_table[gray_value] = [r, g, b, a]

    rgba_array = lookup_table[gray_array]
    img_rgb = Image.fromarray(rgba_array, mode="RGBA")

    img_io = BytesIO()
    img_rgb.save(img_io, "PNG")
    img_io.seek(0)

    return StreamingResponse(img_io, media_type="image/png")


@router.post(
    "/get_image_segmentation_rgb_resized_with_Removed_defects/",
    response_class=StreamingResponse,
    summary="Get segmentation image (removed defects)",
    description="Return a resized segmentation image removing specified defects.",
    response_description="PNG image stream.",
)
def get_image_segmentation_resized_removed(
    request: RequestGetImageSegmentationRemoveDefectsSchema,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_view_access(current_data)
    segment_repo = CoilSegmentRepository(db_session)
    class_repo = AnnotatorDefectClassRepository(db_session)

    segment_id = request.id
    image_type = request.type
    remove_defect_ids = request.remove_defect_ids

    if image_type not in ["original", "medium", "mini"]:
        raise HTTPException(status_code=400, detail="Tipo de imagem inválido. Use 'original', 'medium' ou 'mini'.")

    image_path, segment = HandleImageUseCases.get_segmentation_context(segment_id, segment_repo)
    if not image_path or not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found.")

    if image_type == "mini":
        height = round(segment.height_image_px * segment.mini_image_scale)
        width = round(segment.width_image_px * segment.mini_image_scale)
    elif image_type == "medium":
        height = round(segment.height_image_px * segment.medium_image_scale)
        width = round(segment.width_image_px * segment.medium_image_scale)
    else:
        height = segment.height_image_px
        width = segment.width_image_px

    img = Image.open(image_path).convert("L")
    img_resized = img.resize((width, height), 2)
    gray_array = np.array(img_resized)

    list_segmentation_defects = HandleImageUseCases.list_segmentation_classes(request.model_id, class_repo)

    color_map: dict[int, tuple[int, int, int, int]] = {}
    for defect in list_segmentation_defects:
        if defect.pixel is None:
            continue
        rgb = _class_rgb(defect)
        if rgb is None:
            continue
        r, g, b = rgb
        if defect.id in remove_defect_ids:
            color_map[defect.pixel] = (0, 0, 0, 0)
        else:
            alpha = 120
            color_map[defect.pixel] = (r, g, b, alpha)

    lookup_table = np.zeros((256, 4), dtype=np.uint8)
    for gray_value, (r, g, b, a) in color_map.items():
        if 0 <= gray_value <= 255:
            lookup_table[gray_value] = [r, g, b, a]

    rgba_array = lookup_table[gray_array]
    img_rgb = Image.fromarray(rgba_array, mode="RGBA")

    img_io = BytesIO()
    img_rgb.save(img_io, "PNG")
    img_io.seek(0)

    return StreamingResponse(img_io, media_type="image/png")


@router.get(
    "/{segment_id}/image-with-bboxes/{image_type}",
    response_class=StreamingResponse,
    summary="Get segment image with bboxes",
    description="Get a segment image with bounding boxes. Options: original, medium, mini.",
    response_description="Segment image file with bboxes.",
)
def get_segment_image_with_bboxes(
    segment_id: int,
    image_type: str,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_view_access(current_data)
    segment_repo = CoilSegmentRepository(db_session)

    if image_type not in ["original", "medium", "mini"]:
        raise HTTPException(status_code=400, detail="Tipo de imagem inválido. Use 'original', 'medium' ou 'mini'.")

    segment = segment_repo.get_by_id(segment_id)
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found.")

    segment_with_bboxes = segment_repo.get_with_bboxes(segment_id=segment_id)

    image_path = HandleImageUseCases.get_image_path_by_fragment_and_type(segment_id, image_type, segment_repo)
    if not image_path or not os.path.exists(image_path):
        if image_type == "mini":
            height = round(segment.height_image_px * segment.mini_image_scale)
            width = round(segment.width_image_px * segment.mini_image_scale)
        elif image_type == "medium":
            height = round(segment.height_image_px * segment.medium_image_scale)
            width = round(segment.width_image_px * segment.medium_image_scale)
        else:
            height = segment.height_image_px
            width = segment.width_image_px
        with Image.new("RGB", (width, height), color="black") as img:
            img_io = BytesIO()
            img.save(img_io, "JPEG")
            img_io.seek(0)
            return StreamingResponse(img_io, media_type="image/jpeg")

    img = Image.open(image_path).convert("RGB")
    width, height = img.size

    # Swapped width/height per request for debugging alignment
    original_width = segment.height_image_px or width
    original_height = segment.width_image_px or height
    scale_x = width / original_width if original_width else 1
    scale_y = height / original_height if original_height else 1

    draw = ImageDraw.Draw(img)
    for defect in (segment_with_bboxes.defects_bbox or []):
        if defect.x_px is None or defect.y_px is None:
            continue
        box_x = defect.x_px * scale_x
        box_y = defect.y_px * scale_y
        box_w = defect.width_px * scale_x
        box_h = defect.height_px * scale_y

        color = "#ef4444"
        if defect.model_class:
            rgb = _class_rgb(defect.model_class)
            if rgb is not None:
                color = f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
        draw.rectangle(
            [box_x, box_y, box_x + box_w, box_y + box_h],
            outline=color,
            width=2,
        )

    img_io = BytesIO()
    img.save(img_io, "JPEG")
    img_io.seek(0)
    return StreamingResponse(img_io, media_type="image/jpeg")


@router.get(
    "/{segment_id}/image/{image_type}",
    response_class=StreamingResponse,
    summary="Get segment image by type",
    description="Get a segment image by type. Options: original, medium, mini.",
    response_description="Segment image file.",
)
def get_segment_image(
    segment_id: int,
    image_type: str,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_view_access(current_data)
    segment_repo = CoilSegmentRepository(db_session)
    if image_type not in ["original", "medium", "mini"]:
        raise HTTPException(status_code=400, detail="Tipo de imagem inválido. Use 'original', 'medium' ou 'mini'.")

    image_path, segment = HandleImageUseCases.get_segmentation_context(segment_id, segment_repo)
    if not image_path or not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found.")

    if image_type == "mini":
        height = round(segment.height_image_px * segment.mini_image_scale)
        width = round(segment.width_image_px * segment.mini_image_scale)
    elif image_type == "medium":
        height = round(segment.height_image_px * segment.medium_image_scale)
        width = round(segment.width_image_px * segment.medium_image_scale)
    else:
        height = segment.height_image_px
        width = segment.width_image_px

    img = Image.open(image_path).convert("RGB")
    img_resized = img.resize((width, height), 2)
    img_io = BytesIO()
    img_resized.save(img_io, "JPEG")
    img_io.seek(0)

    return StreamingResponse(img_io, media_type="image/jpeg")
