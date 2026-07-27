import torch
import requests
import json

class LeaguePredictor:
    """
    Predicts the Premier League table by leveraging a VectorStore of news and stats.
    """
    def __init__(self, embedder, vector_store, ollama_model="llama3"):
        self.embedder = embedder
        self.vector_store = vector_store
        self.ollama_model = ollama_model

        # Baseline prediction (alphabetical or last season's rough order)
        self.base_teams = [
            "Arsenal", "Aston Villa", "Bournemouth", "Brentford", "Brighton & Hove Albion",
            "Chelsea", "Crystal Palace", "Everton", "Fulham", "Ipswich Town",
            "Leicester City", "Liverpool", "Manchester City", "Manchester United", "Newcastle United",
            "Nottingham Forest", "Southampton", "Tottenham Hotspur", "West Ham United", "Wolverhampton Wanderers"
        ]

    def predict_table(self, query):
        """
        Takes a query (e.g., "Predict the table"), embeds it, retrieves top context,
        and dynamically adjusts a baseline table prediction.
        """
        print("\n--- Premier League Prediction Initiated ---")
        
        # 1. Embed the user's query
        query_embedding = self.embedder.embed_texts([query])
        
        # 2. Retrieve top matching news/stats chunks (let's grab the top 5 most relevant pieces of news)
        matches = self.vector_store.search(query_embedding, top_k=5)
        
        # 3. Call local Ollama LLM to generate the prediction based on the retrieved context.
        retrieved_context_texts = []
        for match in matches:
            text = match["metadata"].get("text", "")
            retrieved_context_texts.append(text.strip())
            
        context_str = "\n\n---\n\n".join(retrieved_context_texts)
        
        prompt = (
            f"You are a Premier League football expert. Based on the following retrieved context "
            f"and your own knowledge, answer the user's query.\n\n"
            f"Context:\n{context_str}\n\n"
            f"User Query:\n{query}\n\n"
            f"Prediction:"
        )

        print(f"Calling Ollama (model: {self.ollama_model}) for generation...")
        
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False
                }
            )
            response.raise_for_status()
            
            data = response.json()
            generation = data.get("response", "")
            
            # Formulate report
            report = []
            report.append(f"### Prediction from Ollama ({self.ollama_model})\n")
            report.append(generation)
            
            report.append("\n**Key Factors (Retrieved Context):**")
            if not retrieved_context_texts:
                report.append("> No significant news found.")
            else:
                for ctx in retrieved_context_texts:
                    report.append(f"> \"{ctx}\"")
                    
            return "\n".join(report)
            
        except requests.exceptions.RequestException as e:
            return f"Error communicating with Ollama: {str(e)}\n\nMake sure Ollama is running locally and the model '{self.ollama_model}' is pulled."
