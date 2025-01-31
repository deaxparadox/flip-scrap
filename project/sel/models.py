from sqlalchemy import Column, Integer, String, Sequence
from db import Base

class URLModel(Base):
    __tablename__ = "users"
    
    id = Column(Integer, Sequence("url_id_seq"), primary_key=True)
    url = Column(String)