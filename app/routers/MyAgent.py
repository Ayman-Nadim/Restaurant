from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
import re

# Configuration de l'API de Gemini avec la clé API
genai.configure(api_key="AIzaSyD7gKJclevoJuIpexqsqAY9RDtJSemdoaE")

# Configuration du modèle Gemini 1.5 Pro
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Initialisation du modèle
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
)

# Initialisation du routeur FastAPI
router = APIRouter()

# Modèle pour valider le format du prompt
class PromptRequest(BaseModel):
    prompt: str

# Fonction pour analyser le prompt et extraire les informations clés
def extract_information(prompt: str):
    # Demander à l'IA d'extraire des informations sur la localisation et le type de restaurant
    chat_session = model.start_chat(history=[])
    response = chat_session.send_message(f"Extrait des informations telles que la localisation et le type de restaurant : {prompt}")
    extracted_info = response.text
    
    # Exemple de logique pour extraire des informations spécifiques à partir de la réponse de l'IA
    location = re.search(r"(à|vers|près de)\s([a-zA-Zéèà\- ]+)", extracted_info)  # Recherche simple de localisation
    restaurant_type = re.search(r"(restaurant\s)([a-zA-Z\-]+)", extracted_info)  # Recherche du type de restaurant
    
    # Si l'une des informations est manquante, renvoyer un message approprié
    if not location:
        location = None
    if not restaurant_type:
        restaurant_type = None
        
    # Retourner les informations extraites
    return {
        "location": location.group(2) if location else None,
        "restaurant_type": restaurant_type.group(2) if restaurant_type else None,
    }

# Route FastAPI pour générer du contenu
@router.post("/get-information/") 
async def generate_text(request: PromptRequest):
    prompt = request.prompt
    
    try:
        # Extraire les informations nécessaires du prompt
        extracted_info = extract_information(prompt)
        
        # Vérifier si nous avons les informations nécessaires pour la recherche
        if not extracted_info["location"] and not extracted_info["restaurant_type"]:
            return {"message": "Veuillez spécifier à la fois la localisation et le type de restaurant."}
        elif not extracted_info["location"]:
            return {"message": "Veuillez spécifier la localisation du restaurant."}
        elif not extracted_info["restaurant_type"]:
            return {"message": "Veuillez spécifier le type de restaurant."}
        
        # Recherche dans la base de données (cette partie doit être adaptée à ta base de données)
        # Exemple fictif : trouver un restaurant correspondant à la localisation et au type
        restaurants = find_restaurants(extracted_info["location"], extracted_info["restaurant_type"])
        
        if not restaurants:
            return {"message": "Aucun restaurant correspondant à votre demande n'a été trouvé."}
        
        # Retourner les restaurants sous forme d'objets, en suivant la structure Google Maps
        return {
            "results": restaurants
        }

    except Exception as e:
        # En cas d'erreur, renvoyer un message d'erreur
        raise HTTPException(status_code=500, detail=str(e))


# Fonction fictive pour rechercher des restaurants dans la base de données
def find_restaurants(location: str, restaurant_type: str):
    # Exemple de logique de recherche dans la base de données (à remplacer par la vraie logique de base de données)
    all_restaurants = [
        {
            "name": "Le Bistro",
            "vicinity": "Casablanca",
            "types": ["restaurant", "français"],
            "rating": 4.5,
            "price_level": 2,
            "opening_hours": {"open_now": True},
            "user_ratings_total": 120
        },
        {
            "name": "Pasta Mania",
            "vicinity": "Rabat",
            "types": ["restaurant", "italien"],
            "rating": 4.0,
            "price_level": 1,
            "opening_hours": {"open_now": False},
            "user_ratings_total": 50
        },
        {
            "name": "Sushi Bar",
            "vicinity": "Rabat",
            "types": ["restaurant", "japonais"],
            "rating": 4.7,
            "price_level": 3,
            "opening_hours": {"open_now": True},
            "user_ratings_total": 80
        },
        {
            "name": "La Table du Marché",
            "vicinity": "Casablanca",
            "types": ["restaurant", "français"],
            "rating": 4.2,
            "price_level": 2,
            "opening_hours": {"open_now": True},
            "user_ratings_total": 150
        }
    ]
    
    # Filtrer les restaurants selon la localisation et le type
    filtered_restaurants = [
        restaurant for restaurant in all_restaurants
        if (location.lower() in restaurant["vicinity"].lower() and restaurant_type.lower() in [type.lower() for type in restaurant["types"]])
    ]
    
    return filtered_restaurants