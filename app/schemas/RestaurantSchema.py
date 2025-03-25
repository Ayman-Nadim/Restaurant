from pydantic import BaseModel
from typing import Optional, Dict

class RestaurantBase(BaseModel):
    nom: str
    adresse: str
    telephone: str
    email: str
    site_web: Optional[str] = None
    note_moyenne: float
    capacite: int
    type_cuisine: str
    horaires_ouverture: Dict[str, str]

class RestaurantCreate(RestaurantBase):
    pass

class RestaurantResponse(RestaurantBase):
    id: int

    class Config:
        from_attributes = True
