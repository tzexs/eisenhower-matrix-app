# src/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base # Ensure models are imported before create_all

DATABASE_URL = "sqlite:///./eisenhower_collaborative.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False} # check_same_thread is for SQLite only
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_db_and_tables():
    Base.metadata.create_all(bind=engine)

