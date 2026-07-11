# CrewAI Flows — Orchestration Événementielle

## Objectifs

- Comprendre ce que sont les CrewAI Flows et leur apport vs les Crews classiques
- Utiliser `@start`, `@listen`, `@router` pour construire des workflows événementiels
- Gérer l'état d'un Flow avec `BaseModel` Pydantic
- Composer des Flows et des Crews dans la même application
- Implémenter des flux conditionnels et parallèles

---

## Qu'est-ce qu'un CrewAI Flow ?

Les **Flows** sont une fonctionnalité récente de CrewAI (v0.70+) qui apporte une couche de programmation **événementielle** au-dessus des Crews.

Un Crew est une équipe qui exécute un ensemble de tâches de façon séquentielle ou hiérarchique. Un Flow permet d'orchestrer **plusieurs Crews** et **fonctions Python** avec une logique conditionnelle et des événements.

```
Crew (sans Flow)              Flow (avec Crews imbriqués)
───────────────────           ──────────────────────────────────
Tâche 1 → Agent A             @start() → collecte_donnees()
     ↓                              ↓
Tâche 2 → Agent B             @listen(collecte_donnees)
     ↓                        → si données ok : crew_analyse
Tâche 3 → Agent C             → si données incomplètes : crew_collecte_supplementaire
                                    ↓
                              @listen(crew_analyse)
                              → generer_rapport_final()
```

**Résumé** : Flows = glue entre Crews + logique conditionnelle + état global partagé.

---

## Installation et imports

```python
# Nécessite crewai >= 0.70
pip install "crewai>=0.70" crewai-tools

from crewai.flow.flow import Flow, listen, start, router, and_, or_
from pydantic import BaseModel
```

---

## Structure d'un Flow

```python
from crewai.flow.flow import Flow, listen, start
from pydantic import BaseModel
from typing import Optional

# 1. Définir l'état du Flow (partagé entre toutes les méthodes)
class EtatFlowAnalyse(BaseModel):
    sujet: str = ""
    donnees_brutes: str = ""
    analyse: str = ""
    rapport_final: str = ""
    qualite_score: float = 0.0
    erreur: Optional[str] = None

# 2. Créer le Flow
class FlowAnalyseComplete(Flow[EtatFlowAnalyse]):

    @start()
    def initialiser(self):
        """Première méthode exécutée — déclenche le Flow."""
        print(f"Démarrage de l'analyse sur : {self.state.sujet}")
        return self.state.sujet  # La valeur retournée est passée aux listeners

    @listen(initialiser)
    def collecter_donnees(self, sujet: str):
        """Déclenchée quand initialiser() se termine."""
        print(f"Collecte des données sur : {sujet}")
        # Simulation de collecte
        self.state.donnees_brutes = f"Données collectées sur {sujet}: [données simulées]"
        return self.state.donnees_brutes

    @listen(collecter_donnees)
    def analyser(self, donnees: str):
        """Déclenchée quand collecter_donnees() se termine."""
        print("Analyse en cours...")
        self.state.analyse = f"Analyse : {donnees[:50]}... [analyse approfondie]"
        return self.state.analyse

    @listen(analyser)
    def produire_rapport(self, analyse: str):
        """Dernière étape : production du rapport."""
        self.state.rapport_final = f"RAPPORT FINAL\n\n{analyse}\n\nConclusion : analyse terminée avec succès."
        print("Rapport produit !")
        return self.state.rapport_final


# 3. Exécuter le Flow
flow = FlowAnalyseComplete()
resultat = flow.kickoff(inputs={"sujet": "Intelligence Artificielle Générative"})
print(resultat)
print(f"\nÉtat final : {flow.state}")
```

---

## @router — Branchements conditionnels

Le décorateur `@router` permet de brancher le flux selon une condition :

```python
from crewai.flow.flow import Flow, listen, start, router
from pydantic import BaseModel
from typing import Literal

class EtatAvecValidation(BaseModel):
    sujet: str = ""
    donnees: str = ""
    qualite: str = ""  # "haute" | "faible" | "nulle"
    rapport: str = ""

class FlowAvecValidation(Flow[EtatAvecValidation]):

    @start()
    def demarrer(self):
        print(f"Démarrage : {self.state.sujet}")
        return self.state.sujet

    @listen(demarrer)
    def collecter(self, sujet: str):
        """Simule une collecte qui peut réussir ou échouer."""
        print("Collecte...")
        if "vide" in sujet.lower():
            self.state.donnees = ""
            self.state.qualite = "nulle"
        elif "incomplet" in sujet.lower():
            self.state.donnees = "Données partielles disponibles."
            self.state.qualite = "faible"
        else:
            self.state.donnees = f"Données complètes sur {sujet}."
            self.state.qualite = "haute"

        return self.state.qualite

    @router(collecter)
    def evaluer_qualite(self, qualite: str) -> Literal["bonne_qualite", "qualite_moyenne", "pas_de_donnees"]:
        """Routeur — décide quelle branche prendre selon la qualité des données."""
        print(f"Évaluation qualité : {qualite}")
        if qualite == "haute":
            return "bonne_qualite"
        elif qualite == "faible":
            return "qualite_moyenne"
        else:
            return "pas_de_donnees"

    @listen("bonne_qualite")
    def analyser_completement(self):
        """Branche : données complètes → analyse approfondie."""
        print("Analyse complète...")
        self.state.rapport = f"Rapport complet basé sur données de haute qualité.\n{self.state.donnees}"
        return self.state.rapport

    @listen("qualite_moyenne")
    def analyser_partiellement(self):
        """Branche : données incomplètes → analyse partielle avec avertissements."""
        print("Analyse partielle (données insuffisantes)...")
        self.state.rapport = f"⚠️ Analyse partielle — données incomplètes.\n{self.state.donnees}\nRecommandation : compléter la collecte."
        return self.state.rapport

    @listen("pas_de_donnees")
    def signaler_erreur(self):
        """Branche : pas de données → rapport d'erreur."""
        print("Erreur : aucune donnée disponible.")
        self.state.rapport = "❌ Impossible de générer un rapport : aucune donnée collectée."
        return self.state.rapport

    @listen(analyser_completement, analyser_partiellement, signaler_erreur)
    def finaliser(self, rapport: str):
        """Déclenchée après TOUTES les branches possibles — finalisation commune."""
        print("\n=== RAPPORT FINAL ===")
        print(rapport)
        return rapport


# Tests des différentes branches
for sujet_test in ["Machine Learning", "Données incomplètes sur Python", "Sujet vide"]:
    print(f"\n{'='*50}")
    print(f"Test : {sujet_test}")
    flow = FlowAvecValidation()
    flow.kickoff(inputs={"sujet": sujet_test})
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** L'exécution du `FlowAvecValidation` pour les 3 sujets test différents, montrant que les branches activées sont différentes selon la qualité des données — la branche "bonne_qualite" pour le premier, "qualite_moyenne" pour le second, "pas_de_donnees" pour le troisième.
> **Expliquer :** C'est le pattern fondamental des Flows : une logique de contrôle Python qui orchestre des Crews ou des fonctions. Comparer avec un Crew classique où il faudrait mettre cette logique dans le Manager LLM — ici c'est du Python pur, déterministe et testable.

---

## Intégrer des Crews dans un Flow

L'usage le plus puissant : déclencher des Crews entiers depuis un Flow :

```python
# flow_avec_crews.py
import os
from typing import Optional
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai.flow.flow import Flow, listen, start, router
from pydantic import BaseModel
from langchain_openai import ChatOpenAI

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)

# ============================================================
# CREWS SPÉCIALISÉS
# ============================================================

def creer_crew_recherche(sujet: str) -> Crew:
    """Créer un crew de recherche pour un sujet donné."""
    chercheur = Agent(
        role="Chercheur",
        goal="Collecter des informations précises sur le sujet",
        backstory="Expert en recherche documentaire.",
        llm=llm, verbose=False
    )
    tache = Task(
        description=f"Recherche des informations clés sur : {sujet}. Trouve 3-5 faits importants.",
        expected_output="Liste de 3-5 faits importants avec sources.",
        agent=chercheur
    )
    return Crew(agents=[chercheur], tasks=[tache], process=Process.sequential, verbose=False)


def creer_crew_analyse(donnees: str) -> Crew:
    """Créer un crew d'analyse pour des données données."""
    analyste = Agent(
        role="Analyste",
        goal="Analyser les données et en extraire des insights",
        backstory="Expert en analyse de données et synthèse stratégique.",
        llm=llm, verbose=False
    )
    tache = Task(
        description=f"""Analyse ces données et produis des insights actionnables :

        {donnees}

        Identifie : tendances principales, opportunités, risques.""",
        expected_output="Analyse structurée avec tendances, opportunités et risques.",
        agent=analyste
    )
    return Crew(agents=[analyste], tasks=[tache], process=Process.sequential, verbose=False)


def creer_crew_rapport(recherche: str, analyse: str, sujet: str) -> Crew:
    """Créer un crew de rédaction de rapport final."""
    redacteur = Agent(
        role="Rédacteur Senior",
        goal="Produire un rapport professionnel et structuré",
        backstory="Rédacteur expert en rapports exécutifs.",
        llm=llm, verbose=False
    )
    tache = Task(
        description=f"""Rédige un rapport exécutif sur '{sujet}' basé sur :

        RECHERCHE : {recherche[:500]}...

        ANALYSE : {analyse[:500]}...

        Format : résumé exécutif (100 mots), points clés (5 bullets), recommandations (3 points).""",
        expected_output="Rapport exécutif structuré en markdown.",
        agent=redacteur
    )
    return Crew(agents=[redacteur], tasks=[tache], process=Process.sequential, verbose=False)


# ============================================================
# ÉTAT DU FLOW
# ============================================================

class EtatRapportFlow(BaseModel):
    sujet: str = ""
    domaine: str = ""         # "technologie" | "finance" | "general"
    donnees_recherche: str = ""
    analyse: str = ""
    rapport_final: str = ""
    besoin_analyse_approfondie: bool = False


# ============================================================
# FLOW PRINCIPAL
# ============================================================

class FlowProductionRapport(Flow[EtatRapportFlow]):

    @start()
    def classifier_sujet(self):
        """Classifie le sujet pour choisir le workflow adapté."""
        sujet = self.state.sujet.lower()

        if any(mot in sujet for mot in ["ia", "ml", "tech", "logiciel", "cloud", "api"]):
            self.state.domaine = "technologie"
        elif any(mot in sujet for mot in ["action", "bourse", "finance", "investissement", "marché"]):
            self.state.domaine = "finance"
        else:
            self.state.domaine = "general"

        print(f"[FLOW] Sujet classifié : domaine = {self.state.domaine}")
        return self.state.domaine

    @listen(classifier_sujet)
    def rechercher(self, domaine: str):
        """Lance le crew de recherche."""
        print(f"[FLOW] Lancement du crew de recherche (domaine: {domaine})...")
        crew = creer_crew_recherche(self.state.sujet)
        resultat = crew.kickoff()
        self.state.donnees_recherche = resultat.raw
        print(f"[FLOW] Recherche terminée ({len(self.state.donnees_recherche)} caractères)")
        return self.state.donnees_recherche

    @router(rechercher)
    def decider_profondeur_analyse(self, donnees: str):
        """Décide si une analyse approfondie est nécessaire."""
        # Analyse approfondie si les données sont riches (> 200 chars) ou domaine tech/finance
        if len(donnees) > 200 or self.state.domaine in ["technologie", "finance"]:
            self.state.besoin_analyse_approfondie = True
            return "analyse_approfondie"
        return "analyse_standard"

    @listen("analyse_approfondie")
    def analyser_en_profondeur(self):
        """Analyse approfondie pour les sujets complexes."""
        print("[FLOW] Lancement de l'analyse approfondie...")
        crew = creer_crew_analyse(self.state.donnees_recherche)
        resultat = crew.kickoff()
        self.state.analyse = f"[APPROFONDIE] {resultat.raw}"
        return self.state.analyse

    @listen("analyse_standard")
    def analyser_rapidement(self):
        """Analyse rapide pour les sujets simples."""
        print("[FLOW] Analyse rapide...")
        self.state.analyse = f"[STANDARD] Analyse synthétique : {self.state.donnees_recherche[:300]}"
        return self.state.analyse

    @listen(analyser_en_profondeur, analyser_rapidement)
    def rediger_rapport(self, analyse: str):
        """Lance le crew de rédaction — exécuté après TOUTES les branches d'analyse."""
        print("[FLOW] Rédaction du rapport final...")
        crew = creer_crew_rapport(
            self.state.donnees_recherche,
            analyse,
            self.state.sujet
        )
        resultat = crew.kickoff()
        self.state.rapport_final = resultat.raw
        return self.state.rapport_final

    @listen(rediger_rapport)
    def finaliser(self, rapport: str):
        """Publication du rapport."""
        print("\n" + "="*60)
        print("RAPPORT FINAL PRODUIT")
        print("="*60)
        print(rapport)
        return rapport


# Exécution
print("Démarrage du Flow de production de rapport...\n")
flow = FlowProductionRapport()
resultat = flow.kickoff(inputs={
    "sujet": "L'adoption de l'IA générative dans les entreprises françaises",
})

print(f"\nÉtat final du Flow :")
print(f"  Domaine : {flow.state.domaine}")
print(f"  Analyse approfondie : {flow.state.besoin_analyse_approfondie}")
print(f"  Rapport : {len(flow.state.rapport_final)} caractères")
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** L'exécution du `FlowProductionRapport` montrant la séquence des logs : classification → recherche → décision de profondeur → analyse (approfondie ici) → rédaction → rapport final. Afficher l'état final du Flow avec les métadonnées.
> **Expliquer :** Le Flow est le chef d'orchestre qui décide dynamiquement quel Crew lancer et dans quel ordre. La classification du sujet est faite en Python pur (déterministe) alors que chaque Crew utilise des LLMs. C'est la séparation intelligente entre logique métier (Flow) et intelligence (Crews).

---

## Exécution parallèle avec and_

```python
from crewai.flow.flow import Flow, listen, start, and_
from pydantic import BaseModel

class EtatParallele(BaseModel):
    sujet: str = ""
    analyse_technique: str = ""
    analyse_marche: str = ""
    synthese: str = ""

class FlowParallele(Flow[EtatParallele]):

    @start()
    def demarrer(self):
        return self.state.sujet

    @listen(demarrer)
    def analyser_techniquement(self, sujet: str):
        """S'exécute en parallèle avec analyser_marche."""
        print(f"[Parallèle A] Analyse technique de : {sujet}")
        self.state.analyse_technique = f"Analyse technique de {sujet}: [données techniques simulées]"
        return self.state.analyse_technique

    @listen(demarrer)  # Écoute aussi demarrer → parallèle !
    def analyser_marche(self, sujet: str):
        """S'exécute en parallèle avec analyser_techniquement."""
        print(f"[Parallèle B] Analyse de marché de : {sujet}")
        self.state.analyse_marche = f"Analyse marché de {sujet}: [données marché simulées]"
        return self.state.analyse_marche

    # and_() attend que LES DEUX analyses soient terminées avant de continuer
    @listen(and_(analyser_techniquement, analyser_marche))
    def synthetiser(self):
        """Exécutée SEULEMENT quand les deux analyses sont disponibles."""
        print("[Synthèse] Les deux analyses sont prêtes, synthèse en cours...")
        self.state.synthese = f"""SYNTHÈSE COMPLÈTE :
        Technique : {self.state.analyse_technique}
        Marché : {self.state.analyse_marche}"""
        return self.state.synthese


flow_p = FlowParallele()
flow_p.kickoff(inputs={"sujet": "Plateforme MLOps"})
print(flow_p.state.synthese)
```

---

## Persister l'état d'un Flow

```python
from crewai.flow.flow import Flow, listen, start
from pydantic import BaseModel
import json
import os

class EtatPersistant(BaseModel):
    sujet: str = ""
    etape_courante: str = "debut"
    resultats: dict = {}

class FlowAvecPersistence(Flow[EtatPersistant]):
    FICHIER_ETAT = "/tmp/flow_etat.json"

    def sauvegarder_etat(self):
        """Sauvegarde l'état sur disque."""
        with open(self.FICHIER_ETAT, "w") as f:
            json.dump(self.state.model_dump(), f, indent=2)
        print(f"[SAVE] État sauvegardé dans {self.FICHIER_ETAT}")

    @classmethod
    def reprendre(cls):
        """Recharge un état précédemment sauvegardé."""
        if os.path.exists(cls.FICHIER_ETAT):
            with open(cls.FICHIER_ETAT) as f:
                etat_sauvegarde = json.load(f)
            flow = cls()
            flow.state = EtatPersistant(**etat_sauvegarde)
            print(f"[RESTORE] État chargé, étape : {flow.state.etape_courante}")
            return flow
        return cls()

    @start()
    def etape_1(self):
        print("Étape 1 : initialisation")
        self.state.etape_courante = "etape_1_done"
        self.state.resultats["etape_1"] = "Données initiales collectées"
        self.sauvegarder_etat()
        return "continuer"

    @listen(etape_1)
    def etape_2(self, _):
        print("Étape 2 : traitement")
        self.state.etape_courante = "etape_2_done"
        self.state.resultats["etape_2"] = "Traitement effectué"
        self.sauvegarder_etat()
        return "terminé"
```

---

## Visualiser un Flow

```python
from crewai.flow.flow import Flow

# Générer un diagramme Mermaid du Flow
flow = FlowProductionRapport()
flow.plot("mon_flow")  # Génère mon_flow.html — diagramme interactif

# Ou afficher en console
print(flow.get_graph())
```

---

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** La sortie de `flow.plot("mon_flow")` — ouvrir le fichier HTML généré dans un navigateur et montrer le diagramme interactif du Flow avec les nœuds colorés, les connexions entre méthodes, et les branches conditionnelles visibles.
> **Expliquer :** Ce diagramme interactif est généré automatiquement à partir du code Python du Flow. C'est l'équivalent du `draw_mermaid()` de LangGraph mais pour les Flows. Pointer comment chaque `@listen` et `@router` crée une arête dans le graphe. Utile pour la documentation et la présentation à des non-développeurs.

---

## Quand utiliser un Flow vs un Crew

| Besoin | Solution recommandée |
|--------|---------------------|
| Pipeline de tâches séquentielles avec agents | Crew séquentiel |
| Orchestration hiérarchique dynamique | Crew hiérarchique |
| Logique conditionnelle complexe entre Crews | Flow avec @router |
| Exécution parallèle de plusieurs Crews | Flow avec and_/or_ |
| État global partagé entre plusieurs Crews | Flow avec BaseModel |
| Reprendre après une erreur | Flow avec persistence |
| Workflow simple sans branchements | Crew uniquement (pas besoin de Flow) |

---

## Points clés à retenir

1. `@start()` marque le point d'entrée du Flow — une seule méthode par Flow
2. `@listen(methode)` s'exécute automatiquement quand `methode` se termine
3. `@router(methode)` retourne une string qui pointe vers la prochaine branche
4. `@listen("nom_branche")` écoute le résultat d'un routeur
5. `and_(m1, m2)` attend que **les deux** méthodes aient terminé
6. L'état (`self.state`) est partagé entre toutes les méthodes du Flow
7. Un Flow peut **instancier et lancer des Crews** comme des fonctions normales
8. `flow.plot()` génère un diagramme HTML interactif du workflow

---

## Suite

Vous avez terminé le module CrewAI ! Passez à `Comparatif/01-quand-utiliser-quoi.md` pour le guide de décision entre les frameworks, puis aux exercices pratiques.
