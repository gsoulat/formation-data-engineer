# Spring Boot — Introduction, Auto-configuration, Starter Dependencies

## 1. Qu'est-ce que Spring et Spring Boot ?

**Spring Framework** est le framework Java le plus utilisé pour les applications d'entreprise. Il fournit : injection de dépendances, gestion des transactions, sécurité, accès aux données, etc.

**Spring Boot** simplifie Spring en fournissant :
- Une **auto-configuration** : détecte automatiquement les bibliothèques présentes et les configure
- Des **starters** : dépendances regroupées et préconfigurées
- Un **serveur embarqué** (Tomcat, Jetty) : pas besoin de déployer un WAR
- Un exécutable **fat JAR** : `java -jar app.jar` suffit à lancer l'application

```
Avant Spring Boot               Avec Spring Boot
──────────────────              ─────────────────
Configure web.xml               @SpringBootApplication
Configure applicationContext    (c'est tout !)
Configure dispatcher servlet
Configure datasource
Configure JPA
Déployer sur Tomcat
```

## 2. Créer un projet Spring Boot

### pom.xml minimal

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <!-- Parent Spring Boot : hérite de la configuration et des versions gérées -->
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.0</version>
    </parent>

    <groupId>com.formation</groupId>
    <artifactId>demo-spring</artifactId>
    <version>0.0.1-SNAPSHOT</version>
    <packaging>jar</packaging>

    <properties>
        <java.version>21</java.version>
    </properties>

    <dependencies>
        <!-- Web MVC + Tomcat embarqué -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>

        <!-- Spring Data JPA + Hibernate -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>

        <!-- Base de données H2 (en mémoire, pour les tests/démos) -->
        <dependency>
            <groupId>com.h2database</groupId>
            <artifactId>h2</artifactId>
            <scope>runtime</scope>
        </dependency>

        <!-- OU : PostgreSQL en production -->
        <!--
        <dependency>
            <groupId>org.postgresql</groupId>
            <artifactId>postgresql</artifactId>
            <scope>runtime</scope>
        </dependency>
        -->

        <!-- Lombok : génère le boilerplate (getters, constructeurs...) -->
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <optional>true</optional>
        </dependency>

        <!-- Validation -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-validation</artifactId>
        </dependency>

        <!-- Tests -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <!-- Plugin pour créer le fat JAR exécutable -->
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
                <configuration>
                    <excludes>
                        <exclude>
                            <groupId>org.projectlombok</groupId>
                            <artifactId>lombok</artifactId>
                        </exclude>
                    </excludes>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
```

## 3. Classe principale — @SpringBootApplication

```java
package com.formation.demo;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

// @SpringBootApplication = @Configuration + @EnableAutoConfiguration + @ComponentScan
@SpringBootApplication
public class DemoApplication {

    public static void main(String[] args) {
        // Lance le contexte Spring et le serveur Tomcat embarqué
        SpringApplication.run(DemoApplication.class, args);
    }
}
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Lancer `DemoApplication` dans IntelliJ et montrer les logs de démarrage dans la console : la bannière Spring Boot, les beans créés, le port Tomcat (`Tomcat started on port(s): 8080`), et la ligne `Started DemoApplication in X.XXX seconds`.
> **Expliquer :** Montrer ce que l'auto-configuration a fait : détecté H2 et configuré une datasource, configuré Hibernate, créé le DispatcherServlet, démarré Tomcat. Tout sans aucun code de configuration ! Comparer avec la configuration XML d'un projet Spring classique (montrer un exemple de 200 lignes de XML).
---

## 4. Configuration avec application.properties

```properties
# src/main/resources/application.properties

# --- Serveur ---
server.port=8080
server.servlet.context-path=/api  # Préfixe toutes les routes

# --- H2 (base de données en mémoire) ---
spring.datasource.url=jdbc:h2:mem:testdb
spring.datasource.driver-class-name=org.h2.Driver
spring.datasource.username=sa
spring.datasource.password=
spring.h2.console.enabled=true    # Interface web H2 sur /h2-console
spring.h2.console.path=/h2-console

# --- JPA / Hibernate ---
spring.jpa.show-sql=true           # Affiche les requêtes SQL
spring.jpa.properties.hibernate.format_sql=true
spring.jpa.hibernate.ddl-auto=create-drop  # create | create-drop | update | validate | none

# --- PostgreSQL (production) ---
# spring.datasource.url=jdbc:postgresql://localhost:5432/ma_base
# spring.datasource.username=postgres
# spring.datasource.password=secret
# spring.jpa.hibernate.ddl-auto=validate

# --- Logging ---
logging.level.root=INFO
logging.level.com.formation=DEBUG
logging.level.org.springframework.web=DEBUG
logging.level.org.hibernate.SQL=DEBUG

# --- Actuator (monitoring) ---
# management.endpoints.web.exposure.include=health,info,metrics
```

### Utiliser YAML (application.yml — alternative à .properties)

```yaml
# src/main/resources/application.yml
server:
  port: 8080

spring:
  datasource:
    url: jdbc:h2:mem:testdb
    username: sa
    password:
  h2:
    console:
      enabled: true
  jpa:
    show-sql: true
    hibernate:
      ddl-auto: create-drop

logging:
  level:
    root: INFO
    com.formation: DEBUG
```

## 5. Injection de dépendances (IoC)

Le cœur de Spring est le **conteneur IoC** (Inversion of Control) qui crée et gère les beans.

```java
package com.formation.demo.service;

import org.springframework.stereotype.Service;

// @Service : marque cette classe comme bean Spring
@Service
public class NotificationService {

    public void envoyer(String destinataire, String message) {
        System.out.printf("Email envoyé à %s : %s%n", destinataire, message);
    }
}
```

```java
package com.formation.demo.service;

import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Autowired;

@Service
public class CommandeService {

    // --- Injection par constructeur (RECOMMANDÉE) ---
    private final NotificationService notificationService;

    // @Autowired sur le constructeur (optionnel si un seul constructeur en Java)
    public CommandeService(NotificationService notificationService) {
        this.notificationService = notificationService;
    }

    public void passerCommande(String client, String article) {
        System.out.println("Commande passée : " + client + " → " + article);
        notificationService.envoyer(client, "Votre commande a été confirmée : " + article);
    }
}

// --- Injection par champ (déconseillée en production) ---
@Service
public class CommandeServiceV2 {
    @Autowired
    private NotificationService notificationService;  // ✗ difficile à tester
}

// --- Injection par setter (cas particulier) ---
@Service
public class CommandeServiceV3 {
    private NotificationService notificationService;

    @Autowired
    public void setNotificationService(NotificationService ns) {
        this.notificationService = ns;  // ✓ pour dépendances optionnelles
    }
}
```

## 6. Annotations Spring essentielles

```java
// Stéréotypes (marqueurs de beans)
@Component        // Bean générique
@Service          // Couche service (logique métier)
@Repository       // Couche d'accès aux données (DAO)
@Controller       // Contrôleur Spring MVC (retourne des vues)
@RestController   // Contrôleur REST (retourne du JSON)

// Configuration
@Configuration    // Classe de configuration (équivalent XML)
@Bean             // Méthode qui crée un bean dans une @Configuration
@EnableAutoConfiguration  // Activer l'auto-configuration
@ComponentScan    // Scanner les packages pour trouver les beans

// Injection
@Autowired        // Injection de dépendance
@Qualifier("nom") // Choisir un bean spécifique parmi plusieurs
@Value("${property.name}") // Injecter une propriété de configuration
@Primary          // Bean par défaut quand plusieurs candidats

// Portée
@Scope("singleton")  // Un seul bean (défaut)
@Scope("prototype")  // Nouveau bean à chaque injection
@RequestScope        // Un bean par requête HTTP
@SessionScope        // Un bean par session HTTP
```

```java
// Exemple : @Value pour injecter des propriétés
package com.formation.demo.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

@Component
public class AppConfig {

    @Value("${app.nom:MonApplication}")  // valeur par défaut : "MonApplication"
    private String appNom;

    @Value("${app.version}")
    private String version;

    @Value("${server.port}")
    private int port;

    public String getDescription() {
        return String.format("%s v%s (port %d)", appNom, version, port);
    }
}
```

```properties
# application.properties
app.nom=DemoFormation
app.version=1.0.0
```

## 7. Démarrage et profils

```java
// Exécuter du code au démarrage
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

@Component
public class DataInitializer implements CommandLineRunner {

    private final ProduitRepository repository;

    public DataInitializer(ProduitRepository repository) {
        this.repository = repository;
    }

    @Override
    public void run(String... args) throws Exception {
        // Ce code s'exécute au démarrage de l'application
        System.out.println("Initialisation des données...");
        repository.save(new Produit("Clavier", 79.99));
        repository.save(new Produit("Souris", 29.99));
        System.out.println("Données initialisées : " + repository.count() + " produits");
    }
}
```

```java
// Profils Spring
// application-dev.properties  → profil "dev"
// application-prod.properties → profil "prod"

// Activer un profil :
// - Dans application.properties : spring.profiles.active=dev
// - En ligne de commande : java -jar app.jar --spring.profiles.active=prod
// - Variable d'environnement : SPRING_PROFILES_ACTIVE=prod

@Component
@Profile("dev")  // Ce bean n'existe que dans le profil dev
public class DevDataSeeder implements CommandLineRunner {
    @Override
    public void run(String... args) {
        System.out.println("Données de développement insérées");
    }
}
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Dans IntelliJ, utiliser "Find Bean" (Ctrl+Shift+F12 dans la vue Spring) pour montrer la liste de tous les beans créés par l'auto-configuration. Montrer que Spring a créé des dizaines de beans automatiquement (DataSource, EntityManagerFactory, etc.).
> **Expliquer :** Expliquer le cycle de vie d'un bean Spring, la différence entre Singleton et Prototype, et pourquoi l'injection par constructeur est préférée (testabilité, immuabilité, détection des dépendances circulaires au démarrage).
---

## Récapitulatif

| Annotation | Rôle |
|------------|------|
| `@SpringBootApplication` | Point d'entrée, active tout |
| `@Component` / `@Service` / `@Repository` | Déclarer un bean |
| `@Autowired` | Injecter une dépendance |
| `@Value` | Injecter une propriété |
| `@Configuration` + `@Bean` | Créer des beans manuellement |
| `@Profile` | Conditionner un bean à un profil |
| `CommandLineRunner` | Code exécuté au démarrage |
