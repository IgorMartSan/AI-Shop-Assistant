from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from dotenv import load_dotenv
from infra.postgresql.model import Coils, CoilSegment, CoilSegmentDefect, DefectClass, Cam, UserType, User
from infra.postgresql.base import Base
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import text
from datetime import datetime, timedelta
from sqlalchemy import func


class PostgreSQLConnection:
    def __init__(self, username, password, host, database, port):
        """
        Inicializa a classe Database com uma engine e configura a sessão.
        """
        SQLALCHEMY_DATABASE_URL = URL.create(
            drivername="postgresql",
            username=username,
            password=password,
            host=host,
            database=database,
            port=port
        )
        self.engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_size=20, max_overflow=30)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.session = SessionLocal()
        #Base.metadata.create_all(self.engine)
        

    def create_user_type(self, name, description=None):
        """
        Cria um novo tipo de usuário (UserType) no banco de dados.
        """
        new_user_type = UserType(name=name, description=description)
        try:
            self.session.add(new_user_type)
            self.session.commit()
            self.session.refresh(new_user_type)
            return new_user_type
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Error creating user type: {e}")
            return None

    def create_user(self, username, hashed_password, user_type_id, is_active=True):
        """
        Cria um novo usuário (User) no banco de dados.
        """
        new_user = User(username=username, hashed_password=hashed_password, user_type_id=user_type_id, is_active=is_active)
        try:
            self.session.add(new_user)
            self.session.commit()
            self.session.refresh(new_user)
            return new_user
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Error creating user: {e}")
            return None

    def create_cam(self, name, comment=None):
        """
        Cria uma nova câmera (Cam) no banco de dados.
        """
        new_cam = Cam(name=name, comment=comment)
        try:
            self.session.add(new_cam)
            self.session.commit()
            self.session.refresh(new_cam)
            return new_cam
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Error creating cam: {e}")
            return None

    # def create_coil(self, name, start_time=None, end_time=None):
    #     """
    #     Cria uma nova bobina (Coil) no banco de dados.
    #     """
    #     new_coil = Coils(name=name, start_time=start_time, end_time=end_time)
    #     try:
    #         self.session.add(new_coil)
    #         self.session.commit()
    #         self.session.refresh(new_coil)
    #         return new_coil
    #     except SQLAlchemyError as e:
    #         self.session.rollback()
    #         print(f"Error creating coil: {e}")
    #         return None
    


    def get_or_create_coil(self, name, start_time=None, end_time=None, intervalo_horas=6):
        try:
            # Lock baseado no nome da bobina
            lock_sql = text("SELECT pg_advisory_xact_lock(hashtext(:name))")
            self.session.execute(lock_sql, {"name": name})

            # 🔹 Usa hora do banco para calcular o limite
            limite_tempo = self.session.query(func.now()).scalar() - timedelta(hours=intervalo_horas)

            # Verifica se já existe bobina recente com esse nome
            coil = (
                self.session.query(Coils)
                .filter(Coils.name == name)
                .filter(Coils.start_time >= limite_tempo)
                .order_by(Coils.start_time.desc())
                .first()
            )

            if coil:
                return coil

            # 🔹 Cria nova bobina usando hora do banco
            new_coil = Coils(
                name=name,
                start_time=start_time or func.now(),
                end_time=end_time
            )
            self.session.add(new_coil)
            self.session.commit()
            self.session.refresh(new_coil)
            return new_coil

        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Erro ao criar ou buscar bobina: {e}")
            return None




        



    def create_coil_segment(self, coil_id, cam_id, line_position_start, line_position_end, 
                            original_image_path=None, border_positions_left_px=None, border_positions_right_px=None, 
                            width_image_px=None, height_image_px=None, medium_image_path=None, medium_image_scale=None,
                            mini_image_path=None, mini_image_scale=None, distance_per_px_axis_x=None, 
                            distance_per_px_axis_y=None, segment_metadata=None, image_metadata=None, defect_image_path=None):
        """
        Cria um novo segmento de bobina (CoilSegment) no banco de dados.
        """
        new_coil_segment = CoilSegment(
            coil_id=coil_id,
            cam_id=cam_id,
            line_position_start=line_position_start,
            line_position_end=line_position_end,
            original_image_path=original_image_path,
            defect_image_path=defect_image_path,
            border_positions_left_px=border_positions_left_px,
            border_positions_right_px=border_positions_right_px,
            width_image_px=width_image_px,
            height_image_px=height_image_px,
            medium_image_path=medium_image_path,
            medium_image_scale=medium_image_scale,
            mini_image_path=mini_image_path,
            mini_image_scale=mini_image_scale,
            distance_per_px_axis_x=distance_per_px_axis_x,
            distance_per_px_axis_y=distance_per_px_axis_y,
            segment_metadata=segment_metadata,
            image_metadata=image_metadata,
            

        )
        try:
            self.session.add(new_coil_segment)
            self.session.commit()
            self.session.refresh(new_coil_segment)
            return new_coil_segment
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Error creating coil segment: {e}")
            return None

    def add_defect_in_coil_fragment_by_name(self, coil_segment_id, defect_class_name, center_x_px, center_y_px, 
                                            width_px, height_px, defect_image_path=None, color = None ):
        """
        Adiciona um defeito a um fragmento (segmento) de uma bobina (CoilSegmentDefect) pelo nome da classe de defeito.
        Se a classe de defeito não existir, cria uma nova classe com uma cor padrão e um comentário.
        """
        try:
            # Consulta para obter ou criar a classe de defeito
            defect_class = self.session.query(DefectClass).filter_by(name=defect_class_name).first()
            if not defect_class:
                # Se a classe de defeito não existir, cria uma nova com cor e comentário padrão
                defect_class = DefectClass(
                    name=defect_class_name, 
                    color=color or "#FFFF00",  # Cor padrão
                    comment=f"Defect of type {defect_class_name}"  # Comentário padrão
                )
                self.session.add(defect_class)
                self.session.commit()
                self.session.refresh(defect_class)

            # Criar o defeito associado ao fragmento de bobina
            new_defect = CoilSegmentDefect(
                coil_segment_id=coil_segment_id,
                defect_class_id=defect_class.id,
                center_x_px=center_x_px,
                center_y_px=center_y_px,
                width_px=width_px,
                height_px=height_px,
                defect_image_path=defect_image_path
            )
            self.session.add(new_defect)
            self.session.commit()
            self.session.refresh(new_defect)
            return new_defect
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Error adding defect to coil fragment: {e}")
            return None

    def add_defect_in_coil_fragment_by_id(self, coil_segment_id, defect_class_id, center_x_px, center_y_px, 
                                          width_px, height_px, defect_image_path=None):
        """
        Adiciona um defeito a um fragmento (segmento) de uma bobina (CoilSegmentDefect) pelo ID da classe de defeito.
        Se o ID da classe de defeito não existir, a função não faz nada.
        """
        try:
            # Verifica se o ID da classe de defeito existe
            defect_class = self.session.query(DefectClass).filter_by(id=defect_class_id).first()
            if not defect_class:
                print(f"Defect class with ID {defect_class_id} not found. No defect added.")
                return None

            # Criar o defeito associado ao fragmento de bobina
            new_defect = CoilSegmentDefect(
                coil_segment_id=coil_segment_id,
                defect_class_id=defect_class.id,
                center_x_px=center_x_px,
                center_y_px=center_y_px,
                width_px=width_px,
                height_px=height_px,
                defect_image_path=defect_image_path
            )
            self.session.add(new_defect)
            self.session.commit()
            self.session.refresh(new_defect)
            return new_defect
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Error adding defect to coil fragment: {e}")
            return None

    def create_defect_class(self, name, color, comment=None):
        """
        Cria uma nova classe de defeito (DefectClass) no banco de dados.
        """
        new_defect_class = DefectClass(name=name, color=color, comment=comment)
        try:
            self.session.add(new_defect_class)
            self.session.commit()
            self.session.refresh(new_defect_class)
            return new_defect_class
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Error creating defect class: {e}")
            return None

    def close(self):
        """
        Fecha a sessão atual.
        """
        self.session.close()
