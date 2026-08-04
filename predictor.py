import torch
import requests
import json
from duckduckgo_search import DDGS

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
            "Arsenal", "Aston Villa", "Bournemouth", "Brentford", "Brighton and Hove Albion",
            "Chelsea", "Coventry City", "Crystal Palace", "Everton", "Fulham",
            "Hull City", "Ipswich Town", "Leeds United", "Liverpool", "Manchester City",
            "Manchester United", "Newcastle United", "Nottingham Forest", "Sunderland", "Tottenham Hotspur"
        ]

    def predict_table(self, query):
        """
        Takes a query (e.g., "Predict the table"), searches the web for latest context,
        and dynamically adjusts a baseline table prediction.
        """
        print("\n--- Premier League Prediction Initiated ---")
        
        # 1. Perform live web search instead of vector store search
        print("Performing live web search for context...")
        search_query = query + " Premier League latest news stats"
        retrieved_context_texts = []
        
        try:
            with DDGS() as ddgs:
                results = [r for r in ddgs.text(search_query, max_results=5)]
                for result in results:
                    title = result.get("title", "")
                    body = result.get("body", "")
                    retrieved_context_texts.append(f"Title: {title}\nSummary: {body}")
        except Exception as e:
            print(f"Web search failed: {e}")
            retrieved_context_texts.append("No recent news available due to search error.")
            
        context_str = "\n\n---\n\n".join(retrieved_context_texts)
        
        prompt = (
            f"You are a Premier League football expert. Based on the following retrieved context "
            f"and your own knowledge, answer the user's query.\n\n"
            f"Context:\n{context_str}\n\n"
            f"User Query:\n{query}\n\n"
            f"You MUST output your prediction in strict JSON format matching exactly this schema:\n"
            f"{{\n"
            f"  \"standings\": [\n"
            f"    {{\"position\": 1, \"team\": \"Arsenal\", \"explanation\": \"Short explanation of why they are 1st...\"}},\n"
            f"    {{\"position\": 2, \"team\": \"Manchester City\", \"explanation\": \"Short explanation of why they are 2nd...\"}},\n"
            f"    // ... Provide exactly 20 teams in this exact format. DO NOT use '...', do not skip any teams. You MUST list all 20 teams.\n"
            f"  ]\n"
            f"}}\n"
            f"Ensure every single team has the actual team name in the 'team' field and a valid reason in the 'explanation' field.\n"
            f"You MUST use exactly these 20 teams (and no others): Arsenal, Aston Villa, Bournemouth, Brentford, Brighton and Hove Albion, Chelsea, Coventry City, Crystal Palace, Everton, Fulham, Hull City, Ipswich Town, Leeds United, Liverpool, Manchester City, Manchester United, Newcastle United, Nottingham Forest, Sunderland, Tottenham Hotspur.\n"
            f"Output ONLY the raw JSON object and absolutely nothing else."
        )

        print(f"Calling Ollama (model: {self.ollama_model}) for generation in JSON mode...")
        
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                }
            )
            response.raise_for_status()
            
            data = response.json()
            generation = data.get("response", "{}")
            
            try:
                structured_data = json.loads(generation)
                return structured_data
            except json.JSONDecodeError:
                print("Failed to decode JSON from Ollama.")
                return {"standings": [], "error": "Invalid JSON from model"}
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Error communicating with Ollama: {str(e)}"}
