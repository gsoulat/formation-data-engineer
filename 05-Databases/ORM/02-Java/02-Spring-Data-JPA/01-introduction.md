# Spring Data JPA — Introduction et configuration

## Architecture Spring Data JPA

```
Controller (REST)
      ↓
   Service (logique métier)
      ↓
  Repository (Spring Data JPA)  ← interface uniquement
      ↓
   JPA / Hibernate
      ↓
   PostgreSQL
```

## Configuration Spring Boot

### Structure du projet

```
src/
├── main/
│   ├── java/com/formation/
│   │   ├── FormationApplication.java
│   │   ├── models/
│   │   │   ├── Produit.java
│   │   │   └── Categorie.java
│   │   ├── repositories/
│   │   │   ├── ProduitRepository.java
│   │   │   └── CategorieRepository.java
│   │   ├── services/
│   │   │   └── ProduitService.java
│   │   └── controllers/
│   │       └── ProduitController.java
│   └── resources/
│       └── application.yml
```

### application.yml

```yaml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/orm_db
    username: formation
    password: formation
    hikari:
      maximum-pool-size: 10
      minimum-idle: 2

  jpa:
    hibernate:
      ddl-auto: update
    show-sql: true
    properties:
      hibernate:
        format_sql: true
        use_sql_comments: true
        highlight_sql: true

  # Activer les logs SQL détaillés
logging:
  level:
    org.hibernate.SQL: DEBUG
    org.hibernate.orm.jdbc.bind: TRACE  # Voir les paramètres liés
```

## Entité JPA (identique à JPA pur)

```java
// models/Produit.java
package com.formation.models;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "produits")
public class Produit {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 200)
    private String nom;

    @Column(columnDefinition = "TEXT")
    private String description;

    @Column(precision = 10, scale = 2, nullable = false)
    private BigDecimal prix;

    @Column
    private Integer stock = 0;

    @Column
    private boolean actif = true;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "categorie_id")
    private Categorie categorie;

    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }

    public Produit() {}

    // Getters et Setters
    public Long getId() { return id; }
    public String getNom() { return nom; }
    public void setNom(String nom) { this.nom = nom; }
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
    public BigDecimal getPrix() { return prix; }
    public void setPrix(BigDecimal prix) { this.prix = prix; }
    public Integer getStock() { return stock; }
    public void setStock(Integer stock) { this.stock = stock; }
    public boolean isActif() { return actif; }
    public void setActif(boolean actif) { this.actif = actif; }
    public Categorie getCategorie() { return categorie; }
    public void setCategorie(Categorie categorie) { this.categorie = categorie; }
    public LocalDateTime getCreatedAt() { return createdAt; }
}
```

## Premier Repository

```java
// repositories/ProduitRepository.java
package com.formation.repositories;

import com.formation.models.Produit;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface ProduitRepository extends JpaRepository<Produit, Long> {
    // JpaRepository<EntiteType, IdType> fournit automatiquement :
    // - findAll()
    // - findById(id)
    // - save(entity)
    // - saveAll(entities)
    // - delete(entity)
    // - deleteById(id)
    // - count()
    // - existsById(id)
    // + findAll(Sort), findAll(Pageable) pour tri et pagination
}
```

## Service — logique métier

```java
// services/ProduitService.java
package com.formation.services;

import com.formation.models.Produit;
import com.formation.repositories.ProduitRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

@Service
@Transactional(readOnly = true)  // Transactions lecture seule par défaut
public class ProduitService {

    private final ProduitRepository repository;

    // Injection par constructeur (recommandée)
    public ProduitService(ProduitRepository repository) {
        this.repository = repository;
    }

    public List<Produit> findAll() {
        return repository.findAll();
    }

    public Optional<Produit> findById(Long id) {
        return repository.findById(id);
    }

    @Transactional  // Override : cette méthode écrit
    public Produit create(Produit produit) {
        return repository.save(produit);
    }

    @Transactional
    public Produit update(Long id, Produit updates) {
        Produit produit = repository.findById(id)
            .orElseThrow(() -> new RuntimeException("Produit non trouvé: " + id));

        if (updates.getNom() != null) produit.setNom(updates.getNom());
        if (updates.getPrix() != null) produit.setPrix(updates.getPrix());
        if (updates.getStock() != null) produit.setStock(updates.getStock());

        return repository.save(produit);
    }

    @Transactional
    public void delete(Long id) {
        if (!repository.existsById(id)) {
            throw new RuntimeException("Produit non trouvé: " + id);
        }
        repository.deleteById(id);
    }

    public long count() {
        return repository.count();
    }
}
```

## Controller REST

```java
// controllers/ProduitController.java
package com.formation.controllers;

import com.formation.models.Produit;
import com.formation.services.ProduitService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/produits")
public class ProduitController {

    private final ProduitService service;

    public ProduitController(ProduitService service) {
        this.service = service;
    }

    @GetMapping
    public List<Produit> getAll() {
        return service.findAll();
    }

    @GetMapping("/{id}")
    public ResponseEntity<Produit> getById(@PathVariable Long id) {
        return service.findById(id)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public Produit create(@RequestBody Produit produit) {
        return service.create(produit);
    }

    @PutMapping("/{id}")
    public Produit update(@PathVariable Long id, @RequestBody Produit updates) {
        return service.update(id, updates);
    }

    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void delete(@PathVariable Long id) {
        service.delete(id);
    }
}
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** IntelliJ IDEA — démarrer l'application Spring Boot, montrer les logs de démarrage (Hibernate schéma), tester les endpoints avec Postman ou curl
> **Expliquer :** Montrer que Spring Boot détecte automatiquement les repositories et génère les implémentations. Montrer les logs de démarrage avec la création des tables. Tester chaque endpoint dans Postman et montrer les logs SQL correspondants. Insister sur la quantité de code que Spring Data JPA génère automatiquement.

---

## Application principale

```java
// FormationApplication.java
package com.formation;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class FormationApplication {
    public static void main(String[] args) {
        SpringApplication.run(FormationApplication.class, args);
    }
}
```

```bash
# Lancer avec Maven
mvn spring-boot:run

# Tester
curl http://localhost:8080/api/produits
curl -X POST http://localhost:8080/api/produits \
  -H "Content-Type: application/json" \
  -d '{"nom":"Clavier","prix":89.99,"stock":15}'
```
