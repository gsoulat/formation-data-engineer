# Spring Data JPA — Repositories automatiques avec Spring Boot

Spring Data JPA est une couche supplémentaire au-dessus de JPA/Hibernate. Elle élimine la majorité du code boilerplate en générant automatiquement les implémentations de repositories.

## Ce que Spring Data JPA apporte

```java
// SANS Spring Data JPA — beaucoup de code répétitif
public class ProduitRepository {
    public List<Produit> findAll() {
        EntityManager em = emf.createEntityManager();
        return em.createQuery("SELECT p FROM Produit p", Produit.class).getResultList();
    }
    public Optional<Produit> findById(Long id) { ... }
    public Produit save(Produit p) { ... }
    public void delete(Long id) { ... }
    // ... etc.
}

// AVEC Spring Data JPA — RIEN à implémenter
public interface ProduitRepository extends JpaRepository<Produit, Long> {
    // findAll(), findById(), save(), delete()... sont générés automatiquement !
}
```

## Prérequis Spring Boot

```xml
<!-- pom.xml -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-jpa</artifactId>
</dependency>
<dependency>
    <groupId>org.postgresql</groupId>
    <artifactId>postgresql</artifactId>
    <scope>runtime</scope>
</dependency>
```

```yaml
# application.yml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/orm_db
    username: formation
    password: formation
  jpa:
    hibernate:
      ddl-auto: update       # dev seulement ; prod : validate ou none
    show-sql: true
    properties:
      hibernate:
        format_sql: true
        dialect: org.hibernate.dialect.PostgreSQLDialect
```

## Contenu du module

| Fichier | Description |
|---------|-------------|
| [01-introduction.md](./01-introduction.md) | Configuration Spring Boot, premiers repositories |
| [02-repositories.md](./02-repositories.md) | Query methods, @Query, Specifications, Pageable |
