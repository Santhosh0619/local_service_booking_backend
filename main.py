from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db.base import Base
from app.db.session import engine
from app.features.users.models import User 
from app.features.auth.router import router as auth_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This magically checks the database and creates missing tables on startup
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully!")
    except Exception as e:
        print(f"Warning: Could not connect to database to create tables. {e}")
    yield
    # Shutdown logic goes here if needed

app = FastAPI(title="Local Service Booking API", lifespan=lifespan)

# Wire our new Authentication feature into the main application
app.include_router(auth_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Local Service Booking API"}
