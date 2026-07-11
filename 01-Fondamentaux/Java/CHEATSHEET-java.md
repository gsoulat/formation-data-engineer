# Java — Cheatsheet de Référence Rapide

## Types primitifs
```java
byte b = 127;        // 8 bits
short s = 32767;     // 16 bits
int i = 2_147_483_647; // 32 bits
long l = 100L;       // 64 bits
float f = 3.14f;     // 32 bits
double d = 3.14;     // 64 bits
char c = 'A';        // 16 bits Unicode
boolean ok = true;
final int MAX = 100; // constante
var x = 42;          // inférence de type (Java 10+)
```

## String
```java
String s = "hello";
s.length()           // 5
s.toUpperCase()      // "HELLO"
s.contains("ell")    // true
s.substring(1, 3)    // "el"
s.replace("l", "L") // "heLLo"
s.trim()             // supprime espaces
s.strip()            // idem, supporte Unicode (Java 11+)
s.split(",")         // String[]
s.equals("hello")    // ✓ comparer des Strings
String.format("%s %d", "age", 30)
"hello %s".formatted("world") // Java 15+
"""
  text block
  Java 15+
"""
```

## Tableaux
```java
int[] tab = {1, 2, 3};
int[] tab2 = new int[5];       // [0, 0, 0, 0, 0]
tab.length                     // 3 (propriété, pas méthode)
Arrays.sort(tab);
Arrays.toString(tab);           // "[1, 2, 3]"
Arrays.copyOf(tab, tab.length);
int[][] matrice = {{1,2},{3,4}};
```

## Contrôle de flux
```java
// if/else
if (x > 0) { ... } else if (x == 0) { ... } else { ... }
String r = x > 0 ? "pos" : "neg"; // ternaire

// switch expression (Java 14+)
String s = switch (n) {
    case 1 -> "un";
    case 2, 3 -> "deux ou trois";
    default -> "autre";
};

// for
for (int i = 0; i < n; i++) { ... }
for (String item : liste) { ... }  // for-each

// while / do-while
while (condition) { ... }
do { ... } while (condition);

// break / continue
break;          // sort de la boucle
continue;       // itération suivante
```

## Méthodes
```java
public static int addition(int a, int b) { return a + b; }
public void afficher(String... messages) { ... }  // varargs
// Surcharge : même nom, paramètres différents
```

## Classes et POO
```java
public class Animal {
    private String nom;           // encapsulation
    public Animal(String nom) { this.nom = nom; }
    public String getNom() { return nom; }
    public void setNom(String nom) { this.nom = nom; }
    @Override public String toString() { return "Animal[" + nom + "]"; }
    @Override public boolean equals(Object o) { ... }
    @Override public int hashCode() { return Objects.hash(nom); }
    public static int compteur = 0;  // attribut de classe
}
Animal a = new Animal("Rex");

// Héritage
public class Chien extends Animal {
    public Chien(String nom) { super(nom); }
    @Override public void parler() { System.out.println("Woof!"); }
}

// Classe abstraite
public abstract class Forme {
    public abstract double aire();
}

// Interface
public interface Serialisable {
    String serialiser();
    default void log() { System.out.println(serialiser()); }
}

// Record (Java 16+)
public record Point(double x, double y) {}
Point p = new Point(1.0, 2.0);
p.x();  // accesseur

// instanceof pattern matching (Java 16+)
if (obj instanceof String s) { System.out.println(s.length()); }

// Sealed class (Java 17+)
public sealed class Shape permits Circle, Rectangle {}
```

## Génériques
```java
public class Boite<T> { private T valeur; }
public static <T extends Comparable<T>> T max(T a, T b) { ... }
List<? extends Number> lireNombres;    // PECS Producer
List<? super Integer>  ecrireEntiers; // PECS Consumer
```

## Collections
```java
// List
List<String> list = new ArrayList<>();
list.add("a");  list.get(0);  list.size();  list.remove(0);
list.sort(Comparator.naturalOrder());
List<String> immut = List.of("a", "b", "c");

// Map
Map<String, Integer> map = new HashMap<>();
map.put("k", 1);  map.get("k");  map.containsKey("k");
map.getOrDefault("absent", 0);
map.merge("k", 1, Integer::sum);
map.forEach((k, v) -> System.out.println(k + "=" + v));

// Set
Set<String> set = new HashSet<>();
set.add("a");  set.contains("a");
```

## Streams (Java 8+)
```java
list.stream()
    .filter(s -> s.startsWith("A"))
    .map(String::toUpperCase)
    .sorted()
    .limit(5)
    .collect(Collectors.toList());

// Terminaux
.count()
.findFirst() → Optional
.anyMatch(Predicate)   .allMatch()  .noneMatch()
.min(Comparator)       .max()
.reduce(0, Integer::sum)
.forEach(System.out::println)

// Collectors
Collectors.toList()
Collectors.toSet()
Collectors.joining(", ", "[", "]")
Collectors.groupingBy(Function)
Collectors.counting()
Collectors.toMap(keyFunc, valueFunc)

// Streams spécialisés
IntStream.range(0, 10)
IntStream.rangeClosed(1, 10).sum()
```

## Lambda & Method References
```java
// Lambda
(a, b) -> a + b
s -> s.toUpperCase()
() -> System.out.println("hello")
n -> { if (n > 0) return "pos"; else return "neg"; }

// Method references
String::toUpperCase     // instance method (type)
System.out::println     // instance method (objet)
Integer::parseInt       // static method
ArrayList::new          // constructeur
```

## Optional
```java
Optional<String> opt = Optional.ofNullable(valeur);
opt.isPresent()          opt.isEmpty()
opt.get()                // ⚠ lève exception si vide
opt.orElse("défaut")
opt.orElseGet(() -> calculer())
opt.orElseThrow(() -> new RuntimeException())
opt.map(String::length)
opt.filter(s -> s.length() > 3)
opt.ifPresent(System.out::println)
opt.ifPresentOrElse(v -> ..., () -> ...)
```

## Exceptions
```java
try {
    // code risqué
} catch (IOException | SQLException e) {
    System.err.println(e.getMessage());
} finally {
    // toujours exécuté
}

// try-with-resources
try (BufferedReader br = Files.newBufferedReader(path)) {
    br.lines().forEach(System.out::println);
}

// Lancer
throw new IllegalArgumentException("message");

// Exception personnalisée
public class MonException extends RuntimeException {
    public MonException(String msg) { super(msg); }
    public MonException(String msg, Throwable cause) { super(msg, cause); }
}
```

## Fichiers (NIO2)
```java
Path p = Path.of("/chemin/fichier.txt");
Files.writeString(p, "contenu");
String contenu = Files.readString(p);
List<String> lignes = Files.readAllLines(p);
Files.copy(src, dst, StandardCopyOption.REPLACE_EXISTING);
Files.createDirectories(p);
Files.exists(p)  Files.isDirectory(p)  Files.size(p)
try (var stream = Files.lines(p)) { stream.forEach(System.out::println); }
```

## Spring Boot
```java
// Point d'entrée
@SpringBootApplication
public class App { public static void main(String[] a) { SpringApplication.run(App.class, a); } }

// Controller REST
@RestController
@RequestMapping("/api/ressources")
public class MonController {
    @GetMapping                              // GET /api/ressources
    public List<DTO> lister() { ... }

    @GetMapping("/{id}")                     // GET /api/ressources/1
    public ResponseEntity<DTO> trouver(@PathVariable Long id) { ... }

    @PostMapping                             // POST /api/ressources
    public ResponseEntity<DTO> creer(@Valid @RequestBody Request req) { ... }

    @PutMapping("/{id}")                     // PUT /api/ressources/1
    public ResponseEntity<DTO> modifier(@PathVariable Long id, @Valid @RequestBody Request req) { ... }

    @DeleteMapping("/{id}")                  // DELETE /api/ressources/1
    public ResponseEntity<Void> supprimer(@PathVariable Long id) { ... }
}

// Repository JPA
@Repository
public interface MonRepo extends JpaRepository<Entite, Long> {
    List<Entite> findByNom(String nom);
    Page<Entite> findByStatut(String statut, Pageable pageable);
    @Query("SELECT e FROM Entite e WHERE e.actif = true")
    List<Entite> findActifs();
}

// Entité JPA
@Entity @Table(name = "ma_table")
public class MonEntite {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    @Column(nullable = false)
    private String nom;
    @PrePersist void onCreate() { createdAt = LocalDateTime.now(); }
}

// ResponseEntity status codes
ResponseEntity.ok(body)                    // 200
ResponseEntity.created(URI.create(loc))    // 201
ResponseEntity.noContent().build()         // 204
ResponseEntity.badRequest().body(err)      // 400
ResponseEntity.notFound().build()          // 404
```

## Commandes Maven
```bash
mvn compile           # Compiler
mvn test              # Lancer les tests
mvn package           # Créer le JAR
mvn spring-boot:run   # Lancer l'application
java -jar target/app.jar  # Lancer le JAR
```
