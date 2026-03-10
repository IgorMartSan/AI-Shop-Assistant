from enum import Enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    DateTime,
    ForeignKey,
    func,
    Boolean,
)
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import JSONB
from db.database import Base


# ==============================
# Enum de usuário
# ==============================
class UserTypeEnum(str, Enum):
    ADMIN = "admin"
    USER = "user"
    SUPERUSER = "superuser"


# ==============================
# Users
# ==============================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False, unique=True, comment="Username")
    email = Column(String, nullable=False, unique=True, comment="User email for login")
    hashed_password = Column(String, nullable=False, comment="Hashed password")
    is_active = Column(Boolean, default=True, comment="Indicates if the user account is active")
    user_type = Column(SQLAlchemyEnum(UserTypeEnum), nullable=False, comment="Type of user")
    created_at = Column(DateTime, default=func.now(), comment="Account creation date")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="Last update timestamp")


# ==============================
# Cam
# ==============================
class Cam(Base):
    __tablename__ = "cams"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True, comment="Name of the camera")
    comment = Column(Text, nullable=True, comment="Additional information about the camera")
    metadata_cam = Column(JSONB, nullable=True, comment="JSON field to store additional metadata")
    segments = relationship(
        "CoilSegment",
        back_populates="cam",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


# ==============================
# Coils
# ==============================
class Coils(Base):
    __tablename__ = "coils"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, comment="Name of the coil")
    start_time = Column(DateTime, nullable=False, server_default=func.now(), comment="Start time of the coil measurement")
    end_time = Column(DateTime, nullable=True, comment="End time of the coil measurement")
    metadata_coil = Column(JSONB, nullable=True, comment="JSON field to store additional metadata")
    segments = relationship(
        "CoilSegment",
        back_populates="coil",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


# ==============================
# CoilSegment
# ==============================
class CoilSegment(Base):
    __tablename__ = "coil_segments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    data = Column(DateTime, server_default=func.now(), nullable=False, comment="Date and time when the segment was taken")
    coil_id = Column(Integer, ForeignKey("coils.id", ondelete="CASCADE"), nullable=False, comment="Foreign key to the coils table")
    cam_id = Column(Integer, ForeignKey("cams.id", ondelete="CASCADE"), nullable=False, index=True, comment="Foreign key to the cams table")
    line_position_start = Column(Float, nullable=False, index=True, comment="Start position of the segment along the coil, representing the distance in meters (e.g., 0m, 1m, etc.)")
    line_position_end = Column(Float, nullable=False, comment="End position of the segment along the coil, representing the distance in meters (e.g., 0m, 1m, etc.)")
    original_image_path = Column(String, nullable=True, comment="Path of the original image")
    distance_per_px_axis_x = Column(Float, nullable=True, comment="Meters per pixel in the X direction (SI)")
    distance_per_px_axis_y = Column(Float, nullable=True, comment="Meters per pixel in the Y direction (SI)")
    width_image_px = Column(Integer, nullable=True, comment="width of the original image")
    height_image_px = Column(Integer, nullable=True, comment="height of the original image")
    medium_image_path = Column(String, nullable=True, comment="Path of the medium-sized image")
    medium_image_scale = Column(Float, nullable=True, comment="Scaling factor applied to the medium-sized image between (0-1)")
    mini_image_path = Column(String, nullable=True, comment="Path of the mini-sized image")
    mini_image_scale = Column(Float, nullable=True, comment="Scaling factor applied to the mini-sized image between (0-1)")
    metadata_segment = Column(JSONB, nullable=True, comment="JSON field to store additional metadata related to the segment")

    coil = relationship("Coils", back_populates="segments", passive_deletes=True)
    cam = relationship("Cam", back_populates="segments", passive_deletes=True)
    # defects = relationship("CoilSegmentDefect", back_populates="segment", cascade="all, delete-orphan", passive_deletes=True)
    borders = relationship(
        "CoilSegmentBorder",
        back_populates="segment",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    model_segmentations = relationship(
        "CoilSegmentAnnotatorSegmentation",
        back_populates="segment",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    defects_bbox = relationship(
        "CoilSegmentAnnotatorBBox",
        back_populates="segment",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


# ==============================
# CoilSegmentBorder (vários pares por segmento, sem enum)
# ==============================
class CoilSegmentBorder(Base):
    __tablename__ = "coil_segment_borders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    coil_segment_id = Column(Integer, ForeignKey("coil_segments.id", ondelete="CASCADE"), nullable=False, index=True, comment="Segmento ao qual este PAR de borda pertence")
    pair_idx = Column(Integer, nullable=True, comment="Ordem do par (opcional)")
    x1_px = Column(Float, nullable=False, comment="Ponto do LADO ESQUERDO (LEFT) - X em px")
    y1_px = Column(Float, nullable=False, comment="Ponto do LADO ESQUERDO (LEFT) - Y em px")
    x2_px = Column(Float, nullable=False, comment="Ponto do LADO DIREITO (RIGHT) - X em px")
    y2_px = Column(Float, nullable=False, comment="Ponto do LADO DIREITO (RIGHT) - Y em px")
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    segment = relationship(
        "CoilSegment", back_populates="borders", passive_deletes=True
    )


# ==============================
# DefectClass
# ==============================
# class DefectClass(Base):
#     __tablename__ = "defect_class"

#     id = Column(Integer, primary_key=True, autoincrement=True)
#     name = Column(String, nullable=False, unique=True, comment="Name of the defect class")
#     color = Column(String, nullable=False, comment="Hex color for the defect class")
#     comment = Column(Text, nullable=True, comment="Comment about the defect class")
#     defects = relationship("CoilSegmentDefect", back_populates="defect_class", cascade="all, delete-orphan", passive_deletes=True)


# ==============================
# CoilSegmentDefect (bbox legacy por classe humana/geral)
# ==============================
# class CoilSegmentDefect(Base):
#     __tablename__ = "coil_segment_defects"

#     id = Column(Integer, primary_key=True, autoincrement=True)
#     coil_segment_id = Column(Integer, ForeignKey("coil_segments.id", ondelete="CASCADE"), nullable=False, comment="Foreign key to the coil segments table")
#     defect_class_id = Column(Integer, ForeignKey("defect_class.id", ondelete="CASCADE"), nullable=False, comment="Foreign key to the defect class table")
#     width_px = Column(Float, nullable=False, comment="Width of the bounding box in pixels")
#     height_px = Column(Float, nullable=False, comment="Height of the bounding box in pixels")
#     defect_image_path = Column(String, nullable=True, comment="Path of the defect image")
#     segment = relationship("CoilSegment", back_populates="defects", passive_deletes=True)
#     defect_class = relationship("DefectClass", back_populates="defects", passive_deletes=True)


# ==============================
# DefectClassSegmentation (paleta/legenda de cores por pixel, se usar)
# ==============================
# class DefectClassSegmentation(Base):
#     __tablename__ = "defect_class_segmentation"

#     id = Column(Integer, primary_key=True, autoincrement=True)
#     name = Column(String, nullable=False, unique=True, comment="Name of the defect class")
#     color = Column(String, nullable=False, comment="Hex color of the defect class")
#     pixel = Column(Integer, nullable=False, comment="Pixel value used in segmentation mask")
#     comment = Column(Text, nullable=True, comment="Comment about the defect class")


# ==============================
# Annotator (modelo ou humano)
# ==============================
class Annotator(Base):
    __tablename__ = "annotators"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True, comment="Nome do modelo/humano")
    comment = Column(Text, nullable=True, comment="Observações gerais")
    model_metadata = Column(JSONB, nullable=True, comment="Metadados livres (JSON)")
    classes = relationship(
        "AnnotatorDefectClass",
        back_populates="model",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    segmentations = relationship(
        "CoilSegmentAnnotatorSegmentation",
        back_populates="model",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    defects_bbox = relationship(
        "CoilSegmentAnnotatorBBox",
        back_populates="model",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


# ==============================
# AnnotatorDefectClass
# ==============================
class AnnotatorDefectClass(Base):
    __tablename__ = "annotator_defect_classes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    model_id = Column(Integer, ForeignKey("annotators.id", ondelete="CASCADE"), nullable=False, index=True, comment="FK para o anotador (modelo/humano)")
    name = Column(String, nullable=False, comment="Label do anotador (ex.: weld)")
    color_r = Column(Integer, nullable=True, comment="Canal R (0-255) no padrão RGB")
    color_g = Column(Integer, nullable=True, comment="Canal G (0-255) no padrão RGB")
    color_b = Column(Integer, nullable=True, comment="Canal B (0-255) no padrão RGB")
    pixel = Column(Integer, nullable=False, comment="Valor de pixel usado na máscara do anotador")
    comment = Column(Text, nullable=True, comment="Observações")
    model = relationship("Annotator", back_populates="classes", passive_deletes=True)
    defects_bbox = relationship(
        "CoilSegmentAnnotatorBBox",
        back_populates="model_class",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


# ==============================
# CoilSegmentAnnotatorSegmentation
# ==============================
class CoilSegmentAnnotatorSegmentation(Base):
    __tablename__ = "coil_segment_annotator_seg"

    id = Column(Integer, primary_key=True, autoincrement=True)
    coil_segment_id = Column(Integer, ForeignKey("coil_segments.id", ondelete="CASCADE"), nullable=False, index=True, comment="Frame (segment) analisado")
    model_id = Column(Integer, ForeignKey("annotators.id", ondelete="CASCADE"), nullable=False, index=True, comment="Anotador (modelo/humano) que gerou a segmentação")
    mask_url = Column(String, nullable=False, comment="URL/Path da máscara do frame")
    scale = Column(Float, nullable=True, comment="Escala aplicada (0-1)")
    infer_metadata = Column(JSONB, nullable=True, comment="Metadados da inferência (tempo, device, etc.)")
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    segment = relationship(
        "CoilSegment", back_populates="model_segmentations", passive_deletes=True
    )
    model = relationship(
        "Annotator", back_populates="segmentations", passive_deletes=True
    )


# ==============================
# CoilSegmentAnnotatorBBox
# ==============================
class CoilSegmentAnnotatorBBox(Base):
    __tablename__ = "coil_segment_annotator_bbox"

    id = Column(Integer, primary_key=True, autoincrement=True)
    coil_segment_id = Column(Integer, ForeignKey("coil_segments.id", ondelete="CASCADE"), nullable=False, index=True, comment="Frame (segment) analisado")
    model_id = Column(Integer, ForeignKey("annotators.id", ondelete="CASCADE"), nullable=False, index=True, comment="Anotador (modelo/humano) que gerou o bbox")
    model_class_id = Column(Integer, ForeignKey("annotator_defect_classes.id", ondelete="CASCADE"), nullable=False, index=True, comment="Classe (label) do anotador/modelo")
    confidence = Column(Float, nullable=True, comment="Confiança da predição")
    # Canonical format: XYWH with top-left origin in pixels.
    x_px = Column(Float, nullable=True)
    y_px = Column(Float, nullable=True)
    width_px = Column(Float, nullable=False)
    height_px = Column(Float, nullable=False)
    bbox_metadata = Column(JSONB, nullable=True, comment="Extras: tracker_id, tile, etc.")
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    segment = relationship(
        "CoilSegment", back_populates="defects_bbox", passive_deletes=True
    )
    model = relationship(
        "Annotator", back_populates="defects_bbox", passive_deletes=True
    )
    model_class = relationship(
        "AnnotatorDefectClass", back_populates="defects_bbox", passive_deletes=True
    )
