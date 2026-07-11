# JPA / Hibernate — Introduction et configuration

## Configuration Maven (pom.xml)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.formation</groupId>
    <artifactId>jpa-demo</artifactId>
    <version>1.0-SNAPSHOT</version>

    <properties>
        <maven.compiler.source>17</maven.compiler.source>
        <maven.compiler.target>17</maven.compiler.target>
    </properties>

    <dependencies>
        <!-- Hibernate ORM -->
        <dependency>
            <groupId>org.hibernate.orm</groupId>
            <artifactId>hibernate-core</artifactId>
            <version>6.4.0.Final</version>
        </dependency>

        <!-- Driver PostgreSQL -->
        <dependency>
            <groupId>org.postgresql</groupId>
            <artifactId>postgresql</artifactId>
            <version>42.7.0</version>
        </dependency>

        <!-- Pour les logs SQL lisibles -->
        <dependency>
            <groupId>org.slf4j</groupId>
            <artifactId>slf4j-simple</artifactId>
            <version>2.0.9</version>
        </dependency>
    </dependencies>
</project>
```

## Configuration persistence.xml

JPA se configure via un fichier `persistence.xml` placé dans `src/main/resources/META-INF/`.

```xml
<!-- src/main/resources/META-INF/persistence.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<persistence version="3.0"
             xmlns="https://jakarta.ee/xml/ns/persistence"
             xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
             xsi:schemaLocation="https://jakarta.ee/xml/ns/persistence
             https://jakarta.ee/xml/ns/persistence/persistence_3_0.xsd">

    <persistence-unit name="formation-pu" transaction-type="RESOURCE_LOCAL">
        <provider>org.hibernate.jpa.HibernatePersistenceProvider</provider>

        <!-- Entités à gérer -->
        <class>com.formation.models.Produit</class>
        <class>com.formation.models.Categorie</class>

        <properties>
            <!-- Connexion -->
            <property name="jakarta.persistence.jdbc.driver"
                      value="org.postgresql.Driver"/>
            <property name="jakarta.persistence.jdbc.url"
                      value="jdbc:postgresql://localhost:5432/orm_db"/>
            <property name="jakarta.persistence.jdbc.user" value="formation"/>
            <property name="jakarta.persistence.jdbc.password" value="formation"/>

            <!-- Pool de connexions (Hibernate C3P0) -->
            <property name="hibernate.c3p0.min_size" value="2"/>
            <property name="hibernate.c3p0.max_size" value="10"/>

            <!-- Schéma : validate | update | create | create-drop -->
            <!-- En prod : "validate" ou géré par Flyway/Liquibase -->
            <!-- En dev  : "update" ou "create-drop" -->
            <property name="hibernate.hbm2ddl.auto" value="update"/>

            <!-- Afficher les requêtes SQL générées -->
            <property name="hibernate.show_sql" value="true"/>
            <property name="hibernate.format_sql" value="true"/>

            <!-- Dialecte PostgreSQL -->
            <property name="hibernate.dialect"
                      value="org.hibernate.dialect.PostgreSQLDialect"/>
        </properties>
    </persistence-unit>
</persistence>
```

## Première entité JPA

```java
// src/main/java/com/formation/models/Produit.java
package com.formation.models;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity                              // Cette classe est une entité JPA
@Table(name = "produits",            // Nom de la table SQL
    indexes = {
        @Index(name = "idx_produit_actif", columnList = "actif")
    }
)
public class Produit {

    @Id                              // Clé primaire
    @GeneratedValue(strategy = GenerationType.IDENTITY)  // AUTO_INCREMENT
    private Long id;

    @Column(name = "nom", nullable = false, length = 200)
    private String nom;

    @Column(columnDefinition = "TEXT")
    private String description;

    @Column(name = "prix", precision = 10, scale = 2, nullable = false)
    private BigDecimal prix;

    @Column(name = "stock", columnDefinition = "INTEGER DEFAULT 0")
    private int stock = 0;

    @Column(name = "actif", columnDefinition = "BOOLEAN DEFAULT TRUE")
    private boolean actif = true;

    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    // Lifecycle callbacks — appelés automatiquement par Hibernate
    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }

    // Constructeur sans argument OBLIGATOIRE pour JPA
    public Produit() {}

    public Produit(String nom, BigDecimal prix) {
        this.nom = nom;
        this.prix = prix;
    }

    // Getters et Setters
    public Long getId() { return id; }
    public String getNom() { return nom; }
    public void setNom(String nom) { this.nom = nom; }
    public BigDecimal getPrix() { return prix; }
    public void setPrix(BigDecimal prix) { this.prix = prix; }
    public int getStock() { return stock; }
    public void setStock(int stock) { this.stock = stock; }
    public boolean isActif() { return actif; }
    public void setActif(boolean actif) { this.actif = actif; }
    public LocalDateTime getCreatedAt() { return createdAt; }

    @Override
    public String toString() {
        return "Produit{id=" + id + ", nom='" + nom + "', prix=" + prix + "}";
    }
}
```

## EntityManager — l'équivalent de la Session SQLAlchemy

```java
// src/main/java/com/formation/Main.java
package com.formation;

import com.formation.models.Produit;
import jakarta.persistence.*;
import java.math.BigDecimal;

public class Main {

    // Factory globale (une seule instance par application)
    private static final EntityManagerFactory emf =
        Persistence.createEntityManagerFactory("formation-pu");

    public static void main(String[] args) {
        demonstrerCRUD();
        emf.close();  // Fermer à la fin de l'application
    }

    private static void demonstrerCRUD() {
        // Créer un EntityManager pour cette "unité de travail"
        EntityManager em = emf.createEntityManager();
        EntityTransaction tx = em.getTransaction();

        try {
            tx.begin();  // Démarrer la transaction

            // CREATE
            Produit produit = new Produit("Clavier mécanique", new BigDecimal("89.99"));
            produit.setStock(15);
            em.persist(produit);  // Équivalent de session.add() en SQLAlchemy

            tx.commit();  // Envoyer en BDD
            System.out.println("Créé: " + produit);

            // READ par ID
            tx.begin();
            Produit trouvé = em.find(Produit.class, produit.getId());
            System.out.println("Trouvé: " + trouvé);

            // UPDATE
            trouvé.setPrix(new BigDecimal("79.99"));
            trouvé.setStock(20);
            // Pas besoin de em.merge() si l'objet est "managed" (dans le contexte)
            tx.commit();
            System.out.println("Mis à jour: " + trouvé);

            // DELETE
            tx.begin();
            Produit aSupprimer = em.find(Produit.class, produit.getId());
            em.remove(aSupprimer);
            tx.commit();
            System.out.println("Supprimé");

        } catch (Exception e) {
            if (tx.isActive()) tx.rollback();
            e.printStackTrace();
        } finally {
            em.close();  // TOUJOURS fermer l'EntityManager
        }
    }
}
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** IntelliJ IDEA + Terminal — exécuter l'application, montrer les requêtes SQL Hibernate dans la console, puis montrer la table créée dans DBeaver
> **Expliquer :** Montrer les logs SQL Hibernate (`show_sql=true`) : le `CREATE TABLE`, le `INSERT`, le `SELECT` et le `UPDATE`. Comparer avec le code Java correspondant. Montrer dans DBeaver la table créée avec les contraintes. Insister sur `hbm2ddl.auto=update` (pratique en dev, DANGEREUX en prod).

---

## Pattern Repository — bonne pratique

En Java/JPA, on encapsule les accès BDD dans des classes Repository pour séparer la logique métier de la persistance.

```java
// src/main/java/com/formation/repositories/ProduitRepository.java
package com.formation.repositories;

import com.formation.models.Produit;
import jakarta.persistence.*;
import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;

public class ProduitRepository {

    private final EntityManagerFactory emf;

    public ProduitRepository(EntityManagerFactory emf) {
        this.emf = emf;
    }

    public Produit save(Produit produit) {
        EntityManager em = emf.createEntityManager();
        EntityTransaction tx = em.getTransaction();
        try {
            tx.begin();
            if (produit.getId() == null) {
                em.persist(produit);
            } else {
                produit = em.merge(produit);  // merge() pour les objets detached
            }
            tx.commit();
            return produit;
        } catch (Exception e) {
            if (tx.isActive()) tx.rollback();
            throw new RuntimeException("Erreur lors de la sauvegarde", e);
        } finally {
            em.close();
        }
    }

    public Optional<Produit> findById(Long id) {
        EntityManager em = emf.createEntityManager();
        try {
            Produit produit = em.find(Produit.class, id);
            return Optional.ofNullable(produit);
        } finally {
            em.close();
        }
    }

    public List<Produit> findAll() {
        EntityManager em = emf.createEntityManager();
        try {
            return em.createQuery("SELECT p FROM Produit p ORDER BY p.nom", Produit.class)
                     .getResultList();
        } finally {
            em.close();
        }
    }

    public List<Produit> findByPrixMoinsDe(BigDecimal maxPrix) {
        EntityManager em = emf.createEntityManager();
        try {
            return em.createQuery(
                "SELECT p FROM Produit p WHERE p.prix <= :prix ORDER BY p.prix",
                Produit.class
            ).setParameter("prix", maxPrix).getResultList();
        } finally {
            em.close();
        }
    }

    public void delete(Long id) {
        EntityManager em = emf.createEntityManager();
        EntityTransaction tx = em.getTransaction();
        try {
            tx.begin();
            Produit produit = em.find(Produit.class, id);
            if (produit != null) em.remove(produit);
            tx.commit();
        } catch (Exception e) {
            if (tx.isActive()) tx.rollback();
            throw new RuntimeException(e);
        } finally {
            em.close();
        }
    }
}
```

## États d'une entité JPA

Comme SQLAlchemy, JPA gère différents états pour les entités :

```
new/transient  →  [persist()]  →  managed  →  [commit()]  →  persistent (BDD)
                                     ↓
                               [detach()]
                                     ↓
                               detached  →  [merge()]  →  managed
                                     ↓
                               [remove()]
                                     ↓
                               removed  →  [commit()]  →  supprimé de la BDD
```

```java
// Transient — pas dans le contexte de persistance
Produit p = new Produit("Test", new BigDecimal("10.00"));
// p.getId() == null

// Managed — dans le contexte, suivi par Hibernate
em.persist(p);
// Hibernate détecte automatiquement toute modification

// Detached — plus dans le contexte (après em.close() ou em.detach())
em.close();
// Modifications non détectées

// Re-attacher un objet detached
EntityManager em2 = emf.createEntityManager();
Produit managed = em2.merge(p);  // Retourne l'objet managed
```
