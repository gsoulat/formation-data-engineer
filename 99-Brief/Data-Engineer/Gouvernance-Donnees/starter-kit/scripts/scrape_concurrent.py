#!/usr/bin/env python3
"""Veille concurrentielle Bouquineo — alimente data/concurrent_prix.csv.

Scrape le bac à sable légal https://books.toscrape.com (site fictif qui
simule le concurrent) et remplace le fichier placeholder généré par
generate_data.py. Le CSV est ensuite chargé dans raw.concurrent_prix au
premier démarrage de PostgreSQL (ou via un COPY manuel, voir README).

Usage :
    python3 scrape_concurrent.py [--pages 3] [--out ../data/concurrent_prix.csv]

Dépendances : requests, beautifulsoup4 (voir requirements.txt).
"""

from __future__ import annotations

import argparse
import csv
import logging
import sys
import time
from datetime import date
from pathlib import Path

import requests
from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("bouquineo.scraper")

BASE_URL = "https://books.toscrape.com"
PAGE_URL = BASE_URL + "/catalogue/page-{n}.html"
NOTES = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
DELAI_ENTRE_PAGES = 1.0  # politesse : 1 requête/seconde maximum


def scraper_page(session: requests.Session, numero: int) -> list[dict]:
    """Récupère et parse une page du catalogue concurrent.

    Retourne une liste de dicts {titre, prix_concurrent, note}.
    Lève requests.RequestException en cas d'échec réseau/HTTP.
    """
    url = PAGE_URL.format(n=numero)
    log.info("Requête GET %s", url)
    reponse = session.get(url, timeout=10)
    reponse.raise_for_status()

    soup = BeautifulSoup(reponse.text, "html.parser")
    livres = []
    for article in soup.select("article.product_pod"):
        try:
            titre = article.h3.a["title"].strip()
            prix_brut = article.select_one("p.price_color").get_text(strip=True)
            # ex. '£51.77' — on retire le symbole et tout caractère parasite
            prix = float(prix_brut.lstrip("£Â").replace(",", "."))
            classes_note = article.select_one("p.star-rating")["class"]
            note = next((NOTES[c] for c in classes_note if c in NOTES), 0)
            livres.append({"titre": titre, "prix_concurrent": prix, "note": note})
        except (AttributeError, KeyError, TypeError, ValueError) as exc:
            log.warning("Article illisible ignoré (%s)", exc)
    return livres


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scrape books.toscrape.com vers concurrent_prix.csv")
    parser.add_argument("--pages", type=int, default=3,
                        help="nombre de pages du catalogue à relever (défaut : 3, soit 60 livres)")
    parser.add_argument("--out", default=str(Path(__file__).resolve().parent.parent / "data" / "concurrent_prix.csv"),
                        help="chemin du CSV de sortie")
    args = parser.parse_args(argv)

    session = requests.Session()
    session.headers["User-Agent"] = "BouquineoVeille/1.0 (exercice pedagogique)"

    releves: list[dict] = []
    for n in range(1, args.pages + 1):
        try:
            releves.extend(scraper_page(session, n))
        except requests.RequestException as exc:
            log.error("Échec sur la page %d : %s", n, exc)
            if not releves:
                log.error("Aucune donnée collectée : abandon (le placeholder reste utilisable).")
                return 1
            log.warning("On s'arrête à la page %d avec %d relevés.", n - 1, len(releves))
            break
        if n < args.pages:
            time.sleep(DELAI_ENTRE_PAGES)

    if not releves:
        log.error("Aucun livre extrait : structure du site modifiée ?")
        return 1

    out = Path(args.out)
    try:
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "titre", "prix_concurrent", "note", "source", "date_releve"])
            for i, livre in enumerate(releves, start=1):
                writer.writerow([
                    i, livre["titre"], f"{livre['prix_concurrent']:.2f}",
                    livre["note"], "books.toscrape.com", date.today().isoformat(),
                ])
    except OSError as exc:
        log.error("Écriture impossible dans %s : %s", out, exc)
        return 1

    log.info("%d relevés concurrents écrits dans %s", len(releves), out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
