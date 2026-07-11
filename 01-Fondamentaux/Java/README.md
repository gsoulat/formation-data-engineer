# Formation Java — Du Fondamental au Spring Boot

## Objectifs pédagogiques

Ce module de formation couvre Java de manière progressive, depuis les bases du langage jusqu'au développement d'APIs REST avec Spring Boot. À l'issue de cette formation, l'apprenant sera capable de :

- Comprendre le fonctionnement de la JVM et l'écosystème Java
- Maîtriser la programmation orientée objet en Java
- Utiliser les collections, les streams et les lambdas
- Gérer les exceptions et les entrées/sorties
- Développer des APIs REST avec Spring Boot
- Utiliser Spring Data JPA pour persister des données

## Prérequis

- Notions de programmation (variables, boucles, fonctions) dans n'importe quel langage
- Environnement de développement installé (voir ci-dessous)

## Installation de l'environnement

### JDK (Java Development Kit)

```bash
# Vérifier si Java est installé
java -version
javac -version

# Installer via SDKMAN (recommandé)
curl -s "https://get.sdkman.io" | bash
source "$HOME/.sdkman/bin/sdkman-init.sh"
sdk install java 21.0.2-tem

# Ou via Homebrew (macOS)
brew install openjdk@21

# Ou téléchargement direct
# https://adoptium.net/ → Temurin 21 LTS
```

### IDE recommandé : IntelliJ IDEA

- **IntelliJ IDEA Community Edition** (gratuit) : https://www.jetbrains.com/idea/download/
- Plugins utiles : Lombok, Spring Boot (inclus dans la version Ultimate)

### Maven et Gradle

```bash
# Maven (gestionnaire de dépendances)
brew install maven   # macOS
mvn -version

# Gradle (alternative moderne)
brew install gradle
gradle -version
```

## Plan du cours

| Module | Contenu | Durée estimée |
|--------|---------|---------------|
| **Fondamentaux** | JVM, types, contrôle, méthodes | 4h |
| **POO** | Classes, héritage, interfaces, génériques | 6h |
| **Standard Library** | Collections, exceptions, I/O | 4h |
| **Java Moderne** | Records, sealed classes, Streams, lambdas | 4h |
| **Spring Boot** | REST API, Spring Data JPA | 6h |
| **Exercices** | Projets guidés | 4h |

**Durée totale estimée : ~28 heures**

## Structure des fichiers

```
Java/
├── README.md                    ← Ce fichier
├── Fondamentaux/
│   ├── 01-introduction.md       ← JVM, JDK/JRE, compilation, types primitifs
│   ├── 02-controle.md           ← if/else, switch, boucles, tableaux
│   └── 03-methodes.md           ← Méthodes, surcharge, récursion, varargs
├── POO/
│   ├── 01-classes-objets.md     ← Classes, constructeurs, this, static
│   ├── 02-heritage.md           ← extends, super, abstract, final
│   ├── 03-interfaces.md         ← interface, implements, default methods
│   └── 04-generiques.md         ← Generics <T>, wildcards, bounded types
├── Standard-Library/
│   ├── 01-collections.md        ← List, Set, Map, Streams API
│   ├── 02-exceptions.md         ← try/catch/finally, custom exceptions
│   └── 03-io-fichiers.md        ← Files, NIO2, try-with-resources
├── Moderne/
│   ├── 01-java-moderne.md       ← Records, sealed classes, Java 17+
│   └── 02-streams-lambdas.md    ← Stream API, lambdas, Optional
├── Spring-Boot/
│   ├── README.md
│   ├── 01-introduction.md       ← Spring Boot, auto-configuration
│   ├── 02-rest-api.md           ← @RestController, mappings
│   └── 03-spring-data.md        ← JPA, Repository, @Transactional
├── exercices/
│   ├── exercice-01-poo.md
│   └── exercice-02-api-spring.md
└── CHEATSHEET-java.md
```

## Ressources complémentaires

- [Documentation officielle Java 21](https://docs.oracle.com/en/java/javase/21/)
- [Spring Boot Reference](https://docs.spring.io/spring-boot/docs/current/reference/html/)
- [Baeldung](https://www.baeldung.com/) — tutoriels Java de qualité
- [Spring Initializr](https://start.spring.io/) — générateur de projets Spring Boot
- [JavaDoc en ligne](https://docs.oracle.com/en/java/javase/21/docs/api/)

## Convention de notation dans ce cours

- `// commentaire` — explication inline dans le code
- `// ✓ Bonne pratique` — ce qu'il faut faire
- `// ✗ À éviter` — ce qu'il ne faut pas faire
- Les blocs `> 🔴 ACTION FORMATEUR` indiquent les moments où une démonstration en direct est attendue
