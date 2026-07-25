import os
import pandas as pd

class DataLoader:
    """
    Handles reading news, stats, and CSV tabular data and chunking them.
    """
    def __init__(self, chunk_size=512, overlap=50):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text, metadata):
        """
        Splits text into overlapping chunks, preserving metadata.
        For simplicity in this prototype, we chunk by character length.
        """
        chunks = []
        start = 0
        text_len = len(text)
        
        while start < text_len:
            end = min(start + self.chunk_size, text_len)
            chunk_text = text[start:end]
            chunks.append({
                "text": chunk_text,
                "metadata": metadata
            })
            if end == text_len:
                break
            start += (self.chunk_size - self.overlap)
            
        return chunks

    def load_directory(self, directory_path):
        """
        Reads all text files in a directory and returns chunks.
        """
        all_chunks = []
        if not os.path.exists(directory_path):
            return all_chunks
            
        for root, _, files in os.walk(directory_path):
            for file in files:
                if file.endswith('.txt') or file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    source_name = os.path.splitext(file)[0].replace('_', ' ')
                    category = os.path.basename(root)
                    metadata = {
                        "source": source_name,
                        "category": category,
                        "file_path": file_path
                    }
                    
                    chunks = self.chunk_text(content, metadata)
                    all_chunks.extend(chunks)
                    
        return all_chunks

    def load_csvs(self, directory_path):
        """
        Reads players, teams, and playerstats CSVs and converts rows into natural language chunks.
        """
        all_chunks = []
        if not os.path.exists(directory_path):
            return all_chunks

        teams_path = os.path.join(directory_path, "teams.csv")
        players_path = os.path.join(directory_path, "players.csv")
        stats_path = os.path.join(directory_path, "playerstats.csv")

        if not (os.path.exists(teams_path) and os.path.exists(players_path) and os.path.exists(stats_path)):
            print("Warning: CSV files not found in", directory_path)
            return all_chunks

        # Load CSVs
        teams_df = pd.read_csv(teams_path)
        players_df = pd.read_csv(players_path)
        stats_df = pd.read_csv(stats_path)

        # Process Teams
        for _, row in teams_df.iterrows():
            text = f"Team {row['name']} (short name {row['short_name']}) has an overall strength of {row['strength']} and a ClubElo rating of {row['elo']}."
            metadata = {"source": f"Team Stats: {row['name']}", "category": "csv"}
            all_chunks.extend(self.chunk_text(text, metadata))

        # Process Players
        # Join players with teams to get team name, then with stats
        merged_players = pd.merge(players_df, teams_df, left_on='team_code', right_on='code', suffixes=('_player', '_team'))
        merged_all = pd.merge(merged_players, stats_df, left_on='player_id', right_on='id', suffixes=('', '_stat'))

        for _, row in merged_all.iterrows():
            # Skip players with very low points to save embedding time for the prototype
            if row.get('total_points', 0) < 10 and row.get('now_cost', 0) < 5.0:
                continue
                
            first = row.get('first_name', '')
            last = row.get('second_name', '')
            team = row.get('name', 'Unknown Team')
            cost = row.get('now_cost', 0)
            points = row.get('total_points', 0)
            xg = row.get('expected_goals', 0)
            xa = row.get('expected_assists', 0)
            form = row.get('form', 0)
            news = row.get('news', '')

            news_str = f" Latest news: {news}" if pd.notna(news) and news else ""
            
            text = (f"Player {first} {last} plays for {team}. His current FPL cost is {cost}. "
                    f"He has {points} total points, an expected goals (xG) of {xg}, an expected assists (xA) of {xa}, "
                    f"and a recent form rating of {form}.{news_str}")
            
            metadata = {"source": f"Player Stats: {first} {last}", "category": "csv"}
            all_chunks.extend(self.chunk_text(text, metadata))
            
        return all_chunks
