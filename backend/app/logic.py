import random
from .models import Recipe
import re
from collections import defaultdict


# ============================================================
# INGREDIENT SHELF LIFE CLASSIFICATION
# ============================================================

SHELF_LIFE_MAP = {
    "milk": 1,
    "chicken": 1,
    "fish": 1,
    "spinach": 1,
    "cream": 1,

    "bread": 2,
    "cheese": 2,
    "eggs": 2,
    "yogurt": 2,

    "rice": 3,
    "pasta": 3,
    "flour": 3,
    "oil": 3,
    "honey": 3
}


def get_ingredient_tier(ingredient_name):
    name = ingredient_name.lower()
    for key, tier in SHELF_LIFE_MAP.items():
        if key in name:
            return tier
    return 3


# ============================================================
# INGREDIENT PARSING
# ============================================================

def parse_quantity(qty_str):
    parts = qty_str.split()
    total = 0.0

    for part in parts:
        if '/' in part:
            try:
                num, den = part.split('/')
                total += float(num) / float(den)
            except:
                pass
        else:
            try:
                total += float(part)
            except:
                pass

    return total if total > 0 else 1.0


def is_unit(word):
    units = {
        "cup", "cups", "tbsp", "tsp", "tablespoon", "teaspoons", "teaspoon", "tablespoons",
        "lb", "lbs", "oz", "ounce", "ounces", "pound", "pounds",
        "g", "kg", "gram", "grams", "kilogram", "kilograms",
        "ml", "l", "liter", "liters", "milliliter", "milliliters",
        "can", "cans", "package", "packages", "bottle", "bottles",
        "clove", "cloves", "slice", "slices", "piece", "pieces"
    }
    return word.lower() in units


# ============================================================
# 🔥 AGGRESSIVE CLEANING
# ============================================================

def clean_name_aggressive(name):
    if not name:
        return ""

    name = name.lower()

    # Remove R-style junk
    name = re.sub(r'^c\(', '', name)
    name = re.sub(r'[\"\)]', '', name)

    # Remove "na"
    name = re.sub(r'^na\s+', '', name)
    if name == 'na':
        return ""

    # Remove trailing numbers
    name = re.sub(r'\d+$', '', name)

    # Cleanup
    name = name.strip("- ").strip()

    return name


# ============================================================
# 🔥 IMPROVED PARSER
# ============================================================

def parse_ingredient(ing_str):
    if not ing_str:
        return 1.0, "", ""

    ing_str = ing_str.replace('c(', '').replace('"', '').replace(')', '').strip()

    match = re.match(r'^([\d\s\/\-\.]+)?(.*)', ing_str)
    qty_part = match.group(1) if match.group(1) else "1"
    rest = match.group(2).strip()

    qty = parse_quantity(qty_part)

    tokens = rest.split()

    if tokens and is_unit(tokens[0]):
        unit = tokens[0]
        name = " ".join(tokens[1:])
    else:
        unit = ""
        name = rest

    clean_name = clean_name_aggressive(name)

    return qty, unit, clean_name


# ============================================================
# CALORIE / BMR CALCULATOR
# ============================================================

def calculate_bmr(height, weight, age, gender, goal):
    if gender.lower() == "male":
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161

    tdee = bmr * 1.375

    if goal == "weight_loss":
        return tdee - 500
    if goal == "weight_gain":
        return tdee + 500

    return tdee


# ============================================================
# MONTHLY PLAN GENERATION
# ============================================================

def generate_monthly_plan(db, target_cals):

    targets = {
        "breakfast": target_cals * 0.25,
        "lunch": target_cals * 0.35,
        "dinner": target_cals * 0.40
    }

    pools = {}

    for meal_type in ["breakfast", "lunch", "dinner"]:
        candidates = db.query(Recipe).limit(3000).all()
        results = [
            recipe for recipe in candidates
            if meal_type in {str(tag).lower() for tag in (recipe.tags or [])}
        ][:500]

        if not results:
            print(f"⚠️ Warning: No recipes found for {meal_type}. Using fallback.")
            results = db.query(Recipe).limit(100).all()

        if not results:
            raise Exception("No recipes available in database at all.")

        pools[meal_type] = results

    full_plan = []
    used_recipes = {"breakfast": set(), "lunch": set(), "dinner": set()}

    for day in range(1, 31):
        day_meals = {}
        day_used = set()

        for meal_type, target in targets.items():
            pool = pools[meal_type]

            suitable = [
                r for r in pool
                if r.calories is not None
                and abs(r.calories - target) < 300
                and r.id not in used_recipes[meal_type]
                and r.id not in day_used
            ]

            if not suitable:
                suitable = [r for r in pool if r.id not in used_recipes[meal_type] and r.id not in day_used]

            if not suitable:
                suitable = [r for r in pool if r.id not in day_used]

            if not suitable:
                suitable = pool

            chosen = random.choice(suitable)
            used_recipes[meal_type].add(chosen.id)
            day_used.add(chosen.id)

            day_meals[meal_type] = {
                "id": chosen.id,
                "name": chosen.name,
                "calories": round(chosen.calories or 0, 1),
                "ingredients": chosen.ingredients or [],
                "steps": chosen.steps or [],
                "minutes": chosen.minutes
            }

        full_plan.append({
            "day": day,
            "meals": day_meals
        })

    return full_plan


# ============================================================
# 🛒 FINAL GROCERY LIST GENERATION (POLISHED)
# ============================================================

def generate_grocery_list(plan_list, week_number):

    start_day = (week_number - 1) * 7 + 1
    end_day = week_number * 7
    if week_number == 5:
        end_day = 30

    week_days = [d for d in plan_list if start_day <= d['day'] <= end_day]

    aggregated = defaultdict(float)

    for day in week_days:
        for meal in day['meals'].values():
            if not meal:
                continue

            for ing_str in meal.get('ingredients', []):
                qty, unit, name = parse_ingredient(ing_str)

                if not name:
                    continue

                key = (name.lower(), unit.lower().rstrip('s'))
                aggregated[key] += qty

    tiers = {
        "tier_1": [],
        "tier_2": [],
        "tier_3": []
    }

    # ✅ FINAL CLEAN OUTPUT LOOP (YOUR REQUEST)
    for (name, unit), total_qty in aggregated.items():
        tier_num = get_ingredient_tier(name)
        tier_key = f"tier_{tier_num}"

        # Format quantity
        pretty_qty = int(total_qty) if total_qty.is_integer() else round(total_qty, 2)

        if pretty_qty <= 0:
            pretty_qty = 1

        display_name = name.title()
        display_unit = unit if unit else ""

        tiers[tier_key].append({
            "item": display_name,
            "quantity": pretty_qty,
            "unit": display_unit,
            "amount": f"{pretty_qty} {display_unit}".strip(),
            "formatted_string": f"{pretty_qty} {display_unit} {display_name}".replace("  ", " ").strip()
        })

    # Sort
    for key in tiers:
        tiers[key] = sorted(tiers[key], key=lambda x: x['item'])

    return tiers
