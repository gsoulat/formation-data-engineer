# JPA / Hibernate — JPQL et Criteria API

## JPQL — Jakarta Persistence Query Language

JPQL est un langage de requêtes orienté objet. Il ressemble à SQL mais opère sur les **entités et leurs attributs** (pas sur les tables et colonnes).

```java
// SQL :  SELECT * FROM produits WHERE prix > 100 ORDER BY nom
// JPQL : SELECT p FROM Produit p WHERE p.prix > 100 ORDER BY p.nom
//               ↑                           ↑                  ↑
//          classe Java                  attribut Java      attribut Java
```

## Requêtes JPQL de base

```java
EntityManager em = emf.createEntityManager();

// SELECT simple
List<Produit> tous = em
    .createQuery("SELECT p FROM Produit p", Produit.class)
    .getResultList();

// WHERE
List<Produit> actifs = em
    .createQuery("SELECT p FROM Produit p WHERE p.actif = true ORDER BY p.nom", Produit.class)
    .getResultList();

// Paramètres nommés (TOUJOURS utiliser des paramètres — protection contre injection SQL)
List<Produit> parCategorie = em
    .createQuery(
        "SELECT p FROM Produit p WHERE p.categorie.nom = :catNom AND p.prix < :maxPrix",
        Produit.class
    )
    .setParameter("catNom", "Informatique")
    .setParameter("maxPrix", new BigDecimal("200"))
    .getResultList();

// LIKE
List<Produit> recherche = em
    .createQuery("SELECT p FROM Produit p WHERE LOWER(p.nom) LIKE :terme", Produit.class)
    .setParameter("terme", "%clavier%")
    .getResultList();

// IN
List<Produit> parIds = em
    .createQuery("SELECT p FROM Produit p WHERE p.id IN :ids", Produit.class)
    .setParameter("ids", List.of(1L, 2L, 3L))
    .getResultList();

// IS NULL / IS NOT NULL
List<Produit> sansDescription = em
    .createQuery("SELECT p FROM Produit p WHERE p.description IS NULL", Produit.class)
    .getResultList();

// Pagination
List<Produit> page2 = em
    .createQuery("SELECT p FROM Produit p ORDER BY p.id", Produit.class)
    .setFirstResult(10)  // OFFSET
    .setMaxResults(10)   // LIMIT
    .getResultList();
```

## Agrégations JPQL

```java
// COUNT
Long total = em
    .createQuery("SELECT COUNT(p) FROM Produit p WHERE p.actif = true", Long.class)
    .getSingleResult();

// SUM, AVG, MIN, MAX
Object[] stats = (Object[]) em
    .createQuery(
        "SELECT MIN(p.prix), MAX(p.prix), AVG(p.prix), SUM(p.stock) FROM Produit p"
    )
    .getSingleResult();
System.out.printf("Min=%.2f Max=%.2f Moy=%.2f Stock=%d%n",
    stats[0], stats[1], stats[2], stats[3]);

// GROUP BY
List<Object[]> parCategorie = em
    .createQuery(
        "SELECT p.categorie.nom, COUNT(p), AVG(p.prix) " +
        "FROM Produit p GROUP BY p.categorie.nom " +
        "HAVING COUNT(p) > 2 " +
        "ORDER BY COUNT(p) DESC"
    )
    .getResultList();

for (Object[] row : parCategorie) {
    System.out.printf("Catégorie: %s — %d produits — %.2f€ moy%n",
        row[0], row[1], row[2]);
}
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** IntelliJ IDEA — exécuter les requêtes JPQL avec les logs SQL activés, montrer le SQL généré vs la JPQL
> **Expliquer :** Pour chaque requête JPQL, montrer le SQL généré dans la console Hibernate. Insister sur la différence sémantique : en JPQL on parle d'objets et d'attributs, Hibernate traduit en SQL avec les bons noms de tables/colonnes. Montrer aussi la requête GROUP BY dans DBeaver directement en SQL pour comparaison.

---

## Projections — DTO avec constructeur

Au lieu de charger des entités complètes, projeter seulement les champs nécessaires.

```java
// Créer un DTO (Data Transfer Object)
public class ProduitResume {
    private final String nom;
    private final BigDecimal prix;
    private final String categorieNom;

    // Constructeur JPQL (doit correspondre exactement aux types dans la requête)
    public ProduitResume(String nom, BigDecimal prix, String categorieNom) {
        this.nom = nom;
        this.prix = prix;
        this.categorieNom = categorieNom;
    }

    public String getNom() { return nom; }
    public BigDecimal getPrix() { return prix; }
    public String getCategorieNom() { return categorieNom; }
}

// Requête avec projection
List<ProduitResume> resumes = em
    .createQuery(
        "SELECT new com.formation.dto.ProduitResume(p.nom, p.prix, p.categorie.nom) " +
        "FROM Produit p WHERE p.actif = true ORDER BY p.prix",
        ProduitResume.class
    )
    .getResultList();

for (ProduitResume r : resumes) {
    System.out.printf("%s (%s) — %.2f€%n", r.getNom(), r.getCategorieNom(), r.getPrix());
}
```

## @NamedQuery — requêtes prédéfinies

```java
@Entity
@Table(name = "produits")
@NamedQueries({
    @NamedQuery(
        name = "Produit.findActifs",
        query = "SELECT p FROM Produit p WHERE p.actif = true ORDER BY p.nom"
    ),
    @NamedQuery(
        name = "Produit.findByCategorie",
        query = "SELECT p FROM Produit p WHERE p.categorie.nom = :categorie AND p.actif = true"
    ),
    @NamedQuery(
        name = "Produit.countByStatut",
        query = "SELECT p.statut, COUNT(p) FROM Produit p GROUP BY p.statut"
    )
})
public class Produit { /* ... */ }

// Utilisation
List<Produit> actifs = em
    .createNamedQuery("Produit.findActifs", Produit.class)
    .getResultList();

List<Produit> infoProducts = em
    .createNamedQuery("Produit.findByCategorie", Produit.class)
    .setParameter("categorie", "Informatique")
    .getResultList();
```

## Criteria API — requêtes type-safe

La Criteria API permet de construire des requêtes programmatiquement avec des type checks à la compilation.

```java
import jakarta.persistence.criteria.*;

EntityManager em = emf.createEntityManager();
CriteriaBuilder cb = em.getCriteriaBuilder();

// Requête simple
CriteriaQuery<Produit> cq = cb.createQuery(Produit.class);
Root<Produit> root = cq.from(Produit.class);

cq.select(root)
  .where(
      cb.and(
          cb.isTrue(root.get("actif")),
          cb.greaterThan(root.get("prix"), new BigDecimal("50"))
      )
  )
  .orderBy(cb.asc(root.get("prix")));

List<Produit> produits = em.createQuery(cq).getResultList();

// Requête avec JOIN
CriteriaQuery<Produit> cqJoin = cb.createQuery(Produit.class);
Root<Produit> pRoot = cqJoin.from(Produit.class);
Join<Produit, Categorie> catJoin = pRoot.join("categorie", JoinType.LEFT);

cqJoin.select(pRoot)
    .where(cb.equal(catJoin.get("nom"), "Informatique"))
    .orderBy(cb.desc(pRoot.get("prix")));

List<Produit> informatique = em.createQuery(cqJoin).getResultList();

// Requête dynamique (selon les filtres présents)
public List<Produit> rechercher(String nom, BigDecimal minPrix, BigDecimal maxPrix, Boolean actif) {
    CriteriaBuilder cb = em.getCriteriaBuilder();
    CriteriaQuery<Produit> cq = cb.createQuery(Produit.class);
    Root<Produit> root = cq.from(Produit.class);

    List<Predicate> predicates = new ArrayList<>();

    if (nom != null && !nom.isBlank()) {
        predicates.add(cb.like(cb.lower(root.get("nom")), "%" + nom.toLowerCase() + "%"));
    }
    if (minPrix != null) {
        predicates.add(cb.greaterThanOrEqualTo(root.get("prix"), minPrix));
    }
    if (maxPrix != null) {
        predicates.add(cb.lessThanOrEqualTo(root.get("prix"), maxPrix));
    }
    if (actif != null) {
        predicates.add(cb.equal(root.get("actif"), actif));
    }

    cq.select(root)
      .where(predicates.toArray(new Predicate[0]))
      .orderBy(cb.asc(root.get("nom")));

    return em.createQuery(cq).getResultList();
}
```

## Requêtes SQL natives

Quand JPQL n'est pas suffisant :

```java
// SQL natif avec mapping vers une entité
List<Produit> produits = em
    .createNativeQuery(
        "SELECT * FROM produits WHERE EXTRACT(YEAR FROM created_at) = :annee",
        Produit.class
    )
    .setParameter("annee", 2024)
    .getResultList();

// SQL natif avec résultat brut (List<Object[]>)
List<Object[]> stats = em
    .createNativeQuery("""
        SELECT
            c.nom AS categorie,
            COUNT(p.id) AS nb_produits,
            ROUND(AVG(p.prix)::numeric, 2) AS prix_moyen,
            SUM(p.stock * p.prix)::numeric AS valeur_stock
        FROM categories c
        LEFT JOIN produits p ON p.categorie_id = c.id AND p.actif = true
        GROUP BY c.id, c.nom
        ORDER BY valeur_stock DESC NULLS LAST
    """)
    .getResultList();

for (Object[] row : stats) {
    System.out.printf("%s: %d produits, %.2f€ moy, %.2f€ stock%n",
        row[0], ((Number)row[1]).intValue(), row[2], row[3]);
}
```

## UPDATE et DELETE en JPQL

```java
EntityTransaction tx = em.getTransaction();
tx.begin();

// UPDATE en masse (sans charger les entités)
int nb = em
    .createQuery("UPDATE Produit p SET p.actif = false WHERE p.stock = 0")
    .executeUpdate();
System.out.println(nb + " produits désactivés");

// DELETE en masse
int nbSupp = em
    .createQuery("DELETE FROM Produit p WHERE p.actif = false AND p.stock = 0")
    .executeUpdate();
System.out.println(nbSupp + " produits supprimés");

tx.commit();
```
