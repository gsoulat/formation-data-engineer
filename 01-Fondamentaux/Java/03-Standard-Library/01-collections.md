# Java — Collections : List, Set, Map, ArrayList, HashMap, Iterator, Streams API

## 1. La hiérarchie des Collections Java

```
java.lang.Iterable
└── java.util.Collection<E>
    ├── List<E>          — ordonné, doublons autorisés
    │   ├── ArrayList    — tableau dynamique (accès rapide par index)
    │   ├── LinkedList   — liste doublement chaînée (insertion rapide)
    │   └── Vector       — ArrayList thread-safe (ancien, préférer ArrayList)
    │
    ├── Set<E>           — non ordonné, sans doublon
    │   ├── HashSet      — basé sur HashMap (le plus rapide)
    │   ├── LinkedHashSet — conserve l'ordre d'insertion
    │   └── TreeSet      — trié (basé sur arbre rouge-noir)
    │
    └── Queue<E>         — file (FIFO)
        ├── LinkedList
        ├── PriorityQueue — file de priorité
        └── Deque<E>     — file double (FIFO + LIFO)
            └── ArrayDeque

java.util.Map<K, V>      — association clé → valeur (pas Collection)
    ├── HashMap          — le plus courant, pas ordonné
    ├── LinkedHashMap    — conserve l'ordre d'insertion
    ├── TreeMap          — trié par clé
    └── Hashtable        — ancien, thread-safe, préférer HashMap
```

## 2. List — ArrayList

```java
import java.util.*;

public class ArrayListDemo {
    public static void main(String[] args) {

        // --- Création ---
        ArrayList<String> fruits = new ArrayList<>();
        ArrayList<String> fruits2 = new ArrayList<>(10);  // capacité initiale
        List<String> immutable = List.of("pomme", "banane", "cerise");  // non modifiable

        // Depuis une collection existante
        ArrayList<String> copie = new ArrayList<>(immutable);

        // --- Ajout ---
        fruits.add("pomme");           // ajout à la fin
        fruits.add("banane");
        fruits.add("cerise");
        fruits.add(1, "fraise");       // insert à l'index 1
        fruits.addAll(List.of("kiwi", "mangue"));  // ajout multiple

        System.out.println(fruits);    // [pomme, fraise, banane, cerise, kiwi, mangue]

        // --- Accès ---
        System.out.println(fruits.get(0));     // "pomme"
        System.out.println(fruits.size());     // 6
        System.out.println(fruits.isEmpty());  // false

        // --- Modification ---
        fruits.set(0, "orange");      // remplace à l'index 0

        // --- Suppression ---
        fruits.remove("banane");       // par valeur
        fruits.remove(2);              // par index
        fruits.removeIf(f -> f.startsWith("k"));  // avec prédicat (Java 8+)

        // --- Recherche ---
        System.out.println(fruits.contains("pomme"));   // false (remplacé)
        System.out.println(fruits.indexOf("cerise"));   // 1 ou -1 si absent
        System.out.println(fruits.lastIndexOf("cerise"));

        // --- Tri ---
        Collections.sort(fruits);           // tri naturel (alphabétique)
        fruits.sort(Comparator.comparingInt(String::length)); // tri par longueur

        // --- Iteration ---
        // for-each
        for (String f : fruits) {
            System.out.println(f);
        }

        // for avec index
        for (int i = 0; i < fruits.size(); i++) {
            System.out.println(i + " : " + fruits.get(i));
        }

        // forEach avec lambda (Java 8+)
        fruits.forEach(f -> System.out.println(f.toUpperCase()));
        fruits.forEach(System.out::println);  // référence de méthode

        // --- Sous-liste ---
        List<String> sous = fruits.subList(1, 3);  // [index 1, index 3[

        // --- Conversion ---
        String[] tableau = fruits.toArray(new String[0]);
        List<String> depuisTableau = Arrays.asList("a", "b", "c");  // taille fixe !

        // --- Vider ---
        fruits.clear();
        System.out.println(fruits.isEmpty());  // true

        // --- Collections.unmodifiableList ---
        List<String> lecture = Collections.unmodifiableList(new ArrayList<>(List.of("a", "b")));
        // lecture.add("c");  // UnsupportedOperationException
    }
}
```

## 3. LinkedList — Usages spécifiques

```java
import java.util.*;

public class LinkedListDemo {
    public static void main(String[] args) {

        // LinkedList implémente List ET Deque
        LinkedList<String> ll = new LinkedList<>();

        // Opérations sur la tête/queue (O(1))
        ll.addFirst("premier");
        ll.addLast("dernier");
        ll.add("milieu");

        System.out.println(ll.getFirst());  // "premier"
        System.out.println(ll.getLast());   // "dernier"
        System.out.println(ll.peekFirst()); // idem mais ne lève pas d'exception si vide

        ll.removeFirst();
        ll.removeLast();

        // Utilisation comme Pile (Stack - LIFO)
        Deque<String> pile = new ArrayDeque<>();  // préférer ArrayDeque à Stack
        pile.push("a");
        pile.push("b");
        pile.push("c");
        System.out.println(pile.pop());   // "c" (dernier entré, premier sorti)

        // Utilisation comme File (Queue - FIFO)
        Queue<String> file = new LinkedList<>();
        file.offer("premier");  // ajoute en queue
        file.offer("second");
        file.offer("troisième");
        System.out.println(file.poll());  // "premier" (premier entré, premier sorti)
        System.out.println(file.peek());  // "second" (regarde sans supprimer)
    }
}
```

## 4. Set — HashSet, LinkedHashSet, TreeSet

```java
import java.util.*;

public class SetDemo {
    public static void main(String[] args) {

        // --- HashSet : le plus rapide, pas d'ordre ---
        Set<String> hashSet = new HashSet<>();
        hashSet.add("banana");
        hashSet.add("apple");
        hashSet.add("cherry");
        hashSet.add("apple");   // doublon ignoré silencieusement

        System.out.println(hashSet.size());  // 3 (pas 4)
        System.out.println(hashSet);         // ordre imprévisible

        // --- LinkedHashSet : conserve l'ordre d'insertion ---
        Set<String> linkedSet = new LinkedHashSet<>();
        linkedSet.add("banana");
        linkedSet.add("apple");
        linkedSet.add("cherry");
        System.out.println(linkedSet);  // [banana, apple, cherry]

        // --- TreeSet : trié ---
        Set<String> treeSet = new TreeSet<>();
        treeSet.add("banana");
        treeSet.add("apple");
        treeSet.add("cherry");
        System.out.println(treeSet);  // [apple, banana, cherry]

        // TreeSet avec Comparator
        TreeSet<String> parLongueur = new TreeSet<>(Comparator.comparingInt(String::length)
                                                              .thenComparing(Comparator.naturalOrder()));
        parLongueur.addAll(List.of("banana", "apple", "cherry", "fig", "kiwi"));
        System.out.println(parLongueur);  // [fig, kiwi, apple, banana, cherry]

        // --- Opérations ensemblistes ---
        Set<Integer> A = new HashSet<>(Set.of(1, 2, 3, 4, 5));
        Set<Integer> B = new HashSet<>(Set.of(3, 4, 5, 6, 7));

        // Union : A ∪ B
        Set<Integer> union = new HashSet<>(A);
        union.addAll(B);
        System.out.println("Union : " + new TreeSet<>(union));  // [1,2,3,4,5,6,7]

        // Intersection : A ∩ B
        Set<Integer> inter = new HashSet<>(A);
        inter.retainAll(B);
        System.out.println("Intersection : " + new TreeSet<>(inter));  // [3,4,5]

        // Différence : A \ B
        Set<Integer> diff = new HashSet<>(A);
        diff.removeAll(B);
        System.out.println("Différence : " + new TreeSet<>(diff));  // [1,2]

        // --- Vérifications ---
        System.out.println(A.contains(3));        // true
        System.out.println(A.containsAll(B));     // false
        System.out.println(A.containsAll(Set.of(1, 2)));  // true
    }
}
```

## 5. Map — HashMap, LinkedHashMap, TreeMap

```java
import java.util.*;

public class MapDemo {
    public static void main(String[] args) {

        // --- HashMap ---
        Map<String, Integer> ages = new HashMap<>();
        ages.put("Alice", 30);
        ages.put("Bob", 25);
        ages.put("Charlie", 35);
        ages.put("Alice", 31);  // met à jour la valeur existante

        // --- Accès ---
        System.out.println(ages.get("Alice"));         // 31
        System.out.println(ages.get("Zeynep"));        // null (clé absente)
        System.out.println(ages.getOrDefault("Zeynep", 0));  // 0 (valeur par défaut)

        // --- Vérifications ---
        System.out.println(ages.containsKey("Bob"));      // true
        System.out.println(ages.containsValue(25));       // true
        System.out.println(ages.size());                  // 3

        // --- Suppression ---
        ages.remove("Bob");
        ages.remove("Charlie", 35);  // supprime seulement si valeur correspond

        // --- putIfAbsent : n'écrase pas si la clé existe ---
        ages.putIfAbsent("David", 28);
        ages.putIfAbsent("Alice", 99);  // Alice existe déjà → pas de changement
        System.out.println(ages.get("Alice"));  // 31

        // --- computeIfAbsent / computeIfPresent ---
        // Utile pour des valeurs calculées ou des collections imbriquées
        Map<String, List<String>> groupes = new HashMap<>();
        groupes.computeIfAbsent("Math", k -> new ArrayList<>()).add("Alice");
        groupes.computeIfAbsent("Math", k -> new ArrayList<>()).add("Bob");
        groupes.computeIfAbsent("Science", k -> new ArrayList<>()).add("Charlie");
        System.out.println(groupes);  // {Math=[Alice, Bob], Science=[Charlie]}

        // --- merge : fusionner des valeurs ---
        Map<String, Integer> compteur = new HashMap<>();
        String[] mots = {"pomme", "banane", "pomme", "cerise", "banane", "pomme"};
        for (String mot : mots) {
            compteur.merge(mot, 1, Integer::sum);
            // Si la clé n'existe pas : valeur = 1
            // Si elle existe : valeur = ancienneValeur + 1
        }
        System.out.println(compteur);  // {cerise=1, banane=2, pomme=3}

        // --- Iteration ---
        // Sur les clés
        for (String cle : ages.keySet()) {
            System.out.println(cle + " → " + ages.get(cle));
        }

        // Sur les valeurs
        for (int age : ages.values()) {
            System.out.println(age);
        }

        // Sur les entrées (le plus efficace)
        for (Map.Entry<String, Integer> entry : ages.entrySet()) {
            System.out.println(entry.getKey() + " = " + entry.getValue());
        }

        // forEach avec lambda (Java 8+)
        ages.forEach((nom, age) -> System.out.printf("%-10s : %d%n", nom, age));

        // --- LinkedHashMap : conserve l'ordre d'insertion ---
        Map<String, Integer> ordered = new LinkedHashMap<>();
        ordered.put("z", 3);
        ordered.put("a", 1);
        ordered.put("m", 2);
        System.out.println(ordered);  // {z=3, a=1, m=2} (ordre d'insertion)

        // --- TreeMap : trié par clé ---
        Map<String, Integer> sorted = new TreeMap<>(ages);
        System.out.println(sorted);  // clés triées alphabétiquement

        // TreeMap avec Comparator
        TreeMap<String, Integer> reverseSorted = new TreeMap<>(Comparator.reverseOrder());
        reverseSorted.putAll(ages);

        // --- Opérations utiles ---
        ages.replaceAll((cle, valeur) -> valeur + 1);  // incrémenter toutes les valeurs
    }
}
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Dans IntelliJ, montrer le débogueur avec une `HashMap` et une `TreeMap`. Dans le panel Variables, montrer que la HashMap n'a pas d'ordre prévisible, alors que la TreeMap est triée par clé. Agrandir les objets pour voir leur structure interne.
> **Expliquer :** Expliquer quand choisir chaque implémentation : HashMap (performance O(1)), LinkedHashMap (ordre d'insertion), TreeMap (ordre naturel, O(log n)). Expliquer aussi l'importance de hashCode()/equals() pour les clés de HashMap.
---

## 6. Iterator

```java
import java.util.*;

public class IteratorDemo {
    public static void main(String[] args) {

        List<String> liste = new ArrayList<>(List.of("a", "b", "c", "d", "e"));

        // Iterator classique
        Iterator<String> it = liste.iterator();
        while (it.hasNext()) {
            String s = it.next();
            System.out.println(s);
        }

        // IMPORTANT : Pour supprimer des éléments pendant l'iteration,
        // utiliser iterator.remove() et PAS liste.remove()
        Iterator<String> it2 = liste.iterator();
        while (it2.hasNext()) {
            String s = it2.next();
            if (s.equals("b") || s.equals("d")) {
                it2.remove();  // ✓ safe
            }
        }
        System.out.println(liste);  // [a, c, e]

        // ✗ NE PAS FAIRE : ConcurrentModificationException !
        // for (String s : liste) {
        //     if (s.equals("a")) liste.remove(s);
        // }

        // ✓ Alternative Java 8+ : removeIf
        liste.removeIf(s -> s.equals("c"));
        System.out.println(liste);  // [a, e]

        // ListIterator : permet de parcourir dans les deux sens
        List<Integer> nums = new ArrayList<>(List.of(1, 2, 3, 4, 5));
        ListIterator<Integer> lit = nums.listIterator(nums.size());

        System.out.print("Inversé : ");
        while (lit.hasPrevious()) {
            System.out.print(lit.previous() + " ");
        }
        System.out.println();  // "Inversé : 5 4 3 2 1"

        // Implémenter Iterable pour ses propres classes
        // (voir l'exemple de classe générique Pile ci-dessous)
    }
}

// Classe Pile iterable
class PileIterable<T> implements Iterable<T> {

    private List<T> elements = new ArrayList<>();

    public void empiler(T e) { elements.add(e); }
    public T depiler()       { return elements.remove(elements.size() - 1); }

    @Override
    public Iterator<T> iterator() {
        // Iteration du sommet vers la base
        return new Iterator<T>() {
            int index = elements.size() - 1;

            @Override
            public boolean hasNext() { return index >= 0; }

            @Override
            public T next() {
                if (!hasNext()) throw new NoSuchElementException();
                return elements.get(index--);
            }
        };
    }
}
```

## 7. Streams API — Introduction

L'API Streams (Java 8+) permet de traiter des collections de façon fonctionnelle et concise.

```java
import java.util.*;
import java.util.stream.*;

public class StreamsIntro {
    public static void main(String[] args) {

        List<Integer> nombres = List.of(1, 2, 3, 4, 5, 6, 7, 8, 9, 10);

        // --- Pipeline de Stream ---
        // 1. Source       : List, Set, tableau, etc.
        // 2. Opérations intermédiaires : lazy, retournent un Stream
        // 3. Opération terminale : déclenche l'exécution, retourne un résultat

        // Exemple simple : nombres pairs, multipliés par 2, triés
        List<Integer> resultat = nombres.stream()
                .filter(n -> n % 2 == 0)      // garde les pairs : [2,4,6,8,10]
                .map(n -> n * 2)               // multiplie par 2 : [4,8,12,16,20]
                .sorted()                      // trie
                .collect(Collectors.toList()); // collecte en List

        System.out.println(resultat);  // [4, 8, 12, 16, 20]

        // --- Opérations intermédiaires ---

        // filter(Predicate) : garde les éléments qui satisfont le prédicat
        List<Integer> pairs = nombres.stream()
                .filter(n -> n % 2 == 0)
                .collect(Collectors.toList());

        // map(Function) : transforme chaque élément
        List<String> strs = nombres.stream()
                .map(n -> "item-" + n)
                .collect(Collectors.toList());

        // mapToInt, mapToLong, mapToDouble : vers primitifs (plus efficace)
        int[] tableauInt = nombres.stream()
                .mapToInt(Integer::intValue)
                .toArray();

        // flatMap : aplatir les streams imbriqués
        List<List<Integer>> nested = List.of(List.of(1, 2), List.of(3, 4), List.of(5));
        List<Integer> flat = nested.stream()
                .flatMap(Collection::stream)
                .collect(Collectors.toList());
        System.out.println(flat);  // [1, 2, 3, 4, 5]

        // distinct : dédoublonnage
        List<Integer> avecDoublons = List.of(1, 2, 2, 3, 3, 3, 4);
        List<Integer> unique = avecDoublons.stream()
                .distinct()
                .collect(Collectors.toList());
        System.out.println(unique);  // [1, 2, 3, 4]

        // limit / skip
        List<Integer> dix = Stream.iterate(1, n -> n + 1)  // 1, 2, 3, ...
                .skip(5)         // sauter les 5 premiers
                .limit(5)        // garder 5 éléments
                .collect(Collectors.toList());
        System.out.println(dix);  // [6, 7, 8, 9, 10]

        // sorted avec Comparator
        List<String> mots = List.of("banane", "pomme", "cerise", "kiwi");
        List<String> triés = mots.stream()
                .sorted(Comparator.comparingInt(String::length))
                .collect(Collectors.toList());
        System.out.println(triés);  // [kiwi, pomme, banane, cerise]

        // peek : pour le débogage (ne consomme pas le stream)
        List<Integer> debug = nombres.stream()
                .filter(n -> n > 5)
                .peek(n -> System.out.print("Filtré: " + n + " "))
                .map(n -> n * 2)
                .collect(Collectors.toList());
        System.out.println("\n" + debug);

        // --- Opérations terminales ---

        // collect : le plus courant
        List<Integer> list = nombres.stream().filter(n -> n > 5).collect(Collectors.toList());
        Set<Integer>  set  = nombres.stream().filter(n -> n > 5).collect(Collectors.toSet());

        // Collectors.joining
        String joined = mots.stream().collect(Collectors.joining(", ", "[", "]"));
        System.out.println(joined);  // [banane, pomme, cerise, kiwi]

        // Collectors.groupingBy
        Map<Integer, List<String>> parLongueur = mots.stream()
                .collect(Collectors.groupingBy(String::length));
        System.out.println(parLongueur);  // {4=[kiwi], 5=[pomme], 6=[banane, cerise]}

        // Collectors.counting
        Map<Integer, Long> nbParLongueur = mots.stream()
                .collect(Collectors.groupingBy(String::length, Collectors.counting()));
        System.out.println(nbParLongueur);  // {4=1, 5=1, 6=2}

        // forEach : pour les effets de bord
        nombres.stream().filter(n -> n > 7).forEach(System.out::println);

        // count
        long nb = nombres.stream().filter(n -> n % 2 == 0).count();
        System.out.println("Pairs : " + nb);  // 5

        // findFirst / findAny
        Optional<Integer> premier = nombres.stream().filter(n -> n > 5).findFirst();
        premier.ifPresent(n -> System.out.println("Premier > 5 : " + n));  // 6

        // min / max
        Optional<Integer> min = nombres.stream().min(Integer::compareTo);
        Optional<Integer> max = nombres.stream().max(Integer::compareTo);
        System.out.println(min.get() + " - " + max.get());  // 1 - 10

        // reduce : agrégation
        int somme = nombres.stream().reduce(0, Integer::sum);
        int produit = nombres.stream().reduce(1, (a, b) -> a * b);
        System.out.println("Somme : " + somme);    // 55
        System.out.println("Produit : " + produit); // 3628800

        // anyMatch / allMatch / noneMatch
        System.out.println(nombres.stream().anyMatch(n -> n > 9));   // true
        System.out.println(nombres.stream().allMatch(n -> n > 0));   // true
        System.out.println(nombres.stream().noneMatch(n -> n > 10)); // true

        // toMap
        Map<String, Integer> longueurs = mots.stream()
                .collect(Collectors.toMap(s -> s, String::length));
        System.out.println(longueurs);

        // --- Streams de primitifs ---
        IntStream.range(0, 5).forEach(i -> System.out.print(i + " "));  // 0 1 2 3 4
        IntStream.rangeClosed(1, 5).sum();    // 15
        DoubleStream.of(1.0, 2.0, 3.0).average().ifPresent(System.out::println);
    }
}
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Montrer en live dans IntelliJ le refactoring d'une boucle for-each classique vers un stream. Écrire d'abord la version impérative (boucle + if + add), puis la réécrire avec `.stream().filter().collect()`. Montrer que les deux produisent le même résultat.
> **Expliquer :** Insister sur le fait que les streams sont **lazy** : les opérations intermédiaires ne s'exécutent que quand une opération terminale est appelée. Montrer avec `peek` que rien ne se passe sans terminal operation.
---

## Récapitulatif des collections

| Collection | Ordre | Doublons | Performance | Cas d'usage |
|------------|-------|----------|-------------|-------------|
| `ArrayList` | Insertion | Oui | get O(1), add O(1) amorti | Liste générale |
| `LinkedList` | Insertion | Oui | add/remove tête O(1) | File, Pile |
| `HashSet` | Aucun | Non | add/contains O(1) | Dédoublonnage |
| `LinkedHashSet` | Insertion | Non | O(1) | Ensemble ordonné |
| `TreeSet` | Trié | Non | O(log n) | Ensemble trié |
| `HashMap` | Aucun | Clés non | get/put O(1) | Association générale |
| `LinkedHashMap` | Insertion | Clés non | O(1) | Cache LRU |
| `TreeMap` | Clé triée | Clés non | O(log n) | Map triée |
| `PriorityQueue` | Priorité | Oui | poll O(log n) | File de priorité |
