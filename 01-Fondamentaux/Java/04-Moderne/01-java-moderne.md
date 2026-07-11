# Java Moderne — Records, Sealed Classes, Pattern Matching (Java 17+)

## 1. Java LTS et versions modernes

| Version | Date | Fonctionnalités clés |
|---------|------|----------------------|
| Java 8 | 2014 | Lambdas, Streams, Optional |
| Java 11 | 2018 | `var` local, `String::strip`, fichiers simplifiés |
| Java 14 | 2020 | Switch expressions (standard), records (preview) |
| Java 15 | 2020 | Text blocks (standard) |
| Java 16 | 2021 | Records (standard), pattern matching instanceof |
| Java 17 | 2021 | Sealed classes (standard) — **LTS recommandée** |
| Java 21 | 2023 | Pattern matching switch (standard), virtual threads — **LTS récente** |

## 2. Records (Java 16+)

Un **record** est une classe immuable dont la seule responsabilité est de stocker des données. Il génère automatiquement le constructeur, les accesseurs, `equals()`, `hashCode()` et `toString()`.

```java
// Version classique (beaucoup de code boilerplate)
public final class PersonneClassique {
    private final String nom;
    private final String prenom;
    private final int age;

    public PersonneClassique(String nom, String prenom, int age) {
        this.nom = nom;
        this.prenom = prenom;
        this.age = age;
    }

    public String getNom()    { return nom; }
    public String getPrenom() { return prenom; }
    public int    getAge()    { return age; }

    @Override public boolean equals(Object o) { /* ... 15 lignes ... */ }
    @Override public int hashCode()            { /* ... */ }
    @Override public String toString()         { /* ... */ }
}

// Version record : équivalent en UNE ligne !
public record Personne(String nom, String prenom, int age) {}
```

### Utilisation des records

```java
public class RecordDemo {

    // Record simple
    record Point(double x, double y) {}

    // Record avec validation dans le constructeur compact
    record Age(int valeur) {
        Age {  // constructeur compact : pas besoin de paramètres ni d'assignation
            if (valeur < 0 || valeur > 150) {
                throw new IllegalArgumentException("Age invalide : " + valeur);
            }
            // valeur = Math.abs(valeur);  // possible mais déconseillé
        }
    }

    // Record avec méthodes supplémentaires
    record Rectangle(double largeur, double hauteur) {

        // Méthodes d'instance (autorisées)
        public double aire() {
            return largeur * hauteur;
        }

        public double perimetre() {
            return 2 * (largeur + hauteur);
        }

        public boolean estCarre() {
            return largeur == hauteur;
        }

        // Méthodes statiques (autorisées)
        public static Rectangle carre(double cote) {
            return new Rectangle(cote, cote);
        }
    }

    // Record générique
    record Paire<A, B>(A premier, B second) {
        public Paire<B, A> inverser() {
            return new Paire<>(second, premier);
        }
    }

    // Records imbriqués (modélisation de données)
    record Adresse(String rue, String ville, String codePostal) {}

    record Client(String nom, String email, Adresse adresse) {}

    // Record implémentant une interface
    interface Forme {
        double aire();
    }
    record Cercle(double rayon) implements Forme {
        @Override
        public double aire() {
            return Math.PI * rayon * rayon;
        }
    }

    public static void main(String[] args) {

        // Création
        Point p = new Point(3.0, 4.0);

        // Accesseurs générés (nom du composant, pas getX)
        System.out.println(p.x());  // 3.0
        System.out.println(p.y());  // 4.0

        // toString() généré
        System.out.println(p);  // Point[x=3.0, y=4.0]

        // equals() généré (comparaison structurelle)
        Point p2 = new Point(3.0, 4.0);
        System.out.println(p.equals(p2));  // true

        // hashCode() généré
        System.out.println(p.hashCode() == p2.hashCode());  // true

        // Immuabilité : pas de setters
        // p.x = 5.0;  // ERREUR : les composants sont final

        // Validation
        try {
            Age age = new Age(-5);
        } catch (IllegalArgumentException e) {
            System.out.println(e.getMessage());
        }

        // Méthodes supplémentaires
        Rectangle rect = new Rectangle(4, 3);
        System.out.println("Aire : " + rect.aire());         // 12.0
        System.out.println("Est carré : " + rect.estCarre()); // false

        Rectangle carre = Rectangle.carre(5);
        System.out.println("Est carré : " + carre.estCarre());  // true

        // Record générique
        Paire<String, Integer> p3 = new Paire<>("Alice", 30);
        System.out.println(p3);           // Paire[premier=Alice, second=30]
        System.out.println(p3.inverser()); // Paire[premier=30, second=Alice]

        // Records dans des listes
        java.util.List<Client> clients = java.util.List.of(
            new Client("Alice", "alice@ex.com", new Adresse("1 rue A", "Paris", "75001")),
            new Client("Bob",   "bob@ex.com",   new Adresse("2 rue B", "Lyon",  "69001"))
        );

        clients.forEach(c ->
            System.out.printf("%-10s %-20s %s%n",
                c.nom(), c.email(), c.adresse().ville())
        );

        // Records dans un switch (Java 21)
        Forme forme = new Cercle(5);
        String description = switch (forme) {
            case Cercle c -> String.format("Cercle de rayon %.1f, aire %.2f", c.rayon(), c.aire());
            default -> "Forme inconnue";
        };
        System.out.println(description);
    }
}
```

## 3. Text Blocks (Java 15+)

```java
public class TextBlocks {
    public static void main(String[] args) {

        // --- Avant les text blocks ---
        String htmlAncien = "<html>\n" +
            "    <body>\n" +
            "        <p>Hello, World!</p>\n" +
            "    </body>\n" +
            "</html>";

        // --- Avec text blocks ---
        String html = """
                <html>
                    <body>
                        <p>Hello, World!</p>
                    </body>
                </html>
                """;
        // L'indentation est retirée jusqu'au guillemet fermant
        System.out.println(html);

        // JSON
        String json = """
                {
                    "nom": "Alice",
                    "age": 30,
                    "actif": true
                }
                """;

        // SQL
        String sql = """
                SELECT u.nom, u.email, c.montant
                FROM utilisateurs u
                JOIN commandes c ON c.user_id = u.id
                WHERE u.actif = true
                  AND c.montant > 100
                ORDER BY c.montant DESC
                """;

        // Interpolation avec variables
        String nom = "Alice";
        int age    = 30;
        String template = """
                Bonjour, %s !
                Vous avez %d ans.
                """.formatted(nom, age);
        System.out.println(template);

        // Caractère \ pour supprimer le saut de ligne (Java 14+)
        String ligne_unique = """
                Ceci est une très longue chaîne qui continue \
                sur la ligne suivante dans le code \
                mais reste une seule ligne à l'exécution.
                """;
        System.out.println(ligne_unique);

        // Espaces significatifs avec \s
        String aligne = """
                a  \s
                bb \s
                ccc\s
                """;  // chaque ligne a exactement 4 caractères + \n
    }
}
```

## 4. Sealed Classes (Java 17+)

Les **sealed classes** permettent de contrôler quelles classes peuvent étendre ou implémenter une classe/interface.

```java
// Classe scellée : seules les classes listées dans 'permits' peuvent l'étendre
public sealed class Forme
        permits Cercle, Rectangle, Triangle {

    public abstract double aire();
    public abstract double perimetre();
}

// Chaque sous-classe doit être : final, sealed, ou non-sealed

// final : ne peut plus être étendue
public final class Cercle extends Forme {
    private final double rayon;

    public Cercle(double rayon) {
        this.rayon = rayon;
    }

    @Override public double aire() { return Math.PI * rayon * rayon; }
    @Override public double perimetre() { return 2 * Math.PI * rayon; }
    public double rayon() { return rayon; }
}

// sealed : peut être étendue mais contrôle qui
public sealed class Rectangle extends Forme
        permits Carre {
    protected final double largeur;
    protected final double hauteur;

    public Rectangle(double largeur, double hauteur) {
        this.largeur = largeur;
        this.hauteur = hauteur;
    }

    @Override public double aire() { return largeur * hauteur; }
    @Override public double perimetre() { return 2 * (largeur + hauteur); }
}

// non-sealed : rouvre la hiérarchie
public non-sealed class Triangle extends Forme {
    private final double a, b, c;

    public Triangle(double a, double b, double c) {
        this.a = a; this.b = b; this.c = c;
    }

    @Override public double aire() {
        double s = (a + b + c) / 2;
        return Math.sqrt(s * (s - a) * (s - b) * (s - c));
    }

    @Override public double perimetre() { return a + b + c; }
}

// final : hérite de Rectangle
public final class Carre extends Rectangle {
    public Carre(double cote) {
        super(cote, cote);
    }
}
```

### Pattern matching avec sealed classes (Java 21)

```java
public class PatternMatchingSealed {
    public static void main(String[] args) {

        Forme[] formes = {
            new Cercle(5),
            new Rectangle(4, 6),
            new Carre(3),
            new Triangle(3, 4, 5)
        };

        for (Forme f : formes) {
            // Pattern matching switch (Java 21)
            // Le compilateur vérifie l'exhaustivité grâce aux sealed classes
            String description = switch (f) {
                case Cercle c       -> String.format("Cercle (r=%.1f)", c.rayon());
                case Carre ca       -> String.format("Carré (c=%.1f)",  ca.largeur);
                case Rectangle r    -> String.format("Rectangle (%.1fx%.1f)", r.largeur, r.hauteur);
                case Triangle t     -> String.format("Triangle");
                // Pas besoin de 'default' : le compilateur sait que tout est couvert
            };
            System.out.printf("%-30s Aire=%.2f%n", description, f.aire());
        }

        // Guarded patterns (Java 21)
        for (Forme f : formes) {
            String categorie = switch (f) {
                case Cercle c when c.rayon() > 4 -> "Grand cercle";
                case Cercle c                    -> "Petit cercle";
                case Rectangle r when r.aire() > 20 -> "Grande surface";
                case Rectangle r                    -> "Petite surface";
                default -> "Autre";
            };
            System.out.println(f.getClass().getSimpleName() + " → " + categorie);
        }
    }
}
```

## 5. Pattern Matching instanceof (Java 16+)

```java
public class PatternMatchingInstanceof {
    public static void main(String[] args) {

        Object[] objets = {"Hello", 42, 3.14, true, null, new int[]{1, 2, 3}};

        for (Object o : objets) {

            // Avant Java 16
            if (o instanceof String) {
                String s = (String) o;  // cast séparé
                System.out.println("String de longueur " + s.length());
            }

            // Java 16+ : pattern matching (bind variable)
            if (o instanceof String s) {  // cast et assignation combinés
                System.out.println("String : " + s.toUpperCase());
            } else if (o instanceof Integer i) {
                System.out.println("Integer : " + (i * 2));
            } else if (o instanceof Double d) {
                System.out.printf("Double : %.2f%n", d);
            } else if (o instanceof int[] tab) {
                System.out.println("Tableau : " + java.util.Arrays.toString(tab));
            } else if (o == null) {
                System.out.println("Null");
            } else {
                System.out.println("Autre : " + o.getClass().getSimpleName());
            }
        }

        // Variable de pattern avec condition
        Object obj = "Java 21";
        if (obj instanceof String s && s.length() > 5) {
            System.out.println("Longue chaîne : " + s);
        }
    }
}
```

## 6. Switch Expressions (Java 14+)

```java
public class SwitchExpressions {

    sealed interface Commande permits Ajout, Suppression, Mise_a_jour {}
    record Ajout(String element) implements Commande {}
    record Suppression(int id) implements Commande {}
    record Mise_a_jour(int id, String valeur) implements Commande {}

    public static String traiterCommande(Commande cmd) {
        return switch (cmd) {
            case Ajout a         -> "Ajout : " + a.element();
            case Suppression s   -> "Suppression de l'id " + s.id();
            case Mise_a_jour m   -> "Mise à jour id=" + m.id() + " → " + m.valeur();
        };
    }

    public static void main(String[] args) {

        // Switch expression simple
        int jour = 3;
        String nomJour = switch (jour) {
            case 1 -> "Lundi";
            case 2 -> "Mardi";
            case 3 -> "Mercredi";
            case 4 -> "Jeudi";
            case 5 -> "Vendredi";
            case 6, 7 -> "Week-end";
            default -> throw new IllegalArgumentException("Jour invalide");
        };
        System.out.println(nomJour);

        // Avec bloc et yield
        int note = 75;
        String mention = switch (note / 10) {
            case 10, 9 -> "Très bien";
            case 8 -> "Bien";
            case 7 -> {
                System.out.println("Dans le bloc pour 70-79");
                yield "Assez bien";
            }
            case 6 -> "Passable";
            default -> "Insuffisant";
        };
        System.out.println(mention);

        // Pattern matching switch sur types
        java.util.List<Object> elements = java.util.List.of(
            "hello", 42, 3.14, java.util.List.of(1, 2, 3)
        );

        for (Object e : elements) {
            String desc = switch (e) {
                case String s when s.length() > 3 -> "Longue chaîne : " + s;
                case String s                     -> "Courte chaîne : " + s;
                case Integer i                    -> "Entier pair/impair : " + (i % 2 == 0 ? "pair" : "impair");
                case Double d                     -> String.format("Réel : %.1f", d);
                case java.util.List<?> l          -> "Liste de " + l.size() + " éléments";
                case null                         -> "Null";
                default                           -> "Inconnu";
            };
            System.out.println(desc);
        }

        // Sealed interface avec pattern matching
        java.util.List<Commande> commandes = java.util.List.of(
            new Ajout("item-1"),
            new Suppression(42),
            new Mise_a_jour(10, "nouvelle valeur")
        );
        commandes.forEach(c -> System.out.println(traiterCommande(c)));
    }
}
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Dans IntelliJ, créer une sealed interface avec des records et utiliser le switch pattern matching. Montrer que si on oublie un cas dans le switch (par ex. enlever `case Triangle`), IntelliJ (et le compilateur) signalent une erreur "Switch expression is not exhaustive". C'est un des grands avantages des sealed classes.
> **Expliquer :** Insister sur le fait que l'exhaustivité du switch est vérifiée à la COMPILATION grâce aux sealed classes. Comparer avec une hiérarchie non-sealed où il faudrait un `default` pour couvrir les cas inconnus.
---

## 7. Autres fonctionnalités modernes

```java
import java.util.*;

public class AutresFonctionnalites {
    public static void main(String[] args) {

        // --- var (Java 10+) : inférence de type local ---
        var liste = new ArrayList<String>();  // ArrayList<String>
        var map   = new HashMap<String, Integer>();  // HashMap<String, Integer>
        var n     = 42;  // int

        // var dans un for-each
        for (var element : liste) {
            System.out.println(element);
        }

        // var n'est PAS dynamique comme en Python/JS : type fixé à la déclaration
        // var x = 42;
        // x = "hello";  // ERREUR de compilation !

        // --- Fabriques de collections (Java 9+) ---
        List<String> immutable = List.of("a", "b", "c");  // non modifiable
        Set<Integer> set = Set.of(1, 2, 3, 4, 5);
        Map<String, Integer> map2 = Map.of("un", 1, "deux", 2, "trois", 3);

        // Java 10+ : copie modifiable
        var modifiable = new ArrayList<>(List.of("a", "b", "c"));
        modifiable.add("d");

        // Map.copyOf, List.copyOf
        var copie = List.copyOf(modifiable);  // non modifiable

        // --- String (Java 11+) ---
        System.out.println("  hello  ".strip());         // "hello"
        System.out.println("  hello  ".stripLeading());  // "hello  "
        System.out.println("  hello  ".stripTrailing()); // "  hello"
        System.out.println("".isBlank());                // true
        System.out.println("  ".isBlank());              // true
        "a\nb\nc".lines().forEach(System.out::println);
        System.out.println("ha".repeat(3));              // "hahaha"

        // --- Optional (Java 8+, amélioré en 11+) ---
        Optional<String> opt = Optional.of("hello");
        Optional<String> empty = Optional.empty();
        Optional<String> nullable = Optional.ofNullable(null);

        System.out.println(opt.isPresent());         // true
        System.out.println(opt.get());               // "hello"
        System.out.println(empty.orElse("défaut"));  // "défaut"
        System.out.println(empty.orElseGet(() -> calculerValeur())); // lazy

        opt.ifPresent(s -> System.out.println("Valeur : " + s));
        opt.ifPresentOrElse(
            s -> System.out.println("Présent : " + s),
            () -> System.out.println("Absent")
        );

        // Transformations
        Optional<Integer> longueur = opt.map(String::length);
        Optional<String> majuscule = opt.filter(s -> s.length() > 3)
                                        .map(String::toUpperCase);

        System.out.println(longueur.orElse(0));   // 5
        System.out.println(majuscule.orElse(""));  // "HELLO"

        // Optional.or (Java 9+)
        Optional<String> resultat = empty.or(() -> Optional.of("fallback"));
        System.out.println(resultat.get());  // "fallback"

        // Optional.stream (Java 9+)
        resultat.stream().forEach(System.out::println);
    }

    static String calculerValeur() {
        return "valeur calculée";
    }
}
```

## Récapitulatif Java Moderne

| Fonctionnalité | Version | Exemple |
|----------------|---------|---------|
| `var` | Java 10 | `var liste = new ArrayList<>()` |
| Text blocks | Java 15 | `""" ... """` |
| Records | Java 16 | `record Point(int x, int y) {}` |
| Pattern matching `instanceof` | Java 16 | `if (o instanceof String s)` |
| Sealed classes | Java 17 | `sealed class C permits A, B` |
| Switch expression | Java 14 | `var r = switch(x) { case 1 -> "a"; }` |
| Pattern matching switch | Java 21 | `switch(o) { case String s -> ... }` |
| `List.of()` | Java 9 | `List.of(1, 2, 3)` |
| `Optional` | Java 8 | `Optional.ofNullable(val).orElse(...)` |
