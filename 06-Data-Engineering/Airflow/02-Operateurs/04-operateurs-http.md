# 04 — Opérateurs HTTP

## Vue d'ensemble

Les opérateurs HTTP permettent d'appeler des APIs REST, d'envoyer des webhooks, ou d'interroger des services web. Ils nécessitent le provider HTTP :

```bash
pip install apache-airflow-providers-http
```

---

## Configurer une connexion HTTP

```python
# Via CLI
airflow connections add 'api_meteo' \
    --conn-type 'http' \
    --conn-host 'api.open-meteo.com' \
    --conn-schema 'https' \
    --conn-port '443'

# Avec authentification Basic
airflow connections add 'api_interne' \
    --conn-type 'http' \
    --conn-host 'api.monentreprise.fr' \
    --conn-schema 'https' \
    --conn-login 'user' \
    --conn-password 'secret'

# Avec token Bearer (dans les extras)
airflow connections add 'api_avec_token' \
    --conn-type 'http' \
    --conn-host 'api.example.com' \
    --conn-schema 'https' \
    --conn-extra '{"Authorization": "Bearer mon_token_secret"}'
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** L'interface Airflow → Admin → Connections — formulaire de création d'une connexion HTTP avec les champs Schema (https), Host, et Extra (JSON avec Authorization)
> **Expliquer :** Insister sur le champ "Extra" en JSON qui permet de passer des headers HTTP supplémentaires (Authorization, Content-Type, etc.). Montrer qu'on ne voit jamais le mot de passe en clair dans l'UI (il est masqué) et expliquer pourquoi c'est important pour la sécurité.

---

## SimpleHttpOperator

Effectue une requête HTTP simple (GET, POST, PUT, DELETE...).

```python
from airflow.providers.http.operators.http import SimpleHttpOperator

# GET simple
appeler_api = SimpleHttpOperator(
    task_id='appeler_api_meteo',
    http_conn_id='api_meteo',
    endpoint='/v1/forecast',
    method='GET',
    data={               # Query parameters pour GET
        'latitude': '48.8566',
        'longitude': '2.3522',
        'daily': 'temperature_2m_max,precipitation_sum',
        'start_date': '{{ ds }}',
        'end_date': '{{ ds }}',
        'timezone': 'Europe/Paris',
    },
    headers={'Accept': 'application/json'},
    # Réponse disponible en XCom
    do_xcom_push=True,
    # Vérifier le code HTTP de retour (200 par défaut)
    response_check=lambda response: response.status_code == 200,
    log_response=True,   # Logger la réponse dans les logs Airflow
)
```

### POST avec un corps JSON

```python
from airflow.providers.http.operators.http import SimpleHttpOperator
import json

# POST avec corps JSON
envoyer_rapport = SimpleHttpOperator(
    task_id='envoyer_rapport_slack',
    http_conn_id='slack_webhook',
    endpoint='/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX',
    method='POST',
    data=json.dumps({
        'text': 'Pipeline ETL terminé ✓',
        'attachments': [{
            'color': 'good',
            'fields': [
                {'title': 'DAG', 'value': '{{ dag.dag_id }}', 'short': True},
                {'title': 'Date', 'value': '{{ ds }}', 'short': True},
            ]
        }]
    }),
    headers={'Content-Type': 'application/json'},
    response_check=lambda response: response.status_code == 200,
)
```

### Vérifier la réponse avec une fonction

```python
def verifier_reponse_api(response, **context) -> bool:
    """
    Fonction de validation de la réponse HTTP.
    Retourne True si la réponse est valide, lève une exception sinon.
    """
    if response.status_code != 200:
        raise ValueError(f"Code HTTP inattendu: {response.status_code}")

    data = response.json()

    # Vérifier que la réponse contient les données attendues
    if 'daily' not in data:
        raise ValueError("Champ 'daily' manquant dans la réponse")

    nb_jours = len(data['daily'].get('time', []))
    if nb_jours == 0:
        raise ValueError("Aucune donnée journalière dans la réponse")

    print(f"Réponse valide : {nb_jours} jours de données")
    return True

appeler_api = SimpleHttpOperator(
    task_id='appeler_api_avec_validation',
    http_conn_id='api_meteo',
    endpoint='/v1/forecast',
    method='GET',
    data={'latitude': '48.8566', 'longitude': '2.3522', 'current_weather': 'true'},
    response_check=verifier_reponse_api,
    do_xcom_push=True,
)
```

---

## HttpSensor — attendre qu'un endpoint soit disponible

```python
from airflow.providers.http.sensors.http import HttpSensor

# Attendre que l'API soit disponible avant de l'appeler
attendre_api = HttpSensor(
    task_id='attendre_api_disponible',
    http_conn_id='api_partenaire',
    endpoint='/health',
    method='GET',
    # La tâche attend que response_check retourne True
    response_check=lambda response: response.status_code == 200,
    poke_interval=30,    # Tester toutes les 30 secondes
    timeout=300,         # Timeout après 5 minutes
    mode='reschedule',
)

# Attendre qu'un rapport soit généré sur une API
attendre_rapport = HttpSensor(
    task_id='attendre_rapport_pret',
    http_conn_id='api_reporting',
    endpoint='/api/rapports/{{ ds }}/status',
    method='GET',
    response_check=lambda response: response.json().get('statut') == 'ready',
    poke_interval=60,
    timeout=3600,
    mode='reschedule',
    soft_fail=True,   # Passer en "skipped" si timeout au lieu d'"échec"
)
```

---

## Utiliser le HttpHook directement

```python
from airflow.providers.http.hooks.http import HttpHook
from airflow.operators.python import PythonOperator

def appeler_api_complexe(**context):
    """
    Utiliser le HttpHook pour des scénarios complexes :
    - Pagination
    - Authentification OAuth
    - Retry avec backoff personnalisé
    """
    hook = HttpHook(method='GET', http_conn_id='api_donnees')

    # ---- Pagination ----
    tous_les_enregistrements = []
    page = 1

    while True:
        response = hook.run(
            endpoint='/api/v1/ventes',
            data={
                'date': context['ds'],
                'page': page,
                'per_page': 100,
            },
            headers={'Accept': 'application/json'},
        )

        data = response.json()
        enregistrements = data.get('data', [])

        if not enregistrements:
            break

        tous_les_enregistrements.extend(enregistrements)
        print(f"Page {page} : {len(enregistrements)} enregistrements récupérés")

        # Vérifier s'il y a une prochaine page
        if not data.get('has_next_page', False):
            break

        page += 1

    print(f"Total : {len(tous_les_enregistrements)} enregistrements sur {page} pages")
    return len(tous_les_enregistrements)

appeler_api_paginee = PythonOperator(
    task_id='appeler_api_paginee',
    python_callable=appeler_api_complexe,
)
```

---

## Traiter la réponse HTTP dans une tâche suivante

```python
from airflow.operators.python import PythonOperator

def traiter_reponse_api(**context):
    """
    Récupérer la réponse HTTP depuis XCom et la traiter.
    """
    import json, pandas as pd

    # Récupérer la réponse JSON depuis XCom (poussée par SimpleHttpOperator)
    ti = context['task_instance']
    reponse_brute = ti.xcom_pull(task_ids='appeler_api_meteo')

    # La réponse est une chaîne JSON
    data = json.loads(reponse_brute)

    # Transformer
    daily = data.get('daily', {})
    df = pd.DataFrame({
        'date': daily.get('time', []),
        'temp_max': daily.get('temperature_2m_max', []),
        'precipitation': daily.get('precipitation_sum', []),
    })

    print(f"Données météo pour le {context['ds']}:")
    print(df.to_string(index=False))

    output_path = f'/tmp/meteo_{context["ds_nodash"]}.csv'
    df.to_csv(output_path, index=False)
    return output_path

traiter_reponse = PythonOperator(
    task_id='traiter_reponse_api',
    python_callable=traiter_reponse_api,
)
```

---

## DAG complet : extraction depuis une API REST paginée

```python
# dags/pipeline_api_rest.py

from datetime import datetime, timedelta
import json

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.http.operators.http import SimpleHttpOperator

default_args = {
    'owner': 'data-team',
    'retries': 3,
    'retry_delay': timedelta(minutes=2),
}

with DAG(
    dag_id='pipeline_api_rest',
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule='@daily',
    catchup=False,
    tags=['api', 'http', 'etl'],
) as dag:

    # 1. Vérifier que l'API est disponible
    verifier_api = HttpSensor(
        task_id='verifier_api_disponible',
        http_conn_id='api_externe',
        endpoint='/health',
        response_check=lambda r: r.status_code == 200 and r.json().get('status') == 'ok',
        poke_interval=30,
        timeout=300,
        mode='reschedule',
    )

    # 2. Récupérer le token d'authentification
    def obtenir_token(**context):
        from airflow.providers.http.hooks.http import HttpHook

        hook = HttpHook(method='POST', http_conn_id='api_externe')
        response = hook.run(
            endpoint='/auth/token',
            data=json.dumps({
                'client_id': 'mon_client_id',
                'client_secret': 'mon_client_secret',  # En pratique : Variable Airflow
                'grant_type': 'client_credentials',
            }),
            headers={'Content-Type': 'application/json'},
        )
        token_data = response.json()
        return token_data['access_token']

    obtenir_token_task = PythonOperator(
        task_id='obtenir_token',
        python_callable=obtenir_token,
    )

    # 3. Extraire les données avec pagination
    def extraire_avec_pagination(**context):
        from airflow.providers.http.hooks.http import HttpHook

        ti = context['task_instance']
        token = ti.xcom_pull(task_ids='obtenir_token')
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json',
        }

        hook = HttpHook(method='GET', http_conn_id='api_externe')
        tous_les_enregistrements = []
        curseur = None

        while True:
            params = {
                'date': context['ds'],
                'limit': 500,
            }
            if curseur:
                params['cursor'] = curseur

            response = hook.run(
                endpoint='/api/v2/transactions',
                data=params,
                headers=headers,
            )
            data = response.json()

            enregistrements = data.get('items', [])
            tous_les_enregistrements.extend(enregistrements)
            print(f"Batch récupéré : {len(enregistrements)} transactions "
                  f"(total: {len(tous_les_enregistrements)})")

            curseur = data.get('next_cursor')
            if not curseur:
                break

        # Sauvegarder
        output_path = f'/tmp/transactions_{context["ds_nodash"]}.json'
        with open(output_path, 'w') as f:
            json.dump(tous_les_enregistrements, f)

        print(f"Total extrait : {len(tous_les_enregistrements)} transactions")
        return output_path

    extraire = PythonOperator(
        task_id='extraire_transactions',
        python_callable=extraire_avec_pagination,
    )

    # 4. Transformer et valider
    def transformer_et_valider(**context):
        import pandas as pd

        ti = context['task_instance']
        input_path = ti.xcom_pull(task_ids='extraire_transactions')

        with open(input_path) as f:
            records = json.load(f)

        df = pd.DataFrame(records)

        # Validation
        assert len(df) > 0, "Aucune transaction extraite"
        colonnes_requises = ['id', 'date', 'montant', 'devise', 'statut']
        for col in colonnes_requises:
            assert col in df.columns, f"Colonne manquante : {col}"

        # Transformation
        df['montant'] = pd.to_numeric(df['montant'])
        df['date'] = pd.to_datetime(df['date'])
        df = df[df['statut'] == 'completed']

        output_path = f'/tmp/transactions_clean_{context["ds_nodash"]}.parquet'
        df.to_parquet(output_path, index=False)

        print(f"Transactions valides : {len(df)} / {len(records)}")
        return {'path': output_path, 'count': len(df)}

    transformer = PythonOperator(
        task_id='transformer_et_valider',
        python_callable=transformer_et_valider,
    )

    # 5. Notifier la fin via webhook
    notifier_fin = SimpleHttpOperator(
        task_id='notifier_fin',
        http_conn_id='slack_webhook',
        endpoint='/hooks/TXXXXX/BXXXXX/XXXXXXXX',
        method='POST',
        data=json.dumps({
            'text': f'Pipeline transactions du {{{{ ds }}}} terminé',
            'blocks': [{
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': '*Pipeline API REST terminé ✓*\nDate: {{{{ ds }}}}\nDAG: {{{{ dag.dag_id }}}}',
                }
            }]
        }),
        headers={'Content-Type': 'application/json'},
    )

    # Dépendances
    verifier_api >> obtenir_token_task >> extraire >> transformer >> notifier_fin
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Les logs d'une tâche `SimpleHttpOperator` dans l'interface Airflow — montrer la requête HTTP envoyée et la réponse reçue
> **Expliquer :** Activer `log_response=True` sur l'opérateur pour afficher la réponse complète dans les logs. Montrer que les headers incluant le token `Authorization` sont bien masqués dans les logs (Airflow masque les secrets connus). Expliquer comment déboguer une erreur 401 ou 404.

---

## Notifications Slack et Teams

```python
# ---- Notification Slack via webhook ----
def notifier_slack(message: str, couleur: str = 'good'):
    """Utilitaire réutilisable pour envoyer une notification Slack."""
    import json
    from airflow.providers.http.operators.http import SimpleHttpOperator

    return SimpleHttpOperator(
        task_id=f'notifier_slack_{message[:20].replace(" ", "_")}',
        http_conn_id='slack_webhook',
        endpoint='/hooks/TXXXXX/BXXXXX/XXXXXXXX',
        method='POST',
        data=json.dumps({
            'attachments': [{
                'color': couleur,  # 'good' (vert), 'warning' (jaune), 'danger' (rouge)
                'text': message,
                'footer': 'Apache Airflow',
                'ts': '{{ ts_nodash }}',
            }]
        }),
        headers={'Content-Type': 'application/json'},
    )

# Utilisation dans un DAG
with DAG('pipeline_avec_notifications', ...) as dag:
    traiter = PythonOperator(task_id='traiter', python_callable=lambda: None)
    notif_succes = notifier_slack('Pipeline terminé avec succès !', 'good')
    notif_echec = notifier_slack('Pipeline en échec !', 'danger')

    traiter >> notif_succes
```

---

## Points clés à retenir

1. `SimpleHttpOperator` pour les appels HTTP simples (GET/POST)
2. `HttpSensor` pour attendre qu'un endpoint retourne une réponse valide
3. Pour la pagination et les scénarios complexes, utiliser le `HttpHook` directement
4. `do_xcom_push=True` sur `SimpleHttpOperator` pour passer la réponse aux tâches suivantes
5. `response_check` permet de valider la réponse — lève une exception si False
6. Les connexions HTTP stockent la base URL + les headers par défaut (pratique pour les tokens)
