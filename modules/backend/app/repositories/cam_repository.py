from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from db.model import Cam as CamModel


class CamRepository:
    def __init__(self, db_session: Session):
        self._db = db_session

    def create(self, cam: CamModel) -> CamModel:
        self._db.add(cam)
        self._db.commit()
        self._db.refresh(cam)
        return cam

    def get_by_id(self, cam_id: int) -> Optional[CamModel]:
        return self._db.query(CamModel).filter(CamModel.id == cam_id).first()

    def get_by_name(self, name: str) -> Optional[CamModel]:
        return self._db.query(CamModel).filter(CamModel.name == name).first()

    def list(self, skip: int = 0, limit: int = 100, name: Optional[str] = None) -> list[CamModel]:
        query = self._db.query(CamModel)
        if name:
            query = query.filter(CamModel.name.ilike(f"%{name}%"))
        return query.offset(skip).limit(limit).all()

    def update(self, cam: CamModel) -> CamModel:
        self._db.commit()
        self._db.refresh(cam)
        return cam

    def delete(self, cam: CamModel) -> None:
        self._db.delete(cam)
        self._db.commit()
