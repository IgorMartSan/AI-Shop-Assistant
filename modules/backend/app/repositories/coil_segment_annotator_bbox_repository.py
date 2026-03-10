from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session, joinedload

from db.model import CoilSegmentAnnotatorBBox as CoilSegmentAnnotatorBBoxModel


class CoilSegmentAnnotatorBBoxRepository:
    def __init__(self, db_session: Session):
        self._db = db_session

    def create(self, bbox: CoilSegmentAnnotatorBBoxModel) -> CoilSegmentAnnotatorBBoxModel:
        self._db.add(bbox)
        self._db.commit()
        self._db.refresh(bbox)
        return bbox

    def get_by_id(self, bbox_id: int) -> Optional[CoilSegmentAnnotatorBBoxModel]:
        return (
            self._db.query(CoilSegmentAnnotatorBBoxModel)
            .options(joinedload(CoilSegmentAnnotatorBBoxModel.model_class))
            .filter(CoilSegmentAnnotatorBBoxModel.id == bbox_id)
            .first()
        )

    def list(
        self,
        coil_segment_id: Optional[int] = None,
        model_id: Optional[int] = None,
        model_class_id: Optional[int] = None,
        confidence_min: Optional[float] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[CoilSegmentAnnotatorBBoxModel]:
        query = self._db.query(CoilSegmentAnnotatorBBoxModel)
        if coil_segment_id is not None:
            query = query.filter(CoilSegmentAnnotatorBBoxModel.coil_segment_id == coil_segment_id)
        if model_id is not None:
            query = query.filter(CoilSegmentAnnotatorBBoxModel.model_id == model_id)
        if model_class_id is not None:
            query = query.filter(CoilSegmentAnnotatorBBoxModel.model_class_id == model_class_id)
        if confidence_min is not None:
            query = query.filter(CoilSegmentAnnotatorBBoxModel.confidence >= confidence_min)
        return query.offset(skip).limit(limit).all()

    def update(self, bbox: CoilSegmentAnnotatorBBoxModel) -> CoilSegmentAnnotatorBBoxModel:
        self._db.commit()
        self._db.refresh(bbox)
        return bbox

    def delete(self, bbox: CoilSegmentAnnotatorBBoxModel) -> None:
        self._db.delete(bbox)
        self._db.commit()
