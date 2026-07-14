[← Precedent](02-dictionnaire-donnees.md) | [🏠 Accueil](README.md) | [Suivant →](04-modele-logique-mld.md)

---

# 03 - Le Modele Conceptuel de Donnees (MCD)

## 🎯 Objectifs de cette lecon

- Maitriser la representation des entites et de leurs attributs
- Comprendre et utiliser les differents types d'associations (binaire, ternaire, reflexive)
- Savoir lire et ecrire les cardinalites en notation MERISE
- Comprendre les associations porteuses de donnees
- Connaitre la generalisation/specialisation (heritage)
- Concevoir un MCD complet a partir d'un dictionnaire de donnees
- Eviter les erreurs courantes de modelisation conceptuelle

---

## 1. Les entites

### 1.1 Definition et representation

Une **entite** est un objet ou concept du monde reel que l'on souhaite decrire et gerer. Dans un MCD MERISE, une entite est representee par un **rectangle** avec :

- Le **nom de l'entite** en haut (en majuscules)
- L'**identifiant** souligne (premiere propriete)
- Les **attributs** listes en dessous

```
┌─────────────────────┐
│       CLIENT        │
├─────────────────────┤
│ id_client (PK)      │  ← Identifiant (souligne dans la notation)
│ nom                 │
│ prenom              │
│ email               │
│ telephone           │
│ date_inscription    │
└─────────────────────┘
```

### 1.2 L'identifiant

L'identifiant est l'attribut (ou le groupe d'attributs) qui permet de distinguer de maniere **unique** chaque occurrence de l'entite.

**Regles pour l'identifiant :**
- ✅ Unique pour chaque occurrence
- ✅ Non nul (jamais vide)
- ✅ Stable (ne change pas dans le temps)
- ✅ Minimal (pas d'attribut superflu dans l'identifiant)

**Exemples :**

| Entite | Bon identifiant | Mauvais identifiant | Pourquoi |
|--------|----------------|--------------------|---------|
| CLIENT | id_client (auto-incremente) | nom + prenom | Deux clients peuvent avoir le meme nom |
| PRODUIT | id_produit | nom_produit | Le nom peut changer |
| COMMANDE | id_commande | date_commande | Plusieurs commandes le meme jour |
| CAPTEUR | numero_serie | modele | Plusieurs capteurs du meme modele |

### 1.3 Types d'attributs

| Type | Description | Exemple |
|------|-------------|---------|
| **Simple** | Une seule valeur atomique | nom, age |
| **Compose** | Decomposable en sous-attributs | adresse → rue, code_postal, ville |
| **Derive** | Calculable a partir d'autres attributs | age (derive de date_naissance) |
| **Multivaleur** | Plusieurs valeurs possibles | telephones (domicile, mobile) |

💡 **En MERISE** : on evite les attributs composes et multivaleurs. Si un attribut est compose, on cree des attributs separes. Si un attribut est multivaleur, on cree une entite separee.

---

## 2. Les associations

### 2.1 Definition

Une **association** (ou relation) est un lien semantique entre deux ou plusieurs entites. Elle est representee par un **ovale** (ou losange dans certaines notations) contenant un verbe.

```
┌──────────┐          ┌──────────┐          ┌──────────┐
│  CLIENT  │          │  PASSE   │          │ COMMANDE │
│          │──────────│          │──────────│          │
│          │          │          │          │          │
└──────────┘          └──────────┘          └──────────┘
```

### 2.2 Association binaire

Une association binaire relie **exactement 2 entites**. C'est le cas le plus courant.

```
┌──────────────┐                              ┌──────────────┐
│   CLIENT     │          PASSE               │  COMMANDE    │
├──────────────┤    ┌──────────────┐          ├──────────────┤
│ id_client    │────│              │──────────│ id_commande  │
│ nom          │    └──────────────┘          │ date_commande│
│ prenom       │  (0,n)              (1,1)    │ statut       │
│ email        │                              │ montant_total│
└──────────────┘                              └──────────────┘

Lecture : "Un CLIENT passe 0 ou N commandes"
          "Une COMMANDE est passee par 1 et 1 seul client"
```

### 2.3 Association ternaire

Une association ternaire relie **3 entites simultanement**. Elle est utilisee quand le lien n'a de sens qu'avec les 3 entites ensemble.

**Exemple** : un ENSEIGNANT enseigne une MATIERE dans une SALLE

```
┌──────────────┐
│  ENSEIGNANT  │
├──────────────┤
│ id_enseignant│
│ nom          │
│ specialite   │
└──────┬───────┘
       │ (0,n)
       │
       │     ┌──────────────┐
       │     │   ENSEIGNE   │
       ├─────│              │
       │     │  jour        │
       │     │  heure_debut │
       │     └──────┬───────┘
       │            │
 (0,n) │            │ (1,n)
┌──────┴───────┐    │
│    SALLE     │    │
├──────────────┤    │
│ id_salle     │────┘
│ nom_salle    │   ┌──────────────┐
│ capacite     │   │   MATIERE    │
└──────────────┘   ├──────────────┤
                   │ id_matiere   │
                   │ nom_matiere  │
                   │ volume_horaire│
                   └──────────────┘
```

💡 **Quand utiliser une association ternaire ?** Quand la question "Qui fait quoi ou ?" necessite les 3 entites pour avoir une reponse. Si vous pouvez decomposer en 2 associations binaires, faites-le : c'est plus simple.

### 2.4 Association reflexive

Une association reflexive relie une entite **a elle-meme**. Elle modelise une relation hierarchique ou un lien entre occurrences de la meme entite.

**Exemple 1 : Hierarchie de categories (arborescence)**

```
                    ┌──────────────┐
            ┌───────│ EST_PARENT_DE│───────┐
            │       └──────────────┘       │
            │ (0,n)                 (0,1)  │
            │                              │
       ┌────▼─────────────────────────────▼────┐
       │              CATEGORIE                │
       ├───────────────────────────────────────┤
       │ id_categorie                          │
       │ nom_categorie                         │
       │ description                           │
       └───────────────────────────────────────┘

Lecture : "Une CATEGORIE est parente de 0 ou N sous-categories"
          "Une CATEGORIE a 0 ou 1 categorie parente"
```

**Exemple 2 : Employes et manager**

```
                    ┌──────────────┐
            ┌───────│   DIRIGE     │───────┐
            │       └──────────────┘       │
            │ (0,n)                 (0,1)  │
            │                              │
       ┌────▼─────────────────────────────▼────┐
       │              EMPLOYE                  │
       ├───────────────────────────────────────┤
       │ id_employe                            │
       │ nom                                   │
       │ poste                                 │
       └───────────────────────────────────────┘

Lecture : "Un EMPLOYE dirige 0 ou N employes"
          "Un EMPLOYE est dirige par 0 ou 1 employe (son manager)"
```

---

## 3. Les cardinalites en notation MERISE

### 3.1 Principe

En MERISE, les cardinalites sont placees **du cote de l'entite** qu'elles concernent. Elles indiquent le nombre minimum et maximum de fois qu'une occurrence de l'entite participe a l'association.

**Format** : **(min, max)**

### 3.2 Les 4 cardinalites possibles

| Cardinalite | Signification | Exemple |
|-------------|---------------|---------|
| **(0,1)** | Zero ou une fois | Un employe occupe 0 ou 1 bureau |
| **(1,1)** | Exactement une fois | Une commande est passee par 1 et 1 seul client |
| **(0,n)** | Zero ou plusieurs fois | Un client passe 0 ou N commandes |
| **(1,n)** | Au moins une fois | Une commande contient 1 ou N produits |

### 3.3 Comment determiner les cardinalites

Pour chaque entite dans une association, posez-vous deux questions :

1. **Minimum** : "Une occurrence de cette entite peut-elle exister sans participer a l'association ?"
   - Oui → minimum = **0**
   - Non → minimum = **1**

2. **Maximum** : "Une occurrence de cette entite peut-elle participer plusieurs fois a l'association ?"
   - Non → maximum = **1**
   - Oui → maximum = **n**

**Exercice de lecture** :

```
┌──────────────┐                              ┌──────────────┐
│   CLIENT     │          PASSE               │  COMMANDE    │
├──────────────┤    ┌──────────────┐          ├──────────────┤
│ id_client    │────│              │──────────│ id_commande  │
│ nom          │    └──────────────┘          │ date_commande│
└──────────────┘  (0,n)              (1,1)    └──────────────┘
```

**Lecture cote CLIENT (0,n)** :
- Minimum 0 : un client peut exister sans avoir passe de commande (il vient de s'inscrire)
- Maximum n : un client peut passer plusieurs commandes

**Lecture cote COMMANDE (1,1)** :
- Minimum 1 : une commande ne peut pas exister sans client (pas de commande anonyme)
- Maximum 1 : une commande est passee par un seul client (pas de commande partagee)

### 3.4 Les types de relations (derives des cardinalites)

| Cote A | Cote B | Type de relation | Exemple |
|--------|--------|-----------------|---------|
| (0,1) ou (1,1) | (0,1) ou (1,1) | **Un-a-Un** (1:1) | Employe - Badge |
| (0,1) ou (1,1) | (0,n) ou (1,n) | **Un-a-Plusieurs** (1:N) | Client - Commande |
| (0,n) ou (1,n) | (0,n) ou (1,n) | **Plusieurs-a-Plusieurs** (N:M) | Commande - Produit |

### 3.5 Difference avec les notations UML et Crow's Foot

⚠️ **Attention** : en UML (et Crow's Foot), les cardinalites sont placees **du cote oppose** a MERISE !

```
MERISE :
┌────────┐  (0,n)    PASSE    (1,1)  ┌──────────┐
│ CLIENT │───────────[    ]──────────│ COMMANDE │
└────────┘                           └──────────┘
  Les cardinalites sont du cote de l'entite qu'elles decrivent.

UML / Crow's Foot :
┌────────┐  1      PASSE      0..*  ┌──────────┐
│ CLIENT │───────────────────────────│ COMMANDE │
└────────┘                           └──────────┘
  Les cardinalites sont du cote oppose !
  "1" cote Client = chaque commande a 1 client
  "0..*" cote Commande = chaque client a 0 ou N commandes
```

**Tableau de correspondance** :

| MERISE (cote entite) | UML (cote oppose) | Crow's Foot |
|---------------------|-------------------|-------------|
| (0,1) | 0..1 | ─○─\| |
| (1,1) | 1 | ──\| |
| (0,n) | 0..* | ─○─<< |
| (1,n) | 1..* | ──<< |

💡 **À retenir** : assurez-vous de maitriser la notation MERISE. C'est une notation de reference dans les formations et epreuves en France.

---

## 4. Les associations porteuses de donnees

### 4.1 Quand une association porte des attributs

Certaines associations ont leurs propres attributs. Cela arrive quand un attribut **n'appartient ni a l'une ni a l'autre entite**, mais au **lien entre les deux**.

**Exemple classique** : la relation CONTIENT entre COMMANDE et PRODUIT

```
┌──────────────┐                              ┌──────────────┐
│  COMMANDE    │         CONTIENT             │   PRODUIT    │
├──────────────┤    ┌──────────────┐          ├──────────────┤
│ id_commande  │────│ quantite     │──────────│ id_produit   │
│ date_commande│    │ prix_unitaire│          │ nom_produit  │
│ statut       │    │  _commande   │          │ prix_unitaire│
│ montant_total│    └──────────────┘          │ stock        │
└──────────────┘  (1,n)              (0,n)    └──────────────┘
```

**Pourquoi `quantite` est dans l'association et pas dans PRODUIT ?**
- La quantite n'est pas une propriete du produit en general
- La quantite n'est pas une propriete de la commande en general
- La quantite est une propriete de **cette commande pour ce produit** → c'est un attribut de l'association

**Pourquoi `prix_unitaire_commande` est dans l'association ?**
- Le prix du produit peut changer dans le temps
- On veut garder le prix **au moment de la commande**
- Ce prix est specifique au couple (commande, produit)

### 4.2 Regle importante

💡 **Regle** : seules les associations de type **N:M** (plusieurs-a-plusieurs) peuvent porter des attributs. Une association 1:N ou 1:1 ne porte jamais d'attributs en MERISE (ils sont absorbes par l'une des entites lors du passage au MLD).

---

## 5. La generalisation / specialisation (heritage)

### 5.1 Principe

La generalisation/specialisation permet de factoriser les attributs communs dans une entite generique et de specifier les attributs particuliers dans des sous-entites.

**Exemple** : Un UTILISATEUR peut etre un CLIENT ou un EMPLOYE

```
                 ┌──────────────────┐
                 │   UTILISATEUR    │
                 ├──────────────────┤
                 │ id_utilisateur   │
                 │ nom              │
                 │ prenom           │
                 │ email            │
                 │ date_creation    │
                 └────────┬─────────┘
                          │
                    ┌─────┴─────┐
                    │  heritage │
                    │   {T,E}   │
                    └─────┬─────┘
              ┌───────────┴───────────┐
              │                       │
     ┌────────▼────────┐    ┌────────▼────────┐
     │     CLIENT      │    │    EMPLOYE      │
     ├─────────────────┤    ├─────────────────┤
     │ adresse_livraison│    │ poste           │
     │ programme_fidelite│   │ date_embauche   │
     │ panier_moyen     │    │ salaire         │
     └─────────────────┘    └─────────────────┘
```

### 5.2 Contraintes d'heritage

| Contrainte | Notation | Signification |
|-----------|----------|---------------|
| **Totalite (T)** | {T} | Tout utilisateur est obligatoirement un client OU un employe |
| **Exclusivite (E)** | {E} | Un utilisateur est SOIT un client, SOIT un employe, jamais les deux |
| **Partition** | {T,E} | Totalite + Exclusivite : tout utilisateur est exactement l'un des deux |

---

## 6. MCD complet : exemple E-commerce

Voici le MCD complet correspondant au dictionnaire de donnees de la lecon 02 :

```
┌──────────────────┐                                    ┌──────────────────┐
│    CATEGORIE     │                                    │     CLIENT       │
├──────────────────┤                                    ├──────────────────┤
│ id_categorie     │                                    │ id_client        │
│ nom_categorie    │                                    │ nom              │
│ description_cat  │                                    │ prenom           │
└───────┬──────────┘                                    │ email            │
        │                                               │ telephone        │
        │ (0,n)                                         │ date_inscription │
        │                                               └────────┬─────────┘
   ┌────┴──────────┐                                             │
   │  APPARTIENT   │                                             │ (0,n)
   └────┬──────────┘                                             │
        │ (1,1)                                            ┌─────┴────────┐
        │                                                  │    PASSE     │
┌───────▼──────────┐                                       └─────┬────────┘
│     PRODUIT      │                                             │ (1,1)
├──────────────────┤                                             │
│ id_produit       │         ┌─────────────────┐        ┌───────▼──────────┐
│ nom_produit      │         │    CONTIENT     │        │    COMMANDE      │
│ description      │         ├─────────────────┤        ├──────────────────┤
│ prix_unitaire    │─────────│ quantite        │────────│ id_commande      │
│ stock_disponible │  (0,n)  │ prix_unit_cmd   │ (1,n)  │ date_commande    │
└──────────────────┘         └─────────────────┘        │ statut           │
                                                        │ montant_total    │
                                                        └──────────────────┘

LECTURE DES CARDINALITES :
- CATEGORIE (0,n) --- APPARTIENT --- (1,1) PRODUIT
  "Une categorie contient 0 ou N produits"
  "Un produit appartient a 1 et 1 seule categorie"

- PRODUIT (0,n) --- CONTIENT --- (1,n) COMMANDE
  "Un produit peut apparaitre dans 0 ou N commandes"
  "Une commande contient 1 ou N produits"
  L'association CONTIENT porte les attributs: quantite, prix_unit_cmd

- CLIENT (0,n) --- PASSE --- (1,1) COMMANDE
  "Un client peut passer 0 ou N commandes"
  "Une commande est passee par 1 et 1 seul client"
```

---

## 7. Erreurs courantes a eviter

### 7.1 Confusion entite / attribut

```
❌ MAUVAIS :
┌─────────────────┐
│    COMMANDE     │
├─────────────────┤
│ id_commande     │
│ nom_client      │  ← NON ! Le client est une entite, pas un attribut
│ email_client    │  ← de la commande
│ date_commande   │
└─────────────────┘

✅ CORRECT :
┌──────────┐      PASSE      ┌──────────┐
│  CLIENT  │────────────────│ COMMANDE │
└──────────┘  (0,n)   (1,1) └──────────┘
```

### 7.2 Oublier les cardinalites minimales

```
❌ Dire "un client a des commandes" sans preciser le minimum.
   Est-ce qu'un client PEUT ne pas avoir de commande ?

✅ Preciser : "Un client peut passer 0 ou N commandes" → (0,n)
   OU "Un client doit avoir au moins 1 commande" → (1,n)
```

### 7.3 Association N:M qui devrait etre decomposee

```
❌ MAUVAIS : association ternaire inutile
ETUDIANT ─── SUIT_DANS ─── MATIERE ─── SALLE
   (quand 2 binaires suffisent)

✅ CORRECT : decomposer si possible
ETUDIANT ─── INSCRIT ─── MATIERE
MATIERE ─── A_LIEU_DANS ─── SALLE
```

### 7.4 Attribut multivaleur dans une entite

```
❌ MAUVAIS :
┌─────────────────┐
│    CLIENT       │
├─────────────────┤
│ id_client       │
│ nom             │
│ telephone_1     │  ← Attributs multivaleurs deguises
│ telephone_2     │
│ telephone_3     │
└─────────────────┘

✅ CORRECT :
┌──────────┐  (0,n)  POSSEDE  (1,1)  ┌──────────┐
│  CLIENT  │──────────────────────────│TELEPHONE │
└──────────┘                          └──────────┘
```

### 7.5 Identifiant non stable

```
❌ MAUVAIS : utiliser un attribut qui peut changer comme identifiant
┌─────────────────┐
│    EMPLOYE      │
├─────────────────┤
│ email           │  ← L'email peut changer ! Mauvais identifiant
│ nom             │
└─────────────────┘

✅ CORRECT : identifiant technique stable
┌─────────────────┐
│    EMPLOYE      │
├─────────────────┤
│ id_employe      │  ← Auto-incremente, ne change jamais
│ email           │
│ nom             │
└─────────────────┘
```

---

## 8. Resume

| Concept | A retenir |
|---------|-----------|
| Entite | Rectangle avec nom, identifiant (souligne), attributs |
| Association | Ovale avec verbe, relie 2+ entites |
| Cardinalites MERISE | (min,max) placees du cote de l'entite concernee |
| (0,1) | Zero ou une participation |
| (1,1) | Exactement une participation (obligatoire et unique) |
| (0,n) | Zero ou plusieurs participations (optionnel) |
| (1,n) | Au moins une participation (obligatoire) |
| Association porteuse | Attributs sur l'association (seulement N:M) |
| Reflexive | Entite reliee a elle-meme (hierarchie) |
| Heritage | Generalisation/Specialisation avec contraintes {T}, {E}, {T,E} |

---

## 📝 Auto-evaluation

1. Dessinez le MCD pour le systeme IoT (Capteur, Zone, Mesure, Alerte) decrit dans la lecon 02.
2. Quelle est la difference entre (0,n) et (1,n) ? Donnez un exemple concret pour chaque.
3. Pourquoi le `prix_unitaire_commande` est-il un attribut de l'association CONTIENT et non de l'entite PRODUIT ?
4. Dans quel cas utiliseriez-vous une association reflexive ?
5. Corrigez le MCD suivant : un ETUDIANT a comme attribut `nom_universite`. Que proposez-vous ?

---

[← Precedent](02-dictionnaire-donnees.md) | [🏠 Accueil](README.md) | [Suivant →](04-modele-logique-mld.md)

---

**Academy** - Formation Data Engineer
