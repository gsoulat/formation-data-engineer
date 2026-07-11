# 02 — Tests de DAGs

## Pourquoi tester ses DAGs ?

Sans tests, les problèmes courants ne se détectent qu'en production :
- DAG mal parsé (erreur de syntaxe Python ou de logique Airflow)
- Dépendances circulaires entre tâches
- Logique métier incorrecte dans les fonctions Python
- Régressions après un refactoring

Les tests Airflow se décomposent en trois niveaux :

| Niveau | Ce qu'on teste | Outils |
|---|---|---|
| **Validation de DAGs** | Syntax, chargement, pas de cycles | `pytest` + `DagBag` |
| **Tests unitaires** | Logique Python des callables | `pytest` + `unittest.mock` |
| **Tests d'intégration** | Exécution réelle des tâches | `pytest` + `airflow tasks test` |

---

## Structure de projet recommandée

```
airflow-projet/
├── dags/
│   ├── etl_ventes.py
│   ├── ml_pipeline.py
│   └── utils/
│       ├── __init__.py
│       ├── transformations.py
│       └── validations.py
├── tests/
│   ├── conftest.py
│   ├── test_dag_integrity.py       ← Validation de tous les DAGs
│   ├── test_etl_ventes.py          ← Tests unitaires du DAG etl_ventes
│   ├── test_ml_pipeline.py         ← Tests unitaires du DAG ml_pipeline
│   └── test_utils.py               ← Tests des utilitaires
├── pyproject.toml
└── requirements-dev.txt
```

```txt
# requirements-dev.txt
apache-airflow==2.9.0
pytest==7.4.3
pytest-mock==3.12.0
freezegun==1.4.0    # Pour mocker la date/heure
```

---

## Test 1 : Validation de l'intégrité des DAGs

```python
# tests/test_dag_integrity.py

import pytest
from airflow.models import DagBag

@pytest.fixture(scope="session")
def dagbag():
    """
    Charge tous les DAGs depuis le dossier dags/.
    Scope session = chargé une seule fois pour toute la session de tests.
    """
    return DagBag(dag_folder="dags/", include_examples=False)


class TestIntegriteDags:
    """Tests d'intégrité appliqués à TOUS les DAGs."""

    def test_pas_erreurs_import(self, dagbag):
        """Aucun DAG ne doit avoir d'erreur d'import."""
        erreurs = dagbag.import_errors
        assert not erreurs, (
            f"Erreurs d'import détectées :\n"
            + "\n".join(f"  {f}: {e}" for f, e in erreurs.items())
        )

    def test_tous_les_dags_charges(self, dagbag):
        """Au moins un DAG doit être chargé."""
        assert len(dagbag.dags) > 0, "Aucun DAG chargé — vérifier le dag_folder"

    def test_pas_de_cycle(self, dagbag):
        """Aucun DAG ne doit avoir de cycle dans ses dépendances."""
        for dag_id, dag in dagbag.dags.items():
            try:
                dag.test_cycle()
            except Exception as e:
                pytest.fail(f"Cycle détecté dans le DAG '{dag_id}': {e}")

    def test_catchup_desactive_par_defaut(self, dagbag):
        """
        Convention d'équipe : tous les DAGs doivent avoir catchup=False.
        Supprimer ce test si le catchup est voulu.
        """
        dags_avec_catchup = [
            dag_id for dag_id, dag in dagbag.dags.items()
            if dag.catchup
        ]
        assert not dags_avec_catchup, (
            f"Les DAGs suivants ont catchup=True : {dags_avec_catchup}"
        )

    def test_tags_presents(self, dagbag):
        """Convention : chaque DAG doit avoir au moins un tag."""
        dags_sans_tags = [
            dag_id for dag_id, dag in dagbag.dags.items()
            if not dag.tags
        ]
        assert not dags_sans_tags, (
            f"DAGs sans tags : {dags_sans_tags}"
        )

    def test_owner_defini(self, dagbag):
        """Convention : chaque DAG doit avoir un owner."""
        dags_sans_owner = [
            dag_id for dag_id, dag in dagbag.dags.items()
            if dag.owner == 'airflow'   # Owner par défaut = non renseigné
        ]
        assert not dags_sans_owner, (
            f"DAGs avec owner par défaut ('airflow') : {dags_sans_owner}"
        )

    def test_retries_configures(self, dagbag):
        """Convention : toutes les tâches doivent avoir des retries."""
        problemes = []
        for dag_id, dag in dagbag.dags.items():
            for task in dag.tasks:
                if task.retries == 0:
                    problemes.append(f"{dag_id}.{task.task_id}")

        assert not problemes, (
            f"Tâches sans retry configuré : {problemes}"
        )

    @pytest.mark.parametrize("dag_id", [
        "etl_ventes",
        "ml_pipeline",
        "pipeline_meteo",
    ])
    def test_dag_existe(self, dagbag, dag_id):
        """Vérifier que des DAGs spécifiques sont bien chargés."""
        assert dag_id in dagbag.dags, (
            f"DAG '{dag_id}' non trouvé dans le DagBag. "
            f"DAGs chargés : {list(dagbag.dags.keys())}"
        )
```

---

## Test 2 : Tests unitaires des callables

```python
# dags/utils/transformations.py

def nettoyer_donnees(records: list[dict]) -> list[dict]:
    """
    Nettoie une liste d'enregistrements :
    - Supprime les enregistrements avec un montant nul ou négatif
    - Normalise les noms (strip + title case)
    - Arrondit les montants à 2 décimales
    """
    nettoyees = []
    for record in records:
        if record.get('montant') is None or record['montant'] <= 0:
            continue

        nettoyees.append({
            **record,
            'nom': record.get('nom', '').strip().title(),
            'montant': round(float(record['montant']), 2),
        })
    return nettoyees


def calculer_statistiques(valeurs: list[float]) -> dict:
    """Calcule les statistiques de base d'une liste de valeurs."""
    if not valeurs:
        return {'min': None, 'max': None, 'moyenne': None, 'count': 0}

    return {
        'min': min(valeurs),
        'max': max(valeurs),
        'moyenne': sum(valeurs) / len(valeurs),
        'count': len(valeurs),
    }
```

```python
# tests/test_utils.py

import pytest
from dags.utils.transformations import nettoyer_donnees, calculer_statistiques


class TestNettoyerDonnees:

    def test_supprime_montant_nul(self):
        records = [
            {'id': 1, 'nom': 'Alice', 'montant': None},
            {'id': 2, 'nom': 'Bob',   'montant': 50.0},
        ]
        resultat = nettoyer_donnees(records)
        assert len(resultat) == 1
        assert resultat[0]['id'] == 2

    def test_supprime_montant_negatif(self):
        records = [
            {'id': 1, 'nom': 'Alice', 'montant': -10.0},
            {'id': 2, 'nom': 'Bob',   'montant': 50.0},
        ]
        resultat = nettoyer_donnees(records)
        assert len(resultat) == 1

    def test_normalise_nom(self):
        records = [{'id': 1, 'nom': '  alice dupont  ', 'montant': 42.0}]
        resultat = nettoyer_donnees(records)
        assert resultat[0]['nom'] == 'Alice Dupont'

    def test_arrondit_montant(self):
        records = [{'id': 1, 'nom': 'Test', 'montant': 42.12345}]
        resultat = nettoyer_donnees(records)
        assert resultat[0]['montant'] == 42.12

    def test_liste_vide(self):
        assert nettoyer_donnees([]) == []

    def test_tous_invalides(self):
        records = [
            {'id': 1, 'nom': 'A', 'montant': 0},
            {'id': 2, 'nom': 'B', 'montant': -5},
            {'id': 3, 'nom': 'C', 'montant': None},
        ]
        assert nettoyer_donnees(records) == []


class TestCalculerStatistiques:

    def test_valeurs_normales(self):
        stats = calculer_statistiques([10.0, 20.0, 30.0])
        assert stats['min'] == 10.0
        assert stats['max'] == 30.0
        assert stats['moyenne'] == 20.0
        assert stats['count'] == 3

    def test_valeur_unique(self):
        stats = calculer_statistiques([42.0])
        assert stats['min'] == stats['max'] == stats['moyenne'] == 42.0

    def test_liste_vide(self):
        stats = calculer_statistiques([])
        assert stats['count'] == 0
        assert stats['min'] is None
```

---

## Test 3 : Tests avec mocking des connexions

```python
# dags/etl_ventes.py (extrait)

def extraire_depuis_db(**context) -> list[dict]:
    """Extrait les ventes du jour depuis PostgreSQL."""
    from airflow.providers.postgres.hooks.postgres import PostgresHook

    hook = PostgresHook(postgres_conn_id='postgres_production')
    records = hook.get_records(
        "SELECT id, nom, montant FROM ventes WHERE date = %(d)s",
        parameters={'d': context['ds']},
    )
    return [{'id': r[0], 'nom': r[1], 'montant': r[2]} for r in records]


def envoyer_alerte(message: str, **context) -> None:
    """Envoie une alerte Slack."""
    import requests
    webhook_url = "https://hooks.slack.com/services/xxx"
    requests.post(webhook_url, json={'text': message})
```

```python
# tests/test_etl_ventes.py

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

# Importer les fonctions à tester
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'dags'))
from etl_ventes import extraire_depuis_db, envoyer_alerte


class TestExtraireDepsDB:

    @patch('etl_ventes.PostgresHook')
    def test_extraction_normale(self, mock_hook_class):
        """Teste l'extraction en mockant PostgresHook."""
        # Configurer le mock
        mock_hook = MagicMock()
        mock_hook_class.return_value = mock_hook
        mock_hook.get_records.return_value = [
            (1, 'Alice', 42.50),
            (2, 'Bob', 100.00),
        ]

        # Contexte Airflow simulé
        context = {'ds': '2024-01-15'}

        # Exécuter
        result = extraire_depuis_db(**context)

        # Vérifications
        assert len(result) == 2
        assert result[0] == {'id': 1, 'nom': 'Alice', 'montant': 42.50}
        assert result[1] == {'id': 2, 'nom': 'Bob', 'montant': 100.00}

        # Vérifier l'appel SQL
        mock_hook.get_records.assert_called_once_with(
            "SELECT id, nom, montant FROM ventes WHERE date = %(d)s",
            parameters={'d': '2024-01-15'},
        )

    @patch('etl_ventes.PostgresHook')
    def test_extraction_liste_vide(self, mock_hook_class):
        """Teste le comportement avec une liste vide."""
        mock_hook = MagicMock()
        mock_hook_class.return_value = mock_hook
        mock_hook.get_records.return_value = []

        result = extraire_depuis_db(ds='2024-01-15')
        assert result == []

    @patch('etl_ventes.PostgresHook')
    def test_extraction_erreur_connexion(self, mock_hook_class):
        """Teste le comportement en cas d'erreur de connexion."""
        mock_hook = MagicMock()
        mock_hook_class.return_value = mock_hook
        mock_hook.get_records.side_effect = Exception("Connexion refusée")

        with pytest.raises(Exception, match="Connexion refusée"):
            extraire_depuis_db(ds='2024-01-15')


class TestEnvoyerAlerte:

    @patch('etl_ventes.requests.post')
    def test_alerte_envoyee(self, mock_post):
        """Teste que la requête HTTP est bien envoyée."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        envoyer_alerte("Test alerte", ds='2024-01-15')

        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert 'Test alerte' in str(call_args)
```

---

## Test 4 : Tests avec freezegun (dates figées)

```python
# tests/test_dates.py

import pytest
from freezegun import freeze_time
from datetime import datetime

from dags.utils.transformations import generer_rapport_quotidien


class TestRapportQuotidien:

    @freeze_time("2024-01-15 08:30:00")
    def test_rapport_date_correcte(self):
        """Le rapport doit utiliser la date du jour."""
        rapport = generer_rapport_quotidien()
        assert "2024-01-15" in rapport

    @freeze_time("2024-01-15")
    def test_rapport_lundi_inclut_hebdo(self):
        """Le rapport du lundi doit inclure une section hebdomadaire."""
        rapport = generer_rapport_quotidien()
        assert "Résumé hebdomadaire" in rapport

    @freeze_time("2024-01-16")  # Mardi
    def test_rapport_hors_lundi_sans_hebdo(self):
        """Le rapport d'un autre jour ne doit pas inclure la section hebdomadaire."""
        rapport = generer_rapport_quotidien()
        assert "Résumé hebdomadaire" not in rapport
```

---

## Test 5 : conftest.py et fixtures partagées

```python
# tests/conftest.py

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from airflow.models import DagBag


@pytest.fixture(scope="session")
def dagbag():
    """DagBag partagé entre tous les tests."""
    return DagBag(dag_folder="dags/", include_examples=False)


@pytest.fixture
def contexte_airflow():
    """Contexte Airflow simulé pour les tests de callables."""
    ti = MagicMock()
    ti.xcom_pull.return_value = None

    dag = MagicMock()
    dag.dag_id = 'test_dag'

    return {
        'ds': '2024-01-15',
        'ds_nodash': '20240115',
        'ts': '2024-01-15T00:00:00+00:00',
        'logical_date': datetime(2024, 1, 15),
        'data_interval_start': datetime(2024, 1, 15),
        'data_interval_end': datetime(2024, 1, 16),
        'run_id': 'scheduled__2024-01-15T00:00:00+00:00',
        'task_instance': ti,
        'dag': dag,
        'params': {},
    }


@pytest.fixture
def mock_postgres_hook():
    """Mock de PostgresHook prêt à l'emploi."""
    with patch('airflow.providers.postgres.hooks.postgres.PostgresHook') as mock:
        hook = MagicMock()
        mock.return_value = hook
        yield hook


@pytest.fixture
def mock_s3_hook():
    """Mock de S3Hook prêt à l'emploi."""
    with patch('airflow.providers.amazon.aws.hooks.s3.S3Hook') as mock:
        hook = MagicMock()
        mock.return_value = hook
        yield hook
```

---

## Utiliser les fixtures dans les tests

```python
# tests/test_avec_fixtures.py

def test_extraction_avec_fixture(contexte_airflow, mock_postgres_hook):
    """Test utilisant les fixtures partagées."""
    mock_postgres_hook.get_records.return_value = [
        (1, 'Test', 99.99)
    ]

    from dags.etl_ventes import extraire_depuis_db
    result = extraire_depuis_db(**contexte_airflow)

    assert len(result) == 1
    assert result[0]['montant'] == 99.99
```

---

## Exécution des tests

```bash
# Lancer tous les tests
pytest tests/ -v

# Tests avec couverture de code
pip install pytest-cov
pytest tests/ -v --cov=dags --cov-report=html

# Lancer uniquement les tests d'intégrité des DAGs
pytest tests/test_dag_integrity.py -v

# Lancer les tests d'un DAG spécifique
pytest tests/test_etl_ventes.py -v

# Mode watch (relancer à chaque modification)
pip install pytest-watch
ptw tests/

# Test rapide d'un DAG via CLI (sans la suite de tests)
airflow dags test etl_ventes 2024-01-15
airflow tasks test etl_ventes extraire 2024-01-15
```

---

## Intégration CI/CD (GitHub Actions)

```yaml
# .github/workflows/test-dags.yml
name: Test DAGs Airflow

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: airflow
          POSTGRES_PASSWORD: airflow
          POSTGRES_DB: airflow
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install apache-airflow==2.9.0 \
            --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.9.0/constraints-3.11.txt"
          pip install pytest pytest-mock freezegun pytest-cov

      - name: Initialize Airflow DB
        env:
          AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@localhost/airflow
          AIRFLOW__CORE__LOAD_EXAMPLES: 'false'
        run: airflow db init

      - name: Run tests
        env:
          AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@localhost/airflow
          AIRFLOW__CORE__LOAD_EXAMPLES: 'false'
          AIRFLOW__CORE__UNIT_TEST_MODE: 'true'
        run: |
          pytest tests/ -v --cov=dags --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

---

## Points clés à retenir

1. **Toujours tester** l'intégrité des DAGs avec `DagBag` — détecte les erreurs avant la prod
2. Séparer la **logique métier** des opérateurs Airflow pour faciliter les tests unitaires
3. Utiliser `unittest.mock.patch` pour mocker les Hooks (PostgreSQL, S3, HTTP...)
4. Les **fixtures pytest** (`conftest.py`) évitent la duplication dans les tests
5. Intégrer les tests dans la **CI/CD** — aucun DAG ne devrait atteindre la production sans passer les tests
6. `airflow tasks test <dag_id> <task_id> <date>` pour tester rapidement une tâche en CLI
