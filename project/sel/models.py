from sqlalchemy import Column, Integer, String, Sequence
from db import Base

class URLModel(Base):
    __tablename__ = "urls"
    
    id = Column(Integer, Sequence("url_id_seq"), primary_key=True)
    url = Column(String)
    
class RawModel(Base):
    __tablename__ = "raw"
    id = Column(Integer, Sequence('raw_id_seq'), primary_key=True)
    data = Column(String)