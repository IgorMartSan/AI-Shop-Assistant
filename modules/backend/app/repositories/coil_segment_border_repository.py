from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from db.model import CoilSegmentBorder as CoilSegmentBorderModel


class CoilSegmentBorderRepository:
    def __init__(self, db_session: Session):
        self._db = db_session

    def create(self, border: CoilSegmentBorderModel) -> CoilSegmentBorderModel:
        self._db.add(border)
        self._db.commit()
        self._db.refresh(border)
        return border

    def get_by_id(self, border_id: int) -> Optional[CoilSegmentBorderModel]:
        return self._db.query(CoilSegmentBorderModel).filter(CoilSegmentBorderModel.id == border_id).first()

    def list(self, coil_segment_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> list[CoilSegmentBorderModel]:
        query = self._db.query(CoilSegmentBorderModel)
        if coil_segment_id is not None:
            query = query.filter(CoilSegmentBorderModel.coil_segment_id == coil_segment_id)
        return query.offset(skip).limit(limit).all()

    def update(self, border: CoilSegmentBorderModel) -> CoilSegmentBorderModel:
        self._db.commit()
        self._db.refresh(border)
        return border

    def delete(self, border: CoilSegmentBorderModel) -> None:
        self._db.delete(border)
        self._db.commit()
