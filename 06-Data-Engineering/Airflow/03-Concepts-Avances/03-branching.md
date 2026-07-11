# 03 — Branchement et Workflows Conditionnels

## Pourquoi le branchement ?

Dans un pipeline de données, certaines tâches ne doivent s'exécuter que sous certaines conditions :
- Traitement différent selon le jour de la semaine
- Chemin de traitement différent selon le type de fichier reçu
- Alertes conditionnelles selon les métriques calculées
- Environnement (dev/staging/prod) qui détermine la destination

Airflow propose plusieurs mécanismes de branchement :

| Mécanisme | Usage |
|---|---|
| `BranchPythonOperator` | Branchement basé sur une fonction Python |
| `@task.branch` | Idem, style TaskFlow |
| `ShortCircuitOperator` | Court-circuitage complet en aval |
| `BranchDayOfWeekOperator` | Branchement selon le jour de la semaine |
| `BranchDateTimeOperator` | Branchement selon la plage horaire |

---

## BranchPythonOperator

La fonction Python doit **retourner un `task_id`** (ou une liste de `task_ids`) à exécuter. Toutes les autres branches sont marquées `skipped`.

### Exemple simple

```python
from airflow import DAG
from airflow.operators.python import BranchPythonOperator, PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime

def choisir_traitement(**context) -> str:
    """
    Retourne l'identifiant de la tâche à exécuter.
    """
    # Récupérer le jour de la semaine (0=lundi, 6=dimanche)
    jour = context['logical_date'].weekday()

    if jour == 0:   # Lundi
        return 'traitement_hebdomadaire'
    elif jour == 6:  # Dimanche
        return 'traitement_weekend'
    else:
        return 'traitement_quotidien'

with DAG(
    dag_id='branchement_simple',
    start_date=datetime(2024, 1, 1),
    schedule='@daily',
    catchup=False,
) as dag:

    choisir = BranchPythonOperator(
        task_id='choisir_traitement',
        python_callable=choisir_traitement,
    )

    traitement_hebdo = BashOperator(
        task_id='traitement_hebdomadaire',
        bash_command='echo "Traitement hebdomadaire du lundi"',
    )

    traitement_weekend = BashOperator(
        task_id='traitement_weekend',
        bash_command='echo "Traitement du dimanche"',
    )

    traitement_quotidien = BashOperator(
        task_id='traitement_quotidien',
        bash_command='echo "Traitement quotidien standard"',
    )

    # La tâche finale doit avoir trigger_rule='none_failed_min_one_success'
    # pour s'exécuter même si certaines branches sont skippées
    notification = BashOperator(
        task_id='notification',
        bash_command='echo "Pipeline terminé"',
        trigger_rule='none_failed_min_one_success',
    )

    choisir >> [traitement_hebdo, traitement_weekend, traitement_quotidien]
    [traitement_hebdo, traitement_weekend, traitement_quotidien] >> notification
```

---

## Les trigger_rule — règles de déclenchement

Par défaut, une tâche attend que **toutes** ses tâches parentes soient en succès. Mais avec le branchement, certaines tâches parents sont `skipped`. Il faut changer la règle.

```python
from airflow.utils.trigger_rule import TriggerRule

tache_finale = PythonOperator(
    task_id='finalisation',
    python_callable=finaliser,
    trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS,
    # ↑ S'exécute si au moins une tâche parente a réussi et aucune n'a échoué
)
```

### Toutes les trigger_rule

| Rule | Déclenchement |
|---|---|
| `ALL_SUCCESS` | Toutes les tâches parentes en succès **(défaut)** |
| `ALL_FAILED` | Toutes les tâches parentes en échec |
| `ALL_DONE` | Toutes les tâches parentes terminées (quel que soit l'état) |
| `ALL_SKIPPED` | Toutes les tâches parentes en `skipped` |
| `ONE_SUCCESS` | Au moins une tâche parente en succès |
| `ONE_FAILED` | Au moins une tâche parente en échec |
| `ONE_DONE` | Au moins une tâche parente terminée |
| `NONE_FAILED` | Aucune tâche parente en échec (succès + skipped OK) |
| `NONE_FAILED_MIN_ONE_SUCCESS` | Aucun échec ET au moins un succès **(recommandé après branchement)** |
| `NONE_SKIPPED` | Aucune tâche parente skippée |
| `ALWAYS` | Toujours s'exécuter |

---

## @task.branch — TaskFlow API

```python
from airflow.decorators import dag, task
from datetime import datetime

@dag(
    dag_id='branchement_taskflow',
    start_date=datetime(2024, 1, 1),
    schedule='@daily',
    catchup=False,
)
def branchement_taskflow():

    @task
    def analyser_donnees() -> dict:
        import random
        nb_erreurs = random.randint(0, 50)
        total = 1000
        return {'nb_erreurs': nb_erreurs, 'total': total, 'taux_erreur': nb_erreurs / total}

    @task.branch
    def router_selon_qualite(analyse: dict) -> str:
        """
        Retourne le task_id de la branche à exécuter.
        Peut aussi retourner une liste de task_ids pour branches parallèles.
        """
        taux = analyse['taux_erreur']

        if taux > 0.10:   # Plus de 10% d'erreurs
            return 'alerter_equipe_data'
        elif taux > 0.02:  # Entre 2% et 10%
            return 'corriger_automatiquement'
        else:
            return 'charger_directement'

    @task
    def alerter_equipe_data(analyse: dict):
        print(f"ALERTE : taux d'erreur = {analyse['taux_erreur']:.1%}")
        print("Email d'alerte envoyé à data-team@company.com")

    @task
    def corriger_automatiquement(analyse: dict):
        print(f"Correction automatique de {analyse['nb_erreurs']} erreurs")
        # ... logique de correction ...

    @task
    def charger_directement(analyse: dict):
        print(f"Chargement direct : {analyse['total']} lignes")

    @task(trigger_rule='none_failed_min_one_success')
    def finaliser():
        print("Pipeline terminé avec succès")

    # Orchestration
    analyse = analyser_donnees()
    branche = router_selon_qualite(analyse)

    alerte = alerter_equipe_data(analyse)
    correction = corriger_automatiquement(analyse)
    chargement = charger_directement(analyse)

    branche >> [alerte, correction, chargement]
    [alerte, correction, chargement] >> finaliser()

dag = branchement_taskflow()
```

---

## Branchement vers plusieurs branches

```python
@task.branch
def choisir_destinations(config: dict) -> list[str]:
    """
    Peut retourner plusieurs task_ids pour déclencher plusieurs branches en parallèle.
    """
    destinations = []

    if config['activer_postgres']:
        destinations.append('charger_postgres')
    if config['activer_s3']:
        destinations.append('exporter_s3')
    if config['activer_email']:
        destinations.append('envoyer_email_rapport')

    if not destinations:
        return 'log_aucune_destination'

    return destinations  # ← Liste de task_ids
```

---

## DAG complet : pipeline conditionnel selon la qualité des données

```python
# dags/pipeline_qualite_conditionnel.py

from datetime import datetime, timedelta
from airflow.decorators import dag, task
from airflow.operators.bash import BashOperator
from airflow.utils.trigger_rule import TriggerRule

@dag(
    dag_id='pipeline_qualite_conditionnel',
    start_date=datetime(2024, 1, 1),
    schedule='@daily',
    catchup=False,
    default_args={'retries': 1, 'retry_delay': timedelta(minutes=5)},
    tags=['branchement', 'qualite', 'conditionnel'],
)
def pipeline_qualite_conditionnel():
    """
    Pipeline qui adapte son comportement selon la qualité des données :
    - Qualité bonne (< 1% d'erreurs)  → chargement direct
    - Qualité moyenne (1-5%)          → nettoyage puis chargement
    - Qualité mauvaise (> 5%)         → rejet et alerte
    """

    @task
    def extraire() -> dict:
        """Simule une extraction depuis une API."""
        import random

        lignes = [
            {'id': i, 'valeur': random.uniform(0, 1000) if random.random() > 0.03 else None}
            for i in range(1000)
        ]

        chemin = '/tmp/donnees_brutes.json'
        import json
        with open(chemin, 'w') as f:
            json.dump(lignes, f)

        return {'chemin': chemin, 'total': len(lignes)}

    @task
    def analyser_qualite(extraction: dict) -> dict:
        """Calcule les métriques de qualité des données."""
        import json

        with open(extraction['chemin']) as f:
            donnees = json.load(f)

        nb_total = len(donnees)
        nb_nulls = sum(1 for d in donnees if d.get('valeur') is None)
        nb_valides = nb_total - nb_nulls
        taux_erreur = nb_nulls / nb_total if nb_total > 0 else 0

        metriques = {
            'nb_total': nb_total,
            'nb_nulls': nb_nulls,
            'nb_valides': nb_valides,
            'taux_erreur': taux_erreur,
            'qualite': (
                'bonne' if taux_erreur < 0.01 else
                'moyenne' if taux_erreur < 0.05 else
                'mauvaise'
            ),
            'chemin': extraction['chemin'],
        }

        print(f"Qualité : {metriques['qualite']} "
              f"({nb_nulls}/{nb_total} erreurs = {taux_erreur:.1%})")
        return metriques

    @task.branch
    def router(metriques: dict) -> str:
        qualite = metriques['qualite']
        routes = {
            'bonne': 'chargement_direct',
            'moyenne': 'nettoyage_donnees',
            'mauvaise': 'rejeter_et_alerter',
        }
        tache_cible = routes[qualite]
        print(f"Routage vers : {tache_cible} (qualité={qualite})")
        return tache_cible

    @task
    def chargement_direct(metriques: dict):
        """Charge les données directement — qualité bonne."""
        import json
        with open(metriques['chemin']) as f:
            donnees = json.load(f)

        valides = [d for d in donnees if d.get('valeur') is not None]
        print(f"Chargement direct : {len(valides)} lignes")
        return {'lignes_chargees': len(valides), 'mode': 'direct'}

    @task
    def nettoyage_donnees(metriques: dict):
        """Nettoie les données avant chargement — qualité moyenne."""
        import json
        with open(metriques['chemin']) as f:
            donnees = json.load(f)

        # Imputation par la médiane
        valeurs_valides = [d['valeur'] for d in donnees if d.get('valeur') is not None]
        mediane = sorted(valeurs_valides)[len(valeurs_valides) // 2]

        donnees_nettoyees = []
        for d in donnees:
            d_copie = d.copy()
            if d_copie.get('valeur') is None:
                d_copie['valeur'] = mediane  # Imputation
                d_copie['impute'] = True
            donnees_nettoyees.append(d_copie)

        chemin_nettoye = '/tmp/donnees_nettoyees.json'
        with open(chemin_nettoye, 'w') as f:
            json.dump(donnees_nettoyees, f)

        print(f"Nettoyage : {metriques['nb_nulls']} valeurs imputées avec {mediane:.2f}")
        return {'lignes_chargees': len(donnees_nettoyees), 'mode': 'nettoye'}

    @task
    def rejeter_et_alerter(metriques: dict):
        """Rejette le batch et alerte — qualité mauvaise."""
        message = (
            f"ALERTE QUALITÉ DONNÉES\n"
            f"Taux d'erreur : {metriques['taux_erreur']:.1%}\n"
            f"Seuil : 5%\n"
            f"Lignes invalides : {metriques['nb_nulls']}/{metriques['nb_total']}\n"
            f"Action : batch REJETÉ"
        )
        print(message)
        # En production : envoyer un email, une alerte Slack, PagerDuty, etc.
        raise ValueError("Qualité des données insuffisante — batch rejeté")

    @task(trigger_rule='none_failed_min_one_success')
    def audit_et_fin(metriques: dict):
        """Tâche finale d'audit — s'exécute quelle que soit la branche."""
        print(f"Audit final :")
        print(f"  Qualité : {metriques['qualite']}")
        print(f"  Total lignes : {metriques['nb_total']}")
        print(f"  Taux erreur : {metriques['taux_erreur']:.2%}")

    # Orchestration
    extraction = extraire()
    metriques = analyser_qualite(extraction)
    branche = router(metriques)

    direct = chargement_direct(metriques)
    nettoye = nettoyage_donnees(metriques)
    rejet = rejeter_et_alerter(metriques)

    branche >> [direct, nettoye, rejet]
    [direct, nettoye, rejet] >> audit_et_fin(metriques)

dag = pipeline_qualite_conditionnel()
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** La vue Graph d'un DAG avec branchement après exécution — montrer les tâches en vert (branche exécutée) et en rose/gris (branches skippées)
> **Expliquer :** Pointer les tâches skippées et expliquer pourquoi elles sont en rose (skipped) et non en rouge (failed). Montrer dans les logs de `BranchPythonOperator` / `@task.branch` le message indiquant quelle branche a été choisie. Expliquer l'importance de `trigger_rule='none_failed_min_one_success'` sur la tâche finale.

---

## BranchDayOfWeekOperator

```python
from airflow.operators.weekday import BranchDayOfWeekOperator
from airflow.utils.weekday import WeekDay

choisir_par_jour = BranchDayOfWeekOperator(
    task_id='choisir_par_jour',
    follow_task_ids_if_true=['traitement_semaine'],
    follow_task_ids_if_false=['traitement_weekend'],
    week_day={WeekDay.MONDAY, WeekDay.TUESDAY, WeekDay.WEDNESDAY,
              WeekDay.THURSDAY, WeekDay.FRIDAY},
    use_task_logical_date=True,
)
```

## BranchDateTimeOperator

```python
from airflow.operators.datetime import BranchDateTimeOperator
from pendulum import time as ptime

# Choisir selon l'heure du jour
choisir_par_heure = BranchDateTimeOperator(
    task_id='choisir_par_heure',
    follow_task_ids_if_true=['traitement_heure_creuse'],
    follow_task_ids_if_false=['traitement_heure_pointe'],
    target_lower=ptime(0, 0, 0),    # 00:00:00
    target_upper=ptime(6, 0, 0),    # 06:00:00
    # → traitement_heure_creuse entre minuit et 6h
)
```

---

## Patterns avancés

### Branchement imbriqué

```python
@dag(start_date=datetime(2024,1,1), schedule='@daily', catchup=False)
def branchement_imbrique():

    @task
    def extraire() -> dict:
        return {'type': 'json', 'taille': 'large', 'source': 'api'}

    @task.branch
    def router_type(data: dict) -> str:
        return 'traiter_json' if data['type'] == 'json' else 'traiter_csv'

    @task.branch
    def router_taille(data: dict) -> str:
        return 'batch_large' if data['taille'] == 'large' else 'batch_small'

    @task
    def traiter_json(data: dict):
        print("Traitement JSON")

    @task
    def traiter_csv(data: dict):
        print("Traitement CSV")

    @task
    def batch_large(data: dict):
        print("Batch large : traitement par chunks")

    @task
    def batch_small(data: dict):
        print("Batch small : traitement direct")

    @task(trigger_rule='none_failed_min_one_success')
    def finaliser():
        print("Terminé")

    data = extraire()
    route_type = router_type(data)
    json_task = traiter_json(data)
    csv_task = traiter_csv(data)

    route_taille = router_taille(data)
    large = batch_large(data)
    small = batch_small(data)

    route_type >> [json_task, csv_task]
    route_taille >> [large, small]
    [json_task, csv_task, large, small] >> finaliser()

dag = branchement_imbrique()
```

---

## Points clés à retenir

1. `BranchPythonOperator` / `@task.branch` : retourner un `task_id` ou une liste de `task_ids`
2. Les branches non sélectionnées sont marquées **`skipped`** (pas `failed`)
3. Toujours utiliser `trigger_rule='none_failed_min_one_success'` sur les tâches après un branchement
4. `ShortCircuitOperator` pour annuler tout le pipeline en aval
5. Le branchement est transparent dans la vue Graph — couleurs : vert=succès, rose=skipped
