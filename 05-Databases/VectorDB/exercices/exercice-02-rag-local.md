# Exercice 02 — Pipeline RAG Local avec Chroma + Ollama

## Objectif

Construire un **pipeline RAG entièrement local** — sans clé API, sans connexion internet, sans coût. Vous utiliserez :
- **Ollama** pour faire tourner un LLM en local (Llama 3, Mistral, etc.)
- **Chroma** pour la vector database
- **Sentence-Transformers** pour les embeddings
- **LangChain** pour orchestrer le tout

**Durée estimée** : 2h30 à 3h30

---

## Contexte

Votre entreprise veut un chatbot documentaire pour ses politiques RH internes. Pour des raisons de **confidentialité des données**, il est impératif que rien ne soit envoyé vers des serveurs externes (OpenAI, Anthropic, Google...).

Vous devez construire un système 100% on-premise.

---

## Prérequis

### Installer Ollama

```bash
# Linux/Mac
curl -fsSL https://ollama.ai/install.sh | sh

# Windows : télécharger l'installeur sur https://ollama.ai/
```

```bash
# Télécharger un modèle léger (recommandé pour commencer)
ollama pull llama3.2:1b    # Très rapide, 1.3GB (~1B paramètres)
# OU
ollama pull llama3.2:3b    # Plus précis, 2.0GB (~3B paramètres)
# OU
ollama pull mistral        # 4.1GB, excellent rapport qualité/taille

# Vérifier
ollama list
ollama run llama3.2:1b "Dis bonjour en français"
```

### Installer les dépendances Python

```bash
pip install chromadb sentence-transformers langchain langchain-ollama langchain-chroma langchain-community
```

---

## Partie 1 : Créer les documents RH (15 min)

Créez un fichier `documents_rh/` avec plusieurs fichiers texte simulant des politiques RH :

```bash
mkdir documents_rh
```

**`documents_rh/conges.txt`** :
```
POLITIQUE DE CONGÉS - ENTREPRISE NOVA TECH

Article 1 - Congés annuels payés
Tout salarié à temps plein bénéficie de 25 jours ouvrés de congés payés par an.
Les congés sont acquis à raison de 2,08 jours par mois travaillé.
La période de référence court du 1er juin au 31 mai de l'année suivante.

Article 2 - Demande de congés
Les demandes de congés doivent être soumises via l'outil RH interne au minimum :
- 2 semaines à l'avance pour les congés de moins de 5 jours
- 1 mois à l'avance pour les congés de 5 jours ou plus
- 2 mois à l'avance pour les congés de plus de 10 jours consécutifs

L'approbation est soumise à l'accord du responsable hiérarchique.

Article 3 - Report de congés
Les congés non pris peuvent être reportés jusqu'au 31 décembre de l'année suivante.
Au-delà, les congés non pris sont perdus sauf accord exceptionnel de la direction RH.

Article 4 - Congés exceptionnels
Mariage du salarié : 4 jours ouvrés
Naissance ou adoption : 3 jours ouvrés
Décès d'un conjoint ou enfant : 5 jours ouvrés
Décès d'un parent (père, mère) : 3 jours ouvrés
Décès d'un autre proche (frère, sœur) : 1 jour ouvré
Mariage d'un enfant : 1 jour ouvré
```

**`documents_rh/teletravail.txt`** :
```
CHARTE DU TÉLÉTRAVAIL - ENTREPRISE NOVA TECH

1. Éligibilité au télétravail
Le télétravail est accessible à tout salarié en CDI ayant au moins 6 mois d'ancienneté.
Les nouveaux employés en période d'intégration (0-3 mois) ne sont pas éligibles.
Les postes nécessitant une présence physique continue sont exclus du dispositif.

2. Modalités
Le nombre maximum de jours de télétravail est fixé à 2 jours par semaine.
Le choix des jours se fait en accord avec le responsable d'équipe.
Au moins 3 jours de présence au bureau par semaine sont obligatoires.

3. Matériel et équipement
L'entreprise fournit un ordinateur portable aux salariés en télétravail régulier.
Une participation forfaitaire de 50€ par mois est versée pour les frais de connexion internet.
Le salarié est responsable de la sécurité de son espace de travail à domicile.

4. Disponibilité
Les horaires de travail habituels s'appliquent en télétravail.
Le salarié doit être joignable par téléphone et messagerie professionnelle pendant ses heures de travail.
Les réunions d'équipe ne peuvent pas être déclinées pour cause de télétravail.

5. Révision de l'accord
L'accord de télétravail peut être révisé avec un préavis de 15 jours par l'une ou l'autre des parties.
```

**`documents_rh/remboursements.txt`** :
```
POLITIQUE DE REMBOURSEMENT DES FRAIS PROFESSIONNELS - NOVA TECH

1. Frais de déplacement
Les frais de déplacement professionnels sont remboursés sur présentation de justificatifs.
Train et avion : remboursés intégralement (billet économique obligatoire pour les vols)
Voiture personnelle : remboursement au barème kilométrique fiscal en vigueur
Taxi/VTC : remboursés uniquement si absence de transport en commun ou urgence justifiée

2. Frais de repas
Déjeuner lors d'un déplacement : plafonné à 22€ TTC
Dîner lors d'un déplacement : plafonné à 35€ TTC
Repas client (maximum 3 personnes hors salarié) : plafonné à 50€ par personne

3. Hébergement
Hôtel à Paris et grandes métropoles : plafonné à 150€ la nuit (petit-déjeuner non inclus)
Hôtel en province : plafonné à 100€ la nuit
Les réservations doivent être effectuées via la plateforme voyage de l'entreprise.

4. Procédure de remboursement
Les notes de frais doivent être soumises avant le 5 du mois suivant.
Tout justificatif manquant peut entraîner le refus de remboursement.
Le remboursement est effectué avec la paie du mois suivant la validation.

5. Frais non remboursables
Amendes de stationnement ou de circulation
Frais de pressing personnels
Cadeaux d'affaires supérieurs à 150€ sans accord préalable de la direction
```

**`documents_rh/onboarding.txt`** :
```
GUIDE D'INTÉGRATION DES NOUVEAUX EMPLOYÉS - NOVA TECH

Semaine 1 - Arrivée et installation
Jour 1 : Accueil par les RH, remise du matériel, visite des locaux
Jour 1-2 : Formation IT (accès systèmes, outils, sécurité informatique)
Jour 2-3 : Rencontres avec l'équipe et les parties prenantes clés
Jour 3-5 : Prise en main des outils métier avec un parrain désigné

Semaine 2-4 - Montée en compétences
Formation aux processus internes de l'entreprise
Participation aux réunions d'équipe en mode observation
Définition des objectifs des 3 premiers mois avec le manager
Premier bilan à la fin du premier mois

Les 3 premiers mois - Période d'essai
Réunion bilan à 1 mois, 2 mois et en fin de période d'essai
Possibilité de prolonger la période d'essai une fois (accord des deux parties requis)
Formation continue sur les produits et services de l'entreprise

Parrain d'intégration
Chaque nouvel employé se voit attribuer un parrain dans son équipe.
Le parrain est disponible pour répondre aux questions du quotidien.
Le rôle de parrain est valorisé dans l'évaluation annuelle de performance.

Documents obligatoires à fournir à l'arrivée
Pièce d'identité valide
Carte Vitale ou attestation d'affiliation
RIB pour le versement du salaire
Diplômes et certificats de travail des emplois précédents
```

---

## Partie 2 : Pipeline d'ingestion (40 min)

Créez `ingestion.py` :

```python
# ingestion.py
import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma

DOCS_PATH = "./documents_rh/"
DB_PATH = "./rag_rh_db"
COLLECTION_NAME = "politiques_rh"
EMBEDDING_MODEL = "paraphrase-multilingual-mpnet-base-v2"

def ingest_documents():
    """Pipeline d'ingestion complet."""

    # ─────────────────────────────────────────────────────────────
    # TODO 1 : Charger tous les fichiers .txt du dossier documents_rh/
    # Utiliser DirectoryLoader avec glob="**/*.txt" et loader_cls=TextLoader
    # Passer encoding="utf-8" dans loader_kwargs
    # ─────────────────────────────────────────────────────────────
    print("1. Chargement des documents...")
    loader = ???
    documents = loader.load()
    print(f"   → {len(documents)} documents chargés")

    # Afficher les sources
    for doc in documents:
        source = os.path.basename(doc.metadata.get('source', ''))
        print(f"      - {source} ({len(doc.page_content)} caractères)")

    # ─────────────────────────────────────────────────────────────
    # TODO 2 : Découper les documents
    # chunk_size=600, chunk_overlap=100
    # ─────────────────────────────────────────────────────────────
    print("\n2. Découpage en chunks...")
    splitter = ???
    chunks = splitter.split_documents(documents)
    print(f"   → {len(chunks)} chunks générés")
    print(f"   → Taille moyenne : {sum(len(c.page_content) for c in chunks) // len(chunks)} chars")

    # ─────────────────────────────────────────────────────────────
    # TODO 3 : Créer le modèle d'embedding
    # normalize_embeddings=True dans encode_kwargs
    # ─────────────────────────────────────────────────────────────
    print("\n3. Chargement du modèle d'embedding...")
    embeddings = ???
    print("   → Modèle chargé")

    # ─────────────────────────────────────────────────────────────
    # TODO 4 : Créer le vector store Chroma depuis les documents
    # Utiliser Chroma.from_documents()
    # persist_directory=DB_PATH, collection_name=COLLECTION_NAME
    # ─────────────────────────────────────────────────────────────
    print("\n4. Indexation dans Chroma...")

    # Supprimer le DB existant si présent
    import shutil
    if os.path.exists(DB_PATH):
        shutil.rmtree(DB_PATH)
        print("   → Base existante supprimée")

    vectorstore = ???
    count = vectorstore._collection.count()
    print(f"   → {count} vecteurs stockés dans '{DB_PATH}'")

    return vectorstore

if __name__ == "__main__":
    vs = ingest_documents()
    print("\n✅ Ingestion terminée !")

    # Test rapide
    print("\nTest de recherche basique :")
    results = vs.similarity_search("combien de jours de congés ?", k=2)
    for r in results:
        print(f"  Source : {os.path.basename(r.metadata.get('source', ''))}")
        print(f"  Contenu : {r.page_content[:100]}...\n")
```

---

## Partie 3 : Pipeline RAG avec Ollama (60 min)

Créez `rag_local.py` :

```python
# rag_local.py
import os
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

DB_PATH = "./rag_rh_db"
COLLECTION_NAME = "politiques_rh"
EMBEDDING_MODEL = "paraphrase-multilingual-mpnet-base-v2"

# ─────────────────────────────────────────────────────────────
# Choix du modèle Ollama
# Vérifiez les modèles disponibles avec : ollama list
# ─────────────────────────────────────────────────────────────
OLLAMA_MODEL = "llama3.2:3b"  # Ajustez selon vos modèles disponibles

class RagLocalPipeline:

    def __init__(self):
        print(f"Initialisation du pipeline RAG local...")
        print(f"  LLM : {OLLAMA_MODEL} (via Ollama)")
        print(f"  Embeddings : {EMBEDDING_MODEL}")
        print(f"  Vector DB : Chroma ({DB_PATH})")

        # ─────────────────────────────────────────────────────────────
        # TODO 1 : Charger le vector store existant
        # HuggingFaceEmbeddings avec normalize_embeddings=True
        # Chroma avec persist_directory et collection_name
        # ─────────────────────────────────────────────────────────────
        self.embeddings = ???
        self.vectorstore = ???

        # ─────────────────────────────────────────────────────────────
        # TODO 2 : Configurer le retriever avec MMR
        # k=4, fetch_k=10
        # ─────────────────────────────────────────────────────────────
        self.retriever = ???

        # ─────────────────────────────────────────────────────────────
        # TODO 3 : Configurer le LLM Ollama
        # ChatOllama(model=OLLAMA_MODEL, temperature=0)
        # ─────────────────────────────────────────────────────────────
        self.llm = ???

        # ─────────────────────────────────────────────────────────────
        # TODO 4 : Créer le prompt template
        # Instructions : répondre en français, uniquement à partir du contexte,
        # indiquer clairement si l'information n'est pas disponible
        # Variables : {context}, {question}
        # ─────────────────────────────────────────────────────────────
        self.prompt = ChatPromptTemplate.from_template("""
???
""")

        # ─────────────────────────────────────────────────────────────
        # TODO 5 : Construire la chaîne LCEL
        # context → retriever | format_docs
        # question → RunnablePassthrough()
        # Puis → prompt | llm | StrOutputParser()
        # ─────────────────────────────────────────────────────────────
        self.chain = ???

        n_docs = self.vectorstore._collection.count()
        print(f"  Documents indexés : {n_docs}")
        print("  Prêt !\n")

    def format_docs(self, docs) -> str:
        """Formate les documents récupérés pour le contexte."""
        parts = []
        for i, doc in enumerate(docs):
            source = os.path.basename(doc.metadata.get('source', 'inconnu'))
            parts.append(f"[Document {i+1} — source: {source}]\n{doc.page_content}")
        return "\n\n---\n\n".join(parts)

    def ask(self, question: str, stream: bool = False) -> str:
        """Pose une question au pipeline RAG."""
        if stream:
            # Mode streaming (affichage progressif)
            response = ""
            for chunk in self.chain.stream(question):
                print(chunk, end="", flush=True)
                response += chunk
            print()
            return response
        else:
            return self.chain.invoke(question)

    def ask_with_sources(self, question: str) -> tuple[str, list]:
        """Pose une question et retourne la réponse avec les sources."""
        # Récupérer les documents pour affichage des sources
        docs = self.retriever.invoke(question)
        context = self.format_docs(docs)

        # Générer la réponse
        from langchain_core.messages import HumanMessage
        messages = self.prompt.format_messages(context=context, question=question)
        response = self.llm.invoke(messages)
        answer = response.content

        sources = [os.path.basename(d.metadata.get('source', '')) for d in docs]
        return answer, list(set(sources))


def main():
    rag = RagLocalPipeline()

    # ─────────────────────────────────────────────────────────────
    # Série de tests
    # ─────────────────────────────────────────────────────────────
    test_questions = [
        "Combien de jours de congés payés ai-je droit par an ?",
        "Comment faire une demande de congés pour une semaine ?",
        "Est-ce que je peux faire du télétravail dès mon premier jour ?",
        "Quel est le remboursement pour un repas client ?",
        "Qu'est-ce qu'un parrain d'intégration ?",
        "Quel est le plafond pour une nuit d'hôtel à Paris ?",
    ]

    print("="*70)
    print("TESTS DU PIPELINE RAG LOCAL")
    print("="*70)

    for question in test_questions:
        print(f"\nQuestion : {question}")
        print("-" * 50)
        answer, sources = rag.ask_with_sources(question)
        print(f"Réponse  : {answer}")
        print(f"Sources  : {', '.join(sources)}")
        print()

    # ─────────────────────────────────────────────────────────────
    # Mode interactif
    # ─────────────────────────────────────────────────────────────
    print("="*70)
    print("MODE INTERACTIF (tapez 'quit' pour quitter)")
    print("="*70)

    while True:
        question = input("\nVotre question RH : ").strip()
        if question.lower() in ['quit', 'exit', 'q']:
            print("Aurevoir !")
            break
        if not question:
            continue

        print("\nRéponse (en cours de génération...) :")
        answer, sources = rag.ask_with_sources(question)
        print(answer)
        print(f"\n[Sources consultées : {', '.join(sources) if sources else 'aucune'}]")


if __name__ == "__main__":
    main()
```

---

## Partie 4 : Tests et validation (30 min)

### Étape 4.1 — Lancer l'ingestion

```bash
python ingestion.py
```

**Résultat attendu :**
```
1. Chargement des documents...
   → 4 documents chargés
      - conges.txt (XXX caractères)
      - teletravail.txt (XXX caractères)
      - remboursements.txt (XXX caractères)
      - onboarding.txt (XXX caractères)

2. Découpage en chunks...
   → 20-25 chunks générés
   → Taille moyenne : ~400 chars

3. Chargement du modèle d'embedding...
   → Modèle chargé

4. Indexation dans Chroma...
   → XX vecteurs stockés dans './rag_rh_db'

✅ Ingestion terminée !
```

### Étape 4.2 — Lancer le RAG

```bash
python rag_local.py
```

**Vérifiez que :**
- Le LLM répond en français
- Les réponses sont basées sur le contenu des documents (pas inventées)
- Les sources sont correctement identifiées
- Pour des questions hors-sujet ("Quelle est la capitale de la France ?"), le système répond qu'il ne trouve pas l'information dans ses documents

### Étape 4.3 — Questions de validation

Répondez dans un fichier `reponses_validation.md` :

1. Pour la question "Combien de jours de congés pour le mariage de mon enfant ?", le système donne-t-il la bonne réponse (1 jour) ?

2. Pour "Puis-je faire 4 jours de télétravail par semaine ?", le système répond-il correctement non (maximum 2 jours/semaine) ?

3. Pour "C'est quoi le capital social de l'entreprise ?" (information non présente), le système dit-il clairement qu'il ne sait pas ?

4. Testez avec une variante de formulation : "J'ai un enterrement de la belle-mère, combien de jours ?". Le système retrouve-t-il l'information sur les "décès d'un autre proche" ?

---

## Partie 5 : Bonus — Évaluation automatique (optionnel)

Créez `evaluation.py` pour tester automatiquement la qualité du RAG :

```python
# evaluation.py
from rag_local import RagLocalPipeline

rag = RagLocalPipeline()

# Questions avec réponses attendues (fragments)
test_cases = [
    {
        "question": "Combien de jours de congés annuels payés ?",
        "expected_keywords": ["25", "jours", "ouvr"],
        "source_expected": "conges.txt"
    },
    {
        "question": "Délai pour demander 2 semaines de vacances ?",
        "expected_keywords": ["1 mois", "un mois", "mois à l'avance"],
        "source_expected": "conges.txt"
    },
    {
        "question": "Nombre de jours de télétravail maximum par semaine ?",
        "expected_keywords": ["2 jours", "deux jours"],
        "source_expected": "teletravail.txt"
    },
    {
        "question": "Plafond repas au restaurant avec un client ?",
        "expected_keywords": ["50", "50€"],
        "source_expected": "remboursements.txt"
    },
    {
        "question": "Qu'est-ce qu'un parrain dans le onboarding ?",
        "expected_keywords": ["parrain", "équipe", "questions"],
        "source_expected": "onboarding.txt"
    },
]

print("=== Évaluation automatique du pipeline RAG ===\n")
correct = 0

for test in test_cases:
    answer, sources = rag.ask_with_sources(test["question"])
    answer_lower = answer.lower()

    # Vérifier si les mots-clés attendus sont dans la réponse
    keyword_found = any(kw.lower() in answer_lower for kw in test["expected_keywords"])
    source_correct = test["source_expected"] in sources

    status = "✅" if keyword_found else "❌"
    if keyword_found:
        correct += 1

    print(f"{status} Q: {test['question'][:50]}")
    print(f"   Mots-clés attendus : {test['expected_keywords']}")
    print(f"   Trouvés dans réponse : {keyword_found}")
    print(f"   Source : {sources} (attendu : {test['source_expected']}) {'✓' if source_correct else '✗'}")
    print(f"   Réponse : {answer[:120]}...")
    print()

print(f"Score : {correct}/{len(test_cases)} = {correct/len(test_cases):.0%}")
```

---

## Partie 6 : Bonus avancé — Ajout de documents à chaud

```python
# update_knowledge_base.py
"""
Ajouter un nouveau document à la base sans tout réingérer.
"""
import os
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# ─────────────────────────────────────────────────────────────
# Nouveau document : Politique de formation
# ─────────────────────────────────────────────────────────────
new_doc_content = """
POLITIQUE DE FORMATION PROFESSIONNELLE - NOVA TECH

1. Budget formation
Chaque salarié dispose d'un budget annuel de 1500€ pour les formations professionnelles.
Ce budget est disponible sur le compte CPF (Compte Personnel de Formation).
L'entreprise peut abonder le CPF jusqu'à 2000€ supplémentaires pour les formations stratégiques.

2. Types de formations éligibles
Certifications techniques (AWS, Azure, GCP, certifications Python, etc.)
Formations en management et leadership
Cours de langues étrangères professionnelles
Conférences techniques (pass + voyage inclus dans le budget)

3. Procédure de demande
Soumettre la demande de formation au manager 1 mois avant la date souhaitée.
Obtenir la validation du manager et des RH.
Inscription et règlement via la plateforme RH.
Fournir une attestation de participation à l'issue de la formation.

4. Formations obligatoires
Sécurité informatique : tous les salariés, annuelle
Prévention des risques : tous les salariés, à l'embauche puis tous les 3 ans
Management d'équipe : toute personne prenant un rôle de manager
"""

with open("documents_rh/formation.txt", "w", encoding="utf-8") as f:
    f.write(new_doc_content)

print("Nouveau document créé : documents_rh/formation.txt")

# ─────────────────────────────────────────────────────────────
# Ajouter ce document à la base existante sans tout reconstruire
# ─────────────────────────────────────────────────────────────
embeddings = HuggingFaceEmbeddings(model_name="paraphrase-multilingual-mpnet-base-v2")
vectorstore = Chroma(
    persist_directory="./rag_rh_db",
    embedding_function=embeddings,
    collection_name="politiques_rh"
)

print(f"Documents avant ajout : {vectorstore._collection.count()}")

loader = TextLoader("documents_rh/formation.txt", encoding="utf-8")
docs = loader.load()
splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=100)
chunks = splitter.split_documents(docs)

vectorstore.add_documents(chunks)

print(f"Documents après ajout : {vectorstore._collection.count()}")
print(f"Ajoutés : {len(chunks)} nouveaux chunks")

# Test
results = vectorstore.similarity_search("budget pour une certification AWS ?", k=2)
for r in results:
    print(f"\nSource : {os.path.basename(r.metadata.get('source', ''))}")
    print(f"Contenu : {r.page_content[:150]}...")
```

---

## Critères d'évaluation

| Critère | Points |
|---------|--------|
| Pipeline d'ingestion fonctionnel (TODOs 1-4) | 5 pts |
| Classe `RagLocalPipeline` correctement implémentée (TODOs 1-5) | 6 pts |
| Le LLM répond en français à partir des documents | 3 pts |
| Réponses correctes sur les 6 questions de test | 4 pts |
| Refus poli pour les questions hors-corpus | 2 pts |
| Fichier `reponses_validation.md` rempli | 2 pts |
| Bonus : évaluation automatique (score ≥ 80%) | +3 pts |
| Bonus : ajout de document à chaud fonctionnel | +2 pts |

**Total : 22 pts (+ 5 bonus)**

---

## Troubleshooting courant

**Ollama ne répond pas :**
```bash
# Vérifier qu'Ollama tourne
ollama serve &
ollama list
```

**Modèle trop lent sur CPU :**
```python
# Utiliser un modèle plus petit
OLLAMA_MODEL = "llama3.2:1b"  # 1.3GB, plus rapide

# Ou désactiver le streaming si c'est ce qui pose problème
answer = rag.ask(question, stream=False)
```

**Erreur d'import langchain-ollama :**
```bash
pip install langchain-ollama --upgrade
```

**Réponses en anglais :**
- Vérifiez votre prompt template : insistez sur "Réponds TOUJOURS en français"
- Certains modèles (llama3.2:1b) ignorent parfois la langue du prompt

**La réponse invente des informations :**
- Vérifiez que les chunks récupérés sont bien pertinents avec `rag.retriever.invoke(question)`
- Augmentez `k` dans le retriever (plus de contexte)
- Utilisez un modèle plus grand (3b ou 7b)
