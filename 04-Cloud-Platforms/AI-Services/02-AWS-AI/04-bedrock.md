# Amazon Bedrock — Modèles fondationnels et Claude sur AWS

## Introduction

**Amazon Bedrock** est le service AWS d'accès aux modèles d'IA fondationnels (Foundation Models ou FM). Il permet d'utiliser des modèles de grandes entreprises IA — Anthropic (Claude), Meta (Llama), Mistral AI, Cohere, AI21 Labs, Stability AI, et les propres modèles Amazon (Titan) — via une API unifiée, sans gérer d'infrastructure.

L'intérêt principal de Bedrock par rapport à l'API directe d'Anthropic ou d'OpenAI est l'intégration native dans l'écosystème AWS : IAM, VPC, CloudTrail, S3, Lambda, Step Functions...

---

## Modèles disponibles

### Par fournisseur (sélection)

| Fournisseur | Modèles disponibles | Points forts |
|-------------|--------------------|----|
| **Anthropic** | Claude 3.5 Sonnet, Claude 3 Haiku, Claude 3 Opus | Raisonnement, sécurité, instructions longues |
| **Meta** | Llama 3.1 8B, 70B, 405B | Open source, fine-tuning possible |
| **Mistral AI** | Mistral 7B, Mixtral 8x7B, Mistral Large | Modèles français, rapport perf/coût |
| **Amazon** | Titan Text, Titan Embeddings, Titan Image | Intégration AWS, pas de frais de licence |
| **Cohere** | Command R, Command R+ | RAG, recherche sémantique |
| **Stability AI** | Stable Diffusion XL | Génération d'images |
| **AI21 Labs** | Jurassic-2 | Génération et complétion de texte |

---

## Activer les modèles dans la console

Avant d'utiliser un modèle Bedrock, vous devez l'activer dans votre compte AWS.

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Console AWS → Amazon Bedrock → "Model access" → liste des modèles disponibles → cliquer sur "Manage model access" → cocher Claude 3.5 Sonnet et Llama 3.1 → soumettre la demande → montrer le statut "Access granted".
> **Expliquer :** Insister sur le fait que certains modèles nécessitent une approbation d'Anthropic ou d'AWS (quelques minutes à quelques heures). Montrer aussi le playground Bedrock pour tester les modèles sans écrire de code.
---

---

## Installation et configuration

```bash
pip install boto3
```

```python
import boto3
import json
import os

# Client Bedrock Runtime (pour les inférences)
bedrock_runtime = boto3.client(
    "bedrock-runtime",
    region_name="eu-west-1"  # Bedrock disponible en eu-west-1 (Irlande) et eu-central-1 (Francfort)
)

# Client Bedrock (pour la gestion : lister les modèles, etc.)
bedrock = boto3.client(
    "bedrock",
    region_name="eu-west-1"
)
```

---

## Utiliser Claude via Bedrock

### Appel de base avec Claude 3.5 Sonnet

```python
def invoke_claude(prompt: str, model_id: str = "anthropic.claude-3-5-sonnet-20241022-v2:0",
                  max_tokens: int = 1000, temperature: float = 0.7) -> str:
    """
    Appelle Claude via Amazon Bedrock avec l'API Messages.
    """
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = bedrock_runtime.invoke_model(
        modelId=model_id,
        body=json.dumps(body),
        contentType="application/json",
        accept="application/json"
    )

    result = json.loads(response["body"].read())
    return result["content"][0]["text"]


# Usage
answer = invoke_claude(
    "Explique la différence entre Apache Kafka et RabbitMQ en 3 points.",
    temperature=0.5
)
print(answer)
```

### Conversation multi-tours

```python
def chat_with_claude(messages: list[dict], system_prompt: str = None,
                     model_id: str = "anthropic.claude-3-5-sonnet-20241022-v2:0") -> str:
    """
    Conversation multi-tours avec Claude.
    messages: liste de {"role": "user"|"assistant", "content": "..."}
    """
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 2000,
        "messages": messages
    }

    if system_prompt:
        body["system"] = system_prompt

    response = bedrock_runtime.invoke_model(
        modelId=model_id,
        body=json.dumps(body),
        contentType="application/json",
        accept="application/json"
    )

    result = json.loads(response["body"].read())
    return result["content"][0]["text"]


# Exemple de conversation
conversation = []

# Tour 1
conversation.append({"role": "user", "content": "Je veux créer un pipeline Airflow pour traiter des fichiers CSV. Par où commencer ?"})
response1 = chat_with_claude(
    conversation,
    system_prompt="Tu es un expert en data engineering. Donne des conseils pratiques et concis."
)
conversation.append({"role": "assistant", "content": response1})
print("Assistant:", response1[:200], "...")

# Tour 2
conversation.append({"role": "user", "content": "Comment gérer les erreurs dans les DAGs ?"})
response2 = chat_with_claude(conversation)
print("Assistant:", response2[:200], "...")
```

### Streaming des réponses

```python
def invoke_claude_stream(prompt: str) -> None:
    """
    Affiche la réponse de Claude en streaming (token par token).
    """
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "messages": [{"role": "user", "content": prompt}]
    }

    response = bedrock_runtime.invoke_model_with_response_stream(
        modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
        body=json.dumps(body),
        contentType="application/json"
    )

    print("Réponse : ", end="", flush=True)
    for event in response["body"]:
        chunk = json.loads(event["chunk"]["bytes"])
        if chunk["type"] == "content_block_delta":
            delta = chunk.get("delta", {})
            if delta.get("type") == "text_delta":
                print(delta.get("text", ""), end="", flush=True)
    print()  # Saut de ligne final
```

---

## Utiliser Llama via Bedrock

```python
def invoke_llama(prompt: str, model_id: str = "meta.llama3-1-70b-instruct-v1:0",
                 max_gen_len: int = 512) -> str:
    """
    Appelle un modèle Llama 3.1 via Bedrock.
    L'API est différente de Claude.
    """
    body = {
        "prompt": f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n",
        "max_gen_len": max_gen_len,
        "temperature": 0.7,
        "top_p": 0.9
    }

    response = bedrock_runtime.invoke_model(
        modelId=model_id,
        body=json.dumps(body)
    )

    result = json.loads(response["body"].read())
    return result["generation"]


# Usage
answer = invoke_llama("Qu'est-ce qu'un vector database et pourquoi l'utiliser avec un LLM ?")
print(answer)
```

---

## Embeddings avec Amazon Titan

```python
def get_titan_embeddings(texts: list[str],
                          model_id: str = "amazon.titan-embed-text-v2:0") -> list[list[float]]:
    """
    Génère des embeddings vectoriels avec Amazon Titan.
    Idéal pour les pipelines RAG sur AWS.
    """
    embeddings = []

    for text in texts:
        body = {
            "inputText": text,
            "dimensions": 1024,  # 256, 512, ou 1024
            "normalize": True
        }

        response = bedrock_runtime.invoke_model(
            modelId=model_id,
            body=json.dumps(body)
        )

        result = json.loads(response["body"].read())
        embeddings.append(result["embedding"])

    return embeddings


# Usage pour RAG
documents = [
    "Apache Kafka est une plateforme de streaming d'événements distribuée.",
    "Amazon S3 est un service de stockage d'objets scalable et durable.",
    "PostgreSQL est un système de gestion de base de données relationnelle open-source.",
]

embeddings = get_titan_embeddings(documents)
print(f"Embeddings générés : {len(embeddings)} vecteurs de dimension {len(embeddings[0])}")
```

---

## Bedrock Knowledge Bases — RAG managé

Amazon Bedrock propose une fonctionnalité **Knowledge Bases** qui permet de créer un pipeline RAG entièrement managé :

```
Documents S3 → Chunking automatique → Embeddings Titan → Vector store (OpenSearch) → Retrieval + Claude
```

```python
# Requête sur une Knowledge Base
bedrock_agent_runtime = boto3.client(
    "bedrock-agent-runtime",
    region_name="eu-west-1"
)

def query_knowledge_base(question: str, kb_id: str) -> dict:
    """
    Interroge une Knowledge Base Bedrock avec RAG automatique.
    """
    response = bedrock_agent_runtime.retrieve_and_generate(
        input={"text": question},
        retrieveAndGenerateConfiguration={
            "type": "KNOWLEDGE_BASE",
            "knowledgeBaseConfiguration": {
                "knowledgeBaseId": kb_id,
                "modelArn": "arn:aws:bedrock:eu-west-1::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0",
                "retrievalConfiguration": {
                    "vectorSearchConfiguration": {
                        "numberOfResults": 5
                    }
                }
            }
        }
    )

    return {
        "answer": response["output"]["text"],
        "citations": [
            {
                "text": citation["retrievedReferences"][0]["content"]["text"][:200],
                "location": citation["retrievedReferences"][0]["location"]
            }
            for citation in response.get("citations", [])
            if citation.get("retrievedReferences")
        ]
    }


# Usage
kb_id = "VOTRE_KB_ID"
result = query_knowledge_base(
    "Quelle est la politique de sécurité des données de l'entreprise ?",
    kb_id
)
print(f"Réponse : {result['answer']}")
print(f"\nSources utilisées ({len(result['citations'])}) :")
for citation in result["citations"]:
    print(f"  - {citation['text'][:100]}...")
```

---

## Guardrails Bedrock

Les **Guardrails** Bedrock permettent de filtrer le contenu des LLMs côté AWS, indépendamment du modèle utilisé :

```python
def invoke_with_guardrails(prompt: str, guardrail_id: str,
                            guardrail_version: str = "DRAFT") -> dict:
    """
    Appelle un modèle avec les guardrails activés.
    """
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "messages": [{"role": "user", "content": prompt}]
    }

    response = bedrock_runtime.invoke_model(
        modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
        body=json.dumps(body),
        guardrailIdentifier=guardrail_id,
        guardrailVersion=guardrail_version,
        trace="ENABLED"  # Pour voir les décisions du guardrail
    )

    result = json.loads(response["body"].read())

    # Vérifier si le guardrail a bloqué la requête
    amazon_bedrock_guardrail_action = response.get("ResponseMetadata", {}).get(
        "HTTPHeaders", {}
    ).get("x-amzn-bedrock-guardrail-action", "NONE")

    return {
        "text": result["content"][0]["text"] if result.get("content") else None,
        "blocked": amazon_bedrock_guardrail_action == "BLOCKED",
        "guardrail_action": amazon_bedrock_guardrail_action
    }
```

---

## Comparaison des modèles Bedrock pour des tâches data engineering

| Tâche | Modèle recommandé | Raison |
|-------|------------------|--------|
| Génération de code Python/SQL | Claude 3.5 Sonnet | Excellent sur le code, contexte long |
| Résumé de logs d'erreur | Claude 3 Haiku | Rapide et économique |
| Analyse de schémas de BDD | Claude 3.5 Sonnet | Capacité de raisonnement |
| Questions-réponses sur docs techniques | Command R+ (Cohere) | Optimisé RAG |
| Embeddings pour RAG | Titan Embed v2 | Intégration native AWS |
| Génération d'images pour rapports | Titan Image / SDXL | Disponible sur Bedrock |
| Tâches en français | Mistral Large | Modèle français, excellent FR |

---

## Ressources officielles

- Documentation Bedrock : [https://docs.aws.amazon.com/bedrock/](https://docs.aws.amazon.com/bedrock/)
- Liste des modèles disponibles : [https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html](https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html)
- Bedrock Playground (console) : Console AWS → Amazon Bedrock → Playgrounds
- Pricing : [https://aws.amazon.com/bedrock/pricing/](https://aws.amazon.com/bedrock/pricing/)
- SDK Converse API (API unifiée multi-modèles) : [https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html)
