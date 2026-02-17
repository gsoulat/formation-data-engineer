# Module 03b - Modélisation avancée : SCD, Factless Facts et Data Vault

> **Question business :** Un client a déménagé de Paris à Lyon en juin, puis a pris la carte fidélité en septembre. Quand le directeur demande "quel est le CA par ville ?", faut-il compter ce client à Paris ou à Lyon ? Et si on veut comparer "avant fidélité" vs "après fidélité" ? Ce module vous apprend à gérer l'historique des dimensions.

---

## Avant de commencer : l'analogie du CV LinkedIn

<!-- 🔴 IMAGE : Comparaison visuelle des 3 types de SCD avec le profil LinkedIn -->
<!-- 🟢 PROMPT IMAGE : "Infographie en 3 colonnes comparant les SCD via un profil LinkedIn. Colonne 1 'SCD Type 1 - Écrasement' : un profil LinkedIn où le poste 'Développeur' est barré en rouge et remplacé par 'Data Engineer', avec un panneau 'Historique perdu !'. Colonne 2 'SCD Type 2 - Historisation' : un profil LinkedIn montrant 2 lignes d'expérience : '2020-2023 Développeur' et '2023-présent Data Engineer', avec un check vert 'Historique complet'. Colonne 3 'SCD Type 3 - Avant/Après' : un profil avec 2 colonnes 'Poste actuel: Data Engineer' et 'Poste précédent: Développeur', avec un panneau jaune 'Historique limité'. Style flat design professionnel, format paysage 16:9." -->

<!-- 🔴 VIDÉO : Animation "SCD expliqué avec un client qui déménage" -->
<!-- 🟢 PROMPT VIDÉO : "Animation motion design de 60 secondes. Personnage : Martin Dupont. Scène 1 (15s) : Martin habite à Paris, une fiche client apparaît (ville=Paris, segment=Nouveau). Scène 2 (15s) : Martin déménage à Lyon. 3 scénarios s'affichent côte à côte : Type 1 → la fiche est modifiée (Paris disparaît), Type 2 → une nouvelle fiche est créée avec des dates (l'ancienne reste), Type 3 → la fiche ajoute une colonne 'ville_précédente=Paris'. Scène 3 (15s) : Martin prend la carte fidélité. On voit l'évolution en Type 2 : maintenant 3 lignes dans le tableau avec les dates. Scène 4 (15s) : Question finale animée : 'Le CA de Martin en janvier, c'est Paris ou Lyon ? → Grâce au SCD Type 2, c'est Paris !' Style flat design, couleurs douces." -->

Quand vous changez de poste sur LinkedIn :
- **SCD Type 1** = vous **effacez** votre ancien poste et mettez le nouveau. Personne ne sait que vous étiez développeur avant d'être data engineer. Simple mais perte d'historique.
- **SCD Type 2** = vous **ajoutez une ligne** avec les dates (2020-2023 : Développeur, 2023-présent : Data Engineer). Historique complet, mais plus de lignes.
- **SCD Type 3** = vous gardez **deux colonnes** : "Poste actuel" et "Poste précédent". Limité mais rapide.

---

## Slowly Changing Dimensions (SCD)

Comment gérer l'évolution des dimensions dans le temps ?

### SCD Type 1 - Écrasement

On écrase l'ancienne valeur. **Pas d'historique.**

```sql
-- Le client C12345 passe de "Silver" à "Gold"
-- Avant : segment = "Silver"
UPDATE dim_customer
SET segment = 'Gold'
WHERE customer_id = 'C12345';
-- Après : segment = "Gold" (Silver est perdu à jamais)
```

**Quand l'utiliser :**
- Corrections d'erreurs (faute de frappe dans un nom)
- Données qu'on n'a pas besoin d'historiser (numéro de téléphone)

### SCD Type 2 - Historisation complète

On crée une **nouvelle ligne** pour chaque changement. Historique complet.

![SCD Type 2 - Historisation](./images/03/scd-type2.png)

```sql
-- Étape 1 : Clôturer l'ancien enregistrement
UPDATE dim_customer
SET valid_to = CURRENT_DATE - 1, is_current = false
WHERE customer_id = 'C12345' AND is_current = true;

-- Étape 2 : Insérer le nouvel enregistrement
INSERT INTO dim_customer (customer_id, segment, valid_from, valid_to, is_current)
VALUES ('C12345', 'Gold', CURRENT_DATE, '9999-12-31', true);
```

**Exemple concret :** Martin Dupont change de ville et de segment :

| customer_key | customer_id | nom | ville | segment | valid_from | valid_to | is_current |
|---|---|---|---|---|---|---|---|
| 1 | C001 | Martin Dupont | Paris | Nouveau | 2024-01-15 | 2024-05-31 | false |
| 2 | C001 | Martin Dupont | Lyon | Nouveau | 2024-06-01 | 2024-09-14 | false |
| 3 | C001 | Martin Dupont | Lyon | Fidèle | 2024-09-15 | 9999-12-31 | true |

Remarquez : **3 surrogate keys différentes** (1, 2, 3) pour le même client. Les ventes de janvier-mai sont rattachées à `customer_key = 1` (Paris), celles de juin-septembre à `customer_key = 2` (Lyon).

**Quand l'utiliser :**
- Historique requis (audit, réglementaire)
- Analyse "avant/après" (impact d'un changement de segment)

### SCD Type 3 - Colonnes avant/après

On garde l'ancienne ET la nouvelle valeur dans des **colonnes séparées**.

```
┌─────────────┬──────────────┬─────────────────┬─────────────────┐
│customer_key │ customer_id  │ current_segment │previous_segment │
├─────────────┼──────────────┼─────────────────┼─────────────────┤
│      1      │   C12345     │      Gold       │     Silver      │
└─────────────┴──────────────┴─────────────────┴─────────────────┘
```

**Quand l'utiliser :**
- On veut juste comparer "avant" et "après" (pas tout l'historique)
- Cas simple avec un seul changement à tracker

### Résumé : quel SCD choisir ?

| Type | Historique | Complexité | Stockage | Cas d'usage typique |
|------|------------|------------|----------|---------------------|
| **Type 1** | Aucun | Simple | Minimal | Correction d'erreurs |
| **Type 2** | Complet | Complexe | Élevé | Audit, analyse temporelle, RGPD |
| **Type 3** | Avant/après uniquement | Moyen | Modéré | Comparaison simple |

**En pratique :** 80% du temps, on utilise un mix de Type 1 (pour les attributs non critiques) et Type 2 (pour les attributs business importants comme le segment client, la ville, le statut).

---

## Tables de faits sans mesure (Factless Fact Tables)

Certaines tables de faits ne contiennent **aucune mesure numérique** — elles capturent des **événements** ou des **associations**.

Le nom est contre-intuitif : une "table de faits sans fait". En réalité, **la ligne elle-même est l'information**.

### Table d'événements

Enregistre qu'un événement s'est produit (présence, inscription, visite) :

```sql
-- Fait : présence d'un étudiant à un cours
CREATE TABLE fact_attendance (
    date_key        INT REFERENCES dim_date(date_key),
    student_key     INT REFERENCES dim_student(student_key),
    course_key      INT REFERENCES dim_course(course_key),
    classroom_key   INT REFERENCES dim_classroom(classroom_key)
    -- Pas de mesure ! La ligne elle-même EST l'information
);

-- Combien d'étudiants par cours ?
SELECT c.course_name, COUNT(*) as nb_students
FROM fact_attendance f
JOIN dim_course c ON f.course_key = c.course_key
GROUP BY c.course_name;
```

**Exemples du quotidien :**
- Fait "connexion" : un utilisateur s'est connecté à l'application (date, user, device)
- Fait "visite" : un client est entré dans un magasin (date, client, magasin)
- Fait "inscription" : un étudiant s'est inscrit à une formation (date, étudiant, formation)

### Table de couverture (Coverage)

Capture les associations valides pour analyser ce qui **n'a PAS** eu lieu :

```sql
-- Quels produits SONT CENSÉS être vendus dans chaque magasin ?
CREATE TABLE fact_product_store_coverage (
    product_key   INT REFERENCES dim_product(product_key),
    store_key     INT REFERENCES dim_store(store_key),
    date_key      INT REFERENCES dim_date(date_key)
);

-- Quels produits n'ont PAS été vendus dans le magasin 42 ?
SELECT p.product_name
FROM fact_product_store_coverage c
JOIN dim_product p ON c.product_key = p.product_key
LEFT JOIN fact_sales s
    ON c.product_key = s.product_key
    AND c.store_key = s.store_key
WHERE c.store_key = 42
  AND s.product_key IS NULL;
```

**Cas d'usage :** identifier les produits à promouvoir dans un magasin où ils ne se vendent pas alors qu'ils sont référencés.

---

## Au-delà du dimensionnel : Data Vault (aperçu)

Le **Data Vault** est une méthodologie alternative à Kimball/Inmon, conçue pour les environnements avec de **nombreuses sources de données** qui changent souvent.

### Les 3 composants

| Composant | Rôle | Analogie | Exemple |
|-----------|------|----------|---------|
| **Hub** | Identifiant business unique | L'état civil (numéro de sécu) | `hub_customer` (business key) |
| **Link** | Relation entre Hubs | Un acte de mariage (lie deux personnes) | `link_customer_order` |
| **Satellite** | Attributs descriptifs + historique | Le carnet d'adresses (change avec le temps) | `sat_customer_details` |

### Quand considérer Data Vault ?

- **Nombreuses sources** de données à intégrer (10+ systèmes)
- **Évolutions fréquentes** du modèle de données
- Besoin d'**auditabilité** complète (qui a changé quoi, quand)
- Équipe data engineering **expérimentée**

### Data Vault vs Dimensionnel

| Critère | Dimensionnel (Kimball) | Data Vault |
|---------|----------------------|------------|
| **Objectif** | Performance requêtes BI | Intégration agile de données |
| **Complexité** | Modéré | Élevé |
| **Historisation** | SCD explicite | Automatique (Satellites) |
| **Évolutivité** | Schéma rigide | Très évolutif |
| **Utilisateurs** | Analystes, BI | Data Engineers |
| **Quand l'utiliser** | DW classique, BI | DW d'entreprise multi-sources |

> **En pratique :** Le dimensionnel (Star Schema) reste le standard pour les projets BI. Data Vault est utilisé en **couche intermédiaire** (entre les sources et le modèle dimensionnel final), notamment dans les architectures Medallion (Silver layer). Vous n'en aurez pas besoin pour le brief, mais vous le rencontrerez en entreprise.

---

## Points clés à retenir

- **SCD Type 1** = écrasement (pas d'historique)
- **SCD Type 2** = nouvelle ligne avec dates (historique complet) — le plus courant
- **SCD Type 3** = colonnes avant/après (historique limité)
- **Factless fact tables** = tables de faits sans mesure numérique (événements, couverture)
- **Data Vault** = méthodologie Hub/Link/Satellite pour l'intégration multi-sources

---

**Prochain module :** [04 - Architectures et Patterns](./04-architectures.md)

[Module précédent](./03a-modelisation-fondamentaux.md) | [Retour au sommaire](./README.md)
