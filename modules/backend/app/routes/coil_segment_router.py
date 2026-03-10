from __future__ import annotations

from datetime import datetime
from io import BytesIO
import os

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse, StreamingResponse
from PIL import Image, ImageDraw
from sqlalchemy.orm import Session

from db.database import get_db
from repositories.coil_segment_repository import CoilSegmentRepository
from schemas.coil_segment_schemas import (
    CoilSegmentCreateSchema,
    CoilSegmentOutSchema,
    CoilSegmentUpdateSchema,
    CoilSegmentSchemaWithDefects,
    CoilSegmentIngestRequest,
)
from use_cases.coil_segment_use_cases import CoilSegmentUseCases
from utils.auth import AuthUtils
from utils.enums import UserTypeEnum
from db.model import (
    Coils,
    Cam,
    CoilSegment,
    Annotator,
    AnnotatorDefectClass,
    CoilSegmentAnnotatorBBox,
    CoilSegmentAnnotatorSegmentation,
)


def _require_view_access(current_data: dict) -> None:
    user_type = current_data.get("user_type")
    if isinstance(user_type, UserTypeEnum):
        user_type = user_type.value
    if user_type not in {UserTypeEnum.ADMIN.value, UserTypeEnum.SUPERUSER.value, UserTypeEnum.USER.value}:
        raise HTTPException(status_code=403, detail="Forbidden")


def _require_modify_access(current_data: dict) -> None:
    user_type = current_data.get("user_type")
    if isinstance(user_type, UserTypeEnum):
        user_type = user_type.value
    if user_type not in {UserTypeEnum.ADMIN.value, UserTypeEnum.SUPERUSER.value}:
        raise HTTPException(status_code=403, detail="Forbidden")

router = APIRouter(prefix="/coil-segments", tags=["CoilSegments"])

def _class_color_hex(model_class: AnnotatorDefectClass | None) -> str:
    if not model_class:
        return "#000000"
    if model_class.color_r is not None and model_class.color_g is not None and model_class.color_b is not None:
        r, g, b = int(model_class.color_r), int(model_class.color_g), int(model_class.color_b)
    else:
        r, g, b = (0, 0, 0)
    return f"#{r:02x}{g:02x}{b:02x}"


@router.post(
    "",
    response_model=CoilSegmentOutSchema,
    status_code=201,
    summary="Create coil segment",
    description="Create a new coil segment.",
    response_description="Coil segment created.",
)
def create_segment(
    payload: CoilSegmentCreateSchema,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_modify_access(current_data)
    repository = CoilSegmentRepository(db_session)
    return CoilSegmentUseCases.add_coil_segment(payload=payload, repository=repository)


@router.get(
    "",
    response_model=list[CoilSegmentOutSchema],
    summary="List coil segments",
    description="List coil segments with optional filters.",
    response_description="List of coil segments.",
)
def list_segments(
    skip: int = 0,
    limit: int = 100,
    coil_id: int | None = Query(default=None),
    cam_id: int | None = Query(default=None),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    position_start_min: float | None = Query(default=None),
    position_start_max: float | None = Query(default=None),
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_view_access(current_data)
    repository = CoilSegmentRepository(db_session)
    return CoilSegmentUseCases.list_coil_segments(
        repository=repository,
        skip=skip,
        limit=limit,
        coil_id=coil_id,
        cam_id=cam_id,
        date_from=date_from,
        date_to=date_to,
        position_start_min=position_start_min,
        position_start_max=position_start_max,
    )


@router.get(
    "/with-bboxes",
    response_model=list[CoilSegmentSchemaWithDefects],
    summary="List segments with bboxes",
    description="List coil segments including bounding boxes.",
    response_description="List of coil segments with bboxes.",
)
def list_segments_with_bboxes(
    coil_id: int,
    cam_id: int,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_view_access(current_data)
    repository = CoilSegmentRepository(db_session)
    return CoilSegmentUseCases.get_fragments_with_bboxes(coil_id=coil_id, cam_id=cam_id, repository=repository)


@router.get(
    "/{segment_id}",
    response_model=CoilSegmentOutSchema,
    summary="Get coil segment",
    description="Get a coil segment by ID.",
    response_description="Coil segment details.",
)
def get_segment(
    segment_id: int,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_view_access(current_data)
    repository = CoilSegmentRepository(db_session)
    return CoilSegmentUseCases.get_coil_segment_by_id(segment_id=segment_id, repository=repository)


@router.patch(
    "/{segment_id}",
    response_model=CoilSegmentOutSchema,
    summary="Update coil segment",
    description="Update a coil segment by ID.",
    response_description="Coil segment updated.",
)
def update_segment(
    segment_id: int,
    payload: CoilSegmentUpdateSchema,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_modify_access(current_data)
    repository = CoilSegmentRepository(db_session)
    return CoilSegmentUseCases.update_coil_segment_by_id(segment_id=segment_id, payload=payload, repository=repository)


@router.delete(
    "/{segment_id}",
    status_code=204,
    summary="Delete coil segment",
    description="Delete a coil segment by ID.",
    response_description="Coil segment deleted.",
)
def delete_segment(
    segment_id: int,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_modify_access(current_data)
    repository = CoilSegmentRepository(db_session)
    CoilSegmentUseCases.remove_coil_segment_by_id(segment_id=segment_id, repository=repository)
    return None


@router.get(
    "/{segment_id}/with-bboxes",
    response_model=CoilSegmentSchemaWithDefects,
    summary="Get segment with bboxes",
    description="Get a coil segment with its bounding boxes.",
    response_description="Coil segment with bboxes.",
)
def get_segment_with_bboxes(
    segment_id: int,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_view_access(current_data)
    repository = CoilSegmentRepository(db_session)
    return CoilSegmentUseCases.get_coil_segment_with_bboxes(segment_id=segment_id, repository=repository)


@router.get(
    "/{segment_id}/image/{image_type}",
    response_class=FileResponse,
    summary="Get segment image",
    description="Get a segment image by type (original, medium, mini).",
    response_description="Segment image file.",
)
def get_image(
    segment_id: int,
    image_type: str,
    db_session: Session = Depends(get_db),
):
    repository = CoilSegmentRepository(db_session)
    if image_type not in ["original", "medium", "mini"]:
        raise HTTPException(status_code=400, detail="Tipo de imagem inválido. Use 'original', 'medium' ou 'mini'.")
    image_path = CoilSegmentUseCases.get_image_path_by_fragment_and_type(
        segment_id=segment_id, image_type=image_type, repository=repository
    )
    if not image_path or not os.path.exists(image_path):
        segment = CoilSegmentUseCases.get_coil_segment_by_id(segment_id=segment_id, repository=repository)
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
    return FileResponse(image_path)


@router.get(
    "/{segment_id}/image-with-bboxes/{image_type}",
    response_class=StreamingResponse,
    summary="Get segment image with bboxes",
    description="Get a segment image with bounding boxes. Options: original, medium, mini.",
    response_description="Segment image file with bboxes.",
)
def get_image_with_bboxes(
    segment_id: int,
    image_type: str,
    db_session: Session = Depends(get_db),
):
    repository = CoilSegmentRepository(db_session)
    if image_type not in ["original", "medium", "mini"]:
        raise HTTPException(status_code=400, detail="Tipo de imagem inválido. Use 'original', 'medium' ou 'mini'.")

    segment = CoilSegmentUseCases.get_coil_segment_by_id(segment_id=segment_id, repository=repository)
    segment_with_bboxes = repository.get_with_bboxes(segment_id=segment_id)

    image_path = CoilSegmentUseCases.get_image_path_by_fragment_and_type(
        segment_id=segment_id, image_type=image_type, repository=repository
    )
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

    original_width = segment.width_image_px or width
    original_height = segment.height_image_px or height
    scale_x = width / original_width if original_width else 1
    scale_y = height / original_height if original_height else 1

    draw = ImageDraw.Draw(img)
    for defect in segment_with_bboxes.defects_bbox or []:
        if defect.x_px is None or defect.y_px is None:
            continue
        box_x = defect.x_px * scale_x
        box_y = defect.y_px * scale_y
        box_w = defect.width_px * scale_x
        box_h = defect.height_px * scale_y

        color = _class_color_hex(defect.model_class)
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
    "/{segment_id}/image",
    response_class=FileResponse,
    summary="Get segment image (query)",
    description="Get a segment image by query param type (original, medium, mini).",
    response_description="Segment image file.",
)
def get_image_by_query(
    segment_id: int,
    image_type: str = Query(default="medium"),
    db_session: Session = Depends(get_db),
):
    repository = CoilSegmentRepository(db_session)
    if image_type not in ["original", "medium", "mini"]:
        raise HTTPException(status_code=400, detail="Tipo de imagem inválido. Use 'original', 'medium' ou 'mini'.")
    image_path = CoilSegmentUseCases.get_image_path_by_fragment_and_type(
        segment_id=segment_id, image_type=image_type, repository=repository
    )
    if not image_path or not os.path.exists(image_path):
        segment = CoilSegmentUseCases.get_coil_segment_by_id(segment_id=segment_id, repository=repository)
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
    return FileResponse(image_path)


@router.post(
    "/ingest",
    response_model=CoilSegmentSchemaWithDefects,
    summary="Ingest coil segment with related data",
    description=(
        "Create a coil segment and ensure related coil, camera, annotators, defect classes, "
        "segmentations, and bboxes exist. Missing entities are created."
    ),
    response_description="Coil segment with bboxes.",
)
def ingest_segment(
    payload: CoilSegmentIngestRequest,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_modify_access(current_data)
    print("ingest_segment payload.metadata_segment:", payload.segment.metadata_segment)

    coil = db_session.query(Coils).filter(Coils.id == payload.coil_id).first()
    if not coil:
        raise HTTPException(status_code=404, detail="Coil not found")

    cam = db_session.query(Cam).filter(Cam.name == payload.cam.name).first()
    if not cam:
        cam = Cam(
            name=payload.cam.name,
            comment=payload.cam.comment,
            metadata_cam=payload.cam.metadata_cam,
        )
        db_session.add(cam)
        db_session.flush()

    segment = CoilSegment(
        data=payload.segment.data,
        coil_id=payload.coil_id,
        cam_id=cam.id,
        line_position_start=payload.segment.line_position_start,
        line_position_end=payload.segment.line_position_end,
        original_image_path=payload.segment.original_image_path,
        distance_per_px_axis_x=payload.segment.distance_per_px_axis_x,
        distance_per_px_axis_y=payload.segment.distance_per_px_axis_y,
        width_image_px=payload.segment.width_image_px,
        height_image_px=payload.segment.height_image_px,
        medium_image_path=payload.segment.medium_image_path,
        medium_image_scale=payload.segment.medium_image_scale,
        mini_image_path=payload.segment.mini_image_path,
        mini_image_scale=payload.segment.mini_image_scale,
        metadata_segment=payload.segment.metadata_segment,
    )
    db_session.add(segment)
    db_session.flush()
    print("ingest_segment saved metadata_segment:", segment.metadata_segment)

    annotator_by_name: dict[str, Annotator] = {}
    class_by_key: dict[tuple[int, str], AnnotatorDefectClass] = {}

    for annotator_payload in payload.annotators:
        annotator = (
            db_session.query(Annotator)
            .filter(Annotator.name == annotator_payload.name)
            .first()
        )
        if not annotator:
            annotator = Annotator(
                name=annotator_payload.name,
                comment=annotator_payload.comment,
                model_metadata=annotator_payload.model_metadata,
            )
            db_session.add(annotator)
            db_session.flush()

        annotator_by_name[annotator.name] = annotator

        for class_payload in annotator_payload.classes:
            class_key = (annotator.id, class_payload.name)
            model_class = (
                db_session.query(AnnotatorDefectClass)
                .filter(
                    AnnotatorDefectClass.model_id == annotator.id,
                    AnnotatorDefectClass.name == class_payload.name,
                )
                .first()
            )
            if not model_class:
                color_r = class_payload.color_r
                color_g = class_payload.color_g
                color_b = class_payload.color_b
                model_class = AnnotatorDefectClass(
                    model_id=annotator.id,
                    name=class_payload.name,
                    color_r=color_r,
                    color_g=color_g,
                    color_b=color_b,
                    pixel=class_payload.pixel,
                    comment=class_payload.comment,
                )
                db_session.add(model_class)
                db_session.flush()

            if (
                model_class.color_r is None
                or model_class.color_g is None
                or model_class.color_b is None
            ):
                fallback_rgb = (0, 0, 0)
                model_class.color_r = fallback_rgb[0]
                model_class.color_g = fallback_rgb[1]
                model_class.color_b = fallback_rgb[2]

            class_by_key[class_key] = model_class

    for segmentation_payload in payload.segmentations:
        annotator = annotator_by_name.get(segmentation_payload.model_name)
        if not annotator:
            annotator = (
                db_session.query(Annotator)
                .filter(Annotator.name == segmentation_payload.model_name)
                .first()
            )
            if not annotator:
                annotator = Annotator(name=segmentation_payload.model_name)
                db_session.add(annotator)
                db_session.flush()
            annotator_by_name[annotator.name] = annotator

        segmentation = CoilSegmentAnnotatorSegmentation(
            coil_segment_id=segment.id,
            model_id=annotator.id,
            mask_url=segmentation_payload.mask_url,
            scale=segmentation_payload.scale,
            infer_metadata=segmentation_payload.infer_metadata,
        )
        db_session.add(segmentation)

    for bbox_payload in payload.bboxes:
        annotator = annotator_by_name.get(bbox_payload.model_name)
        if not annotator:
            annotator = (
                db_session.query(Annotator)
                .filter(Annotator.name == bbox_payload.model_name)
                .first()
            )
            if not annotator:
                annotator = Annotator(name=bbox_payload.model_name)
                db_session.add(annotator)
                db_session.flush()
            annotator_by_name[annotator.name] = annotator

        class_key = (annotator.id, bbox_payload.class_name)
        model_class = class_by_key.get(class_key)
        if not model_class:
            model_class = (
                db_session.query(AnnotatorDefectClass)
                .filter(
                    AnnotatorDefectClass.model_id == annotator.id,
                    AnnotatorDefectClass.name == bbox_payload.class_name,
                )
                .first()
            )

        if not model_class:
            if bbox_payload.class_pixel is None:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "class_pixel is required to create a new defect class "
                        f"for annotator '{bbox_payload.model_name}'"
                    ),
                )
            color_r = bbox_payload.class_color_r
            color_g = bbox_payload.class_color_g
            color_b = bbox_payload.class_color_b
            model_class = AnnotatorDefectClass(
                model_id=annotator.id,
                name=bbox_payload.class_name,
                color_r=color_r,
                color_g=color_g,
                color_b=color_b,
                pixel=bbox_payload.class_pixel,
                comment=bbox_payload.class_comment,
            )
            db_session.add(model_class)
            db_session.flush()

        if (
            model_class.color_r is None
            or model_class.color_g is None
            or model_class.color_b is None
        ):
            fallback_rgb = (0, 0, 0)
            model_class.color_r = fallback_rgb[0]
            model_class.color_g = fallback_rgb[1]
            model_class.color_b = fallback_rgb[2]

        class_by_key[class_key] = model_class

        x_px = bbox_payload.x_px
        y_px = bbox_payload.y_px
        if x_px is None or y_px is None:
            raise HTTPException(
                status_code=400,
                detail="bbox must contain x_px and y_px",
            )

        bbox = CoilSegmentAnnotatorBBox(
            coil_segment_id=segment.id,
            model_id=annotator.id,
            model_class_id=model_class.id,
            confidence=bbox_payload.confidence,
            x_px=x_px,
            y_px=y_px,
            width_px=bbox_payload.width_px,
            height_px=bbox_payload.height_px,
            bbox_metadata=bbox_payload.bbox_metadata,
        )
        db_session.add(bbox)

    db_session.commit()

    repository = CoilSegmentRepository(db_session)
    return repository.get_with_bboxes(segment_id=segment.id)


legacy_router = APIRouter(prefix="/coil_segment", tags=["CoilSegment-legacy"])


@legacy_router.post(
    "/add",
    response_model=CoilSegmentOutSchema,
    status_code=201,
    summary="Create coil segment (legacy)",
    description="Legacy endpoint to create a coil segment.",
    response_description="Coil segment created.",
)
def add_segment_legacy(
    payload: CoilSegmentCreateSchema,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_modify_access(current_data)
    repository = CoilSegmentRepository(db_session)
    return CoilSegmentUseCases.add_coil_segment(payload=payload, repository=repository)


@legacy_router.get(
    "/list",
    response_model=list[CoilSegmentOutSchema],
    summary="List coil segments (legacy)",
    description="Legacy endpoint to list coil segments.",
    response_description="List of coil segments.",
)
def list_segments_legacy(
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_view_access(current_data)
    repository = CoilSegmentRepository(db_session)
    return CoilSegmentUseCases.list_coil_segments(repository=repository)


@legacy_router.get(
    "/get/{segment_id}",
    response_model=CoilSegmentOutSchema,
    summary="Get coil segment (legacy)",
    description="Legacy endpoint to get a coil segment by ID.",
    response_description="Coil segment details.",
)
def get_segment_legacy(
    segment_id: int,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_view_access(current_data)
    repository = CoilSegmentRepository(db_session)
    return CoilSegmentUseCases.get_coil_segment_by_id(segment_id=segment_id, repository=repository)


@legacy_router.put(
    "/update/{segment_id}",
    response_model=CoilSegmentOutSchema,
    summary="Update coil segment (legacy)",
    description="Legacy endpoint to update a coil segment by ID.",
    response_description="Coil segment updated.",
)
def update_segment_legacy(
    segment_id: int,
    payload: CoilSegmentUpdateSchema,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_modify_access(current_data)
    repository = CoilSegmentRepository(db_session)
    return CoilSegmentUseCases.update_coil_segment_by_id(segment_id=segment_id, payload=payload, repository=repository)


@legacy_router.delete(
    "/remove/{segment_id}",
    status_code=204,
    summary="Delete coil segment (legacy)",
    description="Legacy endpoint to delete a coil segment by ID.",
    response_description="Coil segment deleted.",
)
def delete_segment_legacy(
    segment_id: int,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_modify_access(current_data)
    repository = CoilSegmentRepository(db_session)
    CoilSegmentUseCases.remove_coil_segment_by_id(segment_id=segment_id, repository=repository)
    return None
