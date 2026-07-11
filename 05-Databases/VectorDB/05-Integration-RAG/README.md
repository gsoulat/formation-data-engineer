# Intégration RAG

RAG (Retrieval-Augmented Generation) est le pattern architectural dominant pour construire des applications LLM en production. Il combine la puissance générative des LLM avec la capacité des vector databases à retrouver des informations pertinentes.

## Contenu de ce dossier

| Fichier | Description |
|---------|-------------|
| `01-pipeline-rag.md` | Architecture complète RAG, pipeline minimal Chroma+OpenAI, pipeline Qdrant, LCEL, évaluation RAGAS, patterns avancés, chatbot documentaire |

## Architecture en bref

```
Documents → Chunking → Embedding → Vector DB
                                        ↓
Question → Embedding → Recherche → Contexte → LLM → Réponse sourcée
```

## Ressources

- [LangChain RAG](https://python.langchain.com/docs/tutorials/rag/)
- [RAGAS (évaluation)](https://docs.ragas.io/)
