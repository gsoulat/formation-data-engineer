# ADR-NNNN — [Titre court décrivant la décision]

<!--
Instructions :
- Remplacer NNNN par le numéro séquentiel (0001, 0002, etc.)
- Le titre doit exprimer l'action : "Utiliser X", "Adopter Y", "Migrer vers Z"
- Ne jamais modifier un ADR accepté — créer un nouvel ADR qui le supersede
- Conserver les ADRs rejetés et superseded pour l'historique
-->

* **Status:** [proposed | rejected | accepted | deprecated | superseded by ADR-NNNN]
* **Date:** YYYY-MM-DD
* **Deciders:** [Prénom Nom (Rôle), Prénom Nom (Rôle), ...]
* **Technical Story:** [Lien vers ticket / issue / PR — optionnel]

---

## Contexte et énoncé du problème

<!--
Décrire :
1. Le contexte actuel du système ou du projet
2. Le problème ou la contrainte qui nécessite une décision
3. Les exigences non fonctionnelles pertinentes (volume, latence, budget, délai...)

Exemples : "Le système traite actuellement 10k req/jour et..."
           "Nous avons besoin de X car le système actuel ne supporte pas Y..."

3 à 5 phrases suffisent. Éviter le jargon technique non expliqué.
-->

[Description du contexte et du problème]

---

## Facteurs de décision

<!--
Lister les critères d'évaluation des options.
Ces facteurs seront utilisés dans l'analyse de chaque option.
Être spécifique et mesurable quand possible.
-->

* [Facteur 1 — ex: Performance : < 200ms de latence pour 95% des requêtes]
* [Facteur 2 — ex: Coût : licence open source ou < 500€/mois]
* [Facteur 3 — ex: Courbe d'apprentissage : maîtrisable en 2 semaines]
* [Facteur 4 — ex: Compatibilité avec les outils existants (dbt, Airflow...)]
* [Ajouter autant de facteurs que nécessaire]

---

## Options considérées

<!--
Lister toutes les options évaluées (au moins 2).
Les détails sont dans la section "Analyse des options" ci-dessous.
-->

* [Option 1]
* [Option 2]
* [Option 3 — optionnel]
* [Option 4 — optionnel]

---

## Résultat de la décision

Option retenue : **"[Nom de l'option retenue]"**, car [justification principale en 1-2 phrases].

### Conséquences positives

<!--
Lister les bénéfices directs et les risques évités grâce à cette décision.
-->

* [Bénéfice 1]
* [Bénéfice 2]
* [Bénéfice 3]

### Conséquences négatives

<!--
Lister honnêtement les limitations, dettes techniques ou compromis introduits.
Ne pas minimiser — la transparence est la valeur des ADRs.
-->

* [Limitation ou dette technique 1]
* [Limitation ou dette technique 2]
* [Condition de révision : "À réviser si X dépasse Y"]

---

## Analyse des options

<!--
Pour chaque option, documenter les avantages et inconvénients
EN LIEN AVEC LES FACTEURS DE DÉCISION ci-dessus.
Ne pas décrire l'outil en général — se concentrer sur le projet.
-->

### Option 1 : [Nom]

[Description courte de l'option — 1 phrase]

* Avantage : [en lien avec un facteur de décision]
* Avantage : [...]
* Inconvénient : [en lien avec un facteur de décision]
* Inconvénient : [...]

### Option 2 : [Nom]

[Description courte de l'option — 1 phrase]

* Avantage : [...]
* Avantage : [...]
* Inconvénient : [...]
* Inconvénient : [...]

### Option 3 : [Nom] — optionnel

[Description courte]

* Avantage : [...]
* Inconvénient : [...]

---

## Liens

<!--
Références utiles : documentation officielle, tickets, PRs, articles, autres ADRs.
-->

* [Lien 1 — description]
* [Lien 2 — description]
* Supersedes [ADR-NNNN](./NNNN-titre.md) — si applicable
* Superseded by [ADR-NNNN](./NNNN-titre.md) — si applicable
