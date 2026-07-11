# Spring Boot — Introduction et Setup

## Prérequis

- Java 17+ installé
- Maven ou Gradle installé
- IntelliJ IDEA (Community ou Ultimate)

## Créer un projet Spring Boot

### Via Spring Initializr (https://start.spring.io/)

1. Project : Maven
2. Language : Java
3. Spring Boot : 3.2.x
4. Group : `com.formation`
5. Artifact : `demo`
6. Java : 21
7. Dependencies : Spring Web, Spring Data JPA, H2 Database (ou PostgreSQL)

### Via IntelliJ IDEA

File → New → Project → Spring Initializr → Même paramètres

## Structure d'un projet Spring Boot

```
demo/
├── pom.xml
└── src/
    ├── main/
    │   ├── java/com/formation/demo/
    │   │   ├── DemoApplication.java      ← Point d'entrée (@SpringBootApplication)
    │   │   ├── controller/
    │   │   │   └── ProduitController.java
    │   │   ├── service/
    │   │   │   └── ProduitService.java
    │   │   ├── repository/
    │   │   │   └── ProduitRepository.java
    │   │   └── model/
    │   │       └── Produit.java
    │   └── resources/
    │       ├── application.properties    ← Configuration
    │       └── data.sql                  ← Données initiales (optionnel)
    └── test/
        └── java/com/formation/demo/
            └── DemoApplicationTests.java
```
