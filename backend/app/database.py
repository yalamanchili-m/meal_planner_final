from pathlib import Path
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Look for .env in the repository root
BASE_DIR = Path(__file__).resolve().parents[2]
env_path = BASE_DIR / ".env"

if not env_path.exists():
    env_path = Path.cwd() / ".env"

if not env_path.exists():
    raise RuntimeError(
        "Could not locate .env file. Expected at backend root or current working directory."
    )

load_dotenv(dotenv_path=env_path)
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./meal_planner.db"
else:
    DATABASE_URL = DATABASE_URL.strip().strip('"').strip("'")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
