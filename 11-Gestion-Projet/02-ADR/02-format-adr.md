# Format des ADRs

## Les différents formats

Il existe plusieurs formats d'ADR. Les plus utilisés sont :

| Format | Auteur | Complexité | Adapté pour |
|--------|--------|-----------|-------------|
| **Format Nygard** | Michael Nygard (2011) | Simple | Premiers ADRs, petites équipes |
| **MADR** | Thomas Röhm | Complet | Équipes matures, décisions complexes |
| **Y-Statements** | Olaf Zimmermann | Très concis | Résumés rapides |
| **RFC (Request for Comments)** | Standard ingénierie | Très détaillé | Grandes organisations |

Ce cours couvre principalement le **format MADR** (Markdown Any Decision Records), le plus adopté aujourd'hui.

---

## Le format Nygard (format original)

C'est le format le plus simple, à 5 sections.

```markdown
# [Numéro]. [Titre]

Date : YYYY-MM-DD

## Statut

[Proposed | Accepted | Deprecated | Superseded by ADR-XXXX]

## Contexte

[Le contexte qui a nécessité cette décision]

## Décision

[Ce que nous avons décidé de faire]

## Conséquences

[Les impacts positifs et négatifs de cette décision]
```

**Avantages :** Simple, rapide à rédiger.
**Inconvénients :** Ne force pas à documenter les alternatives considérées.

---

## Le format MADR

MADR (Markdown Architectural Decision Records ou Markdown Any Decision Records) est une évolution plus structurée du format Nygard. Il est maintenu sur [https://adr.github.io/madr/](https://adr.github.io/madr/).

### Structure complète MADR

```markdown
# [short title of solved problem and solution]

* Status: [proposed | rejected | accepted | deprecated | superseded by ADR-0005]
* Date: YYYY-MM-DD
* Deciders: [liste des personnes impliquées dans la décision]
* Technical Story: [lien vers ticket/PR si applicable]

## Contexte et énoncé du problème

[Description du problème à résoudre. 2-3 paragraphes max.
Inclure : situation actuelle, contraintes, besoins identifiés.]

## Facteurs de décision

* [facteur 1, ex: performance requise > 10k req/s]
* [facteur 2, ex: compatibilité avec l'infrastructure existante]
* [facteur 3, ex: courbe d'apprentissage de l'équipe]

## Options considérées

* [Option 1]
* [Option 2]
* [Option 3]

## Résultat de la décision

Option retenue : **"[Option X]"**, car [justification principale en une phrase].

### Conséquences positives

* [conséquence positive 1]
* [conséquence positive 2]

### Conséquences négatives

* [conséquence négative 1]
* [conséquence négative 2]

## Analyse des options

### Option 1 : [nom]

[Description]

* Avantage : [...]
* Avantage : [...]
* Inconvénient : [...]
* Inconvénient : [...]

### Option 2 : [nom]

...

### Option 3 : [nom]

...

## Liens

* [Lien vers ticket, PR, doc technique...]
* Supersedes ADR-XXXX
* Superseded by ADR-XXXX
```

---

## Anatomie détaillée des sections MADR

### En-tête et métadonnées

```markdown
* Status: accepted
* Date: 2024-03-15
* Deciders: Alice Martin, Bob Dupont, Marie Laurent (PO)
* Technical Story: https://github.com/org/project/issues/42
```

**Status :** Toujours visible en haut du document — permet de savoir d'un coup d'œil si l'ADR est en vigueur.

**Deciders :** Liste des personnes qui ont participé à la décision. Important pour savoir qui contacter si une question émerge.

**Technical Story :** Lien vers le ticket, la PR ou l'epic qui a motivé la décision.

### Contexte et énoncé du problème

C'est la section la plus importante. Elle doit répondre à : **"Pourquoi a-t-on dû prendre une décision ?"**

**Bonnes pratiques :**
- Écrire au présent ou passé selon le moment de rédaction
- Inclure les contraintes non fonctionnelles (scalabilité, budget, délai)
- Mentionner l'état actuel du système si c'est une évolution
- 3-5 phrases suffisent généralement

**Mauvais :** "On a besoin d'une base de données."
**Bon :** "Le service de reporting traite actuellement ~50k requêtes par jour et les temps de réponse dépassent 3 secondes sur les requêtes agrégées. La base SQLite en place ne supporte pas les accès concurrents au-delà de 5 utilisateurs simultanés. L'équipe a besoin d'une base de données relationnelle capable de gérer la montée en charge prévue à 500k requêtes/jour d'ici 12 mois."

### Facteurs de décision

Les critères sur lesquels l'option retenue doit être évaluée.

```markdown
## Facteurs de décision

* Performance : capacité à traiter 500k req/jour avec < 200ms de latence
* Scalabilité : support des lectures parallèles et de la réplication
* Coût : licence open source ou coût raisonnable pour une PME
* Maîtrise de l'équipe : courbe d'apprentissage acceptable
* Maturité de l'écosystème : outils de migration, monitoring, backup
```

### Analyse des options

Pour chaque option, documenter les avantages et inconvénients **en lien avec les facteurs de décision**.

Ne pas décrire l'outil en général — se concentrer sur **pourquoi il répond ou non aux besoins identifiés**.

### Conséquences

Les conséquences ne sont pas uniquement négatives. Documenter les deux :

**Positives :**
- Ce qu'on gagne en adoptant cette option
- Les risques qu'on évite

**Négatives (ou dettes) :**
- Les contraintes introduites
- Les migrations futures nécessaires
- Les compétences à acquérir
- Les limitations connues

---

## Conventions de nommage et numérotation

### Numérotation

Les ADRs sont numérotés séquentiellement : `0001`, `0002`, `0003`...

Ne jamais réutiliser un numéro, même si un ADR est rejeté ou supprimé.

### Nommage des fichiers

```
docs/adr/
├── 0001-utiliser-postgresql.md
├── 0002-utiliser-fastapi-pour-lapi-rest.md
├── 0003-containerisation-avec-docker.md
└── 0004-utiliser-kafka-pour-les-evenements.md
```

**Convention :** `NNNN-[titre-en-kebab-case].md`

Le titre est **l'action prise**, pas le problème. Utiliser un verbe d'action :
- ✅ `utiliser-postgresql`
- ✅ `adopter-une-architecture-hexagonale`
- ✅ `migrer-vers-kubernetes`
- ❌ `base-de-donnees` (trop vague, pas d'action)
- ❌ `choix-technique-2024` (pas descriptif)

---

## Patterns et anti-patterns

### Patterns recommandés

**Pattern "Un problème, une décision"**
Un ADR = une décision atomique. Ne pas mélanger "choix de la BDD" et "choix de l'ORM" dans le même ADR.

**Pattern "Options multiples documentées"**
Toujours documenter au moins 2-3 options, même si la décision paraît évidente. Ça montre que l'équipe a réfléchi.

**Pattern "ADR comme RFC"**
Pour les décisions majeures, créer l'ADR en "Proposed" et ouvrir une PR pour discussion avant de prendre la décision. L'approbation de la PR = validation collective.

### Anti-patterns à éviter

**Anti-pattern "ADR rétrospectif sans alternatives"**
Écrire un ADR après coup sans documenter les alternatives considérées. On perd le contexte des arbitrages.

**Anti-pattern "Justification technologique"**
Justifier uniquement par des caractéristiques techniques ("PostgreSQL est plus rapide") sans lien avec les besoins du projet.

**Anti-pattern "ADR trop long"**
Un ADR de 5 pages ne sera pas lu. Rester concis : 1-2 pages pour un ADR normal, 3 pages max pour une décision majeure.

**Anti-pattern "Modifier un ADR accepté"**
Un ADR accepté ne doit pas être modifié. Si la décision change, créer un nouvel ADR qui supersede l'ancien.

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Un ADR en cours de revue dans GitHub — afficher la vue "Files changed" d'une Pull Request qui contient un fichier ADR en Markdown, avec des commentaires de reviewers dans les lignes du document.
> **Expliquer :** Comment la revue d'un ADR fonctionne comme une revue de code (commentaires ligne par ligne), comment les arguments s'échangent dans les commentaires, et comment la décision finale est documentée dans le fichier avant de merger.

---

## Cycle de vie d'une décision — exemple complet

```
Jour 1 : Problème identifié
  → Équipe discute du choix de base de données
  → Ouverture d'un ticket GitHub : "Choisir la BDD principale"

Jour 2 : Rédaction de l'ADR
  → Alice rédige docs/adr/0001-utiliser-postgresql.md
  → Status: Proposed
  → Ouvre une PR sur GitHub

Jours 2-4 : Revue et discussion
  → Bob commente : "Avez-vous considéré MySQL ?"
  → Alice met à jour l'ADR en ajoutant MySQL dans les options
  → Carla ajoute un facteur de décision (support JSON natif)
  → Consensus atteint : PostgreSQL retenu

Jour 5 : Merge et acceptation
  → PR mergée
  → Status passe à: Accepted
  → L'implémentation peut commencer

Sprint 8 (6 mois plus tard) : Changement de contexte
  → Décision d'utiliser CockroachDB pour la distribution multi-région
  → Nouveau ADR : docs/adr/0009-migrer-vers-cockroachdb.md
  → ADR 0001 mis à jour : "Superseded by ADR-0009"
```

---

## Résumé des formats

| Format | Sections | Quand l'utiliser |
|--------|---------|-----------------|
| Nygard simple | Statut, Contexte, Décision, Conséquences | Première adoption, décisions simples |
| MADR complet | + Facteurs, Options, Analyse détaillée | Décisions majeures, équipes matures |
| MADR court | Sous-ensemble de MADR | Usage quotidien, décisions moyennes |

**Règle :** Choisir un format et s'y tenir. La cohérence est plus importante que la perfection.
