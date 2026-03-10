from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from db.model import CoilSegmentAnnotatorSegmentation as CoilSegmentAnnotatorSegmentationModel


class CoilSegmentAnnotatorSegRepository:
    def __init__(self, db_session: Session):
        self._db = db_session

    def create(self, segmentation: CoilSegmentAnnotatorSegmentationModel) -> CoilSegmentAnnotatorSegmentationModel:
        self._db.add(segmentation)
        self._db.commit()
        self._db.refresh(segmentation)
        return segmentation

    def get_by_id(self, segmentation_id: int) -> Optional[CoilSegmentAnnotatorSegmentationModel]:
        return self._db.query(CoilSegmentAnnotatorSegmentationModel).filter(
            CoilSegmentAnnotatorSegmentationModel.id == segmentation_id
        ).first()

    def list(
        self,
        coil_segment_id: Optional[int] = None,
        model_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[CoilSegmentAnnotatorSegmentationModel]:
        query = self._db.query(CoilSegmentAnnotatorSegmentationModel)
        if coil_segment_id is not None:
            query = query.filter(CoilSegmentAnnotatorSegmentationModel.coil_segment_id == coil_segment_id)
        if model_id is not None:
            query = query.filter(CoilSegmentAnnotatorSegmentationModel.model_id == model_id)
        return query.offset(skip).limit(limit).all()

    def update(self, segmentation: CoilSegmentAnnotatorSegmentationModel) -> CoilSegmentAnnotatorSegmentationModel:
        self._db.commit()
        self._db.refresh(segmentation)
        return segmentation

    def delete(self, segmentation: CoilSegmentAnnotatorSegmentationModel) -> None:
        self._db.delete(segmentation)
        self._db.commit()
