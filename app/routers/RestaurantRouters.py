from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.schemas import RestaurantSchema
from app.models import RestaurantModel
from app.database import get_db
from app.core.security import verify_token
from app.dependencies import get_current_user

router = APIRouter(prefix="/restaurants", tags=["restaurants"])

# Sécurisation avec authentification sur chaque route
@router.post("/", response_model=RestaurantSchema.RestaurantResponse, status_code=status.HTTP_201_CREATED)
def create_restaurant(
    restaurant: RestaurantSchema.RestaurantCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)  # Vérifie l'utilisateur connecté
):
    try:
        db_restaurant = RestaurantModel.Restaurant(**restaurant.model_dump())
        db.add(db_restaurant)
        db.commit()
        db.refresh(db_restaurant)
        return db_restaurant
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/", response_model=list[RestaurantSchema.RestaurantResponse])
def get_restaurants(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:
        restaurants = db.query(RestaurantModel.Restaurant).all()
        if not restaurants:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No restaurants found")
        return restaurants
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/{restaurant_id}", response_model=RestaurantSchema.RestaurantResponse)
def get_restaurant(restaurant_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:
        restaurant = db.query(RestaurantModel.Restaurant).filter(RestaurantModel.Restaurant.id == restaurant_id).first()
        if not restaurant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")
        return restaurant
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.put("/{restaurant_id}", response_model=RestaurantSchema.RestaurantResponse)
def update_restaurant(
    restaurant_id: int,
    updated_data: RestaurantSchema.RestaurantCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)  # Vérifie l'utilisateur connecté
):
    try:
        restaurant = db.query(RestaurantModel.Restaurant).filter(RestaurantModel.Restaurant.id == restaurant_id).first()
        if not restaurant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")

        for key, value in updated_data.model_dump().items():
            setattr(restaurant, key, value)

        db.commit()
        db.refresh(restaurant)
        return restaurant
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.delete("/{restaurant_id}", response_model=dict)
def delete_restaurant(
    restaurant_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)  # Vérifie l'utilisateur connecté
):
    try:
        restaurant = db.query(RestaurantModel.Restaurant).filter(RestaurantModel.Restaurant.id == restaurant_id).first()
        if not restaurant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")

        db.delete(restaurant)
        db.commit()
        return {"message": "Restaurant deleted successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
