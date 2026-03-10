from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from db.model import Annotator as AnnotatorModel


class AnnotatorRepository:
    def __init__(self, db_session: Session):
        self._db = db_session

    def create(self, annotator: AnnotatorModel) -> AnnotatorModel:
        self._db.add(annotator)
        self._db.commit()
        self._db.refresh(annotator)
        return annotator

    def get_by_id(self, annotator_id: int) -> Optional[AnnotatorModel]:
        return self._db.query(AnnotatorModel).filter(AnnotatorModel.id == annotator_id).first()

    def get_by_name(self, name: str) -> Optional[AnnotatorModel]:
        return self._db.query(AnnotatorModel).filter(AnnotatorModel.name == name).first()

    def list(self, skip: int = 0, limit: int = 100, name: Optional[str] = None) -> list[AnnotatorModel]:
        query = self._db.query(AnnotatorModel)
        if name:
            query = query.filter(AnnotatorModel.name.ilike(f"%{name}%"))
        return query.offset(skip).limit(limit).all()

    def update(self, annotator: AnnotatorModel) -> AnnotatorModel:
        self._db.commit()
        self._db.refresh(annotator)
        return annotator

    def delete(self, annotator: AnnotatorModel) -> None:
        self._db.delete(annotator)
        self._db.commit()
