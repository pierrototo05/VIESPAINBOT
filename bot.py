import requests
from bs4 import BeautifulSoup
import json
import os

# === CONFIGURATION ===
TOKEN = "7465906532:AAGxQ2lmtCgHm3pXL1IrEU6bhiGJb9FRJXg"
CHAT_ID = "2085048128"
CACHE_FILE = "cache.json"
PAYS_AUTORISES = {"Espagne", "Madrid",}
MOTS_CLES_FINANCE = ["finance", "financial", "financier", "risk", "analyst", "sales", "trading", "contrôle", "gestion"]

# === UTILS ===
def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    response = requests.post(url, data={"chat_id": CHAT_ID, "text": text})
    print("Status Code:", response.status_code)
    print("Response:", response.text)

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_cache(cache_set):
    with open(CACHE_FILE, "w") as f:
        json.dump(list(cache_set), f)

def filtre_offre(titre):
    titre_lc = titre.lower()
    return "vie" in titre_lc and any(m in titre_lc for m in MOTS_CLES_FINANCE) and any(p.lower() in titre_lc for p in PAYS_AUTORISES)

# === SCRAPERS ENTREPRISES ===

def get_sg_offres():
    url = "https://careers.societegenerale.com/offres?contract=V.I.E&country=Espagne"
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    offres = soup.find_all("a", class_="job-title")
    return [("Société Générale", o.text.strip(), "https://careers.societegenerale.com" + o["href"]) for o in offres if filtre_offre(o.text)]

def get_bnp_offres():
    url = "https://group.bnpparibas/emploi-carriere/nos-offres-demploi?contract_type=vie"
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    offres = soup.find_all("a", href=True)
    results = []
    for o in offres:
        titre = o.text.strip()
        lien = o["href"]
        if filtre_offre(titre):
            full_url = lien if lien.startswith("http") else "https://group.bnpparibas" + lien
            results.append(("BNP Paribas", titre, full_url))
    return results

def get_cacib_offres():
    url = "https://group.creditagricole.jobs/fr/nos-offres/contrats/1478/"
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    offres = soup.find_all("a", class_="search-result")
    results = []
    for o in offres:
        titre = o.text.strip()
        lien = o["href"]
        if filtre_offre(titre):
            full_url = lien if lien.startswith("http") else "https://group.creditagricole.jobs" + lien
            results.append(("CACIB", titre, full_url))
    return results

def get_natixis_offres():
    url = "https://recrutement.natixis.com/nos-offres-demploi?tax_contract=vie&external=false"
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    offres = soup.find_all("a", href=True)
    results = []
    for o in offres:
        titre = o.text.strip()
        lien = o["href"]
        if filtre_offre(titre):
            full_url = lien if lien.startswith("http") else "https://recrutement.natixis.com" + lien
            results.append(("Natixis", titre, full_url))
    return results

# === MAIN ===
def main():
    try:
        send_message("✅ Le bot tourne bien, test de notif.")  # <== TEST placé en tout début

        offres = []
        offres += get_sg_offres()
        offres += get_bnp_offres()
        offres += get_cacib_offres()
        offres += get_natixis_offres()

        cache = load_cache()
        new_cache = set(cache)

        for source, titre, lien in offres:
            key = f"{source}|{titre}"
            if key not in cache:
                send_message(f"📢 Nouvelle offre V.I.E - {source} :\n{titre}\n🔗 {lien}")
                new_cache.add(key)

        save_cache(new_cache)
    except Exception as e:
        send_message(f"[BOT ERREUR] : {e}")

if __name__ == "__main__":
    main()
