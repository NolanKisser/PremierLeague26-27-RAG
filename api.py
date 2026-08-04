import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from data_loader import DataLoader
from embedder import Embedder
from vector_store import VectorStore
from predictor import LeaguePredictor

# Global variables to store our models
embedder = None
v_store = None
predictor = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global embedder, v_store, predictor
    print("Starting up the Premier League RAG API...")
    
    # 1. Initialize Loader and load local chunks
    loader = DataLoader(chunk_size=300, overlap=50)
    news_chunks = loader.load_directory("data/news")
    stats_chunks = loader.load_directory("data/stats")
    csv_chunks = loader.load_csvs("data/raw_csv")
    all_chunks = news_chunks + stats_chunks + csv_chunks
    print(f"Loaded {len(all_chunks)} document chunks.")

    # 2. Initialize Embedder and vector store if we have data
    embedder = Embedder(model_name="sentence-transformers/all-MiniLM-L6-v2")
    v_store = VectorStore()
    
    if all_chunks:
        print("Generating embeddings for all chunks...")
        texts = [chunk["text"] for chunk in all_chunks]
        embeddings = embedder.embed_texts(texts)
        v_store.add_embeddings(embeddings, all_chunks)
        print("Embeddings indexed.")
    
    # 3. Initialize Predictor
    predictor = LeaguePredictor(embedder, v_store)
    
    yield
    print("Shutting down the API...")

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(lifespan=lifespan, title="Premier League RAG API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles
import os

# Mount the media directory
os.makedirs("media", exist_ok=True)
app.mount("/media", StaticFiles(directory="media"), name="media")

from typing import List, Optional, Any

class PredictRequest(BaseModel):
    query: str

class TeamStanding(BaseModel):
    position: int
    team: str
    explanation: str

class PredictResponse(BaseModel):
    standings: Optional[List[TeamStanding]] = None
    error: Optional[str] = None
    raw: Optional[Any] = None

@app.post("/api/predict", response_model=PredictResponse)
@limiter.limit("5/minute")
async def predict(request: Request, body: PredictRequest):
    if not predictor:
        raise HTTPException(status_code=500, detail="Predictor not initialized")
    
    # Note: predictor.predict_table is synchronous.
    report = predictor.predict_table(body.query)
    
    # Check if report contains an error
    if "error" in report:
        return PredictResponse(error=report["error"], raw=report)
        
    return PredictResponse(standings=report.get("standings", []), raw=report)
