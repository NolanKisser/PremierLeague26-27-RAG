import os
import requests

def download_file(url, output_path):
    print(f"Downloading {url}...")
    response = requests.get(url)
    if response.status_code == 200:
        with open(output_path, 'wb') as f:
            f.write(response.content)
        print(f"Successfully downloaded to {output_path}")
    else:
        print(f"Failed to download {url}. Status code: {response.status_code}")

def fetch_all_data():
    base_dir = "data/raw_csv"
    os.makedirs(base_dir, exist_ok=True)
    
    print("Fetching FPL Core Insights (Players)...")
    players_url = "https://raw.githubusercontent.com/olbauday/FPL-Core-Insights/main/data/2026-2027/players.csv"
    download_file(players_url, os.path.join(base_dir, "players.csv"))

    print("Fetching FPL Core Insights (Teams)...")
    teams_url = "https://raw.githubusercontent.com/olbauday/FPL-Core-Insights/main/data/2026-2027/teams.csv"
    download_file(teams_url, os.path.join(base_dir, "teams.csv"))
    
    print("Fetching FPL Core Insights (Player Stats)...")
    stats_url = "https://raw.githubusercontent.com/olbauday/FPL-Core-Insights/main/data/2026-2027/playerstats.csv"
    download_file(stats_url, os.path.join(base_dir, "playerstats.csv"))
    
    print("Fetching FPL Core Insights (Gameweek Summaries)...")
    gw_url = "https://raw.githubusercontent.com/olbauday/FPL-Core-Insights/main/data/2026-2027/gameweek_summaries.csv"
    download_file(gw_url, os.path.join(base_dir, "gameweek_summaries.csv"))

    print("Fetching FPL Core Insights (Team History)...")
    team_hist_url = "https://raw.githubusercontent.com/olbauday/FPL-Core-Insights/main/data/2026-2027/team_history.csv"
    download_file(team_hist_url, os.path.join(base_dir, "team_history.csv"))
    
    print("All data fetched successfully.")

if __name__ == "__main__":
    fetch_all_data()
