from fastapi import FastAPI
from app.routers import RestaurantRouters, auth
from app.database import Base, engine

app = FastAPI()

# Création des tables
Base.metadata.create_all(bind=engine)

# Routes
app.include_router(auth.router)
app.include_router(RestaurantRouters.router)