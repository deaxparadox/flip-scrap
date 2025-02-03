from sqlalchemy import Column, Integer, String, Sequence, Float
from sqlalchemy.dialects import postgresql
from db import Base

class URLModel(Base):
    __tablename__ = "urls"
    
    id = Column(Integer, Sequence("url_id_seq"), primary_key=True)
    url = Column(String)
    
class RawModel(Base):
    __tablename__ = "raw"
    id = Column(Integer, Sequence('raw_id_seq'), primary_key=True)
    img = Column(String, nullable=True)
    title = Column(String, nullable=False)
    detail = Column(String, nullable=True)
    cur_price = Column(Float, default=0.)