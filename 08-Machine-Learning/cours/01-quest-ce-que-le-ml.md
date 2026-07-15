# Chapitre 1 : Qu'est-ce que le Machine Learning, vraiment ?

## 🎯 Objectifs — Phase 0 · Semaine 1 · Comprendre avant de calculer

- Comprendre **intuitivement** ce qu'est le Machine Learning sans formule mathématique
- Distinguer un programme classique d'un programme qui « apprend »
- Connaître les 3 grandes familles d'apprentissage et savoir les reconnaître dans la vie quotidienne
- Maîtriser le vocabulaire essentiel (données, features, target, entraînement, prédiction)
- Utiliser un modèle pré-entraîné pour la première fois (Hugging Face)
- Savoir quand le ML est pertinent — et quand il ne l'est **pas**
- Découvrir l'écosystème Python pour le ML

> 💡 **Conseil** : "Ce chapitre ne contient aucun modèle à entraîner. L'objectif est de **comprendre** avant de coder. Prenez le temps de lire les analogies et de manipuler les exemples pandas."

---

## 1. 🧠 Programme classique vs Machine Learning

### 1.1 L'analogie de la calculatrice et de la reconnaissance vocale

Imaginez deux situations :

**Situation A — La calculatrice**
Vous tapez `3 + 5`. Le programme applique une règle que le développeur a codée (`return a + b`). Le résultat est toujours `8`. Le programme suit des **règles écrites à la main** par un humain.

**Situation B — La reconnaissance vocale**
Vous dites « Quel temps fait-il demain ? ». Votre téléphone comprend votre phrase, malgré votre accent, le bruit de fond et le fait que vous avez dit « demain » et pas « domain ». Aucun développeur n'a écrit de règle du type : « si le signal sonore ressemble à ceci → alors c'est le mot "temps" ». Le programme a **appris** à reconnaître les mots en écoutant des millions d'exemples.

C'est **ça**, le Machine Learning : au lieu de coder les règles, on donne des **exemples** au programme et il **découvre les règles tout seul**.

### 1.2 Le schéma fondamental

```
╔══════════════════════════════════════════════════════════════════╗
║              PROGRAMMATION TRADITIONNELLE                       ║
║                                                                  ║
║   Données ──┐                                                    ║
║             ├──► Programme (règles codées) ──► Résultats         ║
║   Règles ───┘                                                    ║
╚══════════════════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════════════════╗
║              MACHINE LEARNING                                    ║
║                                                                  ║
║   Données ──────┐                                                ║
║                 ├──► Algorithme ML ──► Modèle (les règles)       ║
║   Résultats ────┘                                                ║
║   attendus                                                       ║
║                                                                  ║
║   Puis : Nouvelles données ──► Modèle ──► Prédictions            ║
╚══════════════════════════════════════════════════════════════════╝
```

### 1.3 Comparaison détaillée

| Aspect | Programmation classique | Machine Learning |
|--------|------------------------|------------------|
| **Entrée** | Données + Règles codées | Données + Résultats attendus |
| **Sortie** | Résultats calculés | Un modèle (= les règles apprises) |
| **Approche** | Déductive : on part des règles | Inductive : on part des exemples |
| **Cas simples** | Parfait (calculatrice, tri) | Trop lourd, inutile |
| **Cas complexes** | Impossible (vision, langage) | Excelle si on a assez de données |
| **Maintenance** | Modifier le code | Réentraîner avec de nouvelles données |
| **Erreurs** | Bug = mauvaise règle | Erreur = données insuffisantes/biaisées |
| **Explicabilité** | Totale (on lit le code) | Variable (certains modèles sont des « boîtes noires ») |

### 1.4 Exemple concret en Python

```python
# ── Programmation traditionnelle : filtrer les spams ──

def est_spam_classique(email: str) -> bool:
    """Approche à règles : on code CHAQUE cas à la main."""
    mots_interdits = ["gratuit", "gagné", "cliquez ici", "offre limitée"]
    for mot in mots_interdits:
        if mot in email.lower():
            return True
    return False

# Problème : et si le spammeur écrit "gr@tuit" ou "G.R.A.T.U.I.T" ?
# Il faut ajouter une règle à chaque nouveau cas → infini !

# ── Machine Learning : on montre des exemples ──
# On ne code PAS les règles. On donne 10 000 emails étiquetés :
#   - "Vous avez gagné un iPhone !" → spam
#   - "Réunion demain à 10h"       → pas spam
#   - ...
# Et l'algorithme APPREND ce qui distingue un spam d'un non-spam.
```

> ⚠️ **Attention** : "Le ML ne remplace pas la programmation classique. Si le problème peut se résoudre avec une formule ou des règles simples (calcul de TVA, tri alphabétique), le ML est **excessif** et **moins fiable**."

---

## 2. 📊 Les 3 grandes familles du ML

### 2.1 Vue d'ensemble

```
                    Machine Learning
                         │
          ┌──────────────┼──────────────┐
          │              │              │
    ┌─────▼─────┐  ┌────▼────┐  ┌─────▼──────┐
    │ Supervisé │  │  Non-   │  │Renforcement│
    │           │  │supervisé│  │            │
    └─────┬─────┘  └────┬────┘  └─────┬──────┘
          │              │              │
    On a les        On n'a PAS     L'agent apprend
    réponses        les réponses   par essai-erreur
    (étiquettes)                   (récompenses)
```

### 2.2 Apprentissage supervisé — « Apprendre avec un professeur »

**Principe** : on fournit au modèle des exemples **avec la bonne réponse** (étiquette / label). Le modèle apprend la relation entre les caractéristiques (features) et la réponse (target).

**Analogie** : un élève qui révise avec un corrigé. Il regarde les exercices, compare ses réponses au corrigé, et s'améliore.

| Sous-type | Question posée | Exemples du quotidien |
|-----------|---------------|----------------------|
| **Classification** | « Quelle catégorie ? » | Email → spam ou pas spam ? Photo → chat ou chien ? Client → va partir ou rester ? |
| **Régression** | « Quelle valeur numérique ? » | Appartement → quel prix ? Patient → quelle température demain ? Produit → combien de ventes ? |

```python
# Exemple simplifié de supervisé (classification)
# On a des données AVEC les réponses

donnees_entrainement = [
    {"taille": 180, "poids": 80, "sport": "basketball"},   # ← réponse connue
    {"taille": 160, "poids": 55, "sport": "gymnastique"},   # ← réponse connue
    {"taille": 175, "poids": 90, "sport": "rugby"},         # ← réponse connue
]

# Le modèle apprend : grande taille + poids moyen → basketball, etc.
# Puis on lui donne un NOUVEAU cas :
nouveau = {"taille": 182, "poids": 78}
# Le modèle prédit : "basketball" (sans qu'on lui dise !)
```

### 2.3 Apprentissage non-supervisé — « Apprendre sans professeur »

**Principe** : on donne des données **sans étiquette**. Le modèle cherche des **structures cachées** — des groupes, des motifs, des anomalies.

**Analogie** : un enfant qui trie ses Lego par couleur sans qu'on lui ait jamais dit ce qu'est une « couleur ». Il remarque tout seul que certaines pièces se ressemblent.

| Sous-type | Question posée | Exemples du quotidien |
|-----------|---------------|----------------------|
| **Clustering** | « Quels groupes existent ? » | Clients → segments marketing. Articles → thèmes. Patients → profils de risque. |
| **Réduction de dimension** | « Quelles variables sont redondantes ? » | 100 capteurs → 5 informations essentielles. Visualiser des données en 2D. |
| **Détection d'anomalies** | « Qu'est-ce qui est anormal ? » | Transaction bancaire frauduleuse. Pièce défectueuse sur une chaîne de production. |

```python
# Exemple simplifié de non-supervisé (clustering)
# On a des données SANS les réponses

clients = [
    {"age": 22, "depenses_mensuelles": 50},
    {"age": 23, "depenses_mensuelles": 45},
    {"age": 55, "depenses_mensuelles": 300},
    {"age": 58, "depenses_mensuelles": 280},
    {"age": 35, "depenses_mensuelles": 150},
]

# Pas d'étiquette ! Le modèle découvre TOUT SEUL :
# → Groupe 1 : jeunes, faibles dépenses
# → Groupe 2 : seniors, fortes dépenses
# → Groupe 3 : âge moyen, dépenses moyennes
```

### 2.4 Apprentissage par renforcement — « Apprendre par essai-erreur »

**Principe** : un **agent** agit dans un **environnement**, reçoit des **récompenses** (ou des punitions) et apprend à maximiser la récompense totale.

**Analogie** : un chien qui apprend des tours. Il essaie des actions au hasard. Quand il s'assoit sur commande → friandise (récompense +1). Quand il saute sur le canapé → « non ! » (punition -1). Avec le temps, il apprend la stratégie optimale.

| Composant | Exemple : jeu vidéo | Exemple : voiture autonome |
|-----------|---------------------|---------------------------|
| **Agent** | Le personnage du jeu | Le logiciel de conduite |
| **Environnement** | Le monde du jeu | La route, les autres voitures |
| **Actions** | Gauche, droite, sauter | Accélérer, freiner, tourner |
| **Récompense** | +10 points, -1 vie | +1 arrivée saine, -100 accident |

```python
# Pseudo-code simplifié de renforcement
# (on ne code pas ça en vrai dès le début !)

for episode in range(10000):
    etat = environnement.reset()
    while not termine:
        action = agent.choisir_action(etat)        # explore ou exploite
        etat_suivant, recompense = environnement.step(action)
        agent.apprendre(etat, action, recompense)   # met à jour sa stratégie
        etat = etat_suivant
# Après 10 000 épisodes, l'agent est devenu expert !
```

### 2.5 Tableau récapitulatif des 3 familles

| Critère | Supervisé | Non-supervisé | Renforcement |
|---------|-----------|---------------|--------------|
| **Données étiquetées ?** | Oui | Non | Non (récompenses) |
| **Objectif** | Prédire une valeur / catégorie | Trouver des structures | Maximiser une récompense |
| **Difficulté** | Moyenne | Élevée (pas de vérité terrain) | Très élevée |
| **Besoin en données** | Moyen à élevé | Élevé | Très élevé (simulations) |
| **Cas d'usage principal** | Prédiction | Exploration | Contrôle / jeux |
| **Algorithmes populaires** | Régression, Random Forest, SVM | K-Means, DBSCAN, PCA | Q-Learning, PPO, DQN |

> 💡 **Conseil** : "En tant que Data Engineer, 90 % des projets ML que vous rencontrerez seront du **supervisé**. C'est là que les données que vous préparez dans vos pipelines seront le plus directement utilisées."

---

## 3. 📖 Vocabulaire essentiel défini par l'usage

### 3.1 Les données — le carburant du ML

Sans données, pas de ML. C'est aussi simple que ça. Un modèle ML est **aussi bon que les données** qu'on lui fournit.

**Analogie** : les données sont au ML ce que l'essence est à une voiture. Même le meilleur moteur du monde ne roulera pas avec du mauvais carburant (données sales, incomplètes, biaisées).

```python
import pandas as pd

# Voici un VRAI dataset — des données sur des maisons
data = {
    "surface_m2": [45, 70, 120, 85, 200, 55, 95, 150],
    "nb_pieces":  [2,  3,  5,   4,  6,   2,  4,  5],
    "quartier":   ["centre", "banlieue", "centre", "banlieue",
                   "centre", "banlieue", "centre", "banlieue"],
    "annee_construction": [1980, 1995, 2010, 2005, 2020, 1970, 2000, 2015],
    "prix_euros": [150000, 180000, 350000, 220000, 550000, 130000, 280000, 380000],
}

df = pd.DataFrame(data)
print(df)
```

```
   surface_m2  nb_pieces  quartier  annee_construction  prix_euros
0          45          2    centre                1980      150000
1          70          3  banlieue                1995      180000
2         120          5    centre                2010      350000
3          85          4  banlieue                2005      220000
4         200          6    centre                2020      550000
5          55          2  banlieue                1970      130000
6          95          4    centre                2000      280000
7         150          5  banlieue                2015      380000
```

### 3.2 Les features — les caractéristiques qu'on mesure

Les **features** (ou caractéristiques, variables explicatives, variables d'entrée) sont les colonnes que le modèle utilise pour faire sa prédiction. Ce sont les **indices** que le modèle analyse.

```python
# Dans notre dataset maisons :
features = df[["surface_m2", "nb_pieces", "quartier", "annee_construction"]]
print("Features (X) :")
print(features)
```

```
   surface_m2  nb_pieces  quartier  annee_construction
0          45          2    centre                1980
1          70          3  banlieue                1995
2         120          5    centre                2010
...
```

**Quelques exemples de features selon le domaine :**

| Domaine | Features possibles |
|---------|-------------------|
| Immobilier | Surface, nombre de pièces, quartier, étage, année |
| Santé | Âge, poids, tension artérielle, taux de cholestérol |
| Marketing | Nombre de visites, temps passé sur le site, nombre de clics |
| Finance | Revenu mensuel, montant du crédit, historique de paiement |
| E-commerce | Nombre de commandes, panier moyen, ancienneté client |

### 3.3 La target — ce qu'on veut prédire

La **target** (ou variable cible, label, étiquette, variable de sortie) est la colonne qu'on veut que le modèle **prédise**. C'est la « bonne réponse ».

```python
# Dans notre dataset maisons :
target = df["prix_euros"]
print("Target (y) :")
print(target)
```

```
0    150000
1    180000
2    350000
3    220000
4    550000
5    130000
6    280000
7    380000
Name: prix_euros, dtype: int64
```

> 💡 **Conseil** : "La première question à se poser dans un projet ML est toujours : **qu'est-ce que je veux prédire ?** La réponse, c'est votre target. Tout le reste, ce sont vos features."

### 3.4 L'entraînement — la phase d'apprentissage

L'**entraînement** (ou apprentissage, fitting) est le processus pendant lequel le modèle examine les données et ajuste ses paramètres internes pour faire de meilleures prédictions.

```
╔═══════════════════════════════════════════════════════════╗
║                    ENTRAÎNEMENT                           ║
║                                                           ║
║   Données ──► Le modèle observe les exemples              ║
║           ──► Il fait une prédiction                      ║
║           ──► Il compare avec la vraie réponse            ║
║           ──► Il ajuste ses paramètres                    ║
║           ──► Il recommence (des milliers de fois)        ║
║           ──► Il devient de plus en plus précis           ║
╚═══════════════════════════════════════════════════════════╝
```

**Analogie** : un étudiant qui prépare un examen. Il fait des exercices (données d'entraînement), vérifie ses réponses (compare prédiction vs réalité), comprend ses erreurs (ajuste ses paramètres), et recommence jusqu'à maîtriser le sujet.

### 3.5 La prédiction — l'utilisation du modèle

La **prédiction** (ou inférence) est le moment où on utilise le modèle entraîné sur de **nouvelles données** qu'il n'a jamais vues.

```python
# Après entraînement, on peut prédire le prix d'une NOUVELLE maison :
nouvelle_maison = {
    "surface_m2": 100,
    "nb_pieces": 4,
    "quartier": "centre",
    "annee_construction": 2018,
}
# Le modèle prédit : ~310 000 € (sans qu'on lui dise la réponse !)
```

### 3.6 Récapitulatif visuel

```
┌─────────────────────────────────────────────────────────────────┐
│                        VOCABULAIRE ML                           │
│                                                                 │
│  DONNÉES          = le tableau complet (lignes + colonnes)      │
│  ─────────────────────────────────────────────                  │
│  │ surface │ pièces │ quartier │ prix   │                       │
│  │---------|--------|----------|--------|                       │
│  │   45    │   2    │  centre  │ 150000 │  ← une OBSERVATION   │
│  │   70    │   3    │ banlieue │ 180000 │    (un exemple)       │
│  ─────────────────────────────────────────────                  │
│       ▲         ▲        ▲         ▲                            │
│       └─────────┴────────┘         │                            │
│            FEATURES (X)        TARGET (y)                       │
│         « les indices »     « la réponse »                      │
│                                                                 │
│  ENTRAÎNEMENT = le modèle apprend sur ces données               │
│  PRÉDICTION   = le modèle prédit sur de nouvelles données       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. 📅 Bref historique du Machine Learning

Le ML n'est pas né hier. Voici les dates clés qui ont façonné le domaine :

| Année | Événement | Pourquoi c'est important |
|-------|-----------|--------------------------|
| **1943** | McCulloch & Pitts : premier modèle de neurone artificiel | Les bases mathématiques du réseau de neurones |
| **1950** | Alan Turing : « Les machines peuvent-elles penser ? » | Le Test de Turing pose les fondations conceptuelles de l'IA |
| **1957** | Frank Rosenblatt : le Perceptron | Premier algorithme d'apprentissage — un neurone artificiel qui apprend |
| **1969** | Minsky & Papert critiquent le Perceptron | Premier « hiver de l'IA » — les financements s'arrêtent |
| **1986** | Rétropropagation du gradient (Rumelhart, Hinton) | On peut enfin entraîner des réseaux à plusieurs couches |
| **1997** | Deep Blue (IBM) bat Kasparov aux échecs | Force brute + règles, **pas** du ML au sens moderne |
| **2001** | Random Forest (Breiman) | Algorithme robuste, encore très utilisé aujourd'hui |
| **2006** | Geoffrey Hinton relance le Deep Learning | Les réseaux profonds reviennent sur le devant de la scène |
| **2012** | AlexNet gagne ImageNet | Le Deep Learning explose — révolution de la vision par ordinateur |
| **2014** | GANs (Goodfellow) | Les machines apprennent à **générer** des images réalistes |
| **2016** | AlphaGo (DeepMind) bat Lee Sedol au Go | L'apprentissage par renforcement atteint un niveau surhumain |
| **2017** | Transformer (« Attention Is All You Need ») | Architecture qui va révolutionner le traitement du langage |
| **2022** | ChatGPT (OpenAI) | Les LLMs deviennent accessibles au grand public |
| **2023+** | IA générative explose (GPT-4, Midjourney, Claude) | Le ML entre dans la vie quotidienne de millions de personnes |

> 💡 **Conseil** : "Vous n'avez pas besoin de retenir toutes ces dates. Retenez l'essentiel : le ML existe depuis les années 1950, mais c'est l'explosion des données et de la puissance de calcul (GPU) après 2012 qui a tout changé."

---

## 5. 🚀 Projet découverte : utiliser un modèle pré-entraîné

### 5.1 Objectif

Utiliser un modèle ML **sans comprendre le code**. Observer l'entrée et la sortie. Constater que « ça marche ».

On va utiliser **Hugging Face**, une plateforme qui met à disposition des milliers de modèles pré-entraînés.

### 5.2 Installation

```bash
# Installer la librairie transformers de Hugging Face
uv add transformers torch
```

### 5.3 Analyse de sentiment — le modèle devine l'émotion d'un texte

```python
from transformers import pipeline

# Charger un modèle pré-entraîné d'analyse de sentiment
analyseur = pipeline("sentiment-analysis")

# Tester avec des phrases en anglais
textes = [
    "I love this product, it's amazing!",
    "This is the worst experience I've ever had.",
    "The weather is okay today.",
]

for texte in textes:
    resultat = analyseur(texte)
    print(f"Texte   : {texte}")
    print(f"Résultat: {resultat}")
    print()
```

**Sortie attendue :**

```
Texte   : I love this product, it's amazing!
Résultat: [{'label': 'POSITIVE', 'score': 0.9998}]

Texte   : This is the worst experience I've ever had.
Résultat: [{'label': 'NEGATIVE', 'score': 0.9997}]

Texte   : The weather is okay today.
Résultat: [{'label': 'POSITIVE', 'score': 0.9653}]
```

### 5.4 Ce qu'il faut observer

```
┌────────────────────────────────────────────────────────┐
│                  MODÈLE PRÉ-ENTRAÎNÉ                   │
│                                                        │
│  ENTRÉE (texte) ──► BOÎTE NOIRE ──► SORTIE (label)    │
│                                                        │
│  "I love this"   ──►  ???????????  ──► POSITIVE 99.9%  │
│  "Worst ever"    ──►  ???????????  ──► NEGATIVE 99.9%  │
│                                                        │
│  On ne sait pas COMMENT ça marche en interne.          │
│  Mais on constate que ça marche.                       │
│  C'est normal. On comprendra progressivement.          │
└────────────────────────────────────────────────────────┘
```

### 5.5 Exercice : tester d'autres pipelines

```python
from transformers import pipeline

# ── Classification zero-shot (pas besoin d'entraînement !) ──
classifieur = pipeline("zero-shot-classification")

resultat = classifieur(
    "Le nouveau restaurant italien du quartier est excellent",
    candidate_labels=["cuisine", "sport", "technologie", "politique"],
)
print(resultat["labels"][0])    # → "cuisine"
print(resultat["scores"][0])    # → ~0.92

# ── Résumé automatique ──
resumeur = pipeline("summarization")

texte_long = """
Le Machine Learning est une branche de l'intelligence artificielle qui permet
aux ordinateurs d'apprendre à partir de données. Plutôt que de programmer
explicitement chaque règle, on fournit des exemples au programme qui découvre
les patterns par lui-même. Cette approche est particulièrement efficace pour
les tâches complexes comme la reconnaissance d'images ou le traitement du
langage naturel.
"""
resume = resumeur(texte_long, max_length=50, min_length=20)
print(resume[0]["summary_text"])
```

> ⚠️ **Attention** : "Le téléchargement du premier modèle peut prendre plusieurs minutes (plusieurs centaines de Mo). C'est normal. Les modèles suivants seront mis en cache."

---

## 6. ✅ Quand utiliser (et NE PAS utiliser) le ML

### 6.1 Le ML est un bon choix quand...

1. **Les règles sont trop complexes** pour être codées à la main (reconnaissance d'images, traduction)
2. **Les règles changent fréquemment** (détection de spam — les spammeurs s'adaptent)
3. **Il y a beaucoup de données** disponibles pour apprendre
4. **On accepte une marge d'erreur** (le ML n'est jamais fiable à 100 %)
5. **Le problème est bien défini** (on sait ce qu'on veut prédire)

### 6.2 Le ML est un MAUVAIS choix quand...

1. **Les règles sont simples** et connues (calcul de TVA, conversion de devises)
2. **Il n'y a pas assez de données** (moins de quelques centaines d'exemples en général)
3. **L'erreur est inacceptable** (calcul de paie, transactions financières critiques)
4. **Le problème est mal défini** (on ne sait pas ce qu'on cherche)
5. **Les résultats doivent être 100 % explicables** (certains contextes réglementaires)

### 6.3 Tableau de décision

| Situation | ML ? | Pourquoi |
|-----------|------|----------|
| Calculer le total d'une facture | ❌ Non | Règle simple : somme des lignes × TVA |
| Détecter des emails frauduleux | ✅ Oui | Règles trop complexes, changent tout le temps |
| Trier une liste par ordre alphabétique | ❌ Non | Algorithme de tri classique, parfait |
| Recommander un film sur Netflix | ✅ Oui | Beaucoup de données, goûts complexes |
| Convertir des Celsius en Fahrenheit | ❌ Non | Formule exacte : F = C × 9/5 + 32 |
| Prédire le prix d'un appartement | ✅ Oui | Beaucoup de variables, relations non-linéaires |
| Afficher « Bonjour, Jean ! » | ❌ Non | Simple concaténation de chaînes |
| Détecter un cancer sur une radio | ✅ Oui | Trop complexe pour l'œil humain seul |
| Calculer l'âge d'une personne | ❌ Non | Année courante - année de naissance |
| Prédire si un client va quitter l'entreprise | ✅ Oui | Multiples facteurs subtils, données disponibles |
| Vérifier qu'un email est valide (format) | ❌ Non | Expression régulière (regex) suffit |
| Traduire un texte dans 100 langues | ✅ Oui | Impossible à coder par des règles |

> 💡 **Conseil** : "Avant chaque projet ML, posez-vous la question : « Est-ce qu'un stagiaire pourrait résoudre ce problème avec un tableur Excel et 30 minutes ? » Si oui, vous n'avez probablement pas besoin de ML."

### 6.4 Le piège de la « solution ML pour tout »

```
╔══════════════════════════════════════════════════════════╗
║          ❌ NE FAITES PAS ÇA                            ║
║                                                          ║
║  « On a un problème »                                    ║
║       ↓                                                  ║
║  « Utilisons du ML ! »                                   ║
║       ↓                                                  ║
║  3 mois de travail, 50 000 € de GPU                     ║
║       ↓                                                  ║
║  « En fait, un GROUP BY en SQL suffisait... »            ║
║                                                          ║
╠══════════════════════════════════════════════════════════╣
║          ✅ FAITES PLUTÔT ÇA                            ║
║                                                          ║
║  « On a un problème »                                    ║
║       ↓                                                  ║
║  « Peut-on le résoudre avec des règles simples ? »       ║
║       ↓ Non                                              ║
║  « A-t-on assez de données ? »                           ║
║       ↓ Oui                                              ║
║  « Le ML est probablement pertinent. Testons. »          ║
╚══════════════════════════════════════════════════════════╝
```

---

## 7. 🐍 L'écosystème Python pour le ML

### 7.1 Pourquoi Python ?

Python domine le ML pour trois raisons :
1. **Syntaxe simple** — proche du pseudo-code, idéal pour expérimenter
2. **Écosystème massif** — des milliers de librairies spécialisées
3. **Communauté immense** — facile de trouver de l'aide et des tutoriels

### 7.2 Les librairies essentielles

| Librairie | Rôle | Analogie |
|-----------|------|----------|
| **NumPy** | Calcul numérique (tableaux, matrices) | La calculatrice scientifique |
| **Pandas** | Manipulation de données (DataFrames) | Le tableur Excel surpuissant |
| **Matplotlib** | Visualisation (graphiques de base) | Le crayon pour dessiner |
| **Seaborn** | Visualisation statistique (plus joli) | Le crayon + la palette de couleurs |
| **Scikit-learn** | Algorithmes ML classiques | La boîte à outils ML |
| **XGBoost / LightGBM** | Algorithmes de boosting performants | L'outil de précision |
| **TensorFlow / PyTorch** | Deep Learning (réseaux de neurones) | L'usine industrielle |
| **Hugging Face** | Modèles pré-entraînés (NLP, vision) | Le magasin de modèles prêts à l'emploi |
| **MLflow** | Suivi des expériences, déploiement | Le carnet de labo du chercheur |

### 7.3 La stack typique d'un projet ML

```
┌─────────────────────────────────────────────────────────┐
│                    PROJET ML TYPIQUE                     │
│                                                         │
│  ┌───────────┐   ┌──────────┐   ┌────────────────────┐ │
│  │  Données  │──►│  Pandas  │──►│  Exploration (EDA) │ │
│  │  (CSV,    │   │  NumPy   │   │  Matplotlib        │ │
│  │   SQL,    │   │          │   │  Seaborn           │ │
│  │   API)    │   │          │   │                    │ │
│  └───────────┘   └──────────┘   └────────┬───────────┘ │
│                                          │              │
│                                          ▼              │
│                                 ┌────────────────────┐  │
│                                 │  Préparation       │  │
│                                 │  (nettoyage,       │  │
│                                 │   feature eng.)    │  │
│                                 └────────┬───────────┘  │
│                                          │              │
│                                          ▼              │
│                                 ┌────────────────────┐  │
│                                 │  Modélisation      │  │
│                                 │  Scikit-learn      │  │
│                                 │  XGBoost           │  │
│                                 └────────┬───────────┘  │
│                                          │              │
│                                          ▼              │
│                                 ┌────────────────────┐  │
│                                 │  Évaluation        │  │
│                                 │  Scikit-learn      │  │
│                                 │  MLflow            │  │
│                                 └────────┬───────────┘  │
│                                          │              │
│                                          ▼              │
│                                 ┌────────────────────┐  │
│                                 │  Déploiement       │  │
│                                 │  FastAPI / Flask   │  │
│                                 │  Docker / K8s      │  │
│                                 └────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 7.4 Exemple : vérifier que tout fonctionne

```python
# Vérification rapide de l'installation
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import __version__ as sklearn_version

print(f"NumPy     : {np.__version__}")
print(f"Pandas    : {pd.__version__}")
print(f"Matplotlib: {plt.matplotlib.__version__}")
print(f"Seaborn   : {sns.__version__}")
print(f"Scikit-learn: {sklearn_version}")
print("\n✅ Tout est installé correctement !")
```

---

## 🎯 Points clés à retenir

1. Le **Machine Learning** permet aux programmes d'**apprendre à partir de données** au lieu de suivre des règles codées à la main.
2. Il existe **3 familles** : supervisé (avec étiquettes), non-supervisé (sans étiquettes), renforcement (récompenses).
3. Le vocabulaire essentiel : **données** (le carburant), **features** (les indices), **target** (la réponse), **entraînement** (l'apprentissage), **prédiction** (l'utilisation).
4. Le ML **n'est pas toujours la bonne solution** : si une règle simple suffit, utilisez une règle simple.
5. On peut utiliser des **modèles pré-entraînés** (Hugging Face) sans comprendre le fonctionnement interne — c'est normal au début.
6. **Python** est le langage dominant du ML grâce à son écosystème (Pandas, Scikit-learn, PyTorch, etc.).
7. Le ML existe depuis les années 1950, mais c'est l'explosion des **données + puissance de calcul** après 2012 qui a tout changé.

---

## ✅ Checklist de validation

Avant de passer au chapitre suivant, vérifiez que vous pouvez :

- [ ] Expliquer la différence entre programmation classique et ML **avec vos propres mots**
- [ ] Donner un exemple concret pour chacune des 3 familles d'apprentissage
- [ ] Définir : données, features, target, entraînement, prédiction
- [ ] Citer au moins 3 situations où le ML est pertinent et 3 où il ne l'est pas
- [ ] Exécuter un modèle pré-entraîné Hugging Face et interpréter la sortie
- [ ] Nommer les 5 librairies Python essentielles pour le ML et leur rôle
- [ ] Charger un dataset avec pandas et afficher les premières lignes

---

**Précédent** : — (début de la formation) | **Suivant** : [Chapitre 2 — Anatomie d'un Problème ML →](02-anatomie-probleme-ml.md)

---

## 🎥 Vidéos pour approfondir

| Vidéo | Chaîne | Langue | Ce que tu y apprends |
|---|---|:---:|---|
| [Introduction au Machine Learning](https://www.youtube.com/results?search_query=machine+learnia+introduction+machine+learning) | Machine Learnia | FR | Vue d'ensemble du ML, cas d'usage |
| [A Gentle Intro to Machine Learning](https://www.youtube.com/results?search_query=statquest+machine+learning+introduction) | StatQuest | EN | Les grandes familles d'algorithmes |
| [Supervisé vs non-supervisé](https://www.youtube.com/results?search_query=statquest+supervised+vs+unsupervised+learning) | StatQuest | EN | La distinction fondamentale |

> 💡 Liens de recherche YouTube (toujours valides) : clique, la meilleure vidéo est en tête.
