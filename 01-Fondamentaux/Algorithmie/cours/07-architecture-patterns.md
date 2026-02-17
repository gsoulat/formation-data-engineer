# Module 07 — Architecture logicielle et design patterns

## 🎯 Objectifs

- Comprendre les principes d'architecture en couches (layered architecture)
- Maîtriser le pattern MVC et ses variantes
- Découvrir les architectures Clean et Hexagonale
- Comprendre les patterns architecturaux appliqués au data engineering
- Savoir choisir la bonne architecture selon le contexte

---

## 1. 🧠 Pourquoi l'architecture logicielle ?

### 1.1 Le problème

Sans architecture, le code devient vite un **plat de spaghetti** : tout est mélangé, chaque modification casse autre chose, et personne n'ose toucher au code.

```
❌ Code sans architecture :

┌──────────────────────────────────┐
│  main.py (2000 lignes)           │
│                                  │
│  - Connexion BDD                 │
│  - Requêtes SQL                  │
│  - Logique métier                │
│  - Affichage / API               │
│  - Validation                    │
│  - Configuration                 │
│  - Tout mélangé...              │
└──────────────────────────────────┘
```

```
✅ Code avec architecture :

┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Présentation │→ │   Métier     │→ │   Données    │
│ (API/UI)     │  │ (Logique)    │  │ (BDD/Fichiers)│
└──────────────┘  └──────────────┘  └──────────────┘
```

### 1.2 Les bénéfices d'une bonne architecture

| Bénéfice | Description |
|----------|-------------|
| **Séparation des responsabilités** | Chaque composant a un rôle clair |
| **Maintenabilité** | On peut modifier une partie sans casser le reste |
| **Testabilité** | On peut tester chaque couche indépendamment |
| **Réutilisabilité** | Les composants sont réutilisables dans d'autres projets |
| **Scalabilité** | On peut faire évoluer chaque couche séparément |
| **Collaboration** | Plusieurs développeurs peuvent travailler en parallèle |

---

## 2. 🏗️ Architecture multicouche (Layered Architecture)

### 2.1 Principe

L'architecture multicouche (ou **N-tier**) organise le code en couches horizontales, chaque couche ayant une responsabilité spécifique. Une couche ne communique qu'avec la couche directement adjacente.

### 2.2 Architecture 3 couches classique

```
┌─────────────────────────────────────────┐
│        Couche Présentation              │
│  (Interface utilisateur, API REST)      │
│  Rôle : afficher, recevoir les entrées  │
└────────────────┬────────────────────────┘
                 │ appelle
                 ▼
┌─────────────────────────────────────────┐
│        Couche Métier (Business)         │
│  (Logique métier, règles, calculs)      │
│  Rôle : traiter, valider, orchestrer    │
└────────────────┬────────────────────────┘
                 │ appelle
                 ▼
┌─────────────────────────────────────────┐
│        Couche Données (Data Access)     │
│  (BDD, fichiers, API externes)         │
│  Rôle : lire et écrire les données     │
└─────────────────────────────────────────┘
```

### 2.3 Exemple concret en Python

```
projet/
├── presentation/       # Couche Présentation
│   ├── api.py          # Endpoints FastAPI
│   └── schemas.py      # Modèles de requête/réponse (Pydantic)
├── metier/             # Couche Métier
│   ├── services.py     # Logique métier
│   └── regles.py       # Règles de validation
├── donnees/            # Couche Données
│   ├── repositories.py # Accès BDD
│   └── modeles.py      # Modèles ORM (SQLAlchemy)
└── main.py             # Point d'entrée
```

```python
# ── donnees/repositories.py ── Couche Données
class ClientRepository:
    """Accès aux données clients en base."""

    def __init__(self, session):
        self.session = session

    def trouver_par_id(self, client_id: int) -> dict | None:
        """Récupère un client par son ID."""
        result = self.session.execute(
            "SELECT * FROM clients WHERE id = :id",
            {"id": client_id},
        )
        row = result.fetchone()
        return dict(row._mapping) if row else None

    def trouver_tous(self) -> list[dict]:
        """Récupère tous les clients."""
        result = self.session.execute("SELECT * FROM clients")
        return [dict(row._mapping) for row in result]

    def sauvegarder(self, client: dict) -> int:
        """Sauvegarde un client et retourne son ID."""
        result = self.session.execute(
            "INSERT INTO clients (nom, email) VALUES (:nom, :email)",
            client,
        )
        self.session.commit()
        return result.lastrowid


# ── metier/services.py ── Couche Métier
class ClientService:
    """Logique métier pour la gestion des clients."""

    def __init__(self, repository: ClientRepository):
        self.repository = repository

    def obtenir_client(self, client_id: int) -> dict:
        """Récupère un client avec validation."""
        client = self.repository.trouver_par_id(client_id)
        if client is None:
            raise ValueError(f"Client {client_id} introuvable")
        return client

    def creer_client(self, nom: str, email: str) -> dict:
        """Crée un client avec validation métier."""
        # Règles métier
        if not nom or len(nom) < 2:
            raise ValueError("Le nom doit contenir au moins 2 caractères")
        if "@" not in email:
            raise ValueError("Email invalide")

        client = {"nom": nom, "email": email.lower()}
        client_id = self.repository.sauvegarder(client)
        client["id"] = client_id
        return client


# ── presentation/api.py ── Couche Présentation
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class ClientRequest(BaseModel):
    nom: str
    email: str

@app.post("/clients")
def creer_client(request: ClientRequest):
    """Endpoint API — ne contient AUCUNE logique métier."""
    try:
        service = ClientService(ClientRepository(get_session()))
        client = service.creer_client(request.nom, request.email)
        return {"status": "ok", "client": client}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### 2.4 Règle fondamentale

> ⚠️ **Règle de dépendance** : Les couches supérieures dépendent des couches inférieures, **jamais l'inverse**.
>
> - La Présentation appelle le Métier ✅
> - Le Métier appelle les Données ✅
> - Les Données appellent le Métier ❌
> - Le Métier appelle la Présentation ❌

---

## 3. 🎮 Le pattern MVC (Model-View-Controller)

### 3.1 Principe

**MVC** sépare l'application en trois composants interconnectés :

| Composant | Rôle | Contenu |
|-----------|------|---------|
| **Model** | Les données et la logique métier | Classes, BDD, calculs |
| **View** | L'affichage / la présentation | Templates HTML, JSON, CLI |
| **Controller** | Le chef d'orchestre | Reçoit les requêtes, coordonne Model et View |

### 3.2 Flux de communication

```
                    ┌──────────────────┐
  Requête ────────→ │   Controller     │
  (utilisateur)     │                  │
                    │  1. Reçoit       │
                    │  2. Interprète   │
                    │  3. Coordonne    │
                    └───┬──────────┬───┘
                        │          │
               appelle  │          │  passe les
               le Model │          │  données à
                        ▼          ▼
                 ┌──────────┐  ┌──────────┐
                 │  Model   │  │   View   │
                 │          │  │          │
                 │ Données  │  │ Affichage│
                 │ Logique  │  │ Rendu    │
                 └──────────┘  └──────────┘
                                    │
                    Réponse ◄───────┘
                    (utilisateur)
```

### 3.3 Exemple : application de gestion de tâches

```python
# ── model.py ── Le Modèle
class Tache:
    """Représente une tâche avec ses données et sa logique."""

    def __init__(self, titre: str, priorite: int = 3):
        self.titre = titre
        self.priorite = priorite  # 1 = haute, 5 = basse
        self.terminee = False

    def terminer(self):
        self.terminee = True

    def est_urgente(self) -> bool:
        return self.priorite <= 2 and not self.terminee


class GestionnaireTaches:
    """Modèle principal — gère la collection de tâches."""

    def __init__(self):
        self._taches: list[Tache] = []

    def ajouter(self, titre: str, priorite: int = 3) -> Tache:
        tache = Tache(titre, priorite)
        self._taches.append(tache)
        return tache

    def lister(self, filtre: str = "toutes") -> list[Tache]:
        if filtre == "urgentes":
            return [t for t in self._taches if t.est_urgente()]
        if filtre == "terminees":
            return [t for t in self._taches if t.terminee]
        if filtre == "en_cours":
            return [t for t in self._taches if not t.terminee]
        return self._taches

    def terminer(self, index: int):
        if 0 <= index < len(self._taches):
            self._taches[index].terminer()

    def statistiques(self) -> dict:
        total = len(self._taches)
        terminees = sum(1 for t in self._taches if t.terminee)
        return {
            "total": total,
            "terminees": terminees,
            "en_cours": total - terminees,
        }


# ── view.py ── La Vue
class VueTaches:
    """Gère l'affichage — ne contient AUCUNE logique métier."""

    @staticmethod
    def afficher_liste(taches: list[Tache], titre: str = "Tâches"):
        print(f"\n{'='*40}")
        print(f"  {titre}")
        print(f"{'='*40}")
        if not taches:
            print("  (aucune tâche)")
        for i, tache in enumerate(taches):
            statut = "✅" if tache.terminee else "⬜"
            urgence = " 🔴" if tache.est_urgente() else ""
            print(f"  {i}. {statut} [{tache.priorite}] {tache.titre}{urgence}")

    @staticmethod
    def afficher_stats(stats: dict):
        print(f"\n📊 Statistiques :")
        print(f"  Total : {stats['total']}")
        print(f"  Terminées : {stats['terminees']}")
        print(f"  En cours : {stats['en_cours']}")

    @staticmethod
    def demander_commande() -> str:
        return input("\nCommande (ajouter/terminer/lister/stats/quitter) : ").strip()

    @staticmethod
    def demander_titre() -> str:
        return input("Titre de la tâche : ").strip()

    @staticmethod
    def demander_priorite() -> int:
        return int(input("Priorité (1-5) : ").strip())

    @staticmethod
    def demander_index() -> int:
        return int(input("Numéro de la tâche : ").strip())


# ── controller.py ── Le Contrôleur
class ControleurTaches:
    """Coordonne Model et View — ne contient NI logique métier NI affichage."""

    def __init__(self):
        self.model = GestionnaireTaches()
        self.vue = VueTaches()

    def executer(self):
        """Boucle principale de l'application."""
        while True:
            commande = self.vue.demander_commande()

            if commande == "ajouter":
                titre = self.vue.demander_titre()
                priorite = self.vue.demander_priorite()
                self.model.ajouter(titre, priorite)

            elif commande == "terminer":
                self.vue.afficher_liste(self.model.lister("en_cours"), "En cours")
                index = self.vue.demander_index()
                self.model.terminer(index)

            elif commande == "lister":
                self.vue.afficher_liste(self.model.lister())

            elif commande == "stats":
                self.vue.afficher_stats(self.model.statistiques())

            elif commande == "quitter":
                break


# Point d'entrée
if __name__ == "__main__":
    app = ControleurTaches()
    app.executer()
```

### 3.4 Variantes du MVC

```
MVC classique          MVP                    MVVM
(Web backend)          (Mobile/Desktop)       (Frontend moderne)

┌────┐  ┌────┐        ┌────┐  ┌───────┐     ┌────┐  ┌──────────┐
│View│←─│Ctrl│        │View│←→│Present│     │View│←→│ViewModel │
└──┬─┘  └──┬─┘        └────┘  └───┬───┘     └────┘  └────┬─────┘
   │       │                      │              (binding) │
   │    ┌──┴──┐                ┌──┴──┐              ┌──────┴─┐
   └───→│Model│                │Model│              │ Model  │
        └─────┘                └─────┘              └────────┘
```

| Variante | Différence | Usage typique |
|----------|-----------|---------------|
| **MVC** | Le Controller orchestre | Web backend (Django, FastAPI) |
| **MVP** | Le Presenter gère toute la logique de présentation | Applications desktop/mobile |
| **MVVM** | Le ViewModel expose des données avec data binding | Frontend (Vue.js, React) |

---

## 4. 🔷 Architecture hexagonale (Ports & Adapters)

### 4.1 Principe

L'architecture hexagonale (proposée par Alistair Cockburn) isole la **logique métier** au centre et la connecte au monde extérieur via des **ports** (interfaces) et des **adaptateurs** (implémentations).

```
                    Adaptateur HTTP           Adaptateur CLI
                    (FastAPI)                 (argparse)
                        │                         │
                        ▼                         ▼
                   ┌─────────┐              ┌─────────┐
                   │Port     │              │Port     │
                   │Entrée   │              │Entrée   │
                   └────┬────┘              └────┬────┘
                        │                        │
              ┌─────────┴────────────────────────┴──────────┐
              │                                              │
              │              DOMAINE MÉTIER                  │
              │                                              │
              │   (entités, services, règles métier)         │
              │   Aucune dépendance vers l'extérieur         │
              │                                              │
              └─────────┬────────────────────────┬──────────┘
                        │                        │
                   ┌────┴────┐              ┌────┴────┐
                   │Port     │              │Port     │
                   │Sortie   │              │Sortie   │
                   └────┬────┘              └────┬────┘
                        │                        │
                        ▼                        ▼
                   Adaptateur                Adaptateur
                   PostgreSQL                Fichier CSV
```

### 4.2 Avantage clé

La logique métier ne dépend de **rien** d'extérieur. On peut changer de base de données, d'API ou de framework sans toucher au métier.

### 4.3 Implémentation avec le protocole Python

```python
from typing import Protocol


# ── Ports (interfaces) ──
class PortStockageClients(Protocol):
    """Port de sortie : contrat pour stocker des clients."""

    def sauvegarder(self, client: dict) -> int: ...
    def trouver_par_id(self, client_id: int) -> dict | None: ...
    def trouver_tous(self) -> list[dict]: ...


class PortNotification(Protocol):
    """Port de sortie : contrat pour envoyer des notifications."""

    def envoyer(self, destinataire: str, message: str) -> bool: ...


# ── Domaine métier (ne dépend de rien) ──
class ServiceInscription:
    """Logique métier pure — ne connaît que les ports (interfaces)."""

    def __init__(
        self,
        stockage: PortStockageClients,
        notification: PortNotification,
    ):
        self.stockage = stockage
        self.notification = notification

    def inscrire(self, nom: str, email: str) -> dict:
        """Inscrit un nouveau client."""
        if len(nom) < 2:
            raise ValueError("Nom trop court")
        if "@" not in email:
            raise ValueError("Email invalide")

        client = {"nom": nom, "email": email.lower()}
        client_id = self.stockage.sauvegarder(client)
        client["id"] = client_id

        self.notification.envoyer(
            email,
            f"Bienvenue {nom} !",
        )

        return client


# ── Adaptateurs (implémentations concrètes) ──
class StockagePostgreSQL:
    """Adaptateur : stockage dans PostgreSQL."""

    def __init__(self, connection_string: str):
        self.connection_string = connection_string

    def sauvegarder(self, client: dict) -> int:
        # Implémentation PostgreSQL...
        print(f"[PostgreSQL] Sauvegarde : {client}")
        return 1

    def trouver_par_id(self, client_id: int) -> dict | None:
        print(f"[PostgreSQL] Recherche ID={client_id}")
        return None

    def trouver_tous(self) -> list[dict]:
        return []


class StockageFichierCSV:
    """Adaptateur : stockage dans un fichier CSV (pour les tests)."""

    def __init__(self, chemin: str):
        self.chemin = chemin
        self._data = []

    def sauvegarder(self, client: dict) -> int:
        client_id = len(self._data) + 1
        self._data.append({**client, "id": client_id})
        print(f"[CSV] Sauvegarde dans {self.chemin} : {client}")
        return client_id

    def trouver_par_id(self, client_id: int) -> dict | None:
        return next((c for c in self._data if c["id"] == client_id), None)

    def trouver_tous(self) -> list[dict]:
        return self._data


class NotificationEmail:
    """Adaptateur : notification par email."""

    def envoyer(self, destinataire: str, message: str) -> bool:
        print(f"[Email] → {destinataire} : {message}")
        return True


class NotificationConsole:
    """Adaptateur : notification en console (pour les tests)."""

    def envoyer(self, destinataire: str, message: str) -> bool:
        print(f"[Console] Notification pour {destinataire} : {message}")
        return True


# ── Utilisation : on branche les adaptateurs ──

# Production
service_prod = ServiceInscription(
    stockage=StockagePostgreSQL("postgresql://..."),
    notification=NotificationEmail(),
)

# Test / Développement
service_test = ServiceInscription(
    stockage=StockageFichierCSV("/tmp/clients.csv"),
    notification=NotificationConsole(),
)

# Le MÊME code métier, des adaptateurs DIFFÉRENTS
service_test.inscrire("Alice", "alice@example.com")
```

> 💡 **Pour le Data Engineer** : L'architecture hexagonale est très utile pour les pipelines. Le port de sortie peut être un stockage BigQuery en prod et un fichier Parquet local en test, sans changer une seule ligne de logique métier.

---

## 5. 🧹 Clean Architecture

### 5.1 Principe

La Clean Architecture (Robert C. Martin, "Uncle Bob") généralise les architectures hexagonale et en couches en cercles concentriques. La **règle de dépendance** : les dépendances pointent toujours **vers l'intérieur**.

```
┌─────────────────────────────────────────────────────┐
│                  Frameworks & Drivers                │
│  (FastAPI, SQLAlchemy, AWS SDK, Kafka, Spark)       │
│                                                      │
│   ┌─────────────────────────────────────────────┐   │
│   │            Interface Adapters                │   │
│   │  (Controllers, Gateways, Presenters)        │   │
│   │                                              │   │
│   │   ┌─────────────────────────────────────┐   │   │
│   │   │        Use Cases                     │   │   │
│   │   │  (Application Business Rules)       │   │   │
│   │   │                                      │   │   │
│   │   │   ┌─────────────────────────────┐   │   │   │
│   │   │   │        Entities              │   │   │   │
│   │   │   │  (Enterprise Business Rules) │   │   │   │
│   │   │   └─────────────────────────────┘   │   │   │
│   │   │                                      │   │   │
│   │   └─────────────────────────────────────┘   │   │
│   │                                              │   │
│   └─────────────────────────────────────────────┘   │
│                                                      │
└─────────────────────────────────────────────────────┘

          Dépendances → vers l'intérieur uniquement
```

### 5.2 Les couches de la Clean Architecture

| Couche | Contenu | Change quand... |
|--------|---------|-----------------|
| **Entities** | Objets métier, règles universelles | Les règles fondamentales changent (rare) |
| **Use Cases** | Logique d'application, orchestration | Les besoins fonctionnels changent |
| **Interface Adapters** | Conversion de données entre couches | Le format d'entrée/sortie change |
| **Frameworks** | Outils externes (BDD, web, cloud) | On change de technologie |

### 5.3 Exemple de structure pour un pipeline data

```
pipeline_ventes/
├── entities/                # Règles métier pures
│   ├── vente.py             # Entité Vente (validation, calculs)
│   └── client.py            # Entité Client
├── use_cases/               # Logique d'application
│   ├── calculer_ca.py       # Cas d'usage : calculer le CA
│   ├── detecter_fraude.py   # Cas d'usage : détecter les fraudes
│   └── generer_rapport.py   # Cas d'usage : générer un rapport
├── adapters/                # Adaptateurs d'interface
│   ├── csv_reader.py        # Lire depuis CSV
│   ├── bigquery_writer.py   # Écrire dans BigQuery
│   └── api_controller.py    # Exposer via API REST
├── frameworks/              # Configuration des outils
│   ├── spark_config.py      # Configuration Spark
│   └── database.py          # Connexion BDD
└── main.py                  # Assemblage et exécution
```

---

## 6. 🔄 Patterns architecturaux pour le Data Engineering

### 6.1 Pattern Pipeline (ETL/ELT)

```
┌─────────┐    ┌───────────┐    ┌─────────┐
│ Extract  │──→│ Transform  │──→│  Load    │
│          │    │            │    │          │
│ Sources: │    │ - Nettoyage│    │ Cibles:  │
│ - API    │    │ - Jointure │    │ - BQ     │
│ - BDD    │    │ - Agrégat. │    │ - S3     │
│ - Fichier│    │ - Enrichi. │    │ - DW     │
└─────────┘    └───────────┘    └─────────┘
```

Chaque étape est un composant **indépendant et testable** :

```python
from typing import Protocol


class Extracteur(Protocol):
    def extraire(self) -> list[dict]: ...


class Transformateur(Protocol):
    def transformer(self, donnees: list[dict]) -> list[dict]: ...


class Chargeur(Protocol):
    def charger(self, donnees: list[dict]) -> int: ...


class Pipeline:
    """Pipeline ETL composable et testable."""

    def __init__(
        self,
        extracteur: Extracteur,
        transformateurs: list[Transformateur],
        chargeur: Chargeur,
    ):
        self.extracteur = extracteur
        self.transformateurs = transformateurs
        self.chargeur = chargeur

    def executer(self) -> int:
        """Exécute le pipeline complet."""
        donnees = self.extracteur.extraire()

        for transformateur in self.transformateurs:
            donnees = transformateur.transformer(donnees)

        return self.chargeur.charger(donnees)
```

### 6.2 Pattern Medallion (Bronze / Silver / Gold)

L'architecture Medallion est un pattern en couches spécifique au data engineering :

```
┌──────────────────────────────────────────────────────────┐
│                    Data Lakehouse                         │
│                                                          │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐           │
│  │ 🥉 Bronze │──→│ 🥈 Silver │──→│ 🥇 Gold   │          │
│  │           │    │           │    │           │          │
│  │ Données   │    │ Données   │    │ Données   │          │
│  │ brutes    │    │ nettoyées │    │ agrégées  │          │
│  │           │    │ validées  │    │ prêtes BI │          │
│  │ Immutable │    │ Typées    │    │ Dénormal. │          │
│  └──────────┘    └──────────┘    └──────────┘           │
│                                                          │
│  Correspond à :  Extract      Transform      Load/Serve │
│  En MVC :        Model(raw)   Model(clean)   View(BI)   │
└──────────────────────────────────────────────────────────┘
```

> 💡 L'architecture Medallion **est** une architecture en couches appliquée aux données. Chaque couche a une responsabilité unique et ne communique qu'avec la couche adjacente.

### 6.3 Pattern Repository pour l'accès aux données

Le pattern **Repository** abstrait l'accès aux données derrière une interface uniforme :

```python
from typing import Protocol


class ClientRepository(Protocol):
    """Interface abstraite — le métier dépend de CE contrat."""

    def trouver_par_id(self, id: int) -> dict | None: ...
    def trouver_par_email(self, email: str) -> dict | None: ...
    def sauvegarder(self, client: dict) -> int: ...
    def supprimer(self, id: int) -> bool: ...


class BigQueryClientRepository:
    """Implémentation concrète pour BigQuery."""

    def __init__(self, project: str, dataset: str):
        self.table = f"{project}.{dataset}.clients"

    def trouver_par_id(self, id: int) -> dict | None:
        query = f"SELECT * FROM `{self.table}` WHERE id = @id"
        # ... exécution BigQuery
        return None

    def sauvegarder(self, client: dict) -> int:
        # ... insertion BigQuery
        return 1


class DuckDBClientRepository:
    """Implémentation pour DuckDB (développement local)."""

    def __init__(self, db_path: str):
        import duckdb
        self.conn = duckdb.connect(db_path)

    def trouver_par_id(self, id: int) -> dict | None:
        result = self.conn.execute(
            "SELECT * FROM clients WHERE id = ?", [id]
        ).fetchone()
        return dict(result) if result else None

    def sauvegarder(self, client: dict) -> int:
        self.conn.execute(
            "INSERT INTO clients (nom, email) VALUES (?, ?)",
            [client["nom"], client["email"]],
        )
        return 1
```

### 6.4 Pattern Event-Driven

L'architecture événementielle découple les producteurs des consommateurs via des événements :

```
┌──────────┐    ┌───────────────┐    ┌──────────────┐
│Producteur│──→ │  Bus d'events │──→ │Consommateur A│
│          │    │  (Kafka, etc.)│──→ │Consommateur B│
│ "Nouvelle│    │               │──→ │Consommateur C│
│  vente"  │    └───────────────┘    └──────────────┘
└──────────┘
```

```python
from typing import Callable


class BusEvenements:
    """Bus d'événements simple (pattern Observer)."""

    def __init__(self):
        self._abonnes: dict[str, list[Callable]] = {}

    def s_abonner(self, type_event: str, handler: Callable):
        """Enregistre un handler pour un type d'événement."""
        self._abonnes.setdefault(type_event, []).append(handler)

    def publier(self, type_event: str, donnees: dict):
        """Publie un événement à tous les abonnés."""
        for handler in self._abonnes.get(type_event, []):
            handler(donnees)


# Utilisation
bus = BusEvenements()

# Différents consommateurs s'abonnent
bus.s_abonner("nouvelle_vente", lambda d: print(f"[Comptabilité] Vente : {d['montant']}€"))
bus.s_abonner("nouvelle_vente", lambda d: print(f"[Stock] Mettre à jour stock produit {d['produit']}"))
bus.s_abonner("nouvelle_vente", lambda d: print(f"[Analytics] Enregistrer vente dans le DW"))

# Un producteur publie
bus.publier("nouvelle_vente", {"produit": "Widget", "montant": 49.99})
# [Comptabilité] Vente : 49.99€
# [Stock] Mettre à jour stock produit Widget
# [Analytics] Enregistrer vente dans le DW
```

> 💡 **Pour le Data Engineer** : Apache Kafka est un bus d'événements distribué. Les pipelines event-driven sont au cœur du streaming de données et du CDC (Change Data Capture).

---

## 7. 📋 Comparaison des architectures

| Architecture | Complexité | Quand l'utiliser | Exemple DE |
|-------------|-----------|------------------|------------|
| **Monolithique** | 🟢 Simple | Scripts, POC, petits projets | Script ETL one-shot |
| **3 couches** | 🟡 Modérée | Applications classiques | API + BDD + logique |
| **MVC** | 🟡 Modérée | Applications avec UI/API | Dashboard + API data |
| **Hexagonale** | 🟠 Élevée | Logique métier complexe | Pipeline multi-sources |
| **Clean** | 🔴 Haute | Gros projets, longue durée | Plateforme data complète |
| **Event-Driven** | 🟠 Élevée | Streaming, temps réel | Pipeline Kafka/CDC |
| **Medallion** | 🟡 Modérée | Data Lakehouse | Pipeline dbt/Spark |

### Choisir la bonne architecture

```
Projet simple / script ?
  └─→ OUI → Monolithique (un seul fichier, c'est OK)
  └─→ NON
        └─→ Application web classique ?
              └─→ OUI → MVC / 3 couches
              └─→ NON
                    └─→ Pipeline de données ?
                          └─→ Batch → Medallion / ETL en couches
                          └─→ Streaming → Event-Driven
                          └─→ Multi-sources complexe → Hexagonale
```

> ⚠️ **Piège classique** : Ne sur-architecturez pas ! Un script de 100 lignes n'a pas besoin de Clean Architecture. L'architecture doit être **proportionnelle** à la complexité du projet.

---

## 8. 🧠 Les principes SOLID en bref

Les principes SOLID guident les choix architecturaux. Voici un résumé appliqué au data engineering :

| Principe | Signification | Exemple DE |
|----------|--------------|------------|
| **S** — Single Responsibility | Une classe = une responsabilité | Un extracteur n'écrit pas en BDD |
| **O** — Open/Closed | Ouvert à l'extension, fermé à la modification | Ajouter un nouveau format d'extraction sans modifier l'existant |
| **L** — Liskov Substitution | Un sous-type peut remplacer son parent | Un `StockageCSV` remplace un `StockageBDD` si même interface |
| **I** — Interface Segregation | Interfaces petites et spécifiques | Séparer `Readable` et `Writable` plutôt qu'un gros `Storage` |
| **D** — Dependency Inversion | Dépendre d'abstractions, pas de concrétions | Le service dépend de `Repository` (interface), pas de `PostgreSQL` |

> 💡 Pour approfondir SOLID et voir des implémentations détaillées, consultez le cours [`Bonne pratique/01-architecture-structure.md`](../../Bonne%20pratique/01-architecture-structure.md).

---

## ✅ Checklist de validation

Avant de passer aux exercices, vérifiez que vous pouvez :

- [ ] Expliquer l'architecture en 3 couches et la règle de dépendance
- [ ] Décrire les rôles de Model, View et Controller dans le MVC
- [ ] Dessiner un schéma d'architecture hexagonale avec ports et adaptateurs
- [ ] Expliquer la règle de dépendance de la Clean Architecture
- [ ] Identifier le pattern architectural d'un pipeline de données existant
- [ ] Implémenter le pattern Repository avec `Protocol`
- [ ] Choisir la bonne architecture selon la complexité du projet
- [ ] Citer les 5 principes SOLID et donner un exemple pour chacun

---

[← Algorithmes de graphes](06-algorithmes-de-graphes.md) | [🏠 Accueil](../README.md) | [Suivant → Exercices](08-exercices.md)
