from __future__ import annotations

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from db.database import get_db
from repositories.coil_repository import CoilRepository
from schemas.coil_schemas import (
    CoilCreateSchema,
    CoilOutSchema,
    CoilUpdateSchema,
    CoilNavigationSchema,
    PaginatedCoilsSchema,
    CoilWithCamerasSchema,
    CoilCameraCountSchema,
)
from use_cases.coil_use_cases import CoilUseCases
from utils.auth import AuthUtils
from utils.enums import UserTypeEnum
from db.model import CoilSegment, Cam
from sqlalchemy import func


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

router = APIRouter(prefix="/coils", tags=["Coils"])


def _attach_camera_counts(coils: list, db_session: Session) -> list[CoilWithCamerasSchema]:
    if not coils:
        return []

    coil_ids = [coil.id for coil in coils]
    rows = (
        db_session.query(
            CoilSegment.coil_id,
            Cam.id,
            Cam.name,
            func.count(CoilSegment.id),
        )
        .join(Cam, CoilSegment.cam_id == Cam.id)
        .filter(CoilSegment.coil_id.in_(coil_ids))
        .group_by(CoilSegment.coil_id, Cam.id, Cam.name)
        .all()
    )

    camera_map: dict[int, list[CoilCameraCountSchema]] = {coil_id: [] for coil_id in coil_ids}
    for coil_id, cam_id, cam_name, frames in rows:
        camera_map[coil_id].append(
            CoilCameraCountSchema(cam_id=cam_id, cam_name=cam_name, frames=frames)
        )

    result: list[CoilWithCamerasSchema] = []
    for coil in coils:
        result.append(
            CoilWithCamerasSchema(
                id=coil.id,
                name=coil.name,
                start_time=coil.start_time,
                end_time=coil.end_time,
                metadata_coil=coil.metadata_coil,
                cameras=camera_map.get(coil.id, []),
            )
        )
    return result


@router.post(
    "",
    response_model=CoilOutSchema,
    status_code=201,
    summary="Create coil",
    description="Create a new coil.",
    response_description="Coil created.",
)
def create_coil(
    payload: CoilCreateSchema,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_modify_access(current_data)
    repository = CoilRepository(db_session)
    return CoilUseCases.add_coil(payload=payload, repository=repository)


@router.post(
    "/get-or-create",
    response_model=CoilOutSchema,
    summary="Get or create coil",
    description=(
        "Get the most recent coil by name if it was created within the last 3 hours; "
        "otherwise create a new one. Uses a database advisory lock to avoid races."
    ),
    response_description="Existing or newly created coil.",
)
def get_or_create_coil(
    payload: CoilCreateSchema,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_modify_access(current_data)

    repository = CoilRepository(db_session)
    return CoilUseCases.get_or_create_coil(payload=payload, repository=repository, window_hours=3)


@router.get(
    "",
    response_model=list[CoilWithCamerasSchema],
    summary="List coils",
    description="List coils with optional filtering and pagination.",
    response_description="List of coils.",
)
def list_coils(
    skip: int = 0,
    limit: int = 100,
    name: str | None = Query(default=None),
    q: str | None = Query(default=None),
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_view_access(current_data)
    repository = CoilRepository(db_session)
    coils = CoilUseCases.list_coils(repository=repository, skip=skip, limit=limit, name=name, q=q)
    return _attach_camera_counts(coils=coils, db_session=db_session)


@router.get(
    "/paginated",
    response_model=PaginatedCoilsSchema,
    summary="List coils (paginated)",
    description="List coils using page and per_page parameters.",
    response_description="Paginated list of coils.",
)
def list_paginated(
    page: int = 1,
    per_page: int = 50,
    name: str | None = Query(default=None),
    q: str | None = Query(default=None),
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_view_access(current_data)
    repository = CoilRepository(db_session)
    skip = (page - 1) * per_page
    coils = CoilUseCases.list_coils(repository=repository, skip=skip, limit=per_page, name=name, q=q)
    total_count = len(CoilUseCases.list_coils(repository=repository, skip=0, limit=100000, name=name, q=q))
    total_pages = (total_count + per_page - 1) // per_page
    return PaginatedCoilsSchema(
        coils=_attach_camera_counts(coils=coils, db_session=db_session),
        page=page,
        per_page=per_page,
        total_count=total_count,
        total_pages=total_pages,
    )


@router.get(
    "/{coil_id}",
    response_model=CoilOutSchema,
    summary="Get coil",
    description="Get a coil by ID.",
    response_description="Coil details.",
)
def get_coil(
    coil_id: int,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_view_access(current_data)
    repository = CoilRepository(db_session)
    return CoilUseCases.get_coil_by_id(coil_id=coil_id, repository=repository)


@router.patch(
    "/{coil_id}",
    response_model=CoilOutSchema,
    summary="Update coil",
    description="Update a coil by ID.",
    response_description="Coil updated.",
)
def update_coil(
    coil_id: int,
    payload: CoilUpdateSchema,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_modify_access(current_data)
    repository = CoilRepository(db_session)
    return CoilUseCases.update_coil_by_id(coil_id=coil_id, coil_data=payload, repository=repository)


@router.delete(
    "/{coil_id}",
    status_code=204,
    summary="Delete coil",
    description="Delete a coil by ID.",
    response_description="Coil deleted.",
)
def delete_coil(
    coil_id: int,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_modify_access(current_data)
    repository = CoilRepository(db_session)
    CoilUseCases.remove_coil_by_id(coil_id=coil_id, repository=repository)
    return None


@router.get(
    "/{coil_id}/navigation",
    response_model=CoilNavigationSchema,
    summary="Get coil navigation",
    description="Get navigation details for a coil.",
    response_description="Coil navigation details.",
)
def get_navigation(
    coil_id: int,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_view_access(current_data)
    repository = CoilRepository(db_session)
    return CoilUseCases.get_coil_with_navigation(coil_id=coil_id, repository=repository)


legacy_router = APIRouter(prefix="/coil", tags=["Coil-legacy"])


@legacy_router.post(
    "/add",
    response_model=CoilOutSchema,
    status_code=201,
    summary="Create coil (legacy)",
    description="Legacy endpoint to create a new coil.",
    response_description="Coil created.",
)
def add_coil_legacy(
    payload: CoilCreateSchema,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_modify_access(current_data)
    repository = CoilRepository(db_session)
    return CoilUseCases.add_coil(payload=payload, repository=repository)


@legacy_router.get(
    "/list",
    response_model=list[CoilOutSchema],
    summary="List coils (legacy)",
    description="Legacy endpoint to list coils.",
    response_description="List of coils.",
)
def list_coils_legacy(
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_view_access(current_data)
    repository = CoilRepository(db_session)
    return CoilUseCases.list_coils(repository=repository)


@legacy_router.get(
    "/get/{coil_id}",
    response_model=CoilOutSchema,
    summary="Get coil (legacy)",
    description="Legacy endpoint to get a coil by ID.",
    response_description="Coil details.",
)
def get_coil_legacy(
    coil_id: int,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_view_access(current_data)
    repository = CoilRepository(db_session)
    return CoilUseCases.get_coil_by_id(coil_id=coil_id, repository=repository)


@legacy_router.put(
    "/update/{coil_id}",
    response_model=CoilOutSchema,
    summary="Update coil (legacy)",
    description="Legacy endpoint to update a coil by ID.",
    response_description="Coil updated.",
)
def update_coil_legacy(
    coil_id: int,
    payload: CoilUpdateSchema,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_modify_access(current_data)
    repository = CoilRepository(db_session)
    return CoilUseCases.update_coil_by_id(coil_id=coil_id, coil_data=payload, repository=repository)


@legacy_router.delete(
    "/remove/{coil_id}",
    status_code=204,
    summary="Delete coil (legacy)",
    description="Legacy endpoint to delete a coil by ID.",
    response_description="Coil deleted.",
)
def delete_coil_legacy(
    coil_id: int,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_modify_access(current_data)
    repository = CoilRepository(db_session)
    CoilUseCases.remove_coil_by_id(coil_id=coil_id, repository=repository)
    return None


@legacy_router.get(
    "/navigation/{coil_id}",
    response_model=CoilNavigationSchema,
    summary="Get coil navigation (legacy)",
    description="Legacy endpoint to get coil navigation details.",
    response_description="Coil navigation details.",
)
def navigation_legacy(
    coil_id: int,
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_view_access(current_data)
    repository = CoilRepository(db_session)
    return CoilUseCases.get_coil_with_navigation(coil_id=coil_id, repository=repository)


@legacy_router.get(
    "/list_paginated",
    response_model=PaginatedCoilsSchema,
    summary="List coils (paginated, legacy)",
    description="Legacy endpoint to list coils using pagination.",
    response_description="Paginated list of coils.",
)
def list_paginated_legacy(
    page: int = 1,
    per_page: int = 50,
    name: str | None = Query(default=None),
    db_session: Session = Depends(get_db),
    current_data: dict = Depends(AuthUtils.get_current_data_from_token),
):
    _require_view_access(current_data)
    repository = CoilRepository(db_session)
    skip = (page - 1) * per_page
    coils = CoilUseCases.list_coils(repository=repository, skip=skip, limit=per_page, name=name)
    total_count = len(CoilUseCases.list_coils(repository=repository, skip=0, limit=100000, name=name))
    total_pages = (total_count + per_page - 1) // per_page
    return PaginatedCoilsSchema(
        coils=coils,
        page=page,
        per_page=per_page,
        total_count=total_count,
        total_pages=total_pages,
    )
