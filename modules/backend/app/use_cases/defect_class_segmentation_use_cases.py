from sqlalchemy.orm import Session
from sqlalchemy import desc
from db.model import DefectClassSegmentation as DefectClassSegmentationModel
from schemas.defect_class_segmentation_schemas import DefectClassSegmentationSchema, DefectClassSegmentationUpdateSchema

class DefectClassSegmentationUseCases:
    @staticmethod
    def add(defect_class: DefectClassSegmentationSchema, db_session: Session):

        try:
            defect_class_model = DefectClassSegmentationModel(**defect_class.dict())
            db_session.add(defect_class_model)
            db_session.commit()
            db_session.refresh(defect_class_model)
            return defect_class_model
        except Exception as e:
            db_session.rollback()
            raise Exception(f"Erro ao adicionar a classe de defeito: {str(e)}")

    @staticmethod
    def remove_by_id(id: int, db_session: Session):
        try:
            defect_class = db_session.query(DefectClassSegmentationModel).filter(DefectClassSegmentationModel.id == id).first()
            if defect_class:
                db_session.delete(defect_class)
                db_session.commit()
                return True
            return False
        except Exception as e:
            db_session.rollback()
            raise Exception(f"Erro ao remover a classe de defeito: {str(e)}")

    @staticmethod
    def update_by_id(id: int, defect_class_data: DefectClassSegmentationUpdateSchema, db_session: Session):
        try:
            defect_class = db_session.query(DefectClassSegmentationModel).filter(DefectClassSegmentationModel.id == id).first()
            if defect_class:
                for key, value in defect_class_data.dict(exclude_unset=True).items():
                    setattr(defect_class, key, value)
                db_session.commit()
                db_session.refresh(defect_class)
                return defect_class
            return None
        except Exception as e:
            db_session.rollback()
            raise Exception(f"Erro ao atualizar a classe de defeito: {str(e)}")

    @staticmethod
    def list(db_session: Session):
        try:
            return db_session.query(DefectClassSegmentationModel).order_by(desc(DefectClassSegmentationModel.id)).all()
        except Exception as e:
            raise Exception(f"Erro ao listar classes de defeitos: {str(e)}")

    @staticmethod
    def get_by_id(id: int, db_session: Session):
        try:
            return db_session.query(DefectClassSegmentationModel).filter(DefectClassSegmentationModel.id == id).first()
        except Exception as e:
            raise Exception(f"Erro ao obter a classe de defeito: {str(e)}")
