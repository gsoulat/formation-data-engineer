# LLMOps — mettre une application LLM en production

> **Niveau** : avancé · **Prérequis** : [LangChain](../LangChain/), [RAG](../RAG/), [FastAPI](../../01-Fondamentaux/Python/08-FastAPI/), [Observabilité](../../07-DevOps/04-Observabilite/).
> **Objectif** : passer du **« ça marche dans mon notebook »** au **« ça tourne en prod, de façon fiable, mesurée et maîtrisée en coût »**. C'est le chaînon manquant entre construire une appli LLM et l'exploiter.

---

## 1. 🧠 Build ≠ Run

Construire un pipeline RAG ou un agent, c'est le **build** — et c'est bien couvert dans les modules [RAG](../RAG/) et [Agents](../Agents/). Mais une appli LLM en production pose des problèmes que le notebook cache :

- Les **prompts changent** tout le temps — comment les versionner et éviter les régressions ?
- Le modèle peut **déraper** (hallucination, injection de prompt, fuite de données) — comment s'en protéger ?
- Chaque appel **coûte de l'argent** et prend du temps — comment mesurer et réduire ?
- Comment savoir que la **qualité** ne se dégrade pas en prod ?
- Comment **déployer** tout ça de façon reproductible ?

Le LLMOps, c'est le **« Run »** : versioning de prompts, guardrails, caching, monitoring coût/latence, évaluation continue, déploiement.

## 2. 📝 Versioning de prompts

**Un prompt est du code** : il mérite d'être versionné, testé et déployé avec la même rigueur. Une virgule changée peut casser 20 % des réponses.

- **Ne code pas les prompts en dur** dispersés dans le code. Centralise-les (fichiers versionnés dans Git, ou un registre comme **LangSmith Hub** / **PromptLayer**).
- **Versionne** (`v1`, `v2`…) et garde la trace de quelle version a produit quelle réponse.
- **Teste avant de déployer** : un jeu de cas + une éval (voir §5) qui échoue la CI si la qualité baisse. C'est de l'**A/B testing de prompts**, pas du « je change et je pousse ».

```python
# Prompt versionné + tracé (ex. LangSmith Hub)
from langsmith import Client
prompt = Client().pull_prompt("assistant-support:v3")   # version explicite, reproductible
```

## 3. 🛡️ Guardrails (garde-fous)

Un LLM en prod est exposé à des entrées hostiles et peut produire des sorties dangereuses. Trois lignes de défense :

- **Validation de l'entrée** : détecter les **injections de prompt** (« ignore tes instructions… »), filtrer les **données personnelles** (PII), limiter la taille.
- **Contrainte de la sortie** : forcer un **schéma** (JSON/Pydantic — `with_structured_output`), refuser hors-périmètre, filtrer le contenu toxique.
- **Outils** : [Guardrails AI](https://www.guardrailsai.com/), [NeMo Guardrails](https://github.com/NVIDIA/NeMo-Guardrails), ou une validation Pydantic maison.

```python
from pydantic import BaseModel
class Reponse(BaseModel):
    reponse: str
    sources: list[str]
    confiance: float
chaine = llm.with_structured_output(Reponse)   # la sortie DOIT respecter ce schéma
```

> ⚠️ **Règle d'or** : ne jamais faire confiance ni à l'entrée utilisateur, ni à la sortie du modèle. Les deux se valident.

## 4. ⚡ Caching : coût & latence

Beaucoup de requêtes se répètent (à la virgule près, ou en sens proche). Le cache évite de rappeler (et repayer) le modèle.

- **Cache exact** : même prompt → réponse mémorisée (Redis, cache LangChain).
- **Cache sémantique** : prompt *proche* (embedding similaire) → même réponse ([GPTCache](https://github.com/zilliztech/GPTCache)). Très efficace sur une FAQ.

```python
from langchain.globals import set_llm_cache
from langchain_community.cache import RedisSemanticCache
set_llm_cache(RedisSemanticCache(redis_url="redis://localhost:6379", embedding=embeddings, score_threshold=0.2))
```

Gain typique : **–30 à –70 % de coût** et une latence quasi nulle sur les requêtes fréquentes.

## 5. 📊 Monitoring : coût, latence, qualité

On ne pilote que ce qu'on mesure. Trois familles de signaux :

- **Coût** : compte les **tokens réels** renvoyés par l'API (`response.usage`, pas une regex approximative) → coût par requête, par utilisateur, par jour.
- **Latence** : temps total, time-to-first-token (important en streaming), p50/p95.
- **Traçabilité** : chaque appel LLM tracé (prompt, réponse, tokens, latence, version de prompt) via **LangSmith** ou **Arize Phoenix** (open source), et/ou exporté vers **Prometheus/Grafana** ([module Observabilité](../../07-DevOps/04-Observabilite/)).

```python
import tiktoken
enc = tiktoken.encoding_for_model("gpt-4o-mini")
n_in = len(enc.encode(prompt))   # tokens d'ENTRÉE réels (pas une estimation)
# + response.usage.completion_tokens pour la sortie → coût = (n_in*prix_in + n_out*prix_out)
```

**Choisir le bon modèle** est aussi du LLMOps : un petit modèle (moins cher, plus rapide) suffit souvent ; réserve le gros modèle aux cas durs. Documente cette décision.

## 6. 🎯 Évaluation en production

L'éval RAGAS (module [RAG](../RAG/03-Evaluation/)) valide *avant* le déploiement. En prod, ajoute :
- **Détection d'hallucination** (le modèle invente-t-il hors du contexte fourni ?).
- **LLM-as-a-judge** : un modèle note un échantillon des réponses selon une grille.
- **Feedback loop** : un pouce ↑/↓ utilisateur alimente un jeu de cas d'amélioration.

## 7. 🚀 Déploiement d'une API LLM conteneurisée

C'est le livrable qui prouve le LLMOps. Une vraie **API LLM** (pas un CRUD vide) :

```python
# app.py — API qui expose la chaîne LLM
from fastapi import FastAPI
from pydantic import BaseModel
app = FastAPI()
class Q(BaseModel): question: str
@app.post("/ask")
def ask(q: Q):
    # chaine = RAG/agent instrumenté (cache + guardrails + tracing)
    return {"reponse": chaine.invoke(q.question)}
@app.get("/health")
def health(): return {"status": "ok"}
```

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt . && RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# les clés d'API passent par variables d'environnement, JAMAIS dans l'image
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

+ `docker-compose.yml` (API + Redis pour le cache), variables d'environnement pour les clés, `/health` pour Kubernetes, et un pipeline CI/CD (voir [CI/CD](../../07-DevOps/01-CI-CD/)).

## 🧪 Lab

Reprends l'assistant RAG du [projet final](../../99-Brief/FINAL_PROJECT_TEMPLATES/DEV_IA_ASSISTANT_RAG.md) et **industrialise-le** :
1. Externalise et versionne ses prompts.
2. Ajoute des guardrails (sortie structurée + refus hors-périmètre).
3. Ajoute un cache sémantique (Redis) et **mesure** le gain coût/latence.
4. Trace chaque appel (LangSmith ou Phoenix) et expose des métriques.
5. 🎯 **À toi de jouer** : conteneurise l'API (Dockerfile + compose) avec `/health`, clés en variables d'environnement, et démarre-la avec une seule commande.

## ✅ Checklist de validation

- [ ] Prompts externalisés et versionnés (pas en dur)
- [ ] Guardrails : sortie contrainte (schéma) + gestion du hors-périmètre / injection
- [ ] Cache (exact ou sémantique) avec gain coût/latence mesuré
- [ ] Coût par requête (tokens réels) et latence p95 suivis
- [ ] Une API LLM conteneurisée avec `/health`, secrets en variables d'environnement
- [ ] Une évaluation continue (LLM-as-judge ou feedback) en place

## 🔗 Ressources

- LangSmith (tracing & prompt hub) : https://docs.smith.langchain.com/
- Arize Phoenix (observabilité LLM, open source) : https://docs.arize.com/phoenix
- Guardrails AI : https://www.guardrailsai.com/ · NeMo Guardrails : https://github.com/NVIDIA/NeMo-Guardrails
- GPTCache (cache sémantique) : https://github.com/zilliztech/GPTCache
- OpenAI — bonnes pratiques production : https://platform.openai.com/docs/guides/production-best-practices
