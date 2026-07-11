# Java POO — Génériques : Generics <T>, Wildcards, Bounded Types

## 1. Pourquoi les génériques ?

Sans génériques, on devrait écrire une classe séparée pour chaque type, ou utiliser `Object` avec des casts risqués.

```java
// Sans génériques : version Object — problématique
public class BoiteObject {
    private Object contenu;

    public void mettre(Object o) { this.contenu = o; }
    public Object sortir()       { return contenu; }
}

// Utilisation : risqué car pas de vérification de type à la compilation
BoiteObject boite = new BoiteObject();
boite.mettre("Bonjour");
String s = (String) boite.sortir();   // OK
Integer n = (Integer) boite.sortir(); // ClassCastException à l'exécution !

// Avec génériques : sûr à la compilation
public class Boite<T> {
    private T contenu;

    public void mettre(T o)  { this.contenu = o; }
    public T    sortir()     { return contenu; }
}

Boite<String>  boiteStr = new Boite<>();
boiteStr.mettre("Bonjour");
String s = boiteStr.sortir();    // ✓ Aucun cast nécessaire
// Integer n = boiteStr.sortir(); // ✗ Erreur de COMPILATION (sûr !)
```

## 2. Classes génériques

```java
// T = Type (convention)
// E = Element (collections)
// K = Key (maps)
// V = Value (maps)
// N = Number
// R = Return type

public class Paire<A, B> {

    private final A premier;
    private final B second;

    public Paire(A premier, B second) {
        this.premier = premier;
        this.second  = second;
    }

    public A getPremier() { return premier; }
    public B getSecond()  { return second; }

    public Paire<B, A> inverser() {
        return new Paire<>(second, premier);
    }

    @Override
    public String toString() {
        return "(" + premier + ", " + second + ")";
    }

    public static void main(String[] args) {
        Paire<String, Integer> p1 = new Paire<>("Alice", 30);
        Paire<Integer, String> p2 = p1.inverser();

        System.out.println(p1);  // (Alice, 30)
        System.out.println(p2);  // (30, Alice)

        Paire<String, String> coords = new Paire<>("Paris", "48.8566");
        System.out.println(coords);

        // Diamond operator <> : Java infère le type
        Paire<Double, Boolean> p3 = new Paire<>(3.14, true);
    }
}

// Classe générique avec contrainte
public class Pile<T> {

    private java.util.ArrayList<T> elements = new java.util.ArrayList<>();

    public void empiler(T element) {
        elements.add(element);
    }

    public T depiler() {
        if (estVide()) throw new java.util.EmptyStackException();
        return elements.remove(elements.size() - 1);
    }

    public T sommet() {
        if (estVide()) throw new java.util.EmptyStackException();
        return elements.get(elements.size() - 1);
    }

    public boolean estVide() {
        return elements.isEmpty();
    }

    public int taille() {
        return elements.size();
    }

    @Override
    public String toString() {
        return elements.toString();
    }

    public static void main(String[] args) {
        Pile<Integer> pile = new Pile<>();
        pile.empiler(1);
        pile.empiler(2);
        pile.empiler(3);

        System.out.println(pile.sommet());   // 3
        System.out.println(pile.depiler());  // 3
        System.out.println(pile.depiler());  // 2
        System.out.println(pile);            // [1]

        // Pile d'objets
        Pile<String> pileStr = new Pile<>();
        pileStr.empiler("a");
        pileStr.empiler("b");
        System.out.println(pileStr.depiler());  // "b"
    }
}
```

## 3. Méthodes génériques

```java
public class MethodesGeneriques {

    // Méthode générique statique
    public static <T> void echanger(T[] tableau, int i, int j) {
        T temp    = tableau[i];
        tableau[i] = tableau[j];
        tableau[j] = temp;
    }

    // Retourne le maximum de deux éléments comparables
    public static <T extends Comparable<T>> T max(T a, T b) {
        return a.compareTo(b) >= 0 ? a : b;
    }

    // Affiche tous les éléments
    public static <T> void afficherTout(java.util.List<T> liste) {
        for (T element : liste) {
            System.out.print(element + " ");
        }
        System.out.println();
    }

    // Copie une liste dans une autre
    public static <T> java.util.List<T> copier(java.util.List<T> source) {
        return new java.util.ArrayList<>(source);
    }

    // Filtre une liste selon un prédicat
    public static <T> java.util.List<T> filtrer(
            java.util.List<T> liste,
            java.util.function.Predicate<T> predicat) {

        java.util.List<T> resultat = new java.util.ArrayList<>();
        for (T element : liste) {
            if (predicat.test(element)) {
                resultat.add(element);
            }
        }
        return resultat;
    }

    // Transformer chaque élément (map)
    public static <T, R> java.util.List<R> transformer(
            java.util.List<T> liste,
            java.util.function.Function<T, R> fonction) {

        java.util.List<R> resultat = new java.util.ArrayList<>();
        for (T element : liste) {
            resultat.add(fonction.apply(element));
        }
        return resultat;
    }

    public static void main(String[] args) {

        Integer[] nombres = {5, 2, 8, 1, 9, 3};
        System.out.println(java.util.Arrays.toString(nombres)); // avant
        echanger(nombres, 0, 4);
        System.out.println(java.util.Arrays.toString(nombres)); // après

        System.out.println(max(10, 20));          // 20
        System.out.println(max("Alice", "Zoé"));  // "Zoé" (alphabétique)
        System.out.println(max(3.14, 2.72));      // 3.14

        java.util.List<String> noms = java.util.List.of("Alice", "Bob", "Charlie", "Eve");
        afficherTout(noms);

        // Filtrer les noms de plus de 3 lettres
        java.util.List<String> longs = filtrer(noms, s -> s.length() > 3);
        System.out.println(longs);  // [Alice, Charlie]

        // Transformer en majuscules
        java.util.List<String> majuscules = transformer(noms, String::toUpperCase);
        System.out.println(majuscules);  // [ALICE, BOB, CHARLIE, EVE]

        // Transformer en longueurs
        java.util.List<Integer> longueurs = transformer(noms, String::length);
        System.out.println(longueurs);  // [5, 3, 7, 3]
    }
}
```

## 4. Wildcards (jokers)

Le wildcard `?` représente un type inconnu. Il y en a trois formes :

```java
import java.util.*;

public class Wildcards {

    // --- ? unbounded : type quelconque (lecture seule) ---
    public static void afficherListe(List<?> liste) {
        for (Object element : liste) {
            System.out.print(element + " ");
        }
        System.out.println();
    }

    // --- ? extends T : "producer" — lit des T ou sous-types de T ---
    // On peut LIRE, mais pas ÉCRIRE (sauf null)
    public static double sommeNombres(List<? extends Number> liste) {
        double total = 0;
        for (Number n : liste) {
            total += n.doubleValue();
        }
        return total;
    }

    // --- ? super T : "consumer" — accepte T ou super-types de T ---
    // On peut ÉCRIRE des T, mais la lecture retourne Object
    public static void ajouterEntiers(List<? super Integer> liste) {
        liste.add(1);
        liste.add(2);
        liste.add(3);
    }

    // Règle PECS : Producer Extends, Consumer Super
    // - Si tu LIS depuis la liste → ? extends
    // - Si tu ÉCRIS dans la liste → ? super

    public static void main(String[] args) {

        // afficherListe accepte tout
        afficherListe(List.of(1, 2, 3));
        afficherListe(List.of("a", "b", "c"));
        afficherListe(List.of(1.5, 2.5, 3.5));

        // sommeNombres accepte Integer, Double, Long, Float...
        List<Integer>  ints     = List.of(1, 2, 3, 4, 5);
        List<Double>   doubles  = List.of(1.5, 2.5, 3.5);
        List<Long>     longs    = List.of(100L, 200L, 300L);

        System.out.println(sommeNombres(ints));    // 15.0
        System.out.println(sommeNombres(doubles)); // 7.5
        System.out.println(sommeNombres(longs));   // 600.0

        // sommeNombres(List.of("a", "b"));  // ERREUR : String n'étend pas Number

        // ajouterEntiers accepte List<Integer>, List<Number>, List<Object>
        List<Number> nombres = new ArrayList<>();
        ajouterEntiers(nombres);
        System.out.println(nombres);  // [1, 2, 3]

        List<Object> objets = new ArrayList<>();
        ajouterEntiers(objets);
        System.out.println(objets);   // [1, 2, 3]

        // Copier une liste : exemple classique PECS
        copier(ints, new ArrayList<Number>());  // ? extends src, ? super dst
    }

    // Copie de src vers dst
    public static <T> void copier(List<? extends T> src, List<? super T> dst) {
        for (T element : src) {
            dst.add(element);
        }
    }
}
```

## 5. Bounded type parameters

```java
public class BoundedTypes {

    // T doit être un Comparable : permet d'utiliser compareTo()
    public static <T extends Comparable<T>> T minimum(List<T> liste) {
        if (liste.isEmpty()) throw new IllegalArgumentException("Liste vide");
        T min = liste.get(0);
        for (T element : liste) {
            if (element.compareTo(min) < 0) {
                min = element;
            }
        }
        return min;
    }

    // T doit être un Number : accès à doubleValue(), intValue()...
    public static <T extends Number> double moyenne(List<T> liste) {
        if (liste.isEmpty()) return 0;
        double total = liste.stream()
                            .mapToDouble(Number::doubleValue)
                            .sum();
        return total / liste.size();
    }

    // Multiple bounds : T doit implémenter Comparable ET Cloneable
    public static <T extends Comparable<T> & Cloneable> T maxCloneable(T a, T b) {
        return a.compareTo(b) >= 0 ? a : b;
    }

    // Classe avec type borné
    public static class FileMinMax<T extends Comparable<T>> {

        private T minimum;
        private T maximum;

        public FileMinMax(T valeur) {
            this.minimum = valeur;
            this.maximum = valeur;
        }

        public void ajouter(T valeur) {
            if (valeur.compareTo(minimum) < 0) minimum = valeur;
            if (valeur.compareTo(maximum) > 0) maximum = valeur;
        }

        public T getMinimum() { return minimum; }
        public T getMaximum() { return maximum; }

        @Override
        public String toString() {
            return "Min=" + minimum + ", Max=" + maximum;
        }
    }

    public static void main(String[] args) {

        List<Integer>  entiers  = List.of(5, 2, 8, 1, 9, 3);
        List<Double>   reels    = List.of(1.5, 3.2, 0.8, 4.1);
        List<String>   chaines  = List.of("banana", "apple", "cherry", "date");

        System.out.println("Min entiers : "  + minimum(entiers));   // 1
        System.out.println("Min réels : "    + minimum(reels));     // 0.8
        System.out.println("Min chaînes : "  + minimum(chaines));   // "apple"

        System.out.println("Moyenne : " + moyenne(entiers));        // 4.666...
        System.out.println("Moyenne : " + moyenne(reels));          // 2.4

        FileMinMax<Integer> suivi = new FileMinMax<>(10);
        suivi.ajouter(5);
        suivi.ajouter(15);
        suivi.ajouter(3);
        suivi.ajouter(20);
        System.out.println(suivi);  // Min=3, Max=20
    }
}
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Montrer dans IntelliJ l'auto-complétion sur `T` dans une méthode générique avec `<T extends Comparable<T>>`. Montrer que dans le corps de la méthode, IntelliJ propose `compareTo()` parce qu'il sait que T implémente Comparable. Sans la borne, il ne proposerait que les méthodes de Object.
> **Expliquer :** Expliquer l'erasure de type (type erasure) : à la compilation, les génériques sont effacés et remplacés par les bornes (ou Object). C'est pourquoi `List<Integer>` et `List<String>` ont le même type à l'exécution. Montrer pourquoi `new T()` est interdit.
---

## 6. Type erasure et limitations

```java
import java.util.*;

public class TypeErasure {
    public static void main(String[] args) {

        // À la compilation, les génériques existent
        List<String>  listeStr  = new ArrayList<>();
        List<Integer> listeInt  = new ArrayList<>();

        // À l'exécution (après erasure), les deux sont des ArrayList<Object>
        System.out.println(listeStr.getClass() == listeInt.getClass());  // true !

        // Conséquences de l'erasure :

        // 1. Impossible d'utiliser instanceof avec types génériques
        // if (listeStr instanceof List<String>) {}  // ERREUR de compilation
        if (listeStr instanceof List<?>) {}           // OK avec wildcard

        // 2. Impossible de créer des tableaux génériques
        // T[] tableau = new T[10];  // ERREUR (T inconnu à l'exécution)

        // Contournement : passer le Class<T> en paramètre
        System.out.println(creerTableau(String.class, 5));  // tableau de 5 Strings

        // 3. Impossible d'instancier directement T
        // T instance = new T();  // ERREUR

        // Contournement : passer un Supplier<T>
        // Voir l'exemple dans les collections avec factory méthodes

        // 4. Les génériques et les primitifs
        // List<int> listeInt2 = new ArrayList<>();  // ERREUR : doit être Integer
        List<Integer> listeOK = new ArrayList<>();  // utiliser les wrapper classes
    }

    @SuppressWarnings("unchecked")
    public static <T> T[] creerTableau(Class<T> type, int taille) {
        return (T[]) java.lang.reflect.Array.newInstance(type, taille);
    }
}
```

## 7. Generics dans les collections Java (aperçu)

```java
import java.util.*;

public class GenericsCollections {
    public static void main(String[] args) {

        // List<T> : liste ordonnée
        List<String> noms = new ArrayList<>();
        noms.add("Alice");
        noms.add("Bob");
        String premier = noms.get(0);  // pas de cast nécessaire

        // Map<K, V> : association clé → valeur
        Map<String, Integer> ages = new HashMap<>();
        ages.put("Alice", 30);
        ages.put("Bob", 25);
        int ageAlice = ages.get("Alice");  // 30

        // Set<T> : ensemble sans doublon
        Set<Integer> ensemble = new HashSet<>();
        ensemble.add(1);
        ensemble.add(2);
        ensemble.add(1);  // ignoré : déjà présent
        System.out.println(ensemble.size());  // 2

        // Imbrication
        Map<String, List<String>> etudiantsParGroupe = new HashMap<>();
        etudiantsParGroupe.put("GroupeA", new ArrayList<>(List.of("Alice", "Bob")));
        etudiantsParGroupe.put("GroupeB", new ArrayList<>(List.of("Charlie", "David")));

        for (Map.Entry<String, List<String>> entry : etudiantsParGroupe.entrySet()) {
            System.out.println(entry.getKey() + " : " + entry.getValue());
        }

        // Collections.sort() avec Comparable
        List<Integer> nums = new ArrayList<>(List.of(5, 2, 8, 1, 3));
        Collections.sort(nums);  // utilise Integer.compareTo()
        System.out.println(nums);

        // Tri avec Comparator générique
        List<String> langages = new ArrayList<>(List.of("Java", "Rust", "Python", "Go"));
        langages.sort(Comparator.comparingInt(String::length)
                                .thenComparing(Comparator.naturalOrder()));
        System.out.println(langages);  // [Go, Java, Rust, Python]
    }
}
```

## Récapitulatif

| Concept | Syntaxe | À retenir |
|---------|---------|-----------|
| Classe générique | `class C<T>` | T est le paramètre de type |
| Méthode générique | `<T> void f(T t)` | T déclaré avant le type de retour |
| Wildcard libre | `List<?>` | Lecture seule |
| Upper bounded | `List<? extends T>` | Lit des T ou sous-types (Producer) |
| Lower bounded | `List<? super T>` | Écrit des T ou super-types (Consumer) |
| Type borné | `<T extends Number>` | Donne accès aux méthodes de Number |
| Diamond | `new ArrayList<>()` | Java infère le type |
| Type erasure | — | Génériques effacés à l'exécution |
| Primitifs | `List<int>` interdit | Utiliser `List<Integer>` |
