#!/usr/bin/env python3
"""Générateur de données Bouquineo — kit de démarrage du brief 03 (Gouvernance).

Produit dans le dossier data/ les fichiers CSV chargés par PostgreSQL au
premier démarrage (docker-entrypoint-initdb.d) :

  - clients.csv          (~8 000 lignes, PII : email, téléphone, adresse)
  - clients_v2.csv       (table "fantôme" : migration abandonnée, colonnes renommées)
  - crm_export.csv       (table "fantôme" : export CRM obsolète, contient des désinscrits)
  - catalogue.csv        (~12 000 références)
  - ventes.csv           (~50 000 lignes, 3 canaux)
  - evenements_web.csv   (~120 000 lignes, volumétrie la plus forte)
  - concurrent_prix.csv  (données simulées ; remplacées par scrape_concurrent.py)

Usage :
    python3 generate_data.py [--out ../data] [--seed 42] [--small]

--small divise les volumétries par 10 (machines modestes / tests rapides).
Aucune dépendance externe : bibliothèque standard uniquement.
"""

from __future__ import annotations

import argparse
import csv
import logging
import random
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("bouquineo.generator")

# ---------------------------------------------------------------------------
# Référentiels de génération (données synthétiques, aucun individu réel)
# ---------------------------------------------------------------------------

PRENOMS = [
    "Camille", "Louis", "Emma", "Gabriel", "Jade", "Raphaël", "Louise", "Léo",
    "Alice", "Jules", "Chloé", "Adam", "Lina", "Hugo", "Rose", "Arthur",
    "Anna", "Nathan", "Léa", "Paul", "Inès", "Tom", "Julia", "Sacha",
    "Zoé", "Noah", "Manon", "Ethan", "Nina", "Mohamed", "Fatima", "Karim",
]
NOMS = [
    "Martin", "Bernard", "Thomas", "Petit", "Robert", "Richard", "Durand",
    "Dubois", "Moreau", "Laurent", "Simon", "Michel", "Lefebvre", "Leroy",
    "Roux", "David", "Bertrand", "Morel", "Fournier", "Girard", "Bonnet",
    "Dupont", "Lambert", "Fontaine", "Rousseau", "Vincent", "Muller", "Faure",
]
VILLES = [
    ("Lille", "59000"), ("Paris", "75011"), ("Lyon", "69003"), ("Roubaix", "59100"),
    ("Tourcoing", "59200"), ("Arras", "62000"), ("Amiens", "80000"), ("Douai", "59500"),
    ("Valenciennes", "59300"), ("Dunkerque", "59140"), ("Lens", "62300"), ("Nantes", "44000"),
]
RUES = [
    "rue Nationale", "rue de la Gare", "avenue de la République", "rue du Molinel",
    "boulevard de la Liberté", "rue Solférino", "rue Faidherbe", "place du Théâtre",
    "rue de Béthune", "rue Esquermoise", "rue Léon Gambetta", "rue de Paris",
]
DOMAINES_EMAIL = ["exemple.fr", "courriel.example", "mail.example", "poste.example"]

CATEGORIES = [
    "Roman", "Polar & Thriller", "Science-Fiction", "Fantasy", "Jeunesse",
    "Bande dessinée", "Manga", "Essais", "Histoire", "Cuisine",
    "Développement personnel", "Poésie", "Beaux livres", "Scolaire",
]
EDITEURS = [
    "Éditions du Beffroi", "Presses de la Deûle", "Lumen", "Atelier Nord",
    "Les Trois Canaux", "Braderie Éditions", "Papier Plume", "Le Vieux Lille",
]
MOTS_TITRE = [
    "ombre", "jardin", "hiver", "voyage", "silence", "mémoire", "horizon",
    "royaume", "secret", "lumière", "tempête", "frontière", "promesse",
    "labyrinthe", "étoile", "rivage", "brume", "héritage", "sentinelle", "canal",
]

CANAUX = ["site", "marketplace", "librairie"]
POIDS_CANAUX = [0.55, 0.25, 0.20]
EVENT_TYPES = ["page_vue", "recherche", "ajout_panier", "achat", "avis_depose"]
POIDS_EVENTS = [0.62, 0.18, 0.12, 0.05, 0.03]

AUJOURDHUI = date(2026, 7, 6)  # date de référence figée => jeu de données reproductible


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _slug(s: str) -> str:
    table = str.maketrans("àâäéèêëîïôöùûüç", "aaaeeeeiioouuuc")
    return s.lower().translate(table).replace(" ", ".").replace("'", "")


def _date_entre(rng: random.Random, debut: date, fin: date) -> date:
    delta = (fin - debut).days
    return debut + timedelta(days=rng.randint(0, max(delta, 0)))


def _telephone(rng: random.Random) -> str:
    return "0" + str(rng.choice([3, 6, 7])) + "".join(str(rng.randint(0, 9)) for _ in range(8))


def _ecrire_csv(chemin: Path, entetes: list[str], lignes: list[list]) -> None:
    try:
        with chemin.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(entetes)
            writer.writerows(lignes)
    except OSError as exc:
        log.error("Impossible d'écrire %s : %s", chemin, exc)
        raise
    log.info("%-22s : %6d lignes -> %s", chemin.stem, len(lignes), chemin)


# ---------------------------------------------------------------------------
# Générateurs de tables
# ---------------------------------------------------------------------------

def gen_clients(rng: random.Random, n: int) -> list[list]:
    lignes = []
    for i in range(1, n + 1):
        prenom, nom = rng.choice(PRENOMS), rng.choice(NOMS)
        ville, cp = rng.choice(VILLES)
        email = f"{_slug(prenom)}.{_slug(nom)}{i}@{rng.choice(DOMAINES_EMAIL)}"
        inscription = _date_entre(rng, date(2015, 3, 1), AUJOURDHUI)
        # ~12 % de clients inactifs depuis plus de 3 ans (cas RGPD du brief),
        # les autres ont commandé dans les 3 dernières années.
        seuil_3ans = AUJOURDHUI - timedelta(days=1100)
        if rng.random() < 0.12 and inscription < seuil_3ans - timedelta(days=30):
            derniere = _date_entre(rng, inscription, seuil_3ans)
        else:
            derniere = _date_entre(rng, max(inscription, AUJOURDHUI - timedelta(days=1095)), AUJOURDHUI)
        lignes.append([
            i, nom, prenom, email, _telephone(rng),
            f"{rng.randint(1, 180)} {rng.choice(RUES)}", cp, ville,
            inscription.isoformat(), derniere.isoformat(),
            "true" if rng.random() < 0.68 else "false",  # optin_marketing
        ])
    return lignes


def gen_clients_v2(rng: random.Random, clients: list[list]) -> list[list]:
    """Migration abandonnée mi-2024 : ~80 % des clients, colonnes renommées,
    plus jamais alimentée depuis (test de fraîcheur : doit échouer)."""
    coupure = date(2024, 6, 30)
    lignes = []
    for c in clients:
        if rng.random() < 0.80 and date.fromisoformat(c[8]) <= coupure:
            lignes.append([
                c[0], f"{c[2]} {c[1]}",           # full_name
                c[3], c[4],                        # email_address, phone
                f"{c[5]}, {c[6]} {c[7]}",          # postal_address
                c[8],                              # signup_date
                coupure.isoformat(),               # updated_at figé à la coupure
            ])
    return lignes


def gen_crm_export(rng: random.Random, clients: list[list]) -> list[list]:
    """Export CRM du 15/01/2025, jamais rafraîchi. Piège du brief : le flag
    optin y est OBSOLÈTE (des désinscrits y figurent encore comme inscrits)."""
    export_le = "2025-01-15"
    lignes = []
    for c in clients:
        if date.fromisoformat(c[8]) > date(2025, 1, 15):
            continue  # client inscrit après l'export
        optin_reel = c[10]
        # 18 % des optins réels 'false' apparaissent 'true' dans l'export => campagne fautive
        optin_export = "true" if (optin_reel == "true" or rng.random() < 0.18) else "false"
        lignes.append([c[0], c[2], c[1], c[3], optin_export, export_le])
    return lignes


def gen_catalogue(rng: random.Random, n: int) -> list[list]:
    lignes = []
    for i in range(1, n + 1):
        isbn = f"978-2-{rng.randint(10000, 99999)}-{rng.randint(100, 999)}-{rng.randint(0, 9)}"
        titre = f"{rng.choice(['Le', 'La', 'Les'])} {rng.choice(MOTS_TITRE)} {rng.choice(['du', 'de la', 'des'])} {rng.choice(MOTS_TITRE)}".capitalize()
        auteur = f"{rng.choice(PRENOMS)} {rng.choice(NOMS)}"
        prix = round(rng.uniform(4.9, 39.9), 2)
        # ~3 % de prix manquants (test de complétude : doit remonter des trous)
        prix_csv = "" if rng.random() < 0.03 else f"{prix:.2f}"
        lignes.append([
            i, isbn, titre, auteur, rng.choice(EDITEURS), rng.choice(CATEGORIES),
            prix_csv, rng.randint(0, 120),
            _date_entre(rng, date(2015, 1, 1), AUJOURDHUI).isoformat(),
        ])
    return lignes


def gen_ventes(rng: random.Random, n: int, nb_clients: int, nb_refs: int) -> list[list]:
    lignes = []
    for i in range(1, n + 1):
        canal = rng.choices(CANAUX, weights=POIDS_CANAUX, k=1)[0]
        librairie_id = rng.randint(1, 8) if canal == "librairie" else ""
        d = _date_entre(rng, date(2019, 1, 1), AUJOURDHUI)
        lignes.append([
            i, rng.randint(1, nb_clients), rng.randint(1, nb_refs),
            canal, librairie_id, rng.randint(1, 4),
            f"{rng.uniform(4.9, 39.9):.2f}", d.isoformat(),
        ])
    return lignes


def gen_evenements(rng: random.Random, n: int, nb_clients: int) -> list[list]:
    pages = ["/", "/livre/", "/categorie/", "/panier", "/recherche", "/compte", "/promo"]
    lignes = []
    ts = datetime(2025, 1, 1, 0, 0, 0)
    for i in range(1, n + 1):
        ts += timedelta(seconds=rng.randint(5, 420))
        client = rng.randint(1, nb_clients) if rng.random() < 0.35 else ""  # 65 % anonymes
        lignes.append([
            i, client, f"sess_{rng.randint(100000, 999999)}",
            rng.choices(EVENT_TYPES, weights=POIDS_EVENTS, k=1)[0],
            rng.choice(pages) + (str(rng.randint(1, 12000)) if rng.random() < 0.4 else ""),
            ts.isoformat(sep=" "),
        ])
    return lignes


def gen_concurrent_placeholder(rng: random.Random, n: int = 60) -> list[list]:
    """Données simulées pour que l'init DB fonctionne même sans scraping.
    scrape_concurrent.py régénère ce fichier avec les vraies données
    de https://books.toscrape.com."""
    lignes = []
    for i in range(1, n + 1):
        lignes.append([
            i, f"Titre concurrent {i} (placeholder)",
            f"{rng.uniform(10, 60):.2f}", rng.randint(0, 5),
            "placeholder", AUJOURDHUI.isoformat(),
        ])
    return lignes


# ---------------------------------------------------------------------------
# Point d'entrée
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Génère les CSV du kit Bouquineo.")
    parser.add_argument("--out", default=str(Path(__file__).resolve().parent.parent / "data"),
                        help="dossier de sortie des CSV (défaut : ../data)")
    parser.add_argument("--seed", type=int, default=42, help="graine aléatoire (défaut : 42)")
    parser.add_argument("--small", action="store_true", help="volumétries divisées par 10")
    args = parser.parse_args(argv)

    rng = random.Random(args.seed)
    out = Path(args.out)
    try:
        out.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        log.error("Impossible de créer le dossier %s : %s", out, exc)
        return 1

    k = 10 if args.small else 1
    n_clients, n_refs = 8000 // k, 12000 // k
    n_ventes, n_events = 50000 // k, 120000 // k

    log.info("Génération (seed=%d, small=%s) vers %s", args.seed, args.small, out)

    clients = gen_clients(rng, n_clients)
    _ecrire_csv(out / "clients.csv",
                ["client_id", "nom", "prenom", "email", "telephone", "adresse",
                 "code_postal", "ville", "date_inscription", "date_derniere_commande",
                 "optin_marketing"], clients)

    _ecrire_csv(out / "clients_v2.csv",
                ["id", "full_name", "email_address", "phone", "postal_address",
                 "signup_date", "updated_at"], gen_clients_v2(rng, clients))

    _ecrire_csv(out / "crm_export.csv",
                ["client_id", "prenom", "nom", "email", "optin", "exporte_le"],
                gen_crm_export(rng, clients))

    _ecrire_csv(out / "catalogue.csv",
                ["reference_id", "isbn", "titre", "auteur", "editeur", "categorie",
                 "prix", "stock", "date_ajout"], gen_catalogue(rng, n_refs))

    _ecrire_csv(out / "ventes.csv",
                ["vente_id", "client_id", "reference_id", "canal", "librairie_id",
                 "quantite", "prix_unitaire", "date_vente"],
                gen_ventes(rng, n_ventes, n_clients, n_refs))

    _ecrire_csv(out / "evenements_web.csv",
                ["event_id", "client_id", "session_id", "event_type", "url", "ts"],
                gen_evenements(rng, n_events, n_clients))

    if not (out / "concurrent_prix.csv").exists():
        _ecrire_csv(out / "concurrent_prix.csv",
                    ["id", "titre", "prix_concurrent", "note", "source", "date_releve"],
                    gen_concurrent_placeholder(rng))
    else:
        log.info("concurrent_prix.csv déjà présent (scraping ?) : conservé tel quel")

    log.info("Terminé. Lancez ensuite : docker compose up -d (premier démarrage = chargement des CSV)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
