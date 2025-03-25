from fastapi import FastAPI
from app.database import engine
from app.models.RestaurantModel import Base
from app.routers import RestaurantRouters

app = FastAPI()

# Création automatique des tables dans la BDD
Base.metadata.create_all(bind=engine)

# Inclusion des routes
app.include_router(RestaurantRouters.router)
