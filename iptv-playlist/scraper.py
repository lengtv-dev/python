import requests
from bs4 import BeautifulSoup
import json

URL = "https://dooball66d.com/"

headers = {
 "User-Agent": "Mozilla/5.0"
}

r = requests.get(URL, headers=headers)

soup = BeautifulSoup(r.text, "html.parser")

groups = []

for wrapper in soup.select("#sportTabContent .sport-wrapper"):

    header = wrapper.select_one(".match-live-header")

    if not header:
        continue

    league = header.get_text(" ", strip=True)

    stations = []

    for match in wrapper.select(".match-live"):

        time_el = match.select_one(".col-1")
        if not time_el:
            continue

        time_text = time_el.get_text(strip=True)

        teams = match.select("span")

        if len(teams) < 2:
            continue

        home = teams[0].get_text(strip=True)
        away = teams[1].get_text(strip=True)

        link = match.select_one("a[href*='match_id']")

        if not link:
            continue

        stations.append({
            "name": f"{time_text} {home} vs {away}",
            "url": link["href"]
        })

    if stations:
        groups.append({
            "name": league,
            "stations": stations
        })

data = {
 "name": "Live Football",
 "groups": groups
}

with open("playlist.json","w",encoding="utf-8") as f:
    json.dump(data,f,ensure_ascii=False,indent=2)
