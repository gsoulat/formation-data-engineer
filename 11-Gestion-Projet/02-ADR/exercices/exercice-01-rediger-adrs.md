# Exercice 01 — Rédiger des ADRs pour un projet data engineering

## Contexte du projet

Vous rejoignez l'équipe technique de **MétéoData SAS**, une startup qui collecte des données météorologiques depuis 200 stations IoT réparties en France, les enrichit avec des données open data (Météo-France, Copernicus) et les expose à des clients professionnels via une API.

### Architecture actuelle (à remettre en question)

- **Collecte** : Scripts Python cron jobs sur des VMs
- **Stockage** : Fichiers CSV stockés sur un NAS partagé
- **Base de données** : MySQL 5.7 sur une VM dédiée
- **API** : Flask non documentée, sans validation de données
- **Visualisation** : Google Sheets mis à jour manuellement
- **Déploiement** : FTP vers les serveurs de production

### Problèmes actuels signalés

1. Les données IoT arrivent parfois avec 2-3 heures de délai à cause des cron jobs
2. Les CSV ne versionnent pas les schémas — des colonnes ont changé sans qu'on le sache
3. L'API Flask plante régulièrement sous charge (>50 req/s)
4. Impossible de rejouer les données d'une station si elle avait un problème
5. L'équipe data science ne peut pas accéder aux données brutes sans passer par l'IT
6. Aucune documentation de l'API pour les clients

### Objectifs de la refonte

- Ingestion temps quasi-réel des capteurs IoT (latence < 2 min)
- Stockage scalable des données historiques (7 ans, ~500 GB actuellement)
- API documentée, validée, performante
- Accès self-service pour l'équipe data science
- Infrastructure reproductible (fini le "ça marche sur le serveur de Jean-Michel")

---

## Mission

Rédigez **3 ADRs** pour les décisions d'architecture de la refonte.

---

## ADR à rédiger

### ADR 1 — Choix du broker de messages pour l'ingestion IoT

Les capteurs IoT envoient des données toutes les minutes. Il faut décider comment ingérer ces données de façon fiable et scalable.

**Informations supplémentaires pour guider votre réflexion :**
- 200 stations, chacune envoyant 5 métriques toutes les minutes
- Volume : ~1000 messages/minute, ~1.5M messages/jour
- Certaines stations peuvent être hors ligne pendant 24h (réseau rural)
- L'équipe data science veut consommer les données en temps réel
- L'équipe backend veut les stocker dans le Data Warehouse
- 2 consommateurs différents = 2 consumer groups indépendants
- Budget infra : < 200€/mois pour le broker

**Options à évaluer :**
- Apache Kafka (auto-hébergé ou Confluent Cloud)
- MQTT + Eclipse Mosquitto
- AWS IoT Core (ou équivalent cloud)
- Redis Streams

**Questions guides :**
- Que se passe-t-il si une station est hors ligne 24h puis rétablit la connexion ?
- Comment chaque option gère-t-elle les 2 consommateurs indépendants ?
- Laquelle garantit qu'aucun message n'est perdu ?

---

### ADR 2 — Choix du format de stockage des données historiques

Les 500 GB de données historiques CSV doivent être migrés vers un format adapté à l'analytique. Le format influencera les performances des requêtes data science et le coût de stockage.

**Informations supplémentaires :**
- Données très structurées (timestamp, station_id, température, humidité, pression, vent)
- 99% des requêtes sont du type : "Donne-moi les données de la station X entre t1 et t2"
- Requêtes analytiques : moyennes mobiles, agrégations horaires/journalières
- Accès via Python (pandas, polars) et SQL (DuckDB, Spark)
- Stockage cloud objet (S3 ou équivalent)
- Équipe data science préfère travailler avec des outils Python standard

**Options à évaluer :**
- CSV (conserver l'existant)
- Parquet (Apache)
- Delta Lake
- Apache Iceberg

**Questions guides :**
- Quel format permet les meilleures performances de lecture pour des filtres par date et par station ?
- Quel format gère le mieux les évolutions de schéma (ajout d'une nouvelle métrique) ?
- Quel format est le plus accessible pour l'équipe data science avec pandas/polars ?

---

### ADR 3 — Remplacement de Flask par un framework API moderne

L'API Flask actuelle est instable sous charge et non documentée. Il faut choisir un framework moderne pour la réécrire.

**Informations supplémentaires :**
- ~200 clients API en production (entreprises météo, agriculture, assurance)
- Charge actuelle : 100 req/s, objectif : 500 req/s
- L'API expose des données JSON (séries temporelles, agrégations)
- Les clients demandent une documentation Swagger/OpenAPI
- L'équipe est composée de 3 data engineers Python, 0 développeur backend dédié
- Contrainte : la réécriture doit être progressive (pas de big bang)

**Options à évaluer :**
- FastAPI
- Flask + Blueprint restructuré (amélioration de l'existant)
- Django REST Framework
- Litestar (anciennement Starlette)

**Questions guides :**
- Quelle option génère de la documentation OpenAPI automatiquement ?
- Laquelle permet une migration progressive depuis Flask ?
- Quelle est la courbe d'apprentissage pour des data engineers Python ?

---

## Instructions de rédaction

### Format requis

Utiliser le **template MADR** (`templates/template-madr.md`) pour les 3 ADRs.

Nommer les fichiers :
- `0001-choix-broker-messages-iot.md`
- `0002-format-stockage-donnees-historiques.md`
- `0003-remplacement-api-flask.md`

### Critères de qualité

Chaque ADR sera évalué sur :

| Critère | Barème |
|---------|--------|
| Contexte clair et quantifié | 3 pts |
| Facteurs de décision pertinents (min. 4) | 3 pts |
| Au moins 3 options évaluées | 2 pts |
| Avantages/inconvénients en lien avec les facteurs | 4 pts |
| Décision clairement justifiée | 3 pts |
| Conséquences honnêtes (positives ET négatives) | 3 pts |
| Qualité de rédaction et concision | 2 pts |
| **Total par ADR** | **20 pts** |

---

## Bonus — Intégration GitHub (si le temps le permet)

1. Créer un dépôt GitHub fictif `meteosdata-platform`
2. Placer les 3 ADRs dans `docs/adr/`
3. Ouvrir une Pull Request pour l'ADR-0001 en statut "Proposed"
4. Inviter un camarade à reviewer et ajouter des commentaires

---

## Ressources

- Templates disponibles dans `../templates/`
- Exemples dans `../03-exemples-adr.md`
- [MADR Reference](https://adr.github.io/madr/)
- [ADR Tools CLI](https://github.com/npryce/adr-tools)
- [Exemples ADRs publics sur GitHub](https://github.com/joelparkerhenderson/architecture-decision-record/tree/main/locales/fr)
