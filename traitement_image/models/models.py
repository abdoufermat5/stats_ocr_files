from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, JSON

Base = declarative_base()


class ImageResult(Base):
    __tablename__ = "image_results"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    ocr_data = Column(JSON)
