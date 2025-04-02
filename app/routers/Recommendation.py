from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import requests
import google.generativeai as genai
import re
import os
from dotenv import load_dotenv
from typing import Dict, List, Optional
from functools import lru_cache
import logging

# Configuration du logging pour suivre les erreurs et informations
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Chargement des variables d'environnement pour la sécurité des clés API
load_dotenv()

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GOOGLE_MAPS_API_KEY or not GEMINI_API_KEY:
    logger.error("Les clés API ne sont pas définies dans .env!")
    raise ValueError("Les clés API ne sont pas définies dans .env!")

# Configuration de l'IA Gemini avec la clé API
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(model_name="gemini-1.5-pro")

# Initialisation du routeur FastAPI
router = APIRouter()

# Modèles de données avec Pydantic
class PromptRequest(BaseModel):
    prompt: str

class PlaceResult(BaseModel):
    name: str
    address: str
    rating: Optional[float]
    types: List[str]
    location: Dict[str, float]
    photos: List[str]
    phone: Optional[str]
    website: Optional[str]
    reviews: Optional[List[Dict]]
    opening_hours: Optional[Dict]
    price_level: Optional[int]
    map_url: Optional[str]

class RecommendationResponse(BaseModel):
    results: List[PlaceResult]
    location: str
    activity: str

# Fonction avec cache pour les recherches fréquentes
@lru_cache(maxsize=100)
def cached_find_places(query: str) -> List[Dict]:
    """Effectue une recherche optimisée des lieux via l'API Google Places."""
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": query,
        "key": GOOGLE_MAPS_API_KEY,
        "language": "fr"  # Changer la langue en français pour une meilleure localisation
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "OK":
            logger.warning(f"Statut non OK de l'API : {data.get('status')}")
            return []

        return data.get("results", [])
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur lors de la requête API : {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service de localisation temporairement indisponible"
        )

def extract_information(prompt: str) -> Dict[str, str]:
    """
    Extrait la localisation et l'activité à partir du prompt de l'utilisateur à l'aide de l'IA Gemini.
    """
    try:
        structured_prompt = (
            f"Analysez ce texte et identifiez :\n"
            f"1. La localisation (ville, quartier, pays)\n"
            f"2. Le type d'activité (restaurant, café, etc.)\n"
            f"Format attendu : 'LOCALISATION: ... | ACTIVITE: ...'\n\n"
            f"Texte : {prompt}"
        )

        response = model.generate_content(structured_prompt)

        if not response.text:
            raise ValueError("Réponse vide de Gemini AI")

        location, activity = "non spécifiée", "activité générique"

        if "|" in response.text:
            parts = response.text.split("|")
            for part in parts:
                if "LOCALISATION:" in part:
                    location = part.split("LOCALISATION:")[1].strip()
                elif "ACTIVITE:" in part:
                    activity = part.split("ACTIVITE:")[1].strip()
        else:
            location_match = re.search(r"(?:à|près|dans)\s?([a-zA-Zéèà\-' ]+|[أ-ي ]+)", response.text, re.IGNORECASE)
            activity_match = re.search(r"(restaurant|café|parc|cinéma|musée|plage|bar|italien|pizzeria|fast food|sushi|centre commercial|boutique|hôtel)", response.text, re.IGNORECASE)

            location = location_match.group(1).strip() if location_match else location
            activity = activity_match.group(1).strip() if activity_match else activity

        return {"location": location, "activity": activity}

    except Exception as e:
        logger.error(f"Erreur lors de l'extraction des informations : {str(e)}")
        return {"location": "non spécifiée", "activity": "activité générique"}

def find_places(location: str, activity: str) -> List[Dict]:
    """
    Recherche de lieux via l'API Google Places avec gestion des échecs.
    """
    queries = [
        f"{activity} {location}",
        f"{activity} près de {location}",
        activity,
        location
    ]

    for query in queries:
        places = cached_find_places(query)
        if places:
            return places

    return []

def get_place_details(place_id: str) -> Dict:
    """Récupère les détails d'un lieu à partir de son ID."""
    if not place_id:
        return {}

    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "key": GOOGLE_MAPS_API_KEY,
        "fields": "name,formatted_address,rating,types,geometry,photos,formatted_phone_number,website,reviews,opening_hours,price_level,url"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "OK":
            return {}

        return data.get("result", {})
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur lors de la récupération des détails pour l'ID {place_id}: {str(e)}")
        return {}

def process_places_results(places: List[Dict]) -> List[PlaceResult]:
    """Transforme les résultats en objets structurés et les trie par note décroissante."""
    processed_results = []
    for place in places:
        place_id = place.get("place_id", "")
        place_details = get_place_details(place_id)

        if not place_details:
            continue

        photos = []
        if place_details.get("photos"):
            for photo in place_details["photos"]:
                photo_reference = photo.get("photo_reference")
                if photo_reference:
                    photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_reference}&key={GOOGLE_MAPS_API_KEY}"
                    photos.append(photo_url)

        processed_result = {
            "name": place_details.get("name", "Nom non disponible"),
            "address": place_details.get("formatted_address", "Adresse non disponible"),
            "rating": place_details.get("rating", 0),
            "types": place_details.get("types", []),
            "location": place_details.get("geometry", {}).get("location", {}),
            "photos": photos,
            "phone": place_details.get("formatted_phone_number"),
            "website": place_details.get("website"),
            "reviews": place_details.get("reviews"),
            "opening_hours": place_details.get("opening_hours"),
            "price_level": place_details.get("price_level"),
            "map_url": place_details.get("url")
        }
        processed_results.append(PlaceResult(**processed_result))

    return sorted(processed_results, key=lambda x: x.rating or 0, reverse=True)

# Endpoint pour obtenir des recommandations basées sur un prompt naturel
@router.post("/get-recommendations/", response_model=RecommendationResponse)
async def get_recommendations(request: PromptRequest):
    """Retourne des recommandations de lieux basées sur un prompt."""
    try:
        logger.info(f"Traitement du prompt: {request.prompt}")

        extracted_info = extract_information(request.prompt)
        location, activity = extracted_info["location"], extracted_info["activity"]

        if "non spécifiée" in location or "activité générique" in activity:
            logger.warning("Information insuffisante dans le prompt")
            return RecommendationResponse(results=[], location=location, activity=activity)

        places = find_places(location, activity)

        if not places:
            logger.info("Aucun lieu trouvé pour cette recherche")
            return RecommendationResponse(results=[], location=location, activity=activity)

        processed_results = process_places_results(places[:10])

        return RecommendationResponse(results=processed_results, location=location, activity=activity)

    except Exception as e:
        logger.error(f"Erreur lors du traitement: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Une erreur interne est survenue"
        )
