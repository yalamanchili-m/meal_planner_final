from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict, Field

from .database import get_db, engine, Base
from .logic import (
    calculate_bmr,
    generate_monthly_plan,
    generate_grocery_list
)
from .models import Recipe


# ============================================================
# FASTAPI INITIALIZATION
# ============================================================

app = FastAPI(title="MealMealMeal AI Planner")


# ============================================================
# CORS CONFIGURATION
# Allows frontend/backend communication across ports
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # Allow all origins during development
    allow_credentials=True,
    allow_methods=["*"],        # Allow GET, POST, PUT, DELETE etc.
    allow_headers=["*"],        # Allow all headers
)


# ============================================================
# PYDANTIC REQUEST MODELS
# ============================================================

class UserMetrics(BaseModel):
    height: float
    weight: float
    age: int
    gender: str
    goal: str


class PlanData(BaseModel):
    plan: list


class RecipeBase(BaseModel):
    name: str
    minutes: int | None = None
    tags: list[str] = Field(default_factory=list)
    nutrition: list = Field(default_factory=list)
    ingredients: list[str] = Field(default_factory=list)
    steps: list[str] = Field(default_factory=list)
    calories: float | None = None
    protein_pdv: float | None = None
    carbs_pdv: float | None = None


class RecipeCreate(RecipeBase):
    pass


class RecipeOut(RecipeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the MealMealMeal API"
    }


@app.get("/recipes", response_model=list[RecipeOut])
def list_recipes(db: Session = Depends(get_db)):
    return db.query(Recipe).order_by(Recipe.id.desc()).limit(100).all()


@app.post("/recipes", response_model=RecipeOut, status_code=201)
def add_recipe(recipe_data: RecipeCreate, db: Session = Depends(get_db)):
    recipe = Recipe(**recipe_data.model_dump())
    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    return recipe


@app.delete("/recipes/{recipe_id}")
def delete_recipe(recipe_id: int, db: Session = Depends(get_db)):
    recipe = db.get(Recipe, recipe_id)
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found.")

    db.delete(recipe)
    db.commit()
    return {"message": "Recipe deleted successfully."}


# ============================================================
# GENERATE 30 DAY MEAL PLAN
# ============================================================

@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)


@app.post("/generate-plan/")
def create_plan(
    metrics: UserMetrics,
    db: Session = Depends(get_db)
):

    target_cals = calculate_bmr(
        metrics.height,
        metrics.weight,
        metrics.age,
        metrics.gender,
        metrics.goal
    )

    try:
        plan = generate_monthly_plan(
            db,
            target_cals
        )
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc)
        )

    if not plan:
        raise HTTPException(
            status_code=404,
            detail="Could not generate meal plan."
        )

    return {
        "daily_target_calories": round(target_cals, 2),
        "monthly_plan": plan
    }


# ============================================================
# GENERATE GROCERY LIST
# ============================================================

@app.post("/grocery-list/{week}")
def get_groceries(
    week: int,
    data: PlanData
):

    if week < 1 or week > 5:
        raise HTTPException(
            status_code=400,
            detail="Week must be between 1 and 5"
        )

    grocery_list = generate_grocery_list(
        data.plan,
        week
    )

    return grocery_list
