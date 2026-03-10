from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from db.model import AnnotatorDefectClass as AnnotatorDefectClassModel


class AnnotatorDefectClassRepository:
    def __init__(self, db_session: Session):
        self._db = db_session

    def create(self, model_class: AnnotatorDefectClassModel) -> AnnotatorDefectClassModel:
        self._db.add(model_class)
        self._db.commit()
        self._db.refresh(model_class)
        return model_class

    def get_by_id(self, class_id: int) -> Optional[AnnotatorDefectClassModel]:
        return self._db.query(AnnotatorDefectClassModel).filter(AnnotatorDefectClassModel.id == class_id).first()

    def list(self, model_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> list[AnnotatorDefectClassModel]:
        query = self._db.query(AnnotatorDefectClassModel)
        if model_id is not None:
            query = query.filter(AnnotatorDefectClassModel.model_id == model_id)
        return query.offset(skip).limit(limit).all()

    def update(self, model_class: AnnotatorDefectClassModel) -> AnnotatorDefectClassModel:
        self._db.commit()
        self._db.refresh(model_class)
        return model_class

    def delete(self, model_class: AnnotatorDefectClassModel) -> None:
        self._db.delete(model_class)
        self._db.commit()
