import torch

class LeaguePredictor:
    """
    Predicts the Premier League table by leveraging a VectorStore of news and stats.
    """
    def __init__(self, embedder, vector_store):
        self.embedder = embedder
        self.vector_store = vector_store

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
        
        # 3. Simulate an LLM adjusting the table based on retrieved context.
        # We will keep a score for each team based on the retrieved context sentiment.
        # Positive keywords boost a team, negative keywords drop a team.
        team_scores = {team: 0 for team in self.base_teams}
        
        positive_keywords = ["signs", "retains", "improves", "wins", "dominates", "strong", "excellent", "star"]
        negative_keywords = ["injury", "woes", "loses", "sacked", "struggles", "poor", "weakness"]

        retrieved_context_texts = []
        for match in matches:
            text = match["metadata"].get("text", "")
            retrieved_context_texts.append(text.strip())
            text_lower = text.lower()
            
            # Simple keyword matching to simulate sentiment analysis
            for team in self.base_teams:
                if team.lower() in text_lower:
                    for pos in positive_keywords:
                        if pos in text_lower:
                            team_scores[team] += 2
                    for neg in negative_keywords:
                        if neg in text_lower:
                            team_scores[team] -= 2

        # Add some randomness to teams without news, or just leave them at 0
        # To make a realistic base table before applying the news deltas, let's establish a base tier
        base_tiers = {
            "Manchester City": 90, "Arsenal": 88, "Liverpool": 85, "Chelsea": 75,
            "Tottenham Hotspur": 75, "Manchester United": 72, "Newcastle United": 70,
            "Aston Villa": 68, "West Ham United": 60, "Brighton & Hove Albion": 58,
            "Bournemouth": 50, "Crystal Palace": 50, "Fulham": 48, "Wolverhampton Wanderers": 45,
            "Everton": 40, "Brentford": 40, "Nottingham Forest": 35,
            "Leicester City": 30, "Southampton": 28, "Ipswich Town": 25
        }
        
        # Apply news deltas
        final_scores = {}
        for team in self.base_teams:
            final_scores[team] = base_tiers.get(team, 30) + team_scores[team]

        # Sort teams by final score descending
        sorted_teams = sorted(final_scores.keys(), key=lambda x: final_scores[x], reverse=True)

        # Formulate report
        report = []
        report.append("### Predicted Premier League Table (1-20)\n")
        
        for idx, team in enumerate(sorted_teams):
            report.append(f"{idx + 1}. {team}")
            
        report.append("\n**Key Factors (Retrieved Context):**")
        if not retrieved_context_texts:
            report.append("> No significant news found.")
        else:
            for ctx in retrieved_context_texts:
                report.append(f"> \"{ctx}\"")
                
        return "\n".join(report)
