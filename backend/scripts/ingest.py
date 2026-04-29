import pandas as pd
import ast
import sys
import os
import re
from pathlib import Path

# Add the backend directory to sys.path so we can import from 'app'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import engine, SessionLocal
from app.models import Recipe, Base


def parse_iso_duration(value):
    if pd.isna(value) or value is None:
        return 0
    text = str(value).strip()
    if not text.startswith('P'):
        try:
            return int(float(text))
        except Exception:
            return 0

    hours = 0
    minutes = 0
    match = re.search(r'(\d+)H', text)
    if match:
        hours = int(match.group(1))
    match = re.search(r'(\d+)M', text)
    if match:
        minutes = int(match.group(1))
    return hours * 60 + minutes


def safe_eval_list(value):
    if pd.isna(value) or value is None:
        return []
    text = str(value).strip()
    if not text:
        return []
    if text.startswith('c(') and text.endswith(')'):
        quoted_items = re.findall(r'"((?:[^"\\]|\\.)*)"', text)
        if quoted_items:
            return [item.replace('\\"', '"').strip() for item in quoted_items]
        text = text[2:-1]
    if text.startswith('[') or text.startswith('('):
        try:
            parsed = ast.literal_eval(text)
            return list(parsed) if isinstance(parsed, (list, tuple)) else [parsed]
        except Exception:
            pass
    if '||' in text:
        return [item.strip() for item in text.split('||') if item.strip()]
    if ',' in text:
        return [item.strip() for item in text.split(',') if item.strip()]
    return [text]


def safe_float(value, default=0.0):
    if pd.isna(value) or value is None:
        return default
    try:
        text = str(value).strip()
        if not text:
            return default
        return float(re.sub(r'[^0-9.+-eE]', '', text))
    except Exception:
        return default


def build_tags(row):
    tags = []
    if 'tags' in row.index:
        tags.extend(safe_eval_list(row['tags']))
    if 'RecipeCategory' in row.index and not pd.isna(row['RecipeCategory']):
        tags.extend([item.strip() for item in str(row['RecipeCategory']).split(',') if item.strip()])
    if 'Keywords' in row.index and not pd.isna(row['Keywords']):
        tags.extend([item.strip() for item in str(row['Keywords']).split(',') if item.strip()])
    
    tags = [str(item).lower() for item in tags if item]
    
    # Ensure every recipe has a meal type
    meal_types = ['breakfast', 'lunch', 'dinner']
    if not any(mt in tags for mt in meal_types):
        category = str(row.get('RecipeCategory', '')).lower()
        if any(word in category for word in ['breakfast', 'cereal', 'pancake', 'waffle', 'toast']):
            tags.append('breakfast')
        elif any(word in category for word in ['lunch', 'sandwich', 'soup', 'salad']):
            tags.append('lunch')
        elif any(word in category for word in ['dinner', 'main', 'entree', 'chicken', 'beef', 'pasta']):
            tags.append('dinner')
        else:
            # Random assignment
            import random
            tags.append(random.choice(meal_types))
    
    return tags


def build_ingredients(parts_raw, quantities_raw):
    parts = safe_eval_list(parts_raw)
    quantities = safe_eval_list(quantities_raw)
    
    ingredients = []
    for i, part in enumerate(parts):
        qty = quantities[i] if i < len(quantities) else ""
        ingredients.append(f"{qty} {part}".strip())
    
    return ingredients


def build_steps(value):
    items = safe_eval_list(value)
    if len(items) > 1:
        return [str(item) for item in items]
    if isinstance(value, str) and value.strip():
        if '\n' in value:
            return [step.strip() for step in value.split('\n') if step.strip()]
        return [value.strip()]
    return []

def run_ingestion():
    # 1. Create tables in the 'mealmealmeal' database
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)

    # Clear existing data
    print("Clearing existing recipes...")
    db = SessionLocal()
    db.query(Recipe).delete()
    db.commit()
    db.close()

    # 2. Load the CSV
    csv_path = Path(__file__).resolve().parents[1] / "data" / "recipes.csv"
    print(f"Loading data from {csv_path}...")
    
    # We'll read in chunks to be safe with memory
    chunk_size = 5000 
    reader = pd.read_csv(csv_path, chunksize=chunk_size)

    db = SessionLocal()
    total_loaded = 0

    try:
        for chunk in reader:
            for _, row in chunk.iterrows():
                try:
                    recipe_id = row.get('id') if 'id' in row.index else row.get('RecipeId')
                    recipe_name = row.get('name') if 'name' in row.index else row.get('Name')
                    minutes = parse_iso_duration(
                        row.get('TotalTime') or row.get('CookTime') or row.get('PrepTime') or row.get('minutes')
                    )
                    tags = build_tags(row)
                    if not tags:
                        tags = ['breakfast', 'lunch', 'dinner']

                    if 'nutrition' in row.index and not pd.isna(row['nutrition']):
                        nutrition = safe_eval_list(row['nutrition'])
                    else:
                        nutrition = [
                            safe_float(row.get('Calories')),
                            safe_float(row.get('FatContent')),
                            safe_float(row.get('SugarContent')),
                            safe_float(row.get('SodiumContent')),
                            safe_float(row.get('ProteinContent')),
                            safe_float(row.get('SaturatedFatContent')),
                            safe_float(row.get('CarbohydrateContent')),
                        ]

                    ingredients_raw = row.get('RecipeIngredientParts')
                    quantities_raw = row.get('RecipeIngredientQuantities')
                    steps_raw = row.get('steps') if 'steps' in row.index else row.get('RecipeInstructions')

                    recipe = Recipe(
                        id=int(recipe_id) if recipe_id is not None and not pd.isna(recipe_id) else None,
                        name=str(recipe_name).strip() if recipe_name is not None else None,
                        minutes=int(minutes),
                        tags=tags,
                        nutrition=nutrition,
                        ingredients=build_ingredients(ingredients_raw, quantities_raw),
                        steps=build_steps(steps_raw),
                        calories=safe_float(nutrition[0]),
                        protein_pdv=safe_float(nutrition[4]),
                        carbs_pdv=safe_float(nutrition[6])
                    )
                    db.add(recipe)
                except Exception as e:
                    recipe_key = row.get('id') if 'id' in row.index else row.get('RecipeId')
                    print(f"Skipping recipe {recipe_key}: {e}")
                    continue
            
            db.commit()
            total_loaded += len(chunk)
            print(f"Successfully loaded {total_loaded} recipes...")
            
            # For your MVP, 20,000-30,000 recipes is plenty. 
            # You can remove this break if you want all 230k+.
            if total_loaded >= 30000:
                print("Reached target limit for MVP.")
                break

    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
    finally:
        db.close()
        print("Ingestion process finished.")

if __name__ == "__main__":
    run_ingestion()
