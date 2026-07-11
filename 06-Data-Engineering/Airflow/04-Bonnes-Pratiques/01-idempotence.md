# 01 — Idempotence et Sécurité des Ré-exécutions

## Qu'est-ce que l'idempotence ?

Une tâche est **idempotente** si son exécution plusieurs fois avec les mêmes paramètres produit le même résultat que si elle avait été exécutée une seule fois.

En pratique : **re-exécuter une tâche ne doit pas dupliquer les données ni produire d'effets indésirables**.

> L'idempotence est probablement le principe le plus important dans les pipelines de données. Sans elle, un retry automatique ou un rejoue manuel peut corrompre vos données.

---

## Pourquoi c'est crucial avec Airflow

Airflow re-exécute des tâches dans plusieurs situations :
- **Retry automatique** après un échec (si `retries > 0`)
- **Rejoue manuel** via "Clear" dans l'interface
- **Backfill** pour rattraper des dates passées
- **Catchup** au démarrage d'un nouveau DAG

Si vos tâches ne sont pas idempotentes → **données dupliquées**.

---

## Exemples : idempotent vs non-idempotent

### INSERT simple — non-idempotent

```python
# ❌ NON IDEMPOTENT
def charger_donnees(**context):
    hook = PostgresHook('postgres_prod')
    hook.run("""
        INSERT INTO ventes (date, montant)
        SELECT date, montant FROM staging.ventes_temp
        WHERE date = %(d)s
    """, parameters={'d': context['ds']})
# Si exécuté 2 fois le même jour → doublons !
```

### DELETE + INSERT — idempotent

```python
# ✓ IDEMPOTENT
def charger_donnees(**context):
    hook = PostgresHook('postgres_prod')
    hook.run([
        "DELETE FROM ventes WHERE date = %(d)s",
        """
        INSERT INTO ventes (date, montant)
        SELECT date, montant FROM staging.ventes_temp
        WHERE date = %(d)s
        """
    ], parameters={'d': context['ds']})
# Peut être exécuté N fois → résultat identique
```

### INSERT ON CONFLICT — idempotent

```python
# ✓ IDEMPOTENT via UPSERT
def charger_donnees(**context):
    hook = PostgresHook('postgres_prod')
    hook.run("""
        INSERT INTO ventes_journalieres (date, produit_id, total)
        SELECT
            date,
            produit_id,
            SUM(montant) as total
        FROM staging.ventes
        WHERE date = %(d)s
        GROUP BY date, produit_id
        ON CONFLICT (date, produit_id)
        DO UPDATE SET
            total = EXCLUDED.total,
            updated_at = NOW()
    """, parameters={'d': context['ds']})
```

### Fichiers — idempotent

```python
# ❌ NON IDEMPOTENT — append à un fichier existant
def exporter():
    with open('/tmp/output.csv', 'a') as f:  # mode 'a' = append
        f.write(nouvelles_donnees)

# ✓ IDEMPOTENT — écrire avec date dans le nom
def exporter(**context):
    chemin = f'/tmp/output_{context["ds_nodash"]}.csv'
    with open(chemin, 'w') as f:  # mode 'w' = overwrite
        f.write(nouvelles_donnees)

# ✓ IDEMPOTENT — écrire dans un répertoire partitionné
def exporter(**context):
    date = context['ds']
    chemin = f'/data/ventes/date={date}/data.parquet'
    df.to_parquet(chemin)  # Écrase si existe
```

---

## Idempotence dans les pipelines complets

```python
# dags/pipeline_idempotent.py

from datetime import datetime, timedelta
from airflow.decorators import dag, task

@dag(
    dag_id='pipeline_etl_idempotent',
    start_date=datetime(2024, 1, 1),
    schedule='@daily',
    catchup=True,      # Peut rattraper les dates passées en toute sécurité
    default_args={'retries': 3, 'retry_delay': timedelta(minutes=5)},
    tags=['idempotent', 'bonnes-pratiques'],
)
def pipeline_etl_idempotent():

    @task
    def extraire(**context) -> str:
        """
        IDEMPOTENT : utilise la date logique dans le nom du fichier.
        Re-exécuter écrase le fichier précédent.
        """
        import json, os
        date = context['ds']

        # Simulation d'une extraction API
        donnees = [
            {'date': date, 'id': i, 'valeur': i * 42.0}
            for i in range(100)
        ]

        # Chemin unique par date — écrase si existe déjà
        chemin = f'/tmp/extract_{context["ds_nodash"]}.json'
        with open(chemin, 'w') as f:  # 'w' = overwrite, pas append
            json.dump(donnees, f)

        print(f"Extrait et sauvegardé : {chemin}")
        return chemin

    @task
    def transformer(chemin_source: str, **context) -> str:
        """
        IDEMPOTENT : écrase le fichier de sortie si existe.
        """
        import json, os

        with open(chemin_source) as f:
            donnees = json.load(f)

        transformees = [
            {**d, 'valeur_normalisee': d['valeur'] / 100.0}
            for d in donnees
        ]

        chemin_dest = f'/tmp/transform_{context["ds_nodash"]}.json'
        with open(chemin_dest, 'w') as f:
            json.dump(transformees, f)

        return chemin_dest

    @task
    def charger_en_db(chemin: str, **context) -> int:
        """
        IDEMPOTENT via UPSERT : ON CONFLICT DO UPDATE
        ou DELETE + INSERT selon la base de données.
        """
        import json
        from airflow.providers.postgres.hooks.postgres import PostgresHook

        with open(chemin) as f:
            donnees = json.load(f)

        hook = PostgresHook('postgres_prod')
        date = context['ds']

        # Pattern DELETE + INSERT (idempotent)
        hook.run(
            "DELETE FROM resultats_journaliers WHERE date_traitement = %(d)s",
            parameters={'d': date},
        )

        rows = [(d['date'], d['id'], d['valeur'], d['valeur_normalisee']) for d in donnees]
        hook.insert_rows(
            table='resultats_journaliers',
            rows=rows,
            target_fields=['date_traitement', 'id', 'valeur', 'valeur_normalisee'],
        )

        print(f"Chargé {len(rows)} lignes pour le {date}")
        return len(rows)

    @task
    def exporter_s3(chemin: str, **context) -> str:
        """
        IDEMPOTENT : upload S3 avec replace=True
        """
        from airflow.providers.amazon.aws.hooks.s3 import S3Hook

        hook = S3Hook('aws_prod')
        date = context['ds']
        cle_s3 = f'resultats/date={date}/data.json'

        # replace=True → écrase si existe
        hook.load_file(
            filename=chemin,
            key=cle_s3,
            bucket_name='mon-data-lake',
            replace=True,   # ← Idempotent
        )

        print(f"Exporté vers s3://mon-data-lake/{cle_s3}")
        return cle_s3

    @task
    def nettoyer_temp(**context) -> None:
        """Nettoyage des fichiers temporaires."""
        import os
        date_nodash = context['ds_nodash']
        for f in [f'/tmp/extract_{date_nodash}.json', f'/tmp/transform_{date_nodash}.json']:
            if os.path.exists(f):
                os.remove(f)
                print(f"Supprimé : {f}")

    # Orchestration
    chemin_extract = extraire()
    chemin_transform = transformer(chemin_extract)
    nb_charges = charger_en_db(chemin_transform)
    cle_s3 = exporter_s3(chemin_transform)
    nettoyer_temp()

dag = pipeline_etl_idempotent()
```

---

## Le paramètre catchup

```python
# catchup=True (comportement par défaut)
# Airflow va créer des DAG Runs pour TOUTES les dates manquées
# depuis start_date jusqu'à maintenant.

# Exemple :
# start_date = 2024-01-01
# schedule = @daily
# Aujourd'hui = 2024-01-10
# → Airflow crée 9 DAG Runs (2024-01-01 à 2024-01-09)

with DAG(
    dag_id='avec_catchup',
    start_date=datetime(2024, 1, 1),
    schedule='@daily',
    catchup=True,   # Rattraper les dates manquées
    max_active_runs=3,  # Maximum 3 DAG Runs simultanés pendant le catchup
) as dag:
    pass

# catchup=False : ne créer que le run le plus récent
# → Recommandé quand le catchup n'a pas de sens
with DAG(
    dag_id='sans_catchup',
    start_date=datetime(2024, 1, 1),
    schedule='@daily',
    catchup=False,
) as dag:
    pass
```

### Configuration globale du catchup

```ini
# airflow.cfg — désactiver le catchup par défaut pour tous les DAGs
[scheduler]
catchup_by_default = False
```

---

## Backfill manuel

Le backfill permet de re-exécuter un DAG sur des dates passées, même si `catchup=False`.

```bash
# Rejouer le DAG 'etl_ventes' pour janvier 2024
airflow dags backfill \
    --start-date 2024-01-01 \
    --end-date 2024-01-31 \
    etl_ventes

# Avec parallélisme (3 DAG Runs simultanés max)
airflow dags backfill \
    --start-date 2024-01-01 \
    --end-date 2024-01-31 \
    --max-active-runs 3 \
    etl_ventes

# Simuler sans exécuter (dry run)
airflow dags backfill \
    --start-date 2024-01-01 \
    --end-date 2024-01-31 \
    --dry-run \
    etl_ventes
```

> Un backfill n'est sûr que si vos tâches sont **idempotentes**. Sans ça, vous dupliquerez les données.

---

## Gestion des re-exécutions dans l'interface

### Clear d'une tâche

1. Cliquer sur la tâche dans la vue Graph
2. Cliquer "Clear" → la tâche repasse en état `none`
3. Le Scheduler la replanifie automatiquement

### Clear d'un DAG Run entier

1. Dans la liste des DAG Runs, cliquer sur le bouton "Clear"
2. Toutes les tâches du run repassent en `none`

### Options de Clear

```
☐ Past        → Clear aussi les runs précédents
☐ Future      → Clear aussi les runs futurs
☐ Upstream    → Clear aussi les tâches en amont
☒ Downstream  → Clear aussi les tâches en aval (recommandé)
☒ Include itself → Inclure la tâche cliquée
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** L'interface Airflow — dialogue de confirmation "Clear" d'une tâche, avec les options (Past, Future, Upstream, Downstream, Include itself) cochées
> **Expliquer :** Expliquer chaque option. Cas typique : une tâche a échoué et toutes les tâches en aval ont `upstream_failed`. Cocher "Downstream" pour les rejouer toutes en chaîne. Montrer comment le DAG Run repasse de "failed" à "running" après un Clear.

---

## Checklist d'idempotence

Pour vérifier qu'une tâche est idempotente, poser ces questions :

```
□ Si j'exécute cette tâche 2 fois → même résultat qu'une fois ?
□ Mes INSERT utilisent ON CONFLICT DO UPDATE ou DELETE+INSERT ?
□ Mes fichiers de sortie sont en mode write (écrase), pas append ?
□ Je filtre sur l'execution_date dans mes requêtes SQL ?
□ Mes uploads cloud utilisent replace=True ?
□ Je partitionne mes fichiers par date ? (/date=YYYY-MM-DD/)
□ Je supprime les données du jour AVANT de les recréer ?
```

---

## max_active_runs — limiter les runs simultanés

```python
with DAG(
    dag_id='pipeline_lent',
    start_date=datetime(2024, 1, 1),
    schedule='@hourly',
    catchup=True,
    max_active_runs=1,  # Un seul run à la fois (évite les conflits DB)
) as dag:
    pass
```

```python
# Configurer au niveau global dans airflow.cfg
# [core]
# max_active_runs_per_dag = 16
```

---

## Points clés à retenir

1. **Idempotence** = re-exécuter N fois → même résultat qu'une seule fois
2. Utiliser `DELETE WHERE date = ...` + `INSERT` ou `INSERT ON CONFLICT DO UPDATE`
3. Utiliser la date logique (`ds`, `ds_nodash`) dans les noms de fichiers et les filtres SQL
4. `catchup=False` par défaut sauf si le backfill a du sens métier
5. Le **backfill** est sûr uniquement avec des tâches idempotentes
6. `max_active_runs=1` pour les pipelines qui ne peuvent pas tourner en parallèle
