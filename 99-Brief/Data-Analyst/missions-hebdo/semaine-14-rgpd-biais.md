# Semaine 14 — RGPD & biais dans les données (mission hebdomadaire)

> Phase 2 — Solution BI pour analyse avancée · Module 2.5 · Durée : ~1 jour · Modalité : solo · Compétence : C12 (évaluer les risques RGPD, éthique, biais) niv. 1

## Contexte

La cellule data de NordRetail manipule des données clients (noms, e-mails, villes, historique d'achat). Avant d'élargir l'accès aux tableaux de bord et de lancer un ciblage marketing, la direction veut s'assurer que tout est conforme au RGPD et que les analyses ne reproduisent pas de biais injustes envers certains clients ou territoires.

## Objectif de la mission

Auditer la conformité RGPD d'un cas concret d'usage des données NordRetail, identifier les biais présents dans le jeu de données clients/ventes, et proposer des correctifs réalistes.

## Consignes (étapes)

1. **Cartographie des données personnelles** : ouvre `Dim_Client.csv` et `Faits_Ventes.csv`. Liste les colonnes qui constituent des **données personnelles** (ex. `prenom`, `nom`, `email`, `ville`) et celles qui ne le sont pas. Pour chacune, note sa sensibilité.
2. **Audit RGPD** du cas « la direction marketing veut exporter la liste des meilleurs clients (RFM) avec e-mail pour une campagne » : vérifie 5 points clés — base légale, finalité, minimisation, durée de conservation, droits des personnes (accès, opposition, effacement). Conclus : conforme / non conforme et pourquoi.
3. **Correctifs RGPD** : propose des mesures concrètes (anonymisation ou pseudonymisation de `nom`/`email`, agrégation, contrôle d'accès au rapport, mention d'information, registre de traitement).
4. **Détection de biais** : analyse le jeu de données pour repérer au moins 2 biais possibles, par exemple :
   - biais de représentativité (certaines `ville` ou `segment` sur/sous-représentés) ;
   - biais lié aux données manquantes ou aux clients sans achat récent (exclus de l'analyse RFM) ;
   - effet d'un ciblage qui renforcerait toujours les mêmes clients « Champions ».
5. **Correctifs biais** : pour chaque biais, propose une parade (rééquilibrage, segment de contrôle, indicateur de couverture, vigilance sur les exclus).

## Données (../data/)

`Dim_Client.csv` · `Faits_Ventes.csv` (et `Dim_Magasin.csv` pour la répartition territoriale).

## Livrable attendu

Une note d'audit (2 à 3 pages, Markdown ou PDF) structurée en 4 parties : cartographie des données personnelles, audit RGPD du cas (conforme/non + justification), au moins 2 biais identifiés avec preuves chiffrées, et un plan de correctifs RGPD + biais.

## Critères de réussite

- [ ] Les données personnelles du jeu sont correctement identifiées et qualifiées (OUI/NON)
- [ ] L'audit RGPD couvre base légale, finalité, minimisation, conservation et droits (OUI/NON)
- [ ] Une conclusion claire conforme / non conforme est argumentée (OUI/NON)
- [ ] Au moins 2 biais sont identifiés et étayés par des chiffres (OUI/NON)
- [ ] Des correctifs réalistes sont proposés pour le RGPD et pour les biais (OUI/NON)
- [ ] La note est claire, structurée et exploitable par un non-spécialiste (OUI/NON)

## Ressources (renvoi au cours)

Module 2.5 — RGPD pour data analysts (données personnelles, anonymisation/pseudonymisation, principes CNIL) et biais des données (représentativité, sélection, boucle de renforcement). Site CNIL.
