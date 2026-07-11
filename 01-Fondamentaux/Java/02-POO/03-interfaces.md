# Java POO — Interfaces : interface, implements, default methods, functional interfaces

## 1. Qu'est-ce qu'une interface ?

Une interface définit un **contrat** : elle spécifie *ce que* doit faire une classe, sans dire *comment*. C'est une liste de méthodes que toute classe implémentant l'interface doit fournir.

Différences avec la classe abstraite :
| | Interface | Classe abstraite |
|--|-----------|-----------------|
| Héritage multiple | ✓ `implements A, B, C` | ✗ `extends` un seul parent |
| État (attributs) | Non (sauf `static final`) | Oui |
| Constructeur | Non | Oui |
| Méthodes concrètes | `default` et `static` uniquement | Oui |
| Mot-clé | `interface` | `abstract class` |

## 2. Définir et implémenter une interface

```java
// Définition d'une interface
public interface Vehicule {

    // Les attributs d'interface sont implicitement public static final
    int VITESSE_MAXIMALE_LEGALE = 130;  // constante

    // Méthodes abstraites : implicitement public abstract
    void demarrer();
    void arreter();
    double getVitesse();

    // Méthode par défaut (Java 8+) : implémentation optionnelle pour les classes
    default void klaxonner() {
        System.out.println("Beep !");
    }

    // Méthode statique (Java 8+) : appelée sur l'interface, pas sur un objet
    static boolean estVitesseLegale(double vitesse) {
        return vitesse <= VITESSE_MAXIMALE_LEGALE;
    }
}

// Implémentation
public class Voiture implements Vehicule {

    private String marque;
    private double vitesse;

    public Voiture(String marque) {
        this.marque = marque;
        this.vitesse = 0;
    }

    @Override
    public void demarrer() {
        System.out.println(marque + " démarre.");
    }

    @Override
    public void arreter() {
        vitesse = 0;
        System.out.println(marque + " s'arrête.");
    }

    @Override
    public double getVitesse() {
        return vitesse;
    }

    public void accelerer(double kmh) {
        vitesse += kmh;
    }

    // klaxonner() hérité de l'interface, peut aussi être redéfini
    @Override
    public void klaxonner() {
        System.out.println(marque + " : TOOOOT !");
    }
}

public class Moto implements Vehicule {

    private double vitesse;

    public Moto() {
        this.vitesse = 0;
    }

    @Override
    public void demarrer() {
        System.out.println("Vroom !");
    }

    @Override
    public void arreter() {
        vitesse = 0;
    }

    @Override
    public double getVitesse() {
        return vitesse;
    }

    // klaxonner() non redéfini → utilise la version default de Vehicule
}
```

## 3. Implémenter plusieurs interfaces

```java
public interface Serialisable {
    String serialiser();
    void deserialiser(String data);
}

public interface Comparable<T> {
    int compareTo(T autre);
}

public interface Affichable {
    void afficher();

    default void afficherAvecBordure() {
        System.out.println("─".repeat(40));
        afficher();
        System.out.println("─".repeat(40));
    }
}

// Une classe peut implémenter plusieurs interfaces
public class Produit implements Serialisable, Affichable, Comparable<Produit> {

    private String nom;
    private double prix;
    private int stock;

    public Produit(String nom, double prix, int stock) {
        this.nom = nom;
        this.prix = prix;
        this.stock = stock;
    }

    @Override
    public String serialiser() {
        return nom + ";" + prix + ";" + stock;
    }

    @Override
    public void deserialiser(String data) {
        String[] parts = data.split(";");
        // this.nom = parts[0];
        // this.prix = Double.parseDouble(parts[1]);
        // this.stock = Integer.parseInt(parts[2]);
    }

    @Override
    public void afficher() {
        System.out.printf("%-20s %8.2f€  stock: %d%n", nom, prix, stock);
    }

    @Override
    public int compareTo(Produit autre) {
        return Double.compare(this.prix, autre.prix);  // tri par prix
    }

    public String getNom()    { return nom; }
    public double getPrix()   { return prix; }
}

public class MainProduits {
    public static void main(String[] args) {

        Produit[] produits = {
            new Produit("Clavier", 79.99, 10),
            new Produit("Souris", 29.99, 25),
            new Produit("Écran", 299.99, 5)
        };

        // Utilisation comme Affichable
        for (Affichable a : produits) {
            a.afficherAvecBordure();
        }

        // Utilisation comme Serialisable
        for (Serialisable s : produits) {
            System.out.println(s.serialiser());
        }

        // Tri via Comparable
        java.util.Arrays.sort(produits);  // utilise compareTo()
        System.out.println("\nTrié par prix :");
        for (Produit p : produits) {
            p.afficher();
        }
    }
}
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Dans IntelliJ, créer l'interface `Vehicule` avec ses méthodes, puis créer `Voiture implements Vehicule`. IntelliJ va souligner en rouge la classe et proposer "Implement methods". Montrer ce raccourci.
> **Expliquer :** Expliquer que si une classe implémente une interface mais n'implémente pas toutes les méthodes abstraites, c'est une erreur de compilation. IntelliJ aide à générer le squelette des méthodes manquantes automatiquement.
---

## 4. Interfaces fonctionnelles (Java 8+)

Une **interface fonctionnelle** possède exactement **une seule méthode abstraite**. Elle peut être implémentée avec une **lambda expression**.

### Interfaces fonctionnelles du JDK

```java
import java.util.function.*;

public class InterfacesFonctionnelles {
    public static void main(String[] args) {

        // --- Runnable : () -> void ---
        Runnable task = () -> System.out.println("Tâche exécutée");
        task.run();

        // --- Predicate<T> : T -> boolean ---
        Predicate<Integer> estPositif = n -> n > 0;
        Predicate<String> estLong    = s -> s.length() > 5;

        System.out.println(estPositif.test(5));     // true
        System.out.println(estPositif.test(-3));    // false
        System.out.println(estLong.test("Bonjour")); // true

        // Composition de prédicats
        Predicate<Integer> estPair = n -> n % 2 == 0;
        Predicate<Integer> estPositifEtPair = estPositif.and(estPair);
        Predicate<Integer> estPositifOuPair = estPositif.or(estPair);
        Predicate<Integer> nEstPasPositif   = estPositif.negate();

        System.out.println(estPositifEtPair.test(4));   // true
        System.out.println(estPositifEtPair.test(-2));  // false

        // --- Function<T, R> : T -> R ---
        Function<String, Integer> longueur  = s -> s.length();
        Function<Integer, String> intToStr  = n -> "Nombre : " + n;

        System.out.println(longueur.apply("Hello"));  // 5

        // Composition : f.andThen(g) = g(f(x))
        Function<String, String> longueurStr = longueur.andThen(intToStr);
        System.out.println(longueurStr.apply("Hello"));  // "Nombre : 5"

        // --- Consumer<T> : T -> void ---
        Consumer<String> afficher = s -> System.out.println(">> " + s);
        Consumer<String> stocker  = s -> System.out.println("Stocké : " + s);

        afficher.accept("Bonjour");

        // Enchaîner : andThen
        Consumer<String> afficherEtStocker = afficher.andThen(stocker);
        afficherEtStocker.accept("Message");

        // --- Supplier<T> : () -> T ---
        Supplier<String> salutation = () -> "Bonjour !";
        Supplier<java.util.List<String>> listeVide = java.util.ArrayList::new;

        System.out.println(salutation.get());
        System.out.println(listeVide.get());

        // --- BiFunction<T, U, R> : (T, U) -> R ---
        BiFunction<Integer, Integer, Integer> add = (a, b) -> a + b;
        BiFunction<String, String, String>    concat = (a, b) -> a + " " + b;

        System.out.println(add.apply(3, 4));           // 7
        System.out.println(concat.apply("Java", "21")); // "Java 21"

        // --- UnaryOperator<T> : T -> T ---
        UnaryOperator<String> majuscule = String::toUpperCase;  // référence de méthode
        UnaryOperator<Integer> carré    = n -> n * n;

        System.out.println(majuscule.apply("hello"));  // "HELLO"
        System.out.println(carré.apply(5));            // 25

        // --- BinaryOperator<T> : (T, T) -> T ---
        BinaryOperator<Integer> max = (a, b) -> a > b ? a : b;
        System.out.println(max.apply(10, 7));  // 10

        // --- Comparator<T> : interface fonctionnelle très utilisée ---
        java.util.Comparator<String> parLongueur = (a, b) -> a.length() - b.length();
        java.util.Comparator<String> alphabetique = String::compareTo;

        java.util.List<String> noms = new java.util.ArrayList<>(
            java.util.List.of("Zeynep", "Ali", "Bartholoméo", "Bo")
        );
        noms.sort(parLongueur);
        System.out.println(noms);  // [Bo, Ali, Zeynep, Bartholoméo]
    }
}
```

## 5. Créer sa propre interface fonctionnelle

```java
// Annotation optionnelle mais recommandée : vérifie qu'il n'y a qu'une méthode abstraite
@FunctionalInterface
public interface Transformateur<T, R> {
    R transformer(T entree);

    // Méthode par défaut OK
    default Transformateur<T, String> thenToString() {
        return entree -> String.valueOf(transformer(entree));
    }
}

@FunctionalInterface
public interface Validateur<T> {
    boolean valider(T valeur);

    default Validateur<T> et(Validateur<T> autre) {
        return valeur -> this.valider(valeur) && autre.valider(valeur);
    }

    default Validateur<T> ou(Validateur<T> autre) {
        return valeur -> this.valider(valeur) || autre.valider(valeur);
    }
}

public class InterfacesFonctionnellesCustom {
    public static void main(String[] args) {

        Transformateur<String, Integer> parser = s -> Integer.parseInt(s.trim());
        System.out.println(parser.transformer("  42  "));  // 42

        Transformateur<Integer, String> doublerStr = n -> "Double de " + n + " = " + (n * 2);
        System.out.println(doublerStr.transformer(7));  // "Double de 7 = 14"

        // Validateurs composés
        Validateur<String> nonVide   = s -> !s.isEmpty();
        Validateur<String> passTropLong = s -> s.length() <= 50;
        Validateur<String> contientAt = s -> s.contains("@");

        Validateur<String> emailValide = nonVide.et(passTropLong).et(contientAt);

        System.out.println(emailValide.valider("alice@example.com"));  // true
        System.out.println(emailValide.valider("pasd@email"));          // true
        System.out.println(emailValide.valider(""));                     // false
        System.out.println(emailValide.valider("pasdarobase.com"));     // false
    }
}
```

## 6. default methods — Héritage de méthode concrète

```java
public interface Logger {

    // Méthode abstraite
    void ecrire(String message);

    // default : implémentation fournie mais redéfinissable
    default void info(String message) {
        ecrire("[INFO]  " + message);
    }

    default void warn(String message) {
        ecrire("[WARN]  " + message);
    }

    default void error(String message) {
        ecrire("[ERROR] " + message);
    }
}

public class ConsoleLogger implements Logger {
    @Override
    public void ecrire(String message) {
        System.out.println(message);
    }
    // info(), warn(), error() fournis par l'interface
}

public class FileLogger implements Logger {
    private java.util.List<String> lignes = new java.util.ArrayList<>();

    @Override
    public void ecrire(String message) {
        lignes.add(message);
    }

    @Override
    public void error(String message) {
        // Redéfinition : enrichir le comportement par défaut
        ecrire("[ERROR] *** " + message + " ***");
    }

    public void afficherTout() {
        lignes.forEach(System.out::println);
    }
}

// --- Conflit de default methods ---
public interface A {
    default void hello() {
        System.out.println("Hello depuis A");
    }
}

public interface B {
    default void hello() {
        System.out.println("Hello depuis B");
    }
}

// Si une classe implémente A et B, elle DOIT résoudre le conflit
public class C implements A, B {
    @Override
    public void hello() {
        A.super.hello();  // choisir explicitement quelle version utiliser
        // ou fournir sa propre implémentation
    }
}
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Montrer dans IntelliJ la situation de conflit de default methods : créer deux interfaces avec la même méthode `default`, implémenter les deux dans une classe. IntelliJ souligne en rouge et propose le correctif. Montrer la résolution avec `A.super.hello()`.
> **Expliquer :** Expliquer pourquoi les `default` methods ont été introduites (évolution des APIs sans casser le code existant), et que le conflit ne peut pas survenir si on hérite d'une seule interface.
---

## 7. Interfaces du JDK les plus utiles

```java
import java.util.*;
import java.util.function.*;
import java.io.*;

public class InterfacesJDK {
    public static void main(String[] args) {

        // --- Iterable<T> : permet le for-each ---
        List<String> liste = List.of("a", "b", "c");
        for (String s : liste) {  // fonctionne car List implémente Iterable
            System.out.println(s);
        }

        // --- Comparable<T> : ordre naturel ---
        List<String> noms = new ArrayList<>(List.of("Charlie", "Alice", "Bob"));
        Collections.sort(noms);  // utilise String.compareTo()
        System.out.println(noms);  // [Alice, Bob, Charlie]

        // --- Comparator<T> : ordre personnalisé ---
        noms.sort(Comparator.comparingInt(String::length));
        System.out.println(noms);  // [Bob, Alice, Charlie]

        // Comparator composé
        noms.sort(Comparator.comparingInt(String::length)
                             .thenComparing(Comparator.naturalOrder()));

        // --- Cloneable : marque qu'un objet peut être cloné ---
        // --- Serializable : marque pour la sérialisation Java ---

        // --- AutoCloseable : try-with-resources ---
        // Voir le module I/O

        // --- Runnable et Callable : tâches ---
        Runnable r = () -> System.out.println("Tâche en cours");
        r.run();

        // Callable retourne une valeur (utilisé avec ExecutorService)
        java.util.concurrent.Callable<Integer> c = () -> 42;
        try {
            System.out.println(c.call());
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
```

## 8. Interface vs Classe abstraite — Quand choisir ?

```
Utiliser une INTERFACE quand :
  ✓ Tu veux définir un contrat sans imposer d'état
  ✓ Tu veux permettre l'implémentation multiple
  ✓ Tu modélises un comportement/capacité : Serialisable, Comparable, Flyable...
  ✓ Interfaces fonctionnelles pour les lambdas

Utiliser une CLASSE ABSTRAITE quand :
  ✓ Tu veux partager de l'état (attributs) entre les sous-classes
  ✓ Tu veux fournir un constructeur commun
  ✓ Tu veux du code partagé dans plusieurs méthodes concrètes
  ✓ Tu modélises une hiérarchie "est-un" : Forme → Cercle, Rectangl...
```

## Récapitulatif

| Concept | Syntaxe | À retenir |
|---------|---------|-----------|
| Interface | `interface NomInterface {}` | Contrat, pas d'état |
| Implémenter | `class C implements A, B` | Plusieurs interfaces possibles |
| Méthode abstraite | `void methode();` (implicite) | Doit être implémentée |
| `default` | `default void f() {...}` | Implémentation optionnelle |
| `static` | `static void f() {...}` | Appelée sur l'interface |
| Interface fonctionnelle | `@FunctionalInterface` | Une seule méthode abstraite |
| Lambda | `(params) -> expression` | Implémentation inline |
| Référence de méthode | `Classe::methode` | Raccourci lambda |
