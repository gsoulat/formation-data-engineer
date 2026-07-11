# Spring Boot — REST API : @RestController, @GetMapping, @PostMapping, @RequestBody

## 1. Principes REST

REST (Representational State Transfer) est un style d'architecture pour les APIs web :

| Méthode HTTP | Action CRUD | Endpoint exemple | Body ? |
|-------------|-------------|-----------------|--------|
| GET | Read | `/produits` ou `/produits/1` | Non |
| POST | Create | `/produits` | Oui (le nouveau produit) |
| PUT | Update (complet) | `/produits/1` | Oui (produit complet) |
| PATCH | Update (partiel) | `/produits/1` | Oui (champs modifiés) |
| DELETE | Delete | `/produits/1` | Non |

## 2. Modèle et DTOs

```java
package com.formation.demo.model;

import jakarta.persistence.*;

// Entité JPA (voir Spring Data pour les détails)
@Entity
@Table(name = "produits")
public class Produit {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String nom;
    private double prix;
    private int stock;
    private String categorie;

    // Constructeurs
    public Produit() {}

    public Produit(String nom, double prix, int stock, String categorie) {
        this.nom = nom;
        this.prix = prix;
        this.stock = stock;
        this.categorie = categorie;
    }

    // Getters/Setters
    public Long   getId()         { return id; }
    public String getNom()        { return nom; }
    public double getPrix()       { return prix; }
    public int    getStock()      { return stock; }
    public String getCategorie()  { return categorie; }

    public void setId(Long id)              { this.id = id; }
    public void setNom(String nom)          { this.nom = nom; }
    public void setPrix(double prix)        { this.prix = prix; }
    public void setStock(int stock)         { this.stock = stock; }
    public void setCategorie(String cat)    { this.categorie = cat; }
}

// DTO (Data Transfer Object) — sépare l'entité de la couche API
package com.formation.demo.dto;

import jakarta.validation.constraints.*;

public record ProduitRequest(
    @NotBlank(message = "Le nom est obligatoire")
    String nom,

    @Positive(message = "Le prix doit être positif")
    double prix,

    @Min(value = 0, message = "Le stock ne peut pas être négatif")
    int stock,

    @NotBlank(message = "La catégorie est obligatoire")
    String categorie
) {}

public record ProduitResponse(
    Long id,
    String nom,
    double prix,
    int stock,
    String categorie
) {
    // Factory method depuis l'entité
    public static ProduitResponse fromEntity(Produit p) {
        return new ProduitResponse(p.getId(), p.getNom(),
                                   p.getPrix(), p.getStock(), p.getCategorie());
    }
}
```

## 3. Controller REST complet

```java
package com.formation.demo.controller;

import com.formation.demo.dto.*;
import com.formation.demo.service.ProduitService;
import jakarta.validation.Valid;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;
import java.net.URI;
import java.util.List;

// @RestController = @Controller + @ResponseBody
// Toutes les méthodes retournent directement un JSON (pas de vue HTML)
@RestController
@RequestMapping("/produits")  // Préfixe toutes les routes de ce controller
public class ProduitController {

    private final ProduitService produitService;

    // Injection par constructeur
    public ProduitController(ProduitService produitService) {
        this.produitService = produitService;
    }

    // --- GET /produits ---
    // Retourne tous les produits
    @GetMapping
    public ResponseEntity<List<ProduitResponse>> listerTout() {
        List<ProduitResponse> produits = produitService.listerTout();
        return ResponseEntity.ok(produits);  // 200 OK
    }

    // --- GET /produits/{id} ---
    // Retourne un produit par son ID
    @GetMapping("/{id}")
    public ResponseEntity<ProduitResponse> trouverParId(@PathVariable Long id) {
        return produitService.trouverParId(id)
            .map(ResponseEntity::ok)                          // 200 OK si trouvé
            .orElse(ResponseEntity.notFound().build());       // 404 Not Found si absent
    }

    // --- GET /produits/recherche?nom=clavier&categorie=info&maxPrix=100 ---
    // Recherche avec paramètres de requête
    @GetMapping("/recherche")
    public ResponseEntity<List<ProduitResponse>> rechercher(
            @RequestParam(required = false) String nom,
            @RequestParam(required = false) String categorie,
            @RequestParam(required = false, defaultValue = "9999") double maxPrix) {

        List<ProduitResponse> resultats = produitService.rechercher(nom, categorie, maxPrix);
        return ResponseEntity.ok(resultats);
    }

    // --- POST /produits ---
    // Créer un nouveau produit
    @PostMapping
    public ResponseEntity<ProduitResponse> creer(
            @Valid @RequestBody ProduitRequest request) {
        // @Valid : déclenche la validation des annotations (@NotBlank, @Positive...)
        // @RequestBody : désérialise le JSON en ProduitRequest

        ProduitResponse cree = produitService.creer(request);
        URI location = URI.create("/produits/" + cree.id());
        return ResponseEntity.created(location).body(cree);  // 201 Created + Location header
    }

    // --- PUT /produits/{id} ---
    // Remplacer complètement un produit
    @PutMapping("/{id}")
    public ResponseEntity<ProduitResponse> remplacer(
            @PathVariable Long id,
            @Valid @RequestBody ProduitRequest request) {

        return produitService.remplacer(id, request)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }

    // --- PATCH /produits/{id}/stock ---
    // Mise à jour partielle du stock
    @PatchMapping("/{id}/stock")
    public ResponseEntity<ProduitResponse> mettreAJourStock(
            @PathVariable Long id,
            @RequestParam int quantite) {

        return produitService.mettreAJourStock(id, quantite)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }

    // --- DELETE /produits/{id} ---
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> supprimer(@PathVariable Long id) {
        if (produitService.supprimer(id)) {
            return ResponseEntity.noContent().build();   // 204 No Content
        }
        return ResponseEntity.notFound().build();        // 404 Not Found
    }

    // --- GET /produits/categories ---
    // Endpoint supplémentaire
    @GetMapping("/categories")
    public ResponseEntity<List<String>> listerCategories() {
        return ResponseEntity.ok(produitService.listerCategories());
    }
}
```

## 4. Service Layer

```java
package com.formation.demo.service;

import com.formation.demo.dto.*;
import com.formation.demo.model.Produit;
import com.formation.demo.repository.ProduitRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.*;
import java.util.stream.Collectors;

@Service
@Transactional(readOnly = true)  // Transactions en lecture seule par défaut
public class ProduitService {

    private final ProduitRepository repository;

    public ProduitService(ProduitRepository repository) {
        this.repository = repository;
    }

    public List<ProduitResponse> listerTout() {
        return repository.findAll().stream()
            .map(ProduitResponse::fromEntity)
            .collect(Collectors.toList());
    }

    public Optional<ProduitResponse> trouverParId(Long id) {
        return repository.findById(id).map(ProduitResponse::fromEntity);
    }

    public List<ProduitResponse> rechercher(String nom, String categorie, double maxPrix) {
        return repository.findAll().stream()
            .filter(p -> nom == null || p.getNom().toLowerCase().contains(nom.toLowerCase()))
            .filter(p -> categorie == null || p.getCategorie().equalsIgnoreCase(categorie))
            .filter(p -> p.getPrix() <= maxPrix)
            .map(ProduitResponse::fromEntity)
            .collect(Collectors.toList());
    }

    @Transactional
    public ProduitResponse creer(ProduitRequest request) {
        Produit produit = new Produit(
            request.nom(), request.prix(), request.stock(), request.categorie()
        );
        return ProduitResponse.fromEntity(repository.save(produit));
    }

    @Transactional
    public Optional<ProduitResponse> remplacer(Long id, ProduitRequest request) {
        return repository.findById(id).map(existant -> {
            existant.setNom(request.nom());
            existant.setPrix(request.prix());
            existant.setStock(request.stock());
            existant.setCategorie(request.categorie());
            return ProduitResponse.fromEntity(repository.save(existant));
        });
    }

    @Transactional
    public Optional<ProduitResponse> mettreAJourStock(Long id, int quantite) {
        return repository.findById(id).map(p -> {
            p.setStock(p.getStock() + quantite);
            return ProduitResponse.fromEntity(repository.save(p));
        });
    }

    @Transactional
    public boolean supprimer(Long id) {
        if (repository.existsById(id)) {
            repository.deleteById(id);
            return true;
        }
        return false;
    }

    public List<String> listerCategories() {
        return repository.findAll().stream()
            .map(Produit::getCategorie)
            .distinct()
            .sorted()
            .collect(Collectors.toList());
    }
}
```

## 5. Gestion des erreurs globale

```java
package com.formation.demo.exception;

import org.springframework.http.*;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.*;
import org.springframework.web.bind.annotation.*;
import java.util.*;

// Gère les exceptions pour TOUS les controllers
@RestControllerAdvice
public class GlobalExceptionHandler {

    // Erreur de validation (annotations @Valid)
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<Map<String, Object>> handleValidationErrors(
            MethodArgumentNotValidException ex) {

        Map<String, String> erreurs = new LinkedHashMap<>();
        ex.getBindingResult().getAllErrors().forEach(error -> {
            String champ = ((FieldError) error).getField();
            String message = error.getDefaultMessage();
            erreurs.put(champ, message);
        });

        Map<String, Object> response = new LinkedHashMap<>();
        response.put("status", 400);
        response.put("erreur", "Données invalides");
        response.put("details", erreurs);

        return ResponseEntity.badRequest().body(response);
    }

    // Ressource introuvable
    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<Map<String, String>> handleNotFound(ResourceNotFoundException ex) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
            .body(Map.of("erreur", ex.getMessage()));
    }

    // Erreur générale (non gérée)
    @ExceptionHandler(Exception.class)
    public ResponseEntity<Map<String, String>> handleGeneral(Exception ex) {
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
            .body(Map.of("erreur", "Erreur interne du serveur"));
    }
}

// Exception personnalisée
public class ResourceNotFoundException extends RuntimeException {
    public ResourceNotFoundException(String resource, Long id) {
        super(resource + " introuvable avec l'id " + id);
    }
}
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Utiliser Postman (ou curl) pour tester l'API :
> 1. `GET http://localhost:8080/produits` → liste vide ou avec données
> 2. `POST http://localhost:8080/produits` avec body JSON → 201 Created
> 3. `GET http://localhost:8080/produits/1` → le produit créé
> 4. `POST` avec un body invalide (nom vide) → voir la réponse 400 avec les erreurs de validation
> **Expliquer :** Montrer chaque étape dans Postman : comment configurer le Content-Type `application/json`, le body JSON. Montrer les codes de statut HTTP retournés (200, 201, 400, 404). Expliquer que `ResponseEntity` permet de contrôler précisément le statut HTTP retourné.
---

## 6. ResponseEntity — Contrôler la réponse HTTP

```java
// Différentes façons de construire une ResponseEntity

// 200 OK avec body
ResponseEntity.ok(body)
ResponseEntity.ok().body(body)

// 201 Created avec header Location
ResponseEntity.created(URI.create("/produits/1")).body(body)

// 204 No Content (pour DELETE ou PUT sans corps)
ResponseEntity.noContent().build()

// 400 Bad Request
ResponseEntity.badRequest().body(Map.of("erreur", "message"))

// 404 Not Found
ResponseEntity.notFound().build()
ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of("message", "Introuvable"))

// 500 Internal Server Error
ResponseEntity.internalServerError().body(Map.of("erreur", "Erreur serveur"))

// En-têtes personnalisés
ResponseEntity.ok()
    .header("X-Custom-Header", "valeur")
    .header(HttpHeaders.CACHE_CONTROL, "max-age=3600")
    .body(body)
```

## 7. Tester avec curl

```bash
# GET tous les produits
curl -X GET http://localhost:8080/produits

# GET un produit
curl -X GET http://localhost:8080/produits/1

# POST créer un produit
curl -X POST http://localhost:8080/produits \
  -H "Content-Type: application/json" \
  -d '{"nom": "Clavier", "prix": 79.99, "stock": 10, "categorie": "Informatique"}'

# PUT remplacer
curl -X PUT http://localhost:8080/produits/1 \
  -H "Content-Type: application/json" \
  -d '{"nom": "Clavier Mécanique", "prix": 99.99, "stock": 8, "categorie": "Informatique"}'

# PATCH mettre à jour le stock
curl -X PATCH "http://localhost:8080/produits/1/stock?quantite=5"

# DELETE supprimer
curl -X DELETE http://localhost:8080/produits/1

# Recherche avec paramètres
curl "http://localhost:8080/produits/recherche?categorie=Informatique&maxPrix=100"
```

## Récapitulatif

| Annotation | Description |
|------------|-------------|
| `@RestController` | Controller REST (JSON auto) |
| `@RequestMapping("/path")` | Préfixe de route |
| `@GetMapping("/path")` | Handler GET |
| `@PostMapping` | Handler POST |
| `@PutMapping("/{id}")` | Handler PUT |
| `@PatchMapping` | Handler PATCH |
| `@DeleteMapping` | Handler DELETE |
| `@PathVariable` | Variable de chemin : `/produits/{id}` |
| `@RequestParam` | Paramètre de requête : `?nom=x` |
| `@RequestBody` | Corps de la requête (JSON → objet) |
| `@Valid` | Déclenche la validation Bean Validation |
| `ResponseEntity<T>` | Contrôle le statut HTTP et les headers |
| `@RestControllerAdvice` | Gestion centralisée des exceptions |
