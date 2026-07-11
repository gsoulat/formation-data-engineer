# C4 Architecture & Diagrammes Techniques

## Objectifs pédagogiques

À l'issue de ce module, vous serez capable de :

- Expliquer les 4 niveaux du modèle C4 et quand utiliser chacun
- Dessiner un diagramme Context et Container pour un système donné
- Écrire des diagrammes PlantUML avec la bibliothèque C4-PlantUML
- Utiliser Structurizr DSL pour décrire une architecture complète
- Comparer les outils de diagrammes-as-code (PlantUML, Mermaid, Structurizr)

---

## Contenu du module

| Fichier | Thème |
|--------|-------|
| `01-modele-c4.md` | Les 4 niveaux C4, quand utiliser chaque niveau |
| `02-plantuml.md` | Syntaxe PlantUML, bibliothèque C4, diagrammes Context/Container/Component |
| `03-structurizr.md` | DSL Structurizr, workspace, vues, export |
| `04-autres-outils.md` | Mermaid C4, draw.io, Lucidchart, diagrams-as-code |
| `exemples/` | Microservices et plateforme data en C4 |
| `exercices/` | Dessiner Context + Container pour un système donné |

---

## Pourquoi ce module ?

> "Un diagramme d'architecture qui n'est pas maintenu est pire que l'absence de diagramme."

Les diagrammes qui vivent dans des présentations PowerPoint ou des wikis séparés du code deviennent obsolètes en quelques mois. Le mouvement **Diagrams as Code** répond à ce problème : les diagrammes sont du texte versionné avec le code.

C4 fournit un langage visuel commun — n'importe qui dans l'équipe peut lire et comprendre l'architecture sans formation spécifique.

---

## Durée estimée

- **Théorie** : 3 heures
- **Exercices pratiques** : 2 heures
- **Total** : 5 heures

---

## Outils requis

| Outil | Installation | Usage |
|-------|-------------|-------|
| PlantUML | VSCode extension ou plantuml.com | Diagrammes C4 en local |
| Structurizr Lite | Docker | Workspace C4 complet |
| Mermaid | Intégré GitHub/GitLab | Diagrammes dans le Markdown |

```bash
# Structurizr Lite via Docker
docker run -it --rm -p 8080:8080 \
  -v $(pwd):/usr/local/structurizr \
  structurizr/lite
```

---

## Ressources

- [C4 Model officiel](https://c4model.com) — Simon Brown
- [C4-PlantUML GitHub](https://github.com/plantuml-stdlib/C4-PlantUML)
- [Structurizr DSL docs](https://docs.structurizr.com/dsl)
- [Livre : "Software Architecture for Developers" — Simon Brown](https://leanpub.com/software-architecture-for-developers)
