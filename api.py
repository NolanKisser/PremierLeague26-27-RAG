import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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

app = FastAPI(lifespan=lifespan, title="Premier League RAG API")

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PredictRequest(BaseModel):
    query: str

class PredictResponse(BaseModel):
    report: str

@app.post("/api/predict", response_model=PredictResponse)
async def predict(request: PredictRequest):
    if not predictor:
        raise HTTPException(status_code=500, detail="Predictor not initialized")
    
    # Note: predictor.predict_table is synchronous.
    # In a fully async app, we might run this in a threadpool.
    # For this prototype, blocking the event loop is acceptable.
    report = predictor.predict_table(request.query)
    
    return PredictResponse(report=report)
