from sqlalchemy import Column, Float, Integer, JSON, String

try:
    from sqlalchemy.dialects.postgresql import JSONB
except ImportError:
    JSONType = JSON
else:
    JSONType = JSON().with_variant(JSONB, "postgresql")

from .database import Base


class Recipe(Base):
    __tablename__ = "recipes"

    # ============================================================
    # BASIC INFO
    # ============================================================

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    minutes = Column(Integer)


    # ============================================================
    # JSONB FIELDS
    # PostgreSQL optimized JSON storage
    # ============================================================

    tags = Column(JSONType)
    nutrition = Column(JSONType)
    ingredients = Column(JSONType)
    steps = Column(JSONType)


    # ============================================================
    # AI FILTERING / SEARCH FIELDS
    # ============================================================

    calories = Column(Float, index=True)
    protein_pdv = Column(Float)
    carbs_pdv = Column(Float)
