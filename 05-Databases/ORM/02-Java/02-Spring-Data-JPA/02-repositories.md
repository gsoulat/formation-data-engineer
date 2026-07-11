# Spring Data JPA — Query Methods, @Query et Pageable

## Query Methods — nommage auto-magique

Spring Data JPA génère automatiquement les requêtes SQL à partir du nom de la méthode.

```java
// repositories/ProduitRepository.java
package com.formation.repositories;

import com.formation.models.Produit;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;

@Repository
public interface ProduitRepository extends JpaRepository<Produit, Long> {

    // findBy + NomAttribut = WHERE attribut = ?
    List<Produit> findByActif(boolean actif);

    // findBy + Attribut1 + And/Or + Attribut2
    List<Produit> findByActifAndCategorie_Nom(boolean actif, String categorieNom);

    // Comparaisons : GreaterThan, LessThan, Between, Like, In...
    List<Produit> findByPrixLessThan(BigDecimal maxPrix);
    List<Produit> findByPrixBetween(BigDecimal min, BigDecimal max);
    List<Produit> findByPrixGreaterThanEqual(BigDecimal minPrix);

    // LIKE (case sensitive)
    List<Produit> findByNomContaining(String terme);

    // LIKE case-insensitive
    List<Produit> findByNomContainingIgnoreCase(String terme);

    // Commence par / finit par
    List<Produit> findByNomStartingWith(String prefix);

    // NULL / NOT NULL
    List<Produit> findByDescriptionIsNull();
    List<Produit> findByDescriptionIsNotNull();

    // IN
    List<Produit> findByIdIn(List<Long> ids);

    // Tri inclus dans le nom
    List<Produit> findByActifOrderByPrixAsc(boolean actif);
    List<Produit> findByActifOrderByPrixDescNomAsc(boolean actif);

    // Compter
    long countByActif(boolean actif);
    long countByCategorie_Nom(String categorieNom);

    // Existence
    boolean existsByNom(String nom);

    // Suppression
    void deleteByActifFalseAndStockEquals(int stock);

    // Top N résultats
    List<Produit> findTop5ByActifOrderByPrixDesc(boolean actif);
    Optional<Produit> findFirstByCategorie_NomOrderByPrixAsc(String categorieNom);

    // Avec Pageable (tri et pagination dynamiques)
    Page<Produit> findByActif(boolean actif, Pageable pageable);
    Page<Produit> findByCategorie_NomAndActif(String categorieNom, boolean actif, Pageable pageable);
}
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** IntelliJ IDEA — montrer l'autocomplétion des noms de méthodes et les logs SQL correspondants à l'exécution
> **Expliquer :** Taper `findBy` dans l'interface et montrer l'autocomplétion IntelliJ. Exécuter 3-4 méthodes différentes et montrer dans les logs le SQL généré par Spring Data. Insister sur la convention de nommage : `findBy`, `countBy`, `deleteBy`, les opérateurs `And`, `Or`, `Between`, `In`, `Like`, `OrderBy`.

---

## @Query — requêtes personnalisées

Quand le nommage automatique n'est pas suffisant, utilisez `@Query`.

```java
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.repository.query.Param;
import org.springframework.transaction.annotation.Transactional;

public interface ProduitRepository extends JpaRepository<Produit, Long> {

    // JPQL avec @Query
    @Query("SELECT p FROM Produit p WHERE p.actif = true AND p.prix <= :maxPrix ORDER BY p.prix")
    List<Produit> findActifsAbordables(@Param("maxPrix") BigDecimal maxPrix);

    // JPQL avec JOIN sur catégorie
    @Query("""
        SELECT p FROM Produit p
        JOIN p.categorie c
        WHERE c.nom = :categorieNom
          AND p.actif = true
        ORDER BY p.nom
        """)
    List<Produit> findByCategorieNom(@Param("categorieNom") String categorieNom);

    // Projection — retourner seulement certains champs via interface
    @Query("SELECT p.nom AS nom, p.prix AS prix FROM Produit p WHERE p.actif = true")
    List<ProduitResume> findResumes();

    // SQL natif (nativeQuery = true)
    @Query(
        value = """
            SELECT p.*, c.nom AS cat_nom
            FROM produits p
            LEFT JOIN categories c ON c.id = p.categorie_id
            WHERE p.actif = TRUE
              AND EXTRACT(YEAR FROM p.created_at) = :annee
            ORDER BY p.prix DESC
            """,
        nativeQuery = true
    )
    List<Object[]> findCreesEnAnnee(@Param("annee") int annee);

    // @Query avec Pageable
    @Query("SELECT p FROM Produit p WHERE p.actif = :actif")
    Page<Produit> findWithPaging(@Param("actif") boolean actif, Pageable pageable);

    // COUNT séparé pour les requêtes complexes (optimisation)
    @Query(
        value = "SELECT p FROM Produit p JOIN p.categorie c WHERE c.nom = :cat",
        countQuery = "SELECT COUNT(p) FROM Produit p JOIN p.categorie c WHERE c.nom = :cat"
    )
    Page<Produit> findByCatPaged(@Param("cat") String categorieNom, Pageable pageable);

    // UPDATE avec @Modifying
    @Modifying
    @Transactional
    @Query("UPDATE Produit p SET p.actif = false WHERE p.stock = 0")
    int desactiverSansStock();

    @Modifying
    @Transactional
    @Query("UPDATE Produit p SET p.prix = p.prix * :facteur WHERE p.categorie.id = :catId")
    int majPrixCategorie(@Param("catId") Long categorieId, @Param("facteur") BigDecimal facteur);

    // Statistiques par catégorie
    @Query("""
        SELECT c.nom, COUNT(p.id), AVG(p.prix), SUM(p.stock)
        FROM Produit p
        JOIN p.categorie c
        WHERE p.actif = true
        GROUP BY c.id, c.nom
        ORDER BY COUNT(p.id) DESC
        """)
    List<Object[]> getStatistiquesParCategorie();
}

// Interface de projection
interface ProduitResume {
    String getNom();
    BigDecimal getPrix();
}
```

## Pagination avec Pageable

```java
// Dans le service
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;

@Service
public class ProduitService {

    public Page<Produit> findAllPaged(int page, int size, String sortBy, String direction) {
        Sort.Direction dir = direction.equalsIgnoreCase("desc")
            ? Sort.Direction.DESC : Sort.Direction.ASC;

        Pageable pageable = PageRequest.of(page, size, Sort.by(dir, sortBy));
        return repository.findAll(pageable);
    }

    public Page<Produit> findActifsPaged(boolean actif, int page, int size) {
        Pageable pageable = PageRequest.of(page, size, Sort.by("prix").ascending());
        return repository.findByActif(actif, pageable);
    }
}

// Dans le controller
@GetMapping
public Page<Produit> getAll(
    @RequestParam(defaultValue = "0") int page,
    @RequestParam(defaultValue = "20") int size,
    @RequestParam(defaultValue = "nom") String sortBy,
    @RequestParam(defaultValue = "asc") String direction
) {
    return service.findAllPaged(page, size, sortBy, direction);
}
```

```bash
# GET avec pagination et tri
curl "http://localhost:8080/api/produits?page=0&size=10&sortBy=prix&direction=desc"

# Réponse Page<T>
{
  "content": [...],       // Les données
  "pageable": {...},
  "totalElements": 57,    // Total d'éléments
  "totalPages": 6,        // Total de pages
  "last": false,
  "first": true,
  "size": 10,
  "number": 0,
  "numberOfElements": 10
}
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Postman — tester les endpoints de pagination, montrer la réponse JSON avec les métadonnées de pagination
> **Expliquer :** Montrer la structure de réponse `Page<T>` dans Postman : `content`, `totalElements`, `totalPages`, `number`. Tester plusieurs pages successives. Montrer dans les logs SQL le `LIMIT`/`OFFSET` généré par Spring. Comparer avec une liste complète sans pagination.

---

## Specifications — filtres dynamiques

Pour les recherches avec critères multiples optionnels.

```java
import org.springframework.data.jpa.domain.Specification;
import jakarta.persistence.criteria.*;

// Classe de spécifications
public class ProduitSpecifications {

    public static Specification<Produit> actif(Boolean actif) {
        if (actif == null) return null;
        return (root, query, cb) -> cb.equal(root.get("actif"), actif);
    }

    public static Specification<Produit> nomContient(String terme) {
        if (terme == null || terme.isBlank()) return null;
        return (root, query, cb) ->
            cb.like(cb.lower(root.get("nom")), "%" + terme.toLowerCase() + "%");
    }

    public static Specification<Produit> prixEntre(BigDecimal min, BigDecimal max) {
        return (root, query, cb) -> {
            if (min == null && max == null) return null;
            if (min == null) return cb.lessThanOrEqualTo(root.get("prix"), max);
            if (max == null) return cb.greaterThanOrEqualTo(root.get("prix"), min);
            return cb.between(root.get("prix"), min, max);
        };
    }

    public static Specification<Produit> categorieNom(String categorieNom) {
        if (categorieNom == null) return null;
        return (root, query, cb) -> {
            Join<Produit, ?> catJoin = root.join("categorie", JoinType.LEFT);
            return cb.equal(catJoin.get("nom"), categorieNom);
        };
    }
}

// Repository doit étendre JpaSpecificationExecutor
public interface ProduitRepository
    extends JpaRepository<Produit, Long>,
            JpaSpecificationExecutor<Produit> { }

// Service — utilisation
import org.springframework.data.jpa.domain.Specification;

public Page<Produit> rechercher(
    String nom, BigDecimal minPrix, BigDecimal maxPrix,
    Boolean actif, String categorieNom,
    Pageable pageable
) {
    Specification<Produit> spec = Specification
        .where(ProduitSpecifications.actif(actif))
        .and(ProduitSpecifications.nomContient(nom))
        .and(ProduitSpecifications.prixEntre(minPrix, maxPrix))
        .and(ProduitSpecifications.categorieNom(categorieNom));

    return repository.findAll(spec, pageable);
}

// Controller
@GetMapping("/recherche")
public Page<Produit> recherche(
    @RequestParam(required = false) String nom,
    @RequestParam(required = false) BigDecimal minPrix,
    @RequestParam(required = false) BigDecimal maxPrix,
    @RequestParam(required = false) Boolean actif,
    @RequestParam(required = false) String categorie,
    @RequestParam(defaultValue = "0") int page,
    @RequestParam(defaultValue = "20") int size
) {
    Pageable pageable = PageRequest.of(page, size, Sort.by("nom"));
    return service.rechercher(nom, minPrix, maxPrix, actif, categorie, pageable);
}
```

## Comparaison Spring Data JPA vs JPA pur

| Aspect | JPA pur | Spring Data JPA |
|--------|---------|-----------------|
| Boilerplate | Beaucoup | Minimal |
| Query methods | Manuelles | Auto-générées |
| Pagination | Manuelle | `Pageable` natif |
| Transactions | `@Transactional` manuel | `@Transactional` sur service |
| Tests | Plus complexes | `@DataJpaTest` |
| Couplage | Faible | Dépend de Spring |
| Flexibilité | Maximale | Contraintes Spring |

**Recommandation** : Dans tout projet Spring Boot, utilisez Spring Data JPA. Pour les projets Java sans Spring, utilisez JPA/Hibernate directement.
