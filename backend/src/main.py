# src/main.py

from fastapi import FastAPI
from .database import create_db_and_tables #, engine # engine might not be needed here directly
from .routes import router as api_router
from fastapi.middleware.cors import CORSMiddleware

# Create database tables if they don't exist
# This is suitable for development. For production, use migrations (e.g., Alembic).
create_db_and_tables()

app = FastAPI(
    title="Eisenhower Collaborative Matrix API",
    description="API for a collaborative Eisenhower Matrix application.",
    version="0.1.0"
)

# CORS (Cross-Origin Resource Sharing) middleware
origins = [
    "http://localhost",         # For local development if frontend is served by npm/yarn directly
    "http://localhost:3000",    # Default React development server port
    "http://localhost:5173",    # Default Vite React development server port
    "https://pjsiqpdp.manus.space", # Deployed frontend URL
    "https://8000-io2m3it5cy93w7r303rkl-092dd6d3.manusvm.computer" # Exposed backend URL itself, in case of direct access or complex scenarios
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows specific origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Collaborative Eisenhower Matrix API"}

# To run the app (for development):
# uvicorn eisenhower_collaborative_app.src.main:app --reload --port 8000

