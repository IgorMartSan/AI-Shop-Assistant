from sqlalchemy.orm import Session
from db.model import CoilSegmentDefect as CoilSegmentDefectModel
from db.model import DefectClass as DefectClassModel
from schemas.coil_segment_defect_schemas import CoilSegmentDefectSchema, CoilSegmentDefectUpdateSchema

class CoilSegmentDefectUseCases:

    @staticmethod
    def check_defect_class(defect_class_id: int, db_session: Session) -> bool:
        """
        Verifica se um nome e uma cor já existem na tabela de classe de defeitos.

        :param name: Nome da classe de defeito
        :param color: Cor associada à classe de defeito
        :param db_session: Sessão do banco de dados
        :return: True se ambos nome e cor existirem, caso contrário False
        """
        defect_class = db_session.query(DefectClassModel).filter(
            DefectClassModel.id == defect_class_id,
        ).first()

        return defect_class is not None


    @staticmethod
    def add_coil_segment_defect(coil_segment_defect: CoilSegmentDefectSchema, db_session: Session):
        
        coil_segment_defect_model = CoilSegmentDefectModel(**coil_segment_defect.dict())
        db_session.add(coil_segment_defect_model)
        db_session.commit()


        

    @staticmethod
    def remove_coil_segment_defect_by_id(id: int, db_session: Session):
        coil_segment_defect = db_session.query(CoilSegmentDefectModel).filter(CoilSegmentDefectModel.id == id).first()
        if coil_segment_defect:
            db_session.delete(coil_segment_defect)
            db_session.commit()
            return True
        return False

    @staticmethod
    def update_coil_segment_defect_by_id(id: int, coil_segment_defect_data: CoilSegmentDefectUpdateSchema, db_session: Session):
        coil_segment_defect = db_session.query(CoilSegmentDefectModel).filter(CoilSegmentDefectModel.id == id).first()
        if coil_segment_defect:
            for key, value in coil_segment_defect_data.dict().items():
                if value is not None:
                    setattr(coil_segment_defect, key, value)
            db_session.commit()
            return True
        return False

    @staticmethod
    def list_coil_segment_defects(db_session: Session):
        return db_session.query(CoilSegmentDefectModel).all()

    @staticmethod
    def get_coil_segment_defect_by_id(id: int, db_session: Session):
        return db_session.query(CoilSegmentDefectModel).filter(CoilSegmentDefectModel.id == id).first()


    @staticmethod
    def get_defects_by_fragment_id(coil_segment_id: int, db_session: Session):
        """
        Retorna todos os defeitos de um fragmento específico.
        """
        return db_session.query(CoilSegmentDefectModel).filter(
            CoilSegmentDefectModel.coil_segment_id == coil_segment_id
        ).all()