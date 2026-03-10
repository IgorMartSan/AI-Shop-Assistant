from sqlalchemy.orm import Session
from sqlalchemy import desc
from db.model import DefectClass as DefectClassModel
from schemas.defect_class_schemas import DefectClassSchema, DefectClassUpdateSchema

class DefectClassUseCases:
    @staticmethod
    def add_defect_class(defect_class: DefectClassSchema, db_session: Session):
        """
        Adiciona uma nova classe de defeito ao banco de dados.
        """
        try:
     
            defect_class_model = DefectClassModel(**defect_class.dict())
            db_session.add(defect_class_model)
            db_session.commit()
            db_session.refresh(defect_class_model)
            return defect_class_model
        except Exception as e:
            db_session.rollback()
            raise Exception(f"Erro ao adicionar a classe de defeito: {str(e)}")

    @staticmethod
    def remove_defect_class_by_id(id: int, db_session: Session):
        """
        Remove uma classe de defeito por ID.
        """
        try:
            defect_class = db_session.query(DefectClassModel).filter(DefectClassModel.id == id).first()
            if defect_class:
                db_session.delete(defect_class)
                db_session.commit()
                return True
            return False
        except Exception as e:
            db_session.rollback()
            raise Exception(f"Erro ao remover a classe de defeito: {str(e)}")

    @staticmethod
    def update_defect_class_by_id(id: int, defect_class_data: DefectClassUpdateSchema, db_session: Session):
        """
        Atualiza uma classe de defeito por ID.
        """
        try:
            defect_class = db_session.query(DefectClassModel).filter(DefectClassModel.id == id).first()
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
    def list_defect_classes(db_session: Session):
        """
        Lista todas as classes de defeitos.
        """
        try:
            return db_session.query(DefectClassModel).order_by(desc(DefectClassModel.id)).all()
        except Exception as e:
            raise Exception(f"Erro ao listar classes de defeitos: {str(e)}")

    @staticmethod
    def get_defect_class_by_id(id: int, db_session: Session):
        """
        Obtém uma classe de defeito por ID.
        """
        try:
            return db_session.query(DefectClassModel).filter(DefectClassModel.id == id).first()
        except Exception as e:
            raise Exception(f"Erro ao obter a classe de defeito: {str(e)}")
