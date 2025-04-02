from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.routers import RestaurantRouters, auth, Recommendation  # Import du nouveau routeur
from app.database import Base, engine
from app.routers.MyAgent import router  

app = FastAPI()

# Création des tables
Base.metadata.create_all(bind=engine)

# Configuration de CORS pour permettre l'accès à tout le monde
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permet à toutes les origines d'accéder à l'API
    allow_credentials=True,
    allow_methods=["*"],  # Permet toutes les méthodes HTTP (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Permet tous les en-têtes
)

# Routes
app.include_router(auth.router)
app.include_router(RestaurantRouters.router)
app.include_router(router)
app.include_router(Recommendation.router)  # Ajout du routeur de recommandations
