from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session, joinedload

from db.model import CoilSegment as CoilSegmentModel
from db.model import CoilSegmentAnnotatorBBox as CoilSegmentAnnotatorBBoxModel
from db.model import AnnotatorDefectClass as AnnotatorDefectClassModel


class CoilSegmentRepository:
    def __init__(self, db_session: Session):
        self._db = db_session

    def create(self, segment: CoilSegmentModel) -> CoilSegmentModel:
        self._db.add(segment)
        self._db.commit()
        self._db.refresh(segment)
        return segment

    def get_by_id(self, segment_id: int) -> Optional[CoilSegmentModel]:
        return self._db.query(CoilSegmentModel).filter(CoilSegmentModel.id == segment_id).first()

    def get_with_bboxes(self, segment_id: int) -> Optional[CoilSegmentModel]:
        return (
            self._db.query(CoilSegmentModel)
            .options(joinedload(CoilSegmentModel.defects_bbox).joinedload(CoilSegmentAnnotatorBBoxModel.model_class))
            .filter(CoilSegmentModel.id == segment_id)
            .first()
        )

    def list(
        self,
        skip: int = 0,
        limit: int = 100,
        coil_id: Optional[int] = None,
        cam_id: Optional[int] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        position_start_min: Optional[float] = None,
        position_start_max: Optional[float] = None,
    ) -> list[CoilSegmentModel]:
        query = self._db.query(CoilSegmentModel)
        if coil_id is not None:
            query = query.filter(CoilSegmentModel.coil_id == coil_id)
        if cam_id is not None:
            query = query.filter(CoilSegmentModel.cam_id == cam_id)
        if date_from is not None:
            query = query.filter(CoilSegmentModel.data >= date_from)
        if date_to is not None:
            query = query.filter(CoilSegmentModel.data <= date_to)
        if position_start_min is not None:
            query = query.filter(CoilSegmentModel.line_position_start >= position_start_min)
        if position_start_max is not None:
            query = query.filter(CoilSegmentModel.line_position_start <= position_start_max)
        return query.offset(skip).limit(limit).all()

    def list_with_bboxes(
        self,
        coil_id: Optional[int],
        cam_id: Optional[int],
        skip: int = 0,
        limit: int = 100,
    ) -> list[CoilSegmentModel]:
        query = self._db.query(CoilSegmentModel).options(
            joinedload(CoilSegmentModel.defects_bbox).joinedload(CoilSegmentAnnotatorBBoxModel.model_class)
        )
        if coil_id is not None:
            query = query.filter(CoilSegmentModel.coil_id == coil_id)
        if cam_id is not None:
            query = query.filter(CoilSegmentModel.cam_id == cam_id)
        return query.order_by(CoilSegmentModel.line_position_start.asc()).offset(skip).limit(limit).all()

    def update(self, segment: CoilSegmentModel) -> CoilSegmentModel:
        self._db.commit()
        self._db.refresh(segment)
        return segment

    def delete(self, segment: CoilSegmentModel) -> None:
        self._db.delete(segment)
        self._db.commit()
