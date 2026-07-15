# 🧠 Large Language Models (LLM) — le fil du parcours

> Sous-module central du parcours [Développeur IA](../PATH_DEV_IA.md).

Ce dossier contient **deux pistes complémentaires** — et c'est **volontaire**. Beaucoup d'apprenants
se demandent « pourquoi le RAG est-il expliqué à deux endroits ? ». Voici la carte pour ne jamais se
perdre.

---

## 🗺️ Les deux pistes

### 🟢 Piste 1 — Découverte (`LLM/cours/`)
Une **formation linéaire « 3 jours »**, du premier `print()` avec un LLM jusqu'à un premier RAG et une
première idée du fine-tuning. **On construit vite, on comprend les concepts.** Idéale pour démarrer.

- **Jour 1** — [Introduction](LLM/cours/01_introduction.md) · [Environnement](LLM/cours/02_environnement.md) · [Chatbot](LLM/cours/03_chatbot.md) · [Prompt engineering](LLM/cours/04_prompt_engineering.md) · [LLM avec outils](LLM/cours/05_llm_avec_outils.md) · [MCP](LLM/cours/06_mcp_servers.md)
- **Jour 2** — [Introduction RAG](LLM/cours/07_introduction_rag.md) · [Base vectorielle](LLM/cours/08_database_vectorielle.md) · [Interroger un RAG](LLM/cours/09_interrogation_rag.md) · [RAG + SQL](LLM/cours/10_rag_avec_bases_de_donnees_sql.md) · [Multi-agents](LLM/cours/11_multi_agent_collaboration.md)
- **Jour 3** — [Fine-tuning (intro)](LLM/cours/13_introduction_finetuning.md) · [Fine-tuning (pratique)](LLM/cours/14_pratique_finetuning.md)

### 🔵 Piste 2 — Production (modules dédiés)
Les **approfondissements de niveau industriel**, chacun autonome. C'est ici qu'on va **après** avoir
compris les bases, et c'est **cette piste que suit le [PATH Dev IA](../PATH_DEV_IA.md)**.

- [**LangChain**](LangChain/) — LCEL, mémoire, multi-providers, chaînes composables
- [**RAG**](RAG/) — chunking avancé, recherche hybride, reranking, évaluation RAGAS + CI
- [**Agents**](Agents/) — LangGraph (graphes d'état) & CrewAI (crews multi-rôles)
- [**HuggingFace**](HuggingFace/) — Transformers, modèles, datasets, **fine-tuning (LoRA/PEFT)**, embeddings
- [**LLMOps**](LLMOps/) — versioning de prompts, guardrails, caching sémantique, coût/latence, API LLM conteneurisée
- [**Claude Code**](Claude-Code/) — l'agent de code en pratique

---

## 🔁 Où les deux pistes se recouvrent (et quoi lire)

| Sujet | Version **Découverte** (comprendre) | Version **Production** (approfondir) |
|---|---|---|
| **RAG** | [`LLM/cours/07-09`](LLM/cours/07_introduction_rag.md) — premier pipeline | [module `RAG/`](RAG/) — chunking×N, hybrid search, reranking, RAGAS |
| **Multi-agents** | [`LLM/cours/11`](LLM/cours/11_multi_agent_collaboration.md) — concepts | [module `Agents/`](Agents/) — LangGraph/CrewAI en pratique |
| **Fine-tuning** | [`LLM/cours/13-14`](LLM/cours/13_introduction_finetuning.md) — intuition | [module `HuggingFace/04-Fine-Tuning`](HuggingFace/04-Fine-Tuning/) — LoRA/PEFT |
| **Prompt / outils** | [`LLM/cours/04-06`](LLM/cours/04_prompt_engineering.md) | [module `LLMOps/`](LLMOps/) — versioning, guardrails, coût |

> **La règle** : **Découverte d'abord pour comprendre, Production ensuite pour maîtriser.** Un chapitre
> de la piste Découverte n'est jamais une impasse — il pointe vers son approfondissement.

---

## 🎯 Progression recommandée

1. **Piste Découverte complète** (`LLM/cours/` Jours 1→3) pour avoir une vision d'ensemble et coder vite.
2. **Modules de production** dans l'ordre du [PATH Dev IA](../PATH_DEV_IA.md) : LangChain → RAG → Agents → LLMOps.
3. **Brief intégrateur** : [Assistant conversationnel RAG](../99-Brief/Dev-IA/RAG-LLM/BRIEF_RAG_LLM.md), puis le [projet final end-to-end](../99-Brief/FINAL_PROJECT_TEMPLATES/DEV_IA_ASSISTANT_RAG.md).

---

## 📚 Modules connexes

- [HuggingFace — embeddings](HuggingFace/05-Embeddings/) ↔ bases vectorielles du RAG
- [VectorDB](../05-Databases/VectorDB/) — Chroma, Qdrant, FAISS (le stockage derrière le RAG)
- [MLOps](../08-Machine-Learning/MLOps/) — le socle d'industrialisation réutilisé par LLMOps
