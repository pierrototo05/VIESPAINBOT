import requests
from bs4 import BeautifulSoup
import json
import os

# === CONFIGURATION ===
TOKEN = "7465906532:AAGxQ2lmtCgHm3pXL1IrEU6bhiGJb9FRJXg"
CHAT_ID = "2085048128"
CACHE_FILE = "cache.json"
PAYS_AUTORISES = {"Espagne"}
MOTS_CLES_FINANCE = ["finance", "financial", "financier", "risk", "analyst", "sales", "trading"]

# === FONCTIONS UTILES ===
def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_cache(cache_set):
    with open(CACHE_FILE, "w") as f:
        json.dump(list(cache_set), f)

# === SCRAPER SOCIÉTÉ GÉNÉRALE ===
def get_sg_offres():
    url = "https://careers.societegenerale.com/offres?contract=V.I.E&country=Espagne"
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    offres = soup.find_all("a", class_="job-title")
    return [("SG", o.text.strip(), "https://careers.societegenerale.com" + o["href"]) for o in offres]

# === SCRAPER BUSINESS FRANCE ===
def get_bf_offres():
    url = "https://api.mon-vie-via.businessfrance.fr/api/opportunities/search?contractType=VIE&country=Espagne"
    res = requests.get(url).json()
    results = []
    for o in res.get("results", []):
        titre = o["title"]
        lien = "https://mon-vie-via.businessfrance.fr" + o["url"]
        if any(mot in titre.lower() for mot in MOTS_CLES_FINANCE):
            results.append(("Business France", titre, lien))
    return results

# === MAIN ===
def main():
    try:
        offres = get_sg_offres() + get_bf_offres()
        cache = load_cache()
        new_cache = set(cache)

        for source, titre, lien in offres:
            key = f"{source}|{titre}"
            if key not in cache:
                send_message(f"Nouvelle offre V.I.E ({source}) :\n{titre}\n{lien}")
                new_cache.add(key)

        save_cache(new_cache)
    except Exception as e:
        send_message(f"[BOT ERREUR] : {e}")

if __name__ == "__main__":
    main()
