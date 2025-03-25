from sqlalchemy import Column, Integer, String, Float, JSON
from app.database import Base

class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, index=True)
    adresse = Column(String)
    telephone = Column(String)
    email = Column(String, unique=True, index=True)
    site_web = Column(String)
    note_moyenne = Column(Float)
    capacite = Column(Integer)
    type_cuisine = Column(String)
    horaires_ouverture = Column(JSON) 