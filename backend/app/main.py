from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, chantiers, avenants, transcribe, company
from .database import engine, Base
from . import models  # Import models to register them with SQLAlchemy
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="ChantierPlus API")

# CORS
origins = [
    "http://localhost:5173", # Vite default port
    "http://localhost:3000",
    "http://192.168.1.120:5173", # Network access
    "http://192.168.1.120:5174", # Alternative port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(company.router)
app.include_router(chantiers.router)
app.include_router(avenants.router)
app.include_router(transcribe.router)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
def read_root():
    return {"message": "Welcome to ChantierPlus API"}
