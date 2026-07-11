# Java Moderne — Stream API, Lambda Expressions, Method References, Optional

## 1. Lambda Expressions

Une lambda est une **fonction anonyme** : elle n'a pas de nom, pas de classe, et peut être passée comme argument.

```java
import java.util.*;
import java.util.function.*;

public class LambdaExpressions {
    public static void main(String[] args) {

        // Syntaxe : (paramètres) -> corps

        // --- 0 paramètre ---
        Runnable r = () -> System.out.println("Hello !");
        r.run();

        // --- 1 paramètre (parenthèses optionnelles) ---
        Consumer<String> afficher = s -> System.out.println(s);
        Consumer<String> afficher2 = (s) -> System.out.println(s);  // équivalent
        Consumer<String> afficher3 = (String s) -> System.out.println(s);  // type explicite
        afficher.accept("Bonjour");

        // --- 2+ paramètres (parenthèses obligatoires) ---
        BiFunction<Integer, Integer, Integer> add = (a, b) -> a + b;
        System.out.println(add.apply(3, 4));  // 7

        // --- Corps bloc ---
        Function<Integer, String> describe = n -> {
            if (n < 0)       return "négatif";
            else if (n == 0) return "zéro";
            else             return "positif";
        };
        System.out.println(describe.apply(-5));   // "négatif"
        System.out.println(describe.apply(0));    // "zéro"
        System.out.println(describe.apply(10));   // "positif"

        // --- Lambda et variables externes ---
        // Lambda peut capturer des variables locales (doivent être effectivement finales)
        String prefix = ">> ";  // effectivement final
        Consumer<String> logger = msg -> System.out.println(prefix + msg);
        logger.accept("Message");

        // prefix = "!! ";  // ERREUR : ne peut plus modifier prefix après utilisation dans lambda

        // --- Comparators avec lambda ---
        List<String> noms = new ArrayList<>(List.of("Charlie", "Alice", "Bob", "David"));
        noms.sort((a, b) -> a.compareTo(b));                    // tri alphabétique
        noms.sort((a, b) -> a.length() - b.length());           // tri par longueur
        noms.sort((a, b) -> b.compareTo(a));                    // tri inverse
        System.out.println(noms);

        // Comparator.comparing : encore plus lisible
        noms.sort(Comparator.comparing(String::length)
                            .thenComparing(Comparator.naturalOrder()));
        System.out.println(noms);  // [Bob, Alice, David, Charlie]

        // --- Lambda dans des collections ---
        List<Integer> nombres = List.of(5, 2, 8, 1, 9, 3);
        nombres.forEach(n -> System.out.print(n + " "));
        System.out.println();

        // removeIf
        List<Integer> modifiable = new ArrayList<>(nombres);
        modifiable.removeIf(n -> n % 2 == 0);  // enlève les pairs
        System.out.println(modifiable);  // [5, 1, 9, 3]

        // replaceAll
        List<String> fruitsModif = new ArrayList<>(List.of("pomme", "banane", "kiwi"));
        fruitsModif.replaceAll(String::toUpperCase);
        System.out.println(fruitsModif);  // [POMME, BANANE, KIWI]
    }
}
```

## 2. Method References (Références de méthode)

```java
import java.util.*;
import java.util.function.*;
import java.util.stream.*;

public class MethodReferences {

    static class Util {
        public static boolean estPositif(int n) { return n > 0; }
        public static int doubler(int n) { return n * 2; }
    }

    static class Personne {
        private final String nom;
        private final int age;

        public Personne(String nom, int age) {
            this.nom = nom;
            this.age = age;
        }

        public String getNom() { return nom; }
        public int getAge()    { return age; }
        public boolean estAdulte() { return age >= 18; }

        @Override public String toString() { return nom + "(" + age + ")"; }
    }

    public static void main(String[] args) {

        // 4 types de références de méthode

        // --- 1. Référence à une méthode STATIQUE : Classe::methode ---
        // Lambda :     n -> Util.estPositif(n)
        // Ref méthode: Util::estPositif
        Predicate<Integer>        estPositif = Util::estPositif;
        Function<Integer,Integer> doubler    = Util::doubler;

        System.out.println(estPositif.test(5));  // true
        System.out.println(doubler.apply(7));    // 14

        // Exemples avec JDK
        Function<String, Integer> parseInt = Integer::parseInt;
        Function<String, String>  toUpperCase = String::toUpperCase;  // voir type 2
        System.out.println(parseInt.apply("42"));  // 42

        // --- 2. Référence à une méthode d'INSTANCE sur une instance particulière ---
        // Lambda :     s -> System.out.println(s)
        // Ref méthode: System.out::println
        Consumer<String> afficher = System.out::println;
        afficher.accept("Hello");

        String prefixe = ">> ";
        // Lambda :     s -> prefixe.concat(s)
        // Ref méthode: prefixe::concat
        Function<String, String> ajouterPrefixe = prefixe::concat;
        System.out.println(ajouterPrefixe.apply("message"));  // ">> message"

        // --- 3. Référence à une méthode d'INSTANCE sur un TYPE (instance quelconque) ---
        // Lambda :     s -> s.toUpperCase()
        // Ref méthode: String::toUpperCase  (le premier paramètre devient l'instance)
        Function<String, String>   upper    = String::toUpperCase;
        Function<String, Integer>  longueur = String::length;
        Predicate<String>          estVide  = String::isEmpty;
        BiFunction<String, String, Boolean> contient = String::contains;

        System.out.println(upper.apply("hello"));        // "HELLO"
        System.out.println(longueur.apply("Java"));      // 4
        System.out.println(estVide.test(""));            // true

        // Avec des Personnes
        Function<Personne, String>   getNom    = Personne::getNom;
        Function<Personne, Integer>  getAge    = Personne::getAge;
        Predicate<Personne>          estAdulte = Personne::estAdulte;

        Personne alice = new Personne("Alice", 30);
        System.out.println(getNom.apply(alice));      // "Alice"
        System.out.println(estAdulte.test(alice));    // true

        // --- 4. Référence à un CONSTRUCTEUR : Classe::new ---
        // Lambda :     (nom, age) -> new Personne(nom, age)
        // Ref méthode: Personne::new
        BiFunction<String, Integer, Personne> creerPersonne = Personne::new;
        Personne bob = creerPersonne.apply("Bob", 25);
        System.out.println(bob);  // Bob(25)

        // Avec Supplier (constructeur sans argument)
        Supplier<ArrayList<String>> creerListe = ArrayList::new;
        ArrayList<String> liste = creerListe.get();

        // --- Références dans les streams ---
        List<Personne> personnes = List.of(
            new Personne("Alice", 30),
            new Personne("Bob", 17),
            new Personne("Charlie", 25),
            new Personne("Eve", 15)
        );

        // Filtrer les adultes et afficher leurs noms
        personnes.stream()
            .filter(Personne::estAdulte)     // Ref méthode pour filter
            .map(Personne::getNom)           // Ref méthode pour map
            .sorted()                        // tri naturel
            .forEach(System.out::println);   // Ref méthode pour forEach

        // Créer des Personnes depuis des données
        List<String> donnees = List.of("Alice:30", "Bob:25", "Charlie:22");
        List<Personne> nouvellesPersonnes = donnees.stream()
            .map(s -> s.split(":"))
            .map(p -> new Personne(p[0], Integer.parseInt(p[1])))
            .collect(Collectors.toList());
        System.out.println(nouvellesPersonnes);
    }
}
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Dans IntelliJ, écrire une lambda et utiliser Alt+Entrée → "Replace lambda with method reference". Montrer qu'IntelliJ détecte automatiquement quand une référence de méthode peut remplacer une lambda. Faire l'inverse aussi (Expand to lambda expression).
> **Expliquer :** Expliquer quand préférer une lambda (logique complexe, multi-lignes) et quand préférer une référence de méthode (délégation simple, plus lisible). Les deux sont équivalentes en performance.
---

## 3. Stream API — Opérations avancées

```java
import java.util.*;
import java.util.stream.*;
import java.util.function.*;

public class StreamsAvance {
    record Employe(String nom, String departement, double salaire) {}

    public static void main(String[] args) {

        List<Employe> employes = List.of(
            new Employe("Alice",   "Tech",     75000),
            new Employe("Bob",     "Tech",     80000),
            new Employe("Charlie", "Marketing", 60000),
            new Employe("David",   "Tech",     90000),
            new Employe("Eve",     "Marketing", 65000),
            new Employe("Frank",   "RH",        55000)
        );

        // --- Collectors avancés ---

        // groupingBy : regrouper par département
        Map<String, List<Employe>> parDept = employes.stream()
            .collect(Collectors.groupingBy(Employe::departement));
        parDept.forEach((dept, emps) ->
            System.out.println(dept + " : " + emps.stream()
                .map(Employe::nom).collect(Collectors.joining(", "))));

        // groupingBy + counting
        Map<String, Long> nbParDept = employes.stream()
            .collect(Collectors.groupingBy(Employe::departement, Collectors.counting()));
        System.out.println(nbParDept);  // {Tech=3, Marketing=2, RH=1}

        // groupingBy + averagingDouble
        Map<String, Double> salaireMoyenParDept = employes.stream()
            .collect(Collectors.groupingBy(
                Employe::departement,
                Collectors.averagingDouble(Employe::salaire)
            ));
        salaireMoyenParDept.forEach((d, s) ->
            System.out.printf("%-12s %.0f€%n", d, s));

        // groupingBy + mapping
        Map<String, List<String>> nomsParDept = employes.stream()
            .collect(Collectors.groupingBy(
                Employe::departement,
                Collectors.mapping(Employe::nom, Collectors.toList())
            ));
        System.out.println(nomsParDept);

        // partitioningBy : diviser en deux groupes
        Map<Boolean, List<Employe>> partitionSalaire = employes.stream()
            .collect(Collectors.partitioningBy(e -> e.salaire() >= 70000));
        System.out.println("Hauts salaires : " + partitionSalaire.get(true).stream()
            .map(Employe::nom).collect(Collectors.joining(", ")));
        System.out.println("Bas salaires : " + partitionSalaire.get(false).stream()
            .map(Employe::nom).collect(Collectors.joining(", ")));

        // summarizingDouble
        DoubleSummaryStatistics stats = employes.stream()
            .collect(Collectors.summarizingDouble(Employe::salaire));
        System.out.printf("Stats salaires : count=%d, sum=%.0f, min=%.0f, max=%.0f, avg=%.0f%n",
            stats.getCount(), stats.getSum(), stats.getMin(), stats.getMax(), stats.getAverage());

        // joining
        String listeNoms = employes.stream()
            .map(Employe::nom)
            .collect(Collectors.joining(", ", "[", "]"));
        System.out.println(listeNoms);

        // toMap : convertir en Map
        Map<String, Double> salaireParNom = employes.stream()
            .collect(Collectors.toMap(Employe::nom, Employe::salaire));
        System.out.println(salaireParNom.get("Alice"));  // 75000.0

        // --- Streams parallèles ---
        long debut = System.currentTimeMillis();
        long somme = LongStream.rangeClosed(1, 100_000_000L)
            .parallel()  // parallélisation automatique sur plusieurs cœurs
            .sum();
        long fin = System.currentTimeMillis();
        System.out.printf("Somme : %d en %dms%n", somme, fin - debut);

        // Attention : parallel() n'est pas toujours plus rapide (overhead)
        // Utiliser pour des calculs intensifs sur de grandes collections

        // --- flatMap ---
        List<String> phrases = List.of("Bonjour le monde", "Java est génial", "Stream API");
        List<String> mots = phrases.stream()
            .flatMap(p -> Arrays.stream(p.split(" ")))
            .distinct()
            .sorted()
            .collect(Collectors.toList());
        System.out.println(mots);

        // --- Reduction complexe avec reduce ---
        // Calcul de la factorielle avec reduce
        long factorielle10 = LongStream.rangeClosed(1, 10)
            .reduce(1L, (a, b) -> a * b);
        System.out.println("10! = " + factorielle10);  // 3628800

        // reduce avec identité optionnelle
        Optional<Employe> employe_max_salaire = employes.stream()
            .reduce((e1, e2) -> e1.salaire() > e2.salaire() ? e1 : e2);
        employe_max_salaire.ifPresent(e ->
            System.out.println("Salaire max : " + e.nom() + " " + e.salaire()));

        // --- Stream.generate et Stream.iterate ---
        // Suite infinie de nombres aléatoires
        new Random().doubles(5, 0, 100)
            .forEach(d -> System.out.printf("%.2f ", d));
        System.out.println();

        // Fibonacci comme stream infini
        Stream.iterate(new long[]{0, 1}, f -> new long[]{f[1], f[0] + f[1]})
            .limit(10)
            .map(f -> f[0])
            .forEach(n -> System.out.print(n + " "));
        System.out.println();  // 0 1 1 2 3 5 8 13 21 34

        // --- Collectors.teeing (Java 12+) ---
        // Calculer min et max en un seul passage
        record MinMax(double min, double max) {}
        MinMax minMax = employes.stream()
            .collect(Collectors.teeing(
                Collectors.minBy(Comparator.comparingDouble(Employe::salaire)),
                Collectors.maxBy(Comparator.comparingDouble(Employe::salaire)),
                (min, max) -> new MinMax(
                    min.map(Employe::salaire).orElse(0.0),
                    max.map(Employe::salaire).orElse(0.0)
                )
            ));
        System.out.printf("Min: %.0f€, Max: %.0f€%n", minMax.min(), minMax.max());
    }
}
```

## 4. Optional — Gestion élégante des valeurs absentes

```java
import java.util.*;
import java.util.stream.*;

public class OptionalAvance {

    record Utilisateur(String nom, String email, Optional<String> telephone) {}
    record Commande(String id, double montant, Optional<String> codePromo) {}

    // Méthodes qui peuvent retourner une valeur ou rien
    public static Optional<Utilisateur> trouverParEmail(String email,
                                                         List<Utilisateur> utilisateurs) {
        return utilisateurs.stream()
            .filter(u -> u.email().equals(email))
            .findFirst();
    }

    public static Optional<Double> calculerRemise(String codePromo) {
        Map<String, Double> promos = Map.of("SOLDES", 0.20, "NOEL", 0.15, "VIP", 0.30);
        return Optional.ofNullable(promos.get(codePromo));
    }

    public static void main(String[] args) {

        List<Utilisateur> utilisateurs = List.of(
            new Utilisateur("Alice", "alice@ex.com", Optional.of("0601020304")),
            new Utilisateur("Bob",   "bob@ex.com",   Optional.empty())
        );

        // --- Création ---
        Optional<String> present  = Optional.of("valeur");    // non-null, sinon NPE
        Optional<String> vide     = Optional.empty();
        Optional<String> nullable = Optional.ofNullable(null); // null → empty

        // --- Vérification ---
        System.out.println(present.isPresent());  // true
        System.out.println(vide.isEmpty());       // true (Java 11+)

        // --- Accès sécurisé ---
        // get() : lève NoSuchElementException si vide → éviter !
        System.out.println(present.get());  // "valeur"

        // orElse : valeur par défaut
        System.out.println(vide.orElse("défaut"));  // "défaut"

        // orElseGet : valeur calculée (lazy)
        System.out.println(vide.orElseGet(() -> "calculé"));  // "calculé"

        // orElseThrow : exception personnalisée
        try {
            vide.orElseThrow(() -> new RuntimeException("Valeur attendue !"));
        } catch (RuntimeException e) {
            System.out.println(e.getMessage());
        }

        // --- Transformation ---
        Optional<Integer> longueur = present.map(String::length);  // Optional[6]
        Optional<Integer> vide2    = vide.map(String::length);     // Optional.empty

        // flatMap : quand la fonction retourne déjà un Optional
        Optional<Double> remise = Optional.of("SOLDES")
            .flatMap(OptionalAvance::calculerRemise);
        System.out.println(remise);  // Optional[0.2]

        Optional<Double> pasDeRemise = Optional.of("INCONNU")
            .flatMap(OptionalAvance::calculerRemise);
        System.out.println(pasDeRemise);  // Optional.empty

        // filter
        Optional<String> longue = present.filter(s -> s.length() > 3);  // présent si vrai
        Optional<String> courte = present.filter(s -> s.length() > 10); // vide

        // --- Effets de bord ---
        present.ifPresent(s -> System.out.println("Présent : " + s));
        present.ifPresentOrElse(
            s -> System.out.println("Valeur : " + s),
            () -> System.out.println("Absent")
        );

        // --- or : fournir un Optional de secours (Java 9+) ---
        Optional<String> resultat = vide.or(() -> Optional.of("secours"));
        System.out.println(resultat);  // Optional[secours]

        // --- stream() : convertir en Stream (Java 9+) ---
        long nb = utilisateurs.stream()
            .map(Utilisateur::telephone)
            .flatMap(Optional::stream)  // filtre les vides automatiquement
            .count();
        System.out.println("Utilisateurs avec téléphone : " + nb);  // 1

        // --- Chaînage d'Optionals ---
        String email = "alice@ex.com";
        String telephone = trouverParEmail(email, utilisateurs)
            .flatMap(Utilisateur::telephone)
            .map(tel -> "Tél: " + tel)
            .orElse("Pas de téléphone");
        System.out.println(telephone);  // "Tél: 0601020304"

        // Même logique sans Optional (beaucoup plus verbeux) :
        Utilisateur user = null;
        for (Utilisateur u : utilisateurs) {
            if (u.email().equals(email)) { user = u; break; }
        }
        String tel = "";
        if (user != null) {
            Optional<String> optTel = user.telephone();
            if (optTel.isPresent()) {
                tel = "Tél: " + optTel.get();
            } else {
                tel = "Pas de téléphone";
            }
        } else {
            tel = "Pas de téléphone";
        }
        System.out.println(tel);
    }
}
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Montrer côte à côte dans IntelliJ la version avec des vérifications `null` imbriquées et la version avec `Optional` chainé. La différence de lisibilité est frappante. Utiliser le panneau "Split editor" d'IntelliJ pour afficher les deux fichiers en même temps.
> **Expliquer :** Expliquer que `Optional` ne supprime pas les nulls en mémoire, mais force le développeur à gérer explicitement l'absence de valeur. Insister sur les méthodes à préférer : `orElse`, `orElseGet`, `ifPresent`, `map`, `flatMap` plutôt que `get()` ou `isPresent()`.
---

## 5. Exemples pratiques et patterns courants

```java
import java.util.*;
import java.util.stream.*;
import java.util.function.*;

public class PatternsPratiques {

    record Produit(String nom, String categorie, double prix, int stock) {}

    public static void main(String[] args) {
        List<Produit> catalogue = List.of(
            new Produit("Clavier",  "Informatique", 79.99,  15),
            new Produit("Souris",   "Informatique", 29.99,  30),
            new Produit("Écran",    "Informatique", 299.99,  5),
            new Produit("Bureau",   "Mobilier",     450.00,  3),
            new Produit("Chaise",   "Mobilier",     199.99,  8),
            new Produit("Lampe",    "Mobilier",      49.99, 20)
        );

        // --- Pattern 1 : Statistiques par groupe ---
        System.out.println("=== Statistiques par catégorie ===");
        catalogue.stream()
            .collect(Collectors.groupingBy(
                Produit::categorie,
                Collectors.summarizingDouble(Produit::prix)
            ))
            .forEach((cat, stats) ->
                System.out.printf("%-15s nb=%-3d prix moyen=%.2f€%n",
                    cat, stats.getCount(), stats.getAverage()));

        // --- Pattern 2 : Top N par critère ---
        System.out.println("\n=== Top 3 produits les plus chers ===");
        catalogue.stream()
            .sorted(Comparator.comparingDouble(Produit::prix).reversed())
            .limit(3)
            .forEach(p -> System.out.printf("%-15s %.2f€%n", p.nom(), p.prix()));

        // --- Pattern 3 : Index (Map<clé, objet>) ---
        Map<String, Produit> index = catalogue.stream()
            .collect(Collectors.toMap(Produit::nom, Function.identity()));
        System.out.println("\nChercher 'Souris' : " + index.get("Souris"));

        // --- Pattern 4 : Vérifications ensemblistes ---
        boolean tousDisponibles = catalogue.stream().allMatch(p -> p.stock() > 0);
        boolean unEnRupture     = catalogue.stream().anyMatch(p -> p.stock() == 0);
        long nbEnRupture        = catalogue.stream().filter(p -> p.stock() < 5).count();

        System.out.println("\nTous disponibles : " + tousDisponibles);
        System.out.println("Nb avec stock < 5 : " + nbEnRupture);

        // --- Pattern 5 : Transformation pipeline ---
        String rapport = catalogue.stream()
            .filter(p -> p.stock() > 10)
            .sorted(Comparator.comparing(Produit::categorie)
                              .thenComparing(Produit::nom))
            .map(p -> String.format("  %-15s (%s) %.2f€ × %d",
                p.nom(), p.categorie(), p.prix(), p.stock()))
            .collect(Collectors.joining("\n",
                "=== Produits bien stockés ===\n",
                "\n=== Fin du rapport ==="));
        System.out.println(rapport);

        // --- Pattern 6 : Inversion d'une map ---
        Map<String, String> frToEn = Map.of("pomme", "apple", "banane", "banana");
        Map<String, String> enToFr = frToEn.entrySet().stream()
            .collect(Collectors.toMap(Map.Entry::getValue, Map.Entry::getKey));
        System.out.println(enToFr.get("apple"));  // "pomme"

        // --- Pattern 7 : Fréquences ---
        List<String> mots = List.of("java", "rust", "java", "python", "java", "rust");
        Map<String, Long> frequences = mots.stream()
            .collect(Collectors.groupingBy(Function.identity(), Collectors.counting()));
        frequences.entrySet().stream()
            .sorted(Map.Entry.<String, Long>comparingByValue().reversed())
            .forEach(e -> System.out.println(e.getKey() + " : " + e.getValue()));
        // java : 3
        // rust : 2
        // python : 1
    }
}
```

## Récapitulatif

| Concept | Syntaxe | Cas d'usage |
|---------|---------|-------------|
| Lambda | `(a, b) -> a + b` | Implémenter une interface fonctionnelle |
| Ref méthode statique | `Classe::methodeStatique` | Déléguer à une méthode statique |
| Ref méthode instance (type) | `Classe::methodeInstance` | Transformer/filtrer des T |
| Ref méthode instance (objet) | `objet::methode` | Capturer un objet spécifique |
| Ref constructeur | `Classe::new` | Créer des objets dans un stream |
| `stream()` | `collection.stream()` | Démarrer un pipeline |
| `filter()` | `.filter(Predicate)` | Garder les éléments qui satisfont le prédicat |
| `map()` | `.map(Function)` | Transformer chaque élément |
| `flatMap()` | `.flatMap(Function)` | Aplatir les streams imbriqués |
| `collect()` | `.collect(Collectors.toList())` | Terminer le pipeline |
| `groupingBy()` | `Collectors.groupingBy(f)` | Regrouper par critère |
| Optional | `Optional.ofNullable(val)` | Modéliser l'absence de valeur |
