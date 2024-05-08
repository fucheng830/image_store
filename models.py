# 定义数据库模型
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, LargeBinary, TIMESTAMP

Base = declarative_base()

class Image(Base):
    __tablename__ = 'images'
    id = Column(String(255), primary_key=True, nullable=False)
    image_data = Column(LargeBinary, nullable=False)
    format = Column(String(20), nullable=False)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    source_url = Column(String(255))