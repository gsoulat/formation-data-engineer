# ADR — Architecture Decision Records

## Objectifs pédagogiques

À l'issue de ce module, vous serez capable de :

- Expliquer pourquoi documenter les décisions d'architecture est essentiel
- Rédiger un ADR au format MADR (Markdown Any Decision Record)
- Identifier les bonnes décisions à documenter (et celles à ne pas documenter)
- Intégrer les ADRs dans un workflow GitHub (PR, revue, historique)
- Maintenir un registre d'ADRs sur un projet data engineering

---

## Contenu du module

| Fichier | Thème |
|--------|-------|
| `01-introduction.md` | Qu'est-ce qu'un ADR, pourquoi documenter, cycle de vie |
| `02-format-adr.md` | Format MADR, sections clés, statuts, alternatives |
| `03-exemples-adr.md` | 4 exemples concrets : PostgreSQL, FastAPI, Docker, Kafka |
| `templates/template-madr.md` | Template MADR complet |
| `templates/template-simple.md` | Template simple pour équipes débutantes |
| `exercices/` | Rédiger 3 ADRs pour un projet donné |

---

## Pourquoi ce module ?

> "Le coût des mauvaises décisions d'architecture ne vient pas de la décision elle-même, mais de l'incapacité à comprendre pourquoi elle a été prise."

Sans ADRs, les équipes passent du temps à :
- Re-débattre de décisions déjà prises (et oubliées)
- Comprendre pourquoi un choix "bizarre" a été fait 2 ans plus tôt
- Onboarder les nouveaux développeurs sans contexte

---

## Durée estimée

- **Théorie** : 2 heures
- **Exercices** : 1h30
- **Total** : 3h30

---

## Outils recommandés

| Outil | Usage |
|-------|-------|
| Markdown + Git | ADRs versionnés dans le dépôt du projet |
| adr-tools (CLI) | Créer et gérer des ADRs en ligne de commande |
| Log4brains | Visualiser les ADRs sous forme de site web |
| GitHub / GitLab | Revue des ADRs via Pull Requests |
| Architecture Decision Hub | Outil SaaS de gestion d'ADRs |

---

## Ressources

- [Architecture Decision Records — Michael Nygard (article original)](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
- [MADR — Format Markdown Any Decision Records](https://adr.github.io/madr/)
- [adr-tools — GitHub](https://github.com/npryce/adr-tools)
- [Log4brains — Visualiser les ADRs](https://github.com/thomvaill/log4brains)
- [Exemples d'ADRs publics](https://github.com/joelparkerhenderson/architecture-decision-record)
