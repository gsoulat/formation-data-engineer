# Module 09 : Extraction de données pour l'analyse

Ce module aborde le SQL sous l'angle du **Data Analyst** : extraire la bonne donnée, au bon endroit, la valider, puis la croiser avec d'autres sources (API, fichiers) pour alimenter une analyse ou un tableau de bord.

## 🎯 Objectifs

À la fin de ce module, vous serez capable de :
- Traduire une **demande métier** en requête SQL ciblée (filtres, agrégations, classements).
- Écrire des requêtes analytiques avancées : sous-requêtes, CTE, fonctions de fenêtrage, agrégations conditionnelles.
- **Consommer une API REST** en Python (`requests`) : JSON, pagination, clé API.
- **Combiner plusieurs sources** (SQL + API + Excel) avec pandas (`merge`, `concat`).
- **Valider l'exactitude** des données extraites : doublons, valeurs manquantes, contrôle des totaux.

## 📚 Contenu

- [01 - Extraction ciblée pour l'analyse](01-extraction-ciblee.md) — requêtes orientées métier, pièges classiques, TP sur un jeu de données retail.
- [02 - SQL avancé pour l'analyse](02-sql-avance-analyse.md) — sous-requêtes, CTE, window functions, `CASE WHEN`, `UNION` appliqués à l'analyse.
- [03 - Extraction multi-sources](03-extraction-multi-sources.md) — API REST en Python, combinaison SQL + API + Excel avec pandas, validation des données.

## ✅ Prérequis

Ce module s'appuie sur les fondamentaux vus dans les sous-modules précédents :
- [Module 00 : Préparation de l'environnement](../00-Preparation-Environnement/README.md)
- [Module 01 : Les Fondamentaux (SELECT, WHERE)](../01-Introduction-Select/README.md)
- [Module 02 : Agrégations et GROUP BY](../02-Agregations-Groupby/README.md)
- [Module 03 : Jointures](../03-Jointures/README.md)
- [Module 05 : Fonctions Avancées (CTE, Window Functions)](../05-Fonctions-Avancees/README.md)

Pour la partie multi-sources : des bases de Python et de pandas (DataFrame, lecture de fichiers).

## 👥 Public visé

Conçu en priorité pour le **parcours Data Analyst** (objectif : **requêter une base de données et extraire des données de sources variées**), ce module est aussi utile à tout Data Engineer qui veut comprendre les besoins d'extraction de ses utilisateurs.

---
**Academy** - Formation Data Engineer / Data Analyst
