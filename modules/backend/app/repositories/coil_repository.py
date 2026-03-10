from __future__ import annotations

from typing import Optional

from datetime import datetime, timedelta
import hashlib

from sqlalchemy import func, select, or_, cast, String, nulls_last
from sqlalchemy.orm import Session

from db.model import Coils as CoilsModel


class CoilRepository:
    def __init__(self, db_session: Session):
        self._db = db_session

    def create(self, coil: CoilsModel) -> CoilsModel:
        self._db.add(coil)
        self._db.commit()
        self._db.refresh(coil)
        return coil

    def get_by_id(self, coil_id: int) -> Optional[CoilsModel]:
        return self._db.query(CoilsModel).filter(CoilsModel.id == coil_id).first()

    def list(
        self,
        skip: int = 0,
        limit: int = 100,
        name: Optional[str] = None,
        q: Optional[str] = None,
    ) -> list[CoilsModel]:
        query = self._db.query(CoilsModel)
        if q:
            pattern_prefix = f"{q}%"
            pattern_any = f"%{q}%"
            query = query.filter(
                or_(
                    CoilsModel.name.ilike(pattern_prefix),
                    cast(CoilsModel.id, String).ilike(pattern_prefix),
                    func.to_char(CoilsModel.start_time, "DD/MM/YYYY").ilike(pattern_any),
                    func.to_char(CoilsModel.start_time, "DD/MM/YYYY HH24:MI:SS").ilike(pattern_any),
                    func.to_char(CoilsModel.start_time, "YYYY-MM-DD").ilike(pattern_any),
                    func.to_char(CoilsModel.start_time, "YYYY-MM-DD HH24:MI:SS").ilike(pattern_any),
                    func.to_char(CoilsModel.end_time, "DD/MM/YYYY").ilike(pattern_any),
                    func.to_char(CoilsModel.end_time, "DD/MM/YYYY HH24:MI:SS").ilike(pattern_any),
                    func.to_char(CoilsModel.end_time, "YYYY-MM-DD").ilike(pattern_any),
                    func.to_char(CoilsModel.end_time, "YYYY-MM-DD HH24:MI:SS").ilike(pattern_any),
                    cast(CoilsModel.metadata_coil, String).ilike(pattern_any),
                )
            )
        elif name:
            query = query.filter(CoilsModel.name.ilike(f"%{name}%"))
        query = query.order_by(nulls_last(CoilsModel.start_time.desc()), CoilsModel.id.desc())
        return query.offset(skip).limit(limit).all()

    def update(self, coil: CoilsModel) -> CoilsModel:
        self._db.commit()
        self._db.refresh(coil)
        return coil

    def delete(self, coil: CoilsModel) -> None:
        self._db.delete(coil)
        self._db.commit()

    def get_or_create_with_lock(
        self,
        name: str,
        start_time,
        end_time,
        metadata_coil,
        window_hours: int = 3,
    ) -> CoilsModel:
        lock_key = self._advisory_lock_key(name)
        self._db.execute(select(func.pg_advisory_xact_lock(lock_key)))

        latest = (
            self._db.query(CoilsModel)
            .filter(CoilsModel.name == name)
            .order_by(CoilsModel.start_time.desc(), CoilsModel.id.desc())
            .first()
        )
        now = datetime.utcnow()
        if latest:
            reference_time = latest.start_time
            if reference_time and now - reference_time < timedelta(hours=window_hours):
                return latest

        coil = CoilsModel(
            name=name,
            start_time=start_time or now,
            end_time=end_time,
            metadata_coil=metadata_coil,
        )
        self._db.add(coil)
        self._db.commit()
        self._db.refresh(coil)
        return coil

    @staticmethod
    def _advisory_lock_key(value: str) -> int:
        digest = hashlib.sha256(value.encode("utf-8")).digest()
        return int.from_bytes(digest[:8], "big") & 0x7FFFFFFFFFFFFFFF

    def get_navigation(self, coil_id: int):
        selected = self._db.query(CoilsModel).filter(CoilsModel.id == coil_id).first()
        if not selected:
            return None
        previous = (
            self._db.query(CoilsModel)
            .filter(CoilsModel.id < coil_id)
            .order_by(CoilsModel.id.desc())
            .first()
        )
        next_ = (
            self._db.query(CoilsModel)
            .filter(CoilsModel.id > coil_id)
            .order_by(CoilsModel.id.asc())
            .first()
        )
        return selected, previous, next_
