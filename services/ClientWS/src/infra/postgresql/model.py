from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, func, Boolean, JSON, ARRAY, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from infra.postgresql.database import Base


class UserType(Base):
    __tablename__ = "user_types"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True, comment="Type of user (e.g., admin, superuser, user)")
    description = Column(String, nullable=True, comment="Description of the user type")

    # Relacionamento com a tabela de usuários
    users = relationship("User", back_populates="user_type")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False, unique=True, comment="Username for login")
    hashed_password = Column(String, nullable=False, comment="Hashed password")
    is_active = Column(Boolean, default=True, comment="Indicates if the user account is active")
    user_type_id = Column(Integer, ForeignKey("user_types.id"), nullable=False, comment="Foreign key to user type table")
    
    user_type = relationship("UserType", back_populates="users")



# Nova tabela Cam
class Cam(Base):
    __tablename__ = "cams"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True, comment="Name of the camera")
    comment = Column(Text, nullable=True, comment="Additional information about the camera")

    # Relacionamento com CoilSegment
    segments = relationship("CoilSegment", back_populates="cam")



class Coils(Base):
    __tablename__ = "coils"  # Nome da tabela "coils"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, comment="Name of the coil")
    start_time = Column(DateTime, nullable=False, server_default=func.now(), comment="Start time of the coil measurement")
    end_time = Column(DateTime, nullable=True, comment="End time of the coil measurement")
    
    segments = relationship("CoilSegment", back_populates="coil", cascade="all, delete-orphan")




class CoilSegment(Base):
    __tablename__ = "coil_segments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    data = Column(DateTime, server_default=func.now(), nullable=False, comment="Date and time when the segment was taken")
    coil_id = Column(Integer, ForeignKey("coils.id"), nullable=False, comment="Foreign key to the coils table")
    cam_id = Column(Integer, ForeignKey("cams.id"), nullable=False, index=True, comment="Foreign key to the cams table")
    line_position_start = Column(Float, nullable=False, index=True, comment="Start position of the segment along the coil, representing the distance in meters (e.g., 0m, 1m, etc.)")
    line_position_end = Column(Float, nullable=False, comment="End position of the segment along the coil, representing the distance in meters (e.g., 0m, 1m, etc.)")
    
    original_image_path = Column(String, nullable=True, comment="Path of the original image")
    defect_image_path = Column(String, nullable=True, comment="Path of the segmentation defect image")

    distance_per_px_axis_x = Column(Float, nullable=True, comment="Meters or millimeters per pixel in the X direction")
    distance_per_px_axis_y = Column(Float, nullable=True, comment="Meters or millimeters per pixel in the Y direction")
    
    width_image_px = Column(Integer, nullable=True, comment="width of the original image")
    height_image_px = Column(Integer, nullable=True, comment="height of the original image")
    
    medium_image_path = Column(String, nullable=True, comment="Path of the medium-sized image")
    medium_image_scale = Column(Float, nullable=True, comment="Scaling factor applied to the medium-sized image between (0-1)")
    
    mini_image_path = Column(String, nullable=True, comment="Path of the mini-sized image")
    mini_image_scale = Column(Float, nullable=True, comment="Scaling factor applied to the mini-sized image between (0-1)")

    border_positions_left_px = Column(
        JSONB,
        nullable=True,
        comment="""JSONB representing points at the left border of the image in px.
        Example: [{"x": 100.0, "y": 200.0}, {"x": 110.0, "y": 210.0}]
        """
    )
    
    border_positions_right_px = Column(
        JSONB,
        nullable=True,
        comment="""JSONB representing points at the right border of the image.
        Example: [{"x": 500.0, "y": 600.0}, {"x": 510.0, "y": 610.0}]
        """
    )

    segment_metadata = Column(JSONB, nullable=True, comment="JSON field to store additional metadata related to the segment")

    image_metadata = Column(JSONB, nullable=True, comment="JSON field to store additional metadata about the image, update, move, saved...")

    coil = relationship("Coils", back_populates="segments")
    cam = relationship("Cam", back_populates="segments")
    defects = relationship("CoilSegmentDefect", back_populates="segment", cascade="all, delete-orphan")


class CoilSegmentDefect(Base):
    __tablename__ = "coil_segment_defects"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    coil_segment_id = Column(Integer, ForeignKey("coil_segments.id"), nullable=False, comment="Foreign key to the coil segments table")
    defect_class_id = Column(Integer, ForeignKey("defect_class.id"), nullable=False, comment="Foreign key to the defect class table")

    center_x_px = Column(Float, nullable=False, comment="X coordinate of the bounding box center in pixels")
    center_y_px = Column(Float, nullable=False, comment="Y coordinate of the bounding box center in pixels")
    width_px = Column(Float, nullable=False, comment="Width of the bounding box in pixels")
    height_px = Column(Float, nullable=False, comment="Height of the bounding box in pixels")

    defect_image_path = Column(String, nullable=True, comment="Path of the defect image")

    segment = relationship("CoilSegment", back_populates="defects")
    defect_class = relationship("DefectClass", back_populates="defects")


class DefectClass(Base):
    __tablename__ = "defect_class"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True, comment="Name of the defect class")  # Nome do defeito
    color = Column(String, nullable=False, comment="Hexadecimal color code for the defect class")  # Cor associada ao defeito
    comment = Column(Text, nullable=True, comment="Comment about the defect class")  # Comentário sobre o defeito
    

    defects = relationship("CoilSegmentDefect", back_populates="defect_class")


class DefectClassSegmentation(Base):
    __tablename__ = "defect_class_segmentation"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True, comment="Name of the defect class")  # Nome do defeito
    color = Column(String, nullable=False, comment="Hexadecimal color code for the defect")  # Cor associada ao defeito
    pixel = Column(Integer, nullable=False, comment="Pixel representation of the defect image for frontend usage")  #
    comment = Column(Text, nullable=True, comment="Comment about the defect class")  # Comentário sobre o defeito
    






