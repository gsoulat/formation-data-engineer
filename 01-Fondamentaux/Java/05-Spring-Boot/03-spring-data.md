# Spring Boot — Spring Data JPA : @Repository, JpaRepository, @Transactional

## 1. Qu'est-ce que Spring Data JPA ?

Spring Data JPA est une couche d'abstraction au-dessus de JPA (Java Persistence API) et Hibernate. Elle génère automatiquement les requêtes à partir des noms des méthodes.

```
Application Java
     ↓
Spring Data JPA  ← Génère les requêtes automatiquement
     ↓
JPA (API)
     ↓
Hibernate (implémentation JPA)
     ↓
JDBC
     ↓
Base de données (H2, PostgreSQL, MySQL...)
```

## 2. Entités JPA

```java
package com.formation.demo.model;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "produits")
public class Produit {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)  // Auto-incrément
    private Long id;

    @Column(nullable = false, length = 100)
    private String nom;

    @Column(nullable = false, precision = 10, scale = 2)
    private double prix;

    @Column(nullable = false)
    private int stock;

    @Column(length = 50)
    private String categorie;

    @Column(updatable = false)  // Défini à la création, jamais mis à jour
    private LocalDateTime dateCreation;

    private LocalDateTime dateMiseAJour;

    // Callbacks JPA
    @PrePersist
    public void avantCreation() {
        dateCreation = LocalDateTime.now();
        dateMiseAJour = LocalDateTime.now();
    }

    @PreUpdate
    public void avantMiseAJour() {
        dateMiseAJour = LocalDateTime.now();
    }

    // Constructeurs, getters, setters...
    public Produit() {}

    public Produit(String nom, double prix, int stock, String categorie) {
        this.nom = nom;
        this.prix = prix;
        this.stock = stock;
        this.categorie = categorie;
    }

    public Long getId()                { return id; }
    public String getNom()             { return nom; }
    public void setNom(String nom)     { this.nom = nom; }
    public double getPrix()            { return prix; }
    public void setPrix(double prix)   { this.prix = prix; }
    public int getStock()              { return stock; }
    public void setStock(int stock)    { this.stock = stock; }
    public String getCategorie()       { return categorie; }
    public void setCategorie(String c) { this.categorie = c; }
    public LocalDateTime getDateCreation()   { return dateCreation; }
    public LocalDateTime getDateMiseAJour()  { return dateMiseAJour; }
}

// Entité avec relation Many-to-One
@Entity
@Table(name = "commandes")
public class Commande {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)  // Chargement paresseux (recommandé)
    @JoinColumn(name = "client_id", nullable = false)
    private Client client;

    @OneToMany(mappedBy = "commande", cascade = CascadeType.ALL, orphanRemoval = true)
    private java.util.List<LigneCommande> lignes = new java.util.ArrayList<>();

    @Enumerated(EnumType.STRING)  // Stocke le nom de l'enum, pas le numéro
    private StatutCommande statut;

    private LocalDateTime dateCommande;

    public void ajouterLigne(LigneCommande ligne) {
        lignes.add(ligne);
        ligne.setCommande(this);
    }
}

enum StatutCommande { EN_ATTENTE, CONFIRMEE, EXPEDIEE, LIVREE, ANNULEE }

// Entité avec clé composite
@Entity
@Table(name = "evaluations")
public class Evaluation {

    @EmbeddedId
    private EvaluationId id;

    private int note;
    private String commentaire;
}

@Embeddable
public class EvaluationId implements java.io.Serializable {
    private Long produitId;
    private Long clientId;
}
```

## 3. Repository — JpaRepository

```java
package com.formation.demo.repository;

import com.formation.demo.model.Produit;
import org.springframework.data.jpa.repository.*;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import java.util.*;

// JpaRepository<T, ID> fournit 20+ méthodes CRUD automatiquement
@Repository
public interface ProduitRepository extends JpaRepository<Produit, Long> {

    // --- Méthodes héritées de JpaRepository ---
    // save(entity)                    → INSERT ou UPDATE
    // saveAll(entities)               → sauvegarde multiple
    // findById(id)                    → Optional<T>
    // findAll()                       → List<T>
    // findAllById(ids)                → List<T>
    // existsById(id)                  → boolean
    // count()                         → long
    // deleteById(id)                  → void
    // deleteAll()                     → void
    // flush()                         → persiste en base maintenant
    // saveAndFlush(entity)            → save + flush

    // --- Query Methods : Spring génère la requête depuis le nom ---

    // SELECT * FROM produits WHERE nom = ?
    List<Produit> findByNom(String nom);

    // SELECT * FROM produits WHERE categorie = ?
    List<Produit> findByCategorie(String categorie);

    // SELECT * FROM produits WHERE categorie = ? ORDER BY prix ASC
    List<Produit> findByCategorieOrderByPrixAsc(String categorie);

    // SELECT * FROM produits WHERE prix <= ?
    List<Produit> findByPrixLessThanEqual(double prixMax);

    // SELECT * FROM produits WHERE prix BETWEEN ? AND ?
    List<Produit> findByPrixBetween(double min, double max);

    // SELECT * FROM produits WHERE nom LIKE %?%
    List<Produit> findByNomContainingIgnoreCase(String motCle);

    // SELECT * FROM produits WHERE stock = 0
    List<Produit> findByStockEquals(int stock);

    // Stock = 0 → en rupture
    List<Produit> findByStockLessThan(int seuil);

    // SELECT * FROM produits WHERE categorie = ? AND prix <= ?
    List<Produit> findByCategorieAndPrixLessThanEqual(String cat, double max);

    // SELECT * FROM produits WHERE categorie IN (...)
    List<Produit> findByCategorieIn(List<String> categories);

    // Vérifier l'existence
    boolean existsByNom(String nom);

    // Compter
    long countByCategorie(String categorie);

    // Supprimer par critère
    void deleteByCategorie(String categorie);

    // --- @Query : JPQL personnalisé ---
    @Query("SELECT p FROM Produit p WHERE p.prix > :prix ORDER BY p.prix ASC")
    List<Produit> trouverPlusChersQue(@Param("prix") double prix);

    @Query("SELECT p FROM Produit p WHERE LOWER(p.nom) LIKE LOWER(CONCAT('%', :motCle, '%'))")
    List<Produit> rechercherParMotCle(@Param("motCle") String motCle);

    // JPQL avec projection (ne récupérer que certains champs)
    @Query("SELECT p.nom, p.prix FROM Produit p WHERE p.categorie = :cat")
    List<Object[]> projectionNomPrix(@Param("cat") String categorie);

    // --- @Query : SQL natif ---
    @Query(value = "SELECT * FROM produits WHERE stock = 0", nativeQuery = true)
    List<Produit> trouverEnRupture();

    // --- Modifications avec @Modifying ---
    @Modifying
    @Query("UPDATE Produit p SET p.prix = p.prix * :facteur WHERE p.categorie = :cat")
    int mettreAJourPrixCategorie(@Param("facteur") double facteur, @Param("cat") String cat);

    @Modifying
    @Query("DELETE FROM Produit p WHERE p.stock = 0")
    int supprimerEnRupture();
}
```

## 4. Pagination et tri

```java
import org.springframework.data.domain.*;

@Repository
public interface ProduitRepository extends JpaRepository<Produit, Long> {

    // Pagination automatique
    Page<Produit> findByCategorie(String categorie, Pageable pageable);
    Page<Produit> findAll(Pageable pageable);
    List<Produit> findByPrixLessThan(double max, Sort sort);
}

// Utilisation dans le service
@Service
public class ProduitService {

    public Page<ProduitResponse> listerAvecPagination(int page, int taille, String triPar) {
        Pageable pageable = PageRequest.of(
            page,      // numéro de page (commence à 0)
            taille,    // éléments par page
            Sort.by(triPar).ascending()
        );

        return repository.findAll(pageable)
            .map(ProduitResponse::fromEntity);
    }

    public Page<ProduitResponse> listerParCategorie(String cat, int page, int taille) {
        Pageable pageable = PageRequest.of(page, taille,
            Sort.by("prix").ascending().and(Sort.by("nom").ascending()));
        return repository.findByCategorie(cat, pageable)
            .map(ProduitResponse::fromEntity);
    }
}

// Dans le controller
@GetMapping
public ResponseEntity<Map<String, Object>> lister(
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(defaultValue = "10") int taille,
        @RequestParam(defaultValue = "nom") String tri) {

    Page<ProduitResponse> pageResult = produitService.listerAvecPagination(page, taille, tri);

    Map<String, Object> response = new LinkedHashMap<>();
    response.put("contenu", pageResult.getContent());
    response.put("page", pageResult.getNumber());
    response.put("taille", pageResult.getSize());
    response.put("totalElements", pageResult.getTotalElements());
    response.put("totalPages", pageResult.getTotalPages());
    response.put("dernieredPage", pageResult.isLast());

    return ResponseEntity.ok(response);
}
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Activer `spring.jpa.show-sql=true` et `spring.jpa.properties.hibernate.format_sql=true` dans `application.properties`. Lancer une requête `findByCategorie()` et montrer dans la console IntelliJ la requête SQL générée automatiquement par Spring Data.
> **Expliquer :** Montrer comment Spring Data traduit `findByNomContainingIgnoreCase` en SQL `WHERE LOWER(nom) LIKE LOWER(?)`. Insister sur le fait que c'est de la génération de code à la compilation/chargement, pas de la réflexion lente. Montrer aussi le comportement de la pagination dans la console SQL.
---

## 5. @Transactional

```java
package com.formation.demo.service;

import org.springframework.transaction.annotation.Transactional;
import org.springframework.stereotype.Service;

@Service
public class CommandeService {

    private final CommandeRepository commandeRepo;
    private final ProduitRepository  produitRepo;
    private final NotificationService notifService;

    public CommandeService(CommandeRepository commandeRepo,
                           ProduitRepository produitRepo,
                           NotificationService notifService) {
        this.commandeRepo   = commandeRepo;
        this.produitRepo    = produitRepo;
        this.notifService   = notifService;
    }

    // @Transactional : tout se passe dans une seule transaction
    // Si une exception est lancée → ROLLBACK automatique
    @Transactional
    public Commande passerCommande(Long clientId, List<LigneCommandeRequest> lignes) {

        Commande commande = new Commande();
        commande.setStatut(StatutCommande.EN_ATTENTE);
        commande.setDateCommande(LocalDateTime.now());

        for (LigneCommandeRequest ligne : lignes) {
            // 1. Récupérer le produit
            Produit produit = produitRepo.findById(ligne.produitId())
                .orElseThrow(() -> new ResourceNotFoundException("Produit", ligne.produitId()));

            // 2. Vérifier le stock
            if (produit.getStock() < ligne.quantite()) {
                throw new StockInsuffisantException(produit.getNom(), produit.getStock());
                // → ROLLBACK : aucune modification n'est sauvegardée
            }

            // 3. Décrémenter le stock
            produit.setStock(produit.getStock() - ligne.quantite());
            produitRepo.save(produit);

            // 4. Créer la ligne de commande
            LigneCommande lc = new LigneCommande(produit, ligne.quantite(), produit.getPrix());
            commande.ajouterLigne(lc);
        }

        // 5. Sauvegarder la commande
        Commande sauvegardee = commandeRepo.save(commande);

        // 6. Envoyer la notification (hors transaction)
        // notifService.envoyer(clientId, "Commande confirmée");

        return sauvegardee;
    }

    // Propagation des transactions
    @Transactional(propagation = Propagation.REQUIRED)     // rejoint la transaction existante (défaut)
    @Transactional(propagation = Propagation.REQUIRES_NEW) // toujours nouvelle transaction
    @Transactional(propagation = Propagation.SUPPORTS)     // utilise si existe, sinon sans
    @Transactional(propagation = Propagation.NEVER)        // erreur si dans une transaction

    // Isolation level
    @Transactional(isolation = Isolation.READ_COMMITTED)   // défaut sur la plupart des DB
    @Transactional(isolation = Isolation.REPEATABLE_READ)
    @Transactional(isolation = Isolation.SERIALIZABLE)

    // Gestion des exceptions
    @Transactional(rollbackFor = Exception.class)          // rollback sur checked exceptions aussi
    @Transactional(noRollbackFor = BusinessException.class)// pas de rollback pour cette exception

    // Timeout
    @Transactional(timeout = 30)  // rollback si > 30 secondes

    public void exempleAnnotations() {}

    // readOnly = true : optimisation pour les lectures (pas de dirty checking)
    @Transactional(readOnly = true)
    public List<Commande> listerCommandes() {
        return commandeRepo.findAll();
    }
}
```

## 6. Relations JPA

```java
// --- One-to-Many / Many-to-One ---
@Entity
public class Client {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String nom;

    @OneToMany(mappedBy = "client",          // nom du champ dans Commande
               cascade = CascadeType.ALL,    // opérations cascadées
               orphanRemoval = true,         // supprime les orphelins
               fetch = FetchType.LAZY)       // chargement différé (recommandé)
    private List<Commande> commandes = new ArrayList<>();
}

@Entity
public class Commande {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "client_id")
    private Client client;
}

// --- Many-to-Many ---
@Entity
public class Etudiant {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String nom;

    @ManyToMany(cascade = {CascadeType.PERSIST, CascadeType.MERGE})
    @JoinTable(
        name = "etudiant_cours",
        joinColumns = @JoinColumn(name = "etudiant_id"),
        inverseJoinColumns = @JoinColumn(name = "cours_id")
    )
    private Set<Cours> cours = new HashSet<>();
}

@Entity
public class Cours {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String titre;

    @ManyToMany(mappedBy = "cours")
    private Set<Etudiant> etudiants = new HashSet<>();
}

// --- Projection interface (évite le chargement de toutes les colonnes) ---
public interface ProduitSummary {
    String getNom();
    double getPrix();
    String getCategorie();
}

@Repository
public interface ProduitRepository extends JpaRepository<Produit, Long> {
    List<ProduitSummary> findByCategorie(String categorie);  // seulement 3 colonnes
}
```

## 7. Données initiales

```sql
-- src/main/resources/data.sql (chargé au démarrage si spring.jpa.hibernate.ddl-auto=create)
INSERT INTO produits (nom, prix, stock, categorie) VALUES ('Clavier', 79.99, 15, 'Informatique');
INSERT INTO produits (nom, prix, stock, categorie) VALUES ('Souris', 29.99, 30, 'Informatique');
INSERT INTO produits (nom, prix, stock, categorie) VALUES ('Écran 24"', 299.99, 5, 'Informatique');
INSERT INTO produits (nom, prix, stock, categorie) VALUES ('Bureau debout', 450.00, 3, 'Mobilier');
INSERT INTO produits (nom, prix, stock, categorie) VALUES ('Chaise ergonomique', 199.99, 8, 'Mobilier');
```

```java
// Ou via CommandLineRunner (Java)
@Component
@Profile("dev")
public class DataSeeder implements CommandLineRunner {

    private final ProduitRepository repo;

    public DataSeeder(ProduitRepository repo) { this.repo = repo; }

    @Override
    @Transactional
    public void run(String... args) {
        if (repo.count() == 0) {
            repo.saveAll(List.of(
                new Produit("Clavier", 79.99, 15, "Informatique"),
                new Produit("Souris", 29.99, 30, "Informatique"),
                new Produit("Bureau", 450.00, 3, "Mobilier")
            ));
            System.out.println("Données de démo insérées : " + repo.count() + " produits");
        }
    }
}
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Accéder à la console H2 à `http://localhost:8080/h2-console`. Se connecter (JDBC URL: `jdbc:h2:mem:testdb`, user: `sa`, password vide). Montrer le contenu des tables créées automatiquement par Hibernate. Exécuter une requête SQL directe. Puis montrer via l'API que les données sont bien là.
> **Expliquer :** Expliquer le schéma auto-généré par Hibernate (`ddl-auto=create-drop`), les colonnes créées par les annotations JPA (`@Column`, `@Id`, etc.), et la différence entre H2 en mémoire (tests/démo) et PostgreSQL (production). Montrer comment changer la connexion dans `application.properties`.
---

## 8. Exemple complet : API produits avec persistance

```java
// Controller final avec toutes les features
@RestController
@RequestMapping("/produits")
public class ProduitController {

    private final ProduitService service;

    public ProduitController(ProduitService service) {
        this.service = service;
    }

    @GetMapping
    public Page<ProduitResponse> lister(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int taille) {
        return service.lister(PageRequest.of(page, taille, Sort.by("nom")));
    }

    @GetMapping("/{id}")
    public ProduitResponse trouver(@PathVariable Long id) {
        return service.trouver(id)
            .orElseThrow(() -> new ResourceNotFoundException("Produit", id));
    }

    @GetMapping("/recherche")
    public List<ProduitResponse> rechercher(
            @RequestParam(required = false) String q,
            @RequestParam(required = false) String categorie) {
        return service.rechercher(q, categorie);
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public ProduitResponse creer(@Valid @RequestBody ProduitRequest request) {
        return service.creer(request);
    }

    @PutMapping("/{id}")
    public ProduitResponse modifier(@PathVariable Long id,
                                    @Valid @RequestBody ProduitRequest request) {
        return service.modifier(id, request)
            .orElseThrow(() -> new ResourceNotFoundException("Produit", id));
    }

    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void supprimer(@PathVariable Long id) {
        if (!service.supprimer(id)) {
            throw new ResourceNotFoundException("Produit", id);
        }
    }
}
```

## Récapitulatif

| Annotation | Couche | Description |
|------------|--------|-------------|
| `@Entity` | Modèle | Classe mappée à une table |
| `@Table(name)` | Modèle | Nom de la table |
| `@Id` | Modèle | Clé primaire |
| `@GeneratedValue` | Modèle | Auto-incrément |
| `@Column` | Modèle | Contraintes de colonne |
| `@OneToMany`, `@ManyToOne` | Modèle | Relations |
| `@Repository` | Repository | Marqueur de couche DAO |
| `JpaRepository<T, ID>` | Repository | CRUD automatique |
| Query Methods | Repository | Requêtes générées depuis le nom |
| `@Query` | Repository | JPQL ou SQL personnalisé |
| `@Transactional` | Service | Démarcation de transaction |
| `@Modifying` | Repository | Pour les UPDATE/DELETE avec @Query |
