# Exercice 2 — API REST de Gestion de Tâches avec Spring Boot

## Objectif

Construire une API REST complète de gestion de tâches (todo list) avec Spring Boot, Spring Data JPA et validation. L'API devra respecter les conventions REST et gérer les erreurs correctement.

## Durée estimée : 4 à 5 heures

---

## Prérequis

- Projet Spring Boot créé (via https://start.spring.io/)
- Dépendances : Spring Web, Spring Data JPA, H2, Validation, Lombok (optionnel)

---

## Spécifications de l'API

### Modèle de données

Une **Tâche** possède :
- `id` : Long (auto-généré)
- `titre` : String (max 100 caractères, obligatoire)
- `description` : String (max 500 caractères, optionnel)
- `statut` : Enum (`EN_ATTENTE`, `EN_COURS`, `TERMINEE`, `ANNULEE`)
- `priorite` : Enum (`BASSE`, `NORMALE`, `HAUTE`, `CRITIQUE`)
- `categorie` : String (max 50 caractères, optionnel)
- `dateEcheance` : LocalDate (optionnel)
- `dateCreation` : LocalDateTime (auto, non modifiable)
- `dateMiseAJour` : LocalDateTime (auto)

### Endpoints requis

| Méthode | Endpoint | Description | Code succès |
|---------|----------|-------------|-------------|
| GET | `/taches` | Liste paginée avec filtres | 200 |
| GET | `/taches/{id}` | Une tâche | 200 |
| POST | `/taches` | Créer une tâche | 201 |
| PUT | `/taches/{id}` | Modifier complètement | 200 |
| PATCH | `/taches/{id}/statut` | Changer le statut | 200 |
| DELETE | `/taches/{id}` | Supprimer | 204 |
| GET | `/taches/statistiques` | Stats par statut/priorité | 200 |

---

## Partie 1 — Modèle et Repository (45 min)

### 1.1 Entité JPA

```java
// src/main/java/com/formation/todo/model/Tache.java
@Entity
@Table(name = "taches")
public class Tache {
    // À compléter avec toutes les annotations JPA
    // N'oubliez pas : @PrePersist et @PreUpdate
}
```

### 1.2 Enums

```java
// À créer dans le package model
public enum StatutTache { EN_ATTENTE, EN_COURS, TERMINEE, ANNULEE }
public enum PrioriteTache { BASSE, NORMALE, HAUTE, CRITIQUE }
```

### 1.3 Repository

```java
public interface TacheRepository extends JpaRepository<Tache, Long> {
    // À compléter avec les query methods nécessaires :

    // Trouver par statut
    Page<Tache> findByStatut(StatutTache statut, Pageable pageable);

    // Trouver par priorité
    List<Tache> findByPrioriteOrderByDateEcheanceAsc(PrioriteTache priorite);

    // Trouver les tâches en retard (dateEcheance < aujourd'hui AND statut != TERMINEE)
    @Query("SELECT t FROM Tache t WHERE t.dateEcheance < :today AND t.statut <> :statut")
    List<Tache> findEnRetard(@Param("today") LocalDate today,
                              @Param("statut") StatutTache statut);

    // Statistiques par statut
    @Query("SELECT t.statut, COUNT(t) FROM Tache t GROUP BY t.statut")
    List<Object[]> countByStatut();

    // Recherche full-text basique
    List<Tache> findByTitreContainingIgnoreCaseOrDescriptionContainingIgnoreCase(
        String titre, String description);
}
```

---

## Partie 2 — DTOs et Validation (30 min)

### 2.1 TacheRequest

```java
// Valider :
// - titre : obligatoire, 1-100 caractères
// - description : optionnelle, max 500 caractères
// - statut : valide si présent
// - priorite : valide si présent, défaut NORMALE
// - dateEcheance : doit être dans le futur si fournie
public record TacheRequest(
    // À compléter avec les annotations de validation
) {}
```

### 2.2 TacheResponse

```java
public record TacheResponse(
    Long id,
    String titre,
    String description,
    StatutTache statut,
    PrioriteTache priorite,
    String categorie,
    LocalDate dateEcheance,
    LocalDateTime dateCreation,
    LocalDateTime dateMiseAJour,
    boolean enRetard  // calculé : dateEcheance < today && statut != TERMINEE
) {
    public static TacheResponse fromEntity(Tache t) {
        // À implémenter
    }
}
```

### 2.3 StatutUpdateRequest

```java
// Pour PATCH /taches/{id}/statut
public record StatutUpdateRequest(
    @NotNull StatutTache statut
) {}
```

---

## Partie 3 — Service (60 min)

```java
@Service
@Transactional(readOnly = true)
public class TacheService {

    // Implémenter toutes les méthodes :

    // lister(Pageable, StatutTache filtre, PrioriteTache filtrePrio, String recherche)
    // → Page<TacheResponse>

    // trouverParId(Long id) → Optional<TacheResponse>

    // creer(TacheRequest request) → TacheResponse
    // (valeurs par défaut : statut=EN_ATTENTE, priorite=NORMALE si non fourni)

    // modifier(Long id, TacheRequest request) → Optional<TacheResponse>

    // changerStatut(Long id, StatutTache nouveauStatut) → Optional<TacheResponse>
    // Règles de transition valides :
    //   EN_ATTENTE → EN_COURS, ANNULEE
    //   EN_COURS → TERMINEE, EN_ATTENTE, ANNULEE
    //   TERMINEE → (aucune transition)
    //   ANNULEE → EN_ATTENTE

    // supprimer(Long id) → boolean

    // getStatistiques() → Map<String, Object>
    // contenant : nbTotal, nbParStatut, nbParPriorite, nbEnRetard
}
```

---

## Partie 4 — Controller (45 min)

```java
@RestController
@RequestMapping("/taches")
public class TacheController {

    // Implémenter tous les endpoints avec :
    // - Les annotations correctes (@GetMapping, etc.)
    // - Les paramètres appropriés (@PathVariable, @RequestParam, @RequestBody)
    // - Les bons codes HTTP (200, 201, 204, 400, 404)
    // - La validation (@Valid)

    // GET /taches?page=0&taille=10&statut=EN_COURS&priorite=HAUTE&q=spring
    // GET /taches/{id}
    // POST /taches
    // PUT /taches/{id}
    // PATCH /taches/{id}/statut
    // DELETE /taches/{id}
    // GET /taches/statistiques
}
```

---

## Partie 5 — Gestion des erreurs (30 min)

Créez un `@RestControllerAdvice` qui gère :

1. `TacheNotFoundException` (404) — quand une tâche n'existe pas
2. `TransitionStatutInvalideException` (400) — quand la transition de statut est invalide
3. `MethodArgumentNotValidException` (400) — erreurs de validation avec détail des champs
4. `Exception` générale (500)

Format de réponse d'erreur standardisé :
```json
{
  "timestamp": "2024-01-15T10:30:00",
  "status": 404,
  "erreur": "Ressource introuvable",
  "message": "Tâche introuvable avec l'id 42",
  "path": "/taches/42"
}
```

---

## Partie 6 — Tests avec curl (30 min)

Testez votre API avec les requêtes suivantes :

```bash
# 1. Créer plusieurs tâches
curl -X POST http://localhost:8080/taches \
  -H "Content-Type: application/json" \
  -d '{"titre":"Apprendre Spring Boot","priorite":"HAUTE","statut":"EN_ATTENTE"}'

curl -X POST http://localhost:8080/taches \
  -H "Content-Type: application/json" \
  -d '{
    "titre": "Faire les exercices Java",
    "description": "Exercice POO et API Spring",
    "priorite": "HAUTE",
    "statut": "EN_COURS",
    "dateEcheance": "2024-12-31"
  }'

curl -X POST http://localhost:8080/taches \
  -H "Content-Type: application/json" \
  -d '{"titre":"Réviser les collections","priorite":"NORMALE"}'

# 2. Lister toutes les tâches
curl http://localhost:8080/taches

# 3. Lister avec filtres
curl "http://localhost:8080/taches?statut=EN_COURS&page=0&taille=5"

# 4. Récupérer une tâche
curl http://localhost:8080/taches/1

# 5. Modifier le statut
curl -X PATCH http://localhost:8080/taches/1/statut \
  -H "Content-Type: application/json" \
  -d '{"statut":"EN_COURS"}'

# 6. Tenter une transition invalide
curl -X PATCH http://localhost:8080/taches/1/statut \
  -H "Content-Type: application/json" \
  -d '{"statut":"TERMINEE"}'
# (si déjà TERMINEE → 400)

# 7. Modifier complètement une tâche
curl -X PUT http://localhost:8080/taches/1 \
  -H "Content-Type: application/json" \
  -d '{"titre":"Maîtriser Spring Boot","priorite":"CRITIQUE","statut":"EN_COURS"}'

# 8. Tester la validation
curl -X POST http://localhost:8080/taches \
  -H "Content-Type: application/json" \
  -d '{"titre":"","priorite":"INVALIDE"}'
# Attendu : 400 avec détail des erreurs de validation

# 9. Statistiques
curl http://localhost:8080/taches/statistiques

# 10. Supprimer
curl -X DELETE http://localhost:8080/taches/3
# Attendu : 204 No Content

# 11. Supprimer une tâche inexistante
curl -X DELETE http://localhost:8080/taches/999
# Attendu : 404 Not Found
```

---

## Bonus — Améliorations possibles

1. **Authentification** : Ajouter Spring Security avec JWT (connexion par username/password)
2. **Export CSV** : `GET /taches/export?format=csv` → fichier téléchargeable
3. **Notifications** : Envoyer un email quand une tâche approche de son échéance
4. **Tests unitaires** : JUnit 5 + Mockito pour le service
5. **Tests d'intégration** : `@SpringBootTest` + `TestRestTemplate`
6. **Swagger/OpenAPI** : Documenter l'API avec `springdoc-openapi`
7. **Docker** : `Dockerfile` pour containeriser l'application

---

## Réponse attendue pour `GET /taches/statistiques`

```json
{
  "nbTotal": 5,
  "nbParStatut": {
    "EN_ATTENTE": 2,
    "EN_COURS": 2,
    "TERMINEE": 1,
    "ANNULEE": 0
  },
  "nbParPriorite": {
    "BASSE": 1,
    "NORMALE": 2,
    "HAUTE": 1,
    "CRITIQUE": 1
  },
  "nbEnRetard": 1,
  "tauxCompletion": 20.0
}
```
