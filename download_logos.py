import os
import time
import requests

teams = [
    "Arsenal", "Aston Villa", "Bournemouth", "Brentford", "Brighton",
    "Chelsea", "Coventry", "Crystal Palace", "Everton", "Fulham",
    "Hull City", "Ipswich", "Leeds", "Liverpool", "Manchester City",
    "Manchester United", "Newcastle", "Nottingham Forest", "Sunderland", "Tottenham"
]

file_teams = [
    "Arsenal", "Aston Villa", "Bournemouth", "Brentford", "Brighton and Hove Albion",
    "Chelsea", "Coventry City", "Crystal Palace", "Everton", "Fulham",
    "Hull City", "Ipswich Town", "Leeds United", "Liverpool", "Manchester City",
    "Manchester United", "Newcastle United", "Nottingham Forest", "Sunderland", "Tottenham Hotspur"
]

os.makedirs("media/teamlogos", exist_ok=True)

for i, team in enumerate(teams):
    print(f"Searching for {team}...")
    try:
        url = f"https://www.thesportsdb.com/api/v1/json/3/searchteams.php?t={team}"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        
        if data.get("teams"):
            # Find the first english team if possible, else fallback to first
            team_data = next((t for t in data["teams"] if t["strCountry"] == "England"), data["teams"][0])
            logo_url = team_data.get("strBadge")
            
            if logo_url:
                print(f"Downloading {logo_url} for {team}...")
                img_resp = requests.get(logo_url, timeout=10)
                
                safe_name = file_teams[i].replace(" ", "_").lower()
                filepath = f"media/teamlogos/{safe_name}.png"
                with open(filepath, "wb") as f:
                    f.write(img_resp.content)
                print(f"Saved {filepath}")
            else:
                print(f"No badge found for {team}")
        else:
            print(f"No results found for {team} on SportsDB")
    except Exception as e:
        print(f"Failed {team}: {e}")
    time.sleep(1)
