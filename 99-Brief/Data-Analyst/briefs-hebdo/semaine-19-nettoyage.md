# Brief S19 — Fiabiliser un export de ventes corrompu de NordRetail (nettoyage de données)

## Informations

| Critère | Valeur |
|---------|--------|
| **Semaine** | S19 — Phase 3 : Industrialiser la chaîne de données du tableau de bord |
| **Durée** | 1 semaine (5 jours) |
| **Niveau** | Intermédiaire |
| **Modalité** | Binôme |
| **Technologies** | Python 3, pandas, Jupyter Notebook, Git/GitHub |
| **Prérequis** | [Audit & EDA (S06)](semaine-06-eda-ventes-nordretail.md) · [Module Nettoyage des données](../../../15-Business-Intelligence/16-Nettoyage-Donnees/) · [Module ETL & automatisation](../../../15-Business-Intelligence/15-ETL-Automatisation/) |

## Contexte

### L'entreprise

**NordRetail** est une enseigne de distribution implantée dans les Hauts-de-France : un réseau de magasins physiques (Dunkerque, Roubaix, Valenciennes, Tourcoing…) doublé d'un canal e-commerce. Son équipe data, encore naissante, construit depuis plusieurs semaines un **tableau de bord de pilotage** pour la direction commerciale. Vous en faites partie, aux côtés d'un responsable BI et d'une contrôleuse de gestion.

### Le problème

L'audit mené en amont (S06) avait confirmé ce que tout le monde redoutait : les exports de caisse ne sont pas fiables « prêts à l'emploi ». Depuis, la migration de l'outil de caisse a livré un nouvel export annuel, `ventes_sales.csv`, dans un état encore plus dégradé que le précédent : **dates au format français**, **quantités manquantes**, **doublons de saisie**, **casse incohérente** sur les noms de villes, **montants négatifs** (des retours mal codés), et quelques **valeurs aberrantes** qui gonflent artificiellement les totaux.

La contrôleuse de gestion a été claire : elle **refuse d'alimenter le tableau de bord** tant que ce fichier n'est pas fiabilisé et que les règles de correction ne sont pas tracées. Sans données propres, tous les indicateurs construits en aval seront faux — et la confiance de la direction dans l'équipe data en dépend. Votre mission de la semaine : transformer cet export brut en une **source de vérité rejouable**, dont chaque correction est justifiée et documentée.

### La question centrale

Toute la semaine, chaque règle de nettoyage que vous appliquez doit contribuer à répondre à la question que la contrôleuse de gestion vous a posée :

> **« Ces données de ventes sont-elles désormais assez fiables pour piloter NordRetail — et pouvez-vous prouver, ligne par ligne, ce que vous avez corrigé ? »**

### Les données

Un fichier volontairement corrompu, à fiabiliser cette semaine :

- [`../data/ventes_sales.csv`](../data/ventes_sales.csv) — l'export annuel « sale » de NordRetail. Colonnes : `date`, `ville`, `type` (Magasin / E-commerce), `categorie`, `produit`, `quantite`, `prix_unitaire`, `remise`, `montant`, `marge`, `client_id`.

Les dates sont au format `JJ/MM/AAAA`, certaines lignes sont dupliquées, des `quantite` sont vides, des `ville` apparaissent en casses différentes (`lille`, `LILLE`, `Lille`), et des `montant` négatifs se mêlent aux ventes normales. C'est précisément ce désordre que vous devez maîtriser.

## Objectifs pédagogiques

À l'issue de ce brief, vous serez capable de :

- **Établir un diagnostic de qualité** avant tout nettoyage : volume, types, valeurs manquantes, doublons et valeurs uniques suspectes, pour objectiver l'état initial du fichier.
- **Traiter les valeurs manquantes** en choisissant et justifiant une stratégie adaptée à chaque colonne (suppression, imputation, recalcul métier), plutôt qu'une règle unique appliquée aveuglément.
- **Supprimer les doublons et normaliser les libellés** (casse, espaces parasites) pour restaurer la cohérence des dimensions d'analyse.
- **Standardiser les dates** au format ISO et **détecter les valeurs aberrantes** (méthode IQR ou z-score) en distinguant l'erreur de saisie du cas métier légitime (retour, achat professionnel).
- **Produire un pipeline rejouable et un journal de nettoyage** traçant, pour chaque règle, le problème, l'action, la justification et le nombre de lignes impactées.

## Données fournies

Le jeu de données est déjà présent dans le dépôt : [`99-Brief/Data-Analyst/data/ventes_sales.csv`](../data/ventes_sales.csv). Aucune donnée n'est à télécharger. Vous travaillez **sans jamais modifier la source** : toutes vos corrections se font en mémoire (dans un DataFrame) et le résultat propre est exporté dans un **nouveau fichier**. La source corrompue reste intacte pour permettre à quiconque de rejouer votre traitement.

## Travail demandé

Travail en **binôme sur 5 jours**. L'entraide entre binômes est encouragée, mais chaque binôme produit son propre notebook (ou script), son propre CSV nettoyé et son propre journal des règles. Un **socle commun** est obligatoire ; des **pistes bonus** attendent les plus rapides.

### Phase 1 — Cadrage et stratégie de nettoyage, SANS code (J1)

Avant de coder, appropriez-vous le sujet. Ouvrez le fichier dans un tableur pour un premier regard : à quoi ressemble une ligne saine ? Listez, colonne par colonne, ce qu'est une valeur **valide** — par exemple, une `quantite` peut-elle être vide, nulle, décimale ? Un `montant` négatif est-il forcément une erreur, ou peut-il légitimement coder un retour client ? Une `ville` en minuscules est-elle une ville différente ? Écrivez ces règles attendues : elles deviendront votre grille de nettoyage. Réfléchissez aussi à l'**ordre des opérations** — faut-il dédoublonner avant ou après avoir normalisé la casse des villes ? — et pourquoi cet ordre compte. Initialisez votre dépôt GitHub dès aujourd'hui.

### Phase 2 — Diagnostic initial de l'état du fichier (J1-J2)

Chargez le fichier avec pandas et dressez un **état des lieux chiffré, avant toute correction**. Établissez le profil : volume (`shape`), types (`info()` / `dtypes`), statistiques (`describe()`), comptage des valeurs manquantes par colonne, nombre de doublons exacts, et valeurs uniques de `ville`, `type` et `categorie` pour repérer les incohérences de casse. Ce diagnostic est la **photo « avant »** : sans elle, impossible de prouver l'impact de votre nettoyage. Combien de lignes sont concernées par chaque problème ? Lesquels vous semblent les plus critiques pour le futur tableau de bord ?

### Phase 3 — Manquants, doublons et libellés (J2-J3)

Attaquez les défauts structurels. Pour les **valeurs manquantes** (notamment `quantite`), choisissez une stratégie par colonne et justifiez-la : suppression de la ligne, imputation par la médiane, ou recalcul métier depuis `montant / (prix_unitaire * (1 - remise))` ? Traitez les **doublons** exacts (et les quasi-doublons si vous en repérez), en conservant la trace du nombre de lignes retirées. Normalisez enfin la **casse et les espaces** des libellés (`ville`, `categorie`) pour que `lille`, `LILLE` et `  Lille ` ne comptent plus que comme une seule modalité. Chaque décision doit être justifiée : pourquoi imputer plutôt que supprimer ? que perd-on dans chaque cas ?

### Phase 4 — Dates, cohérence et valeurs aberrantes (J3-J4)

Fiabilisez les valeurs numériques et temporelles. Convertissez la colonne `date` du format `JJ/MM/AAAA` vers l'ISO `YYYY-MM-DD` (`to_datetime(format=...)`), et **signalez ou écartez** les dates invalides plutôt que de les ignorer. Décidez du sort des `montant` / `quantite` **négatifs** : s'agit-il de retours à isoler dans une catégorie à part, ou d'erreurs à corriger ? Vérifiez la **cohérence comptable** de chaque ligne (`montant ≈ quantite × prix_unitaire × (1 - remise)`) et repérez les écarts. Détectez enfin les **valeurs aberrantes** de `montant` et `quantite` par une méthode explicite (IQR ou z-score) : documentez-les et tranchez leur traitement. Attention : une valeur extrême n'est pas toujours une erreur — comment distinguer l'anomalie de saisie de l'achat professionnel exceptionnel ?

### Phase 5 — Export, journal des règles et mise en ligne (J5)

Consolidez le résultat. Exportez le fichier nettoyé sous un nom explicite (`ventes_clean_<binome>.csv`) et rédigez le **journal des règles de nettoyage** : un tableau à quatre colonnes `Problème | Règle appliquée | Justification | Lignes impactées`, qui doit permettre à un tiers de comprendre et rejouer chaque correction. Vérifiez que votre notebook (ou script) s'exécute **de bout en bout sans erreur** sur la source d'origine — c'est la garantie qu'il est rejouable. Soignez le README et poussez le tout sur GitHub. En clôture, rédigez un court paragraphe pour la contrôleuse de gestion : le fichier est-il désormais exploitable, et sous quelles réserves ?

### Socle commun (obligatoire)

Phases 1 à 5 complètes : diagnostic initial chiffré, traitement justifié des manquants / doublons / casse, dates converties en ISO, négatifs et aberrants détectés et traités, CSV nettoyé exporté, journal des règles complet, notebook rejouable, dépôt public à jour.

### Pour aller plus loin (bonus)

- Rejouez votre pipeline sur [`../data/ventes_corrompu.csv`](../data/ventes_corrompu.csv) : vos règles tiennent-elles sur un autre export dégradé, ou faut-il les généraliser ?
- Comparez votre fichier nettoyé à la version de référence [`../data/ventes_magasins.csv`](../data/ventes_magasins.csv) : vos totaux par ville se rapprochent-ils d'une base saine ?
- Encapsulez vos règles dans une **fonction `nettoyer(df)`** paramétrable et rejouable, premier pas vers un mini-ETL réutilisable d'une semaine à l'autre.

## Livrables attendus

- **Un dépôt GitHub public** contenant :
  - `nettoyage_ventes.ipynb` (ou `nettoyage.py`) — notebook/script exécuté de bout en bout, commenté, avec diagnostic « avant » et résultat « après » ;
  - le **CSV nettoyé** (`ventes_clean_<binome>.csv`) généré par le pipeline ;
  - le **journal des règles de nettoyage** (`JOURNAL.md` ou tableau dans le notebook) ;
  - un **`README.md`** : description du projet, technologies, instructions de lancement, auteur(s).
- Un **court message métier** (dans le README ou le journal) indiquant si le fichier est exploitable et sous quelles réserves.

## Modalités d'évaluation

Évaluation en deux volets :

- **Notebook, CSV et journal (60 %)** : rigueur du diagnostic, pertinence et justification des règles de nettoyage, correction effective des défauts, cohérence du fichier final, et surtout **rejouabilité** du traitement de bout en bout.
- **Restitution orale (40 %)** : 10 minutes pour présenter à la « contrôleuse de gestion » (le formateur et un autre binôme) les défauts trouvés, les décisions prises et leur impact chiffré, + 5 minutes de questions.

**Validation partielle** : un binôme dont le pipeline n'est pas totalement finalisé mais dont le diagnostic et les règles de nettoyage sont structurés, justifiés et tracés peut valider partiellement les compétences travaillées.

## Critères de performance

**Diagnostiquer la qualité des données**
- Le diagnostic initial (manquants, doublons, types, valeurs uniques) est présenté **avant** tout nettoyage.
- Le volume de lignes concernées par chaque problème est chiffré.
- Les problèmes sont hiérarchisés au regard de leur impact sur l'analyse.

**Nettoyer et fiabiliser**
- Les valeurs manquantes sont traitées avec une stratégie **justifiée** par colonne.
- Les doublons sont supprimés en gardant la trace du nombre de lignes retirées.
- La casse et les espaces parasites des libellés (`ville`, `categorie`) sont normalisés.
- Les dates sont converties en ISO `YYYY-MM-DD` et les dates invalides sont gérées explicitement.

**Traiter les anomalies numériques**
- Les `montant` / `quantite` négatifs sont détectés et traités avec réflexion (retour isolé vs erreur corrigée).
- La cohérence `montant ≈ quantite × prix_unitaire × (1 - remise)` est vérifiée.
- Les valeurs aberrantes sont détectées par une méthode explicite (IQR ou z-score) et leur traitement est argumenté.

**Tracer et restituer**
- Un journal des règles liste, pour chaque correction, le problème, l'action, la justification et les lignes impactées.
- Le CSV final est cohérent et le notebook/script se rejoue de bout en bout sans erreur.
- Le dépôt GitHub public est complet (traitement rejouable + CSV nettoyé + journal + README).

## Ressources

- Module de cours — [Nettoyage des données](../../../15-Business-Intelligence/16-Nettoyage-Donnees/)
- Module de cours — [ETL & automatisation](../../../15-Business-Intelligence/15-ETL-Automatisation/)
- Étape précédente du parcours — [Brief S06 — Audit & EDA des ventes](semaine-06-eda-ventes-nordretail.md)
- Documentation pandas : https://pandas.pydata.org/docs/
- Fonctions clés : `isna`, `drop_duplicates`, `str.strip` / `str.title`, `to_datetime(format=...)`, `quantile` (IQR)
