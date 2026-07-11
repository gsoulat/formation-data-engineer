# JPA / Hibernate — L'ORM de référence en Java

## JPA vs Hibernate : quelle différence ?

- **JPA (Jakarta Persistence API)** : une *spécification* Java (interface standard). Elle définit les annotations (`@Entity`, `@Table`, `@Column`...) et l'API (`EntityManager`). JPA ne fait rien seul — c'est juste un contrat.
- **Hibernate** : l'*implémentation* de référence de JPA. C'est Hibernate qui exécute vraiment les requêtes SQL. Il est utilisé par défaut dans Spring Boot.

```
Votre code Java (annotations JPA)
         ↓
   JPA (interface standard)
         ↓
   Hibernate (implémentation)
         ↓
   JDBC (driver)
         ↓
   PostgreSQL / MySQL / Oracle
```

D'autres implémentations JPA existent (EclipseLink, OpenJPA), mais Hibernate domine le marché avec ~90% d'utilisation.

## Pourquoi JPA/Hibernate en entreprise ?

- **Standard Java EE / Jakarta EE** : toutes les grandes entreprises Java l'utilisent
- **Très complet** : cache L1/L2, lazy loading, criteria API, JPQL
- **Intégration Spring Boot** : `spring-data-jpa` simplifie encore l'usage
- **Mature** : 20+ ans de développement, utilisé sur des millions de projets

## Contenu du module

| Fichier | Description |
|---------|-------------|
| [01-introduction-jpa.md](./01-introduction-jpa.md) | Setup Maven/Gradle, EntityManager, première entité |
| [02-entites-annotations.md](./02-entites-annotations.md) | Annotations JPA, types, contraintes |
| [03-relations.md](./03-relations.md) | @OneToMany, @ManyToMany, @OneToOne, fetch |
| [04-jpql-criteriaapi.md](./04-jpql-criteriaapi.md) | JPQL, Criteria API, requêtes natives |

## Prérequis

- Java 17+
- Maven ou Gradle
- Docker (pour PostgreSQL)
- IDE : IntelliJ IDEA (recommandé) ou Eclipse
