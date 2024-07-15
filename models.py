# 定义数据库模型
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, LargeBinary, TIMESTAMP
from sqlalchemy import  Column, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
from sqlalchemy.sql import func
import uuid



Base = declarative_base()

class Image(Base):
    __tablename__ = 'images'
    id = Column(String(255), primary_key=True, nullable=False)
    image_data = Column(LargeBinary, nullable=False)
    format = Column(String(20), nullable=False)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    source_url = Column(String(255))

class ImageVectorIndex(Base):
    __tablename__ = 'image_vector_indices'
    __table_args__ = {'schema': 'img_vector'}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    image_id = Column(UUID(as_uuid=True), ForeignKey('img_vector.images.id'), nullable=False)
    name = Column(String(255))
    embedding =  Column(Vector(None))
    source_url = Column(String(255))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now())
