from __future__ import annotations

from fastapi import HTTPException

from db.model import Coils as CoilsModel
from repositories.coil_repository import CoilRepository
from schemas.coil_schemas import CoilCreateSchema, CoilUpdateSchema, CoilNavigationSchema


class CoilUseCases:
    @staticmethod
    def add_coil(payload: CoilCreateSchema, repository: CoilRepository) -> CoilsModel:
        coil_model = CoilsModel(**payload.model_dump())
        return repository.create(coil_model)

    @staticmethod
    def get_or_create_coil(
        payload: CoilCreateSchema,
        repository: CoilRepository,
        window_hours: int = 3,
    ) -> CoilsModel:
        return repository.get_or_create_with_lock(
            name=payload.name,
            start_time=payload.start_time,
            end_time=payload.end_time,
            metadata_coil=payload.metadata_coil,
            window_hours=window_hours,
        )

    @staticmethod
    def remove_coil_by_id(coil_id: int, repository: CoilRepository) -> None:
        coil = repository.get_by_id(coil_id)
        if not coil:
            raise HTTPException(status_code=404, detail="Coil not found")
        repository.delete(coil)

    @staticmethod
    def update_coil_by_id(coil_id: int, coil_data: CoilUpdateSchema, repository: CoilRepository) -> CoilsModel:
        coil = repository.get_by_id(coil_id)
        if not coil:
            raise HTTPException(status_code=404, detail="Coil not found")
        for key, value in coil_data.model_dump(exclude_unset=True).items():
            setattr(coil, key, value)
        return repository.update(coil)

    @staticmethod
    def list_coils(
        repository: CoilRepository,
        skip: int = 0,
        limit: int = 100,
        name: str | None = None,
        q: str | None = None,
    ) -> list[CoilsModel]:
        return repository.list(skip=skip, limit=limit, name=name, q=q)

    @staticmethod
    def get_coil_by_id(coil_id: int, repository: CoilRepository) -> CoilsModel:
        coil = repository.get_by_id(coil_id)
        if not coil:
            raise HTTPException(status_code=404, detail="Coil not found")
        return coil

    @staticmethod
    def get_coil_with_navigation(coil_id: int, repository: CoilRepository) -> CoilNavigationSchema:
        result = repository.get_navigation(coil_id)
        if not result:
            raise HTTPException(status_code=404, detail="Coil not found")
        selected, previous, next_ = result
        return CoilNavigationSchema(
            selected_coil=selected,
            previous_coil=previous,
            next_coil=next_,
        )
