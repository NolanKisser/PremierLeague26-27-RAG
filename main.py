import os
import shutil
from data_loader import DataLoader
from embedder import Embedder
from vector_store import VectorStore
from predictor import LeaguePredictor
import fetch_data

def main():
    print("Initializing Premier League RAG Predictor (Live Data Edition)...")
    
    # 1. Fetch live real-world data
    print("Pulling latest data from GitHub repositories...")
    fetch_data.fetch_all_data()

    # 2. Load and Chunk Documents (CSV and Text)
    loader = DataLoader(chunk_size=300, overlap=50)
    
    # We still support news/stats text files if they exist
    news_chunks = loader.load_directory("data/news")
    stats_chunks = loader.load_directory("data/stats")
    
    # Load the new CSV data
    csv_chunks = loader.load_csvs("data/raw_csv")
    
    all_chunks = news_chunks + stats_chunks + csv_chunks
    
    print(f"Loaded {len(all_chunks)} document chunks from real data.")

    # 3. Initialize PyTorch Embedder
    # Uses sentence-transformers, requires downloading ~90MB weights if not cached
    embedder = Embedder(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    # 4. Generate Embeddings for all chunks
    print("Generating embeddings for football documents (this may take a moment)...")
    texts = [chunk["text"] for chunk in all_chunks]
    embeddings = embedder.embed_texts(texts)
    
    # 5. Populate PyTorch Vector Store
    v_store = VectorStore()
    v_store.add_embeddings(embeddings, all_chunks)
    print("Documents successfully indexed into PyTorch Vector Store.")

    # 6. Initialize Predictor
    predictor = LeaguePredictor(embedder, v_store)

    # 7. Predict the table
    query = "Predict the final 20-team Premier League table considering the latest FPL stats, player xG, and team Elo ratings."
    
    print(f"\nUser Query: '{query}'")
    
    report = predictor.predict_table(query)
    print(report)

if __name__ == "__main__":
    main()
