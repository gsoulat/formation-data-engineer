# Java — Introduction : JVM, JDK/JRE, Compilation et Types Primitifs

## 1. Pourquoi Java ?

Java est l'un des langages les plus utilisés au monde depuis sa création en 1995 par Sun Microsystems (aujourd'hui Oracle). Ses points forts :

- **"Write Once, Run Anywhere"** : le code compilé tourne sur n'importe quelle machine disposant d'une JVM
- **Langage fortement typé** : les erreurs de type sont détectées à la compilation
- **Orienté objet** : tout (ou presque) est un objet
- **Garbage Collector** : gestion automatique de la mémoire
- **Écosystème immense** : Maven Central, Spring, Hibernate, Kafka, etc.
- **Utilisé partout** : applications d'entreprise, Android, big data (Hadoop, Spark), microservices

## 2. JDK, JRE, JVM — Comprendre la différence

```
┌─────────────────────────────────────────┐
│               JDK                        │
│  (Java Development Kit)                  │
│  ┌───────────────────────────────────┐  │
│  │             JRE                    │  │
│  │  (Java Runtime Environment)        │  │
│  │  ┌─────────────────────────────┐  │  │
│  │  │          JVM                 │  │  │
│  │  │  (Java Virtual Machine)      │  │  │
│  │  └─────────────────────────────┘  │  │
│  │  + Bibliothèques standard (rt.jar) │  │
│  └───────────────────────────────────┘  │
│  + javac (compilateur)                   │
│  + javadoc, jar, jshell, etc.            │
└─────────────────────────────────────────┘
```

- **JVM** : machine virtuelle qui exécute le bytecode Java. Elle isole le programme du système d'exploitation.
- **JRE** : JVM + bibliothèques standard. Suffisant pour *exécuter* un programme Java.
- **JDK** : JRE + outils de développement (compilateur `javac`, etc.). Nécessaire pour *développer*.

### Le processus de compilation

```
MonProgramme.java  →  [javac]  →  MonProgramme.class  →  [JVM]  →  Exécution
  (code source)      compilateur    (bytecode)           machine
```

Le bytecode (`.class`) est **indépendant de la plateforme** : c'est la JVM qui fait le travail d'adaptation au système.

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Terminal ouvert, taper `java -version` et `javac -version` pour montrer les versions installées
> **Expliquer :** Montrer la différence entre `java` (pour exécuter) et `javac` (pour compiler). Insister sur le numéro de version LTS (21 recommandé).
---

## 3. Premier programme Java

### Structure minimale

```java
// Fichier : HelloWorld.java
// Le nom du fichier DOIT correspondre au nom de la classe publique

public class HelloWorld {

    // Point d'entrée du programme
    // public : accessible de partout
    // static : appartient à la classe, pas à une instance
    // void   : ne retourne rien
    // main   : nom obligatoire pour le point d'entrée
    // String[] args : arguments passés en ligne de commande
    public static void main(String[] args) {
        System.out.println("Hello, World!");
        // System     : classe de la bibliothèque standard
        // out        : flux de sortie standard (PrintStream)
        // println    : affiche + saut de ligne
    }
}
```

### Compilation et exécution

```bash
# Compiler : génère HelloWorld.class
javac HelloWorld.java

# Exécuter
java HelloWorld

# Depuis Java 11 : exécution directe sans compilation explicite
java HelloWorld.java
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Créer `HelloWorld.java` dans un terminal, le compiler avec `javac`, puis l'exécuter avec `java`. Montrer le fichier `.class` généré avec `ls -la`.
> **Expliquer :** Bien insister sur le workflow compilation → exécution. Montrer ce qui se passe si on oublie le point-virgule (erreur de compilation). Montrer aussi l'erreur si le nom de fichier ne correspond pas au nom de classe.
---

### Utilisation de JShell (Java REPL)

```bash
# JShell permet de tester du code Java interactivement (Java 9+)
jshell

# Dans JShell :
jshell> System.out.println("Bonjour")
Bonjour

jshell> int x = 42
x ==> 42

jshell> x * 2
$3 ==> 84

jshell> /exit
```

## 4. Types primitifs

Java distingue deux catégories de types : les **types primitifs** (valeurs directes) et les **types référence** (objets).

### Les 8 types primitifs

| Type | Taille | Valeur min | Valeur max | Valeur par défaut | Exemple |
|------|--------|-----------|-----------|------------------|---------|
| `byte` | 8 bits | -128 | 127 | 0 | `byte b = 100;` |
| `short` | 16 bits | -32 768 | 32 767 | 0 | `short s = 1000;` |
| `int` | 32 bits | -2 147 483 648 | 2 147 483 647 | 0 | `int i = 42;` |
| `long` | 64 bits | -9.2 × 10¹⁸ | 9.2 × 10¹⁸ | 0L | `long l = 100L;` |
| `float` | 32 bits | ~1.4 × 10⁻⁴⁵ | ~3.4 × 10³⁸ | 0.0f | `float f = 3.14f;` |
| `double` | 64 bits | ~4.9 × 10⁻³²⁴ | ~1.8 × 10³⁰⁸ | 0.0 | `double d = 3.14;` |
| `char` | 16 bits | '\u0000' | '\uFFFF' | '\u0000' | `char c = 'A';` |
| `boolean` | 1 bit | — | — | false | `boolean ok = true;` |

```java
public class TypesPrimitifs {
    public static void main(String[] args) {

        // --- Entiers ---
        byte age = 25;
        short annee = 2024;
        int population = 2_000_000;    // underscore autorisé pour lisibilité (Java 7+)
        long distanceTerre = 384_400_000L;  // suffixe L obligatoire pour long

        // --- Flottants ---
        float prix = 9.99f;     // suffixe f obligatoire
        double pi = 3.141592653589793;  // double = précision par défaut

        // Attention aux flottants !
        System.out.println(0.1 + 0.2);  // Affiche 0.30000000000000004 (!)
        // Pour de la finance, utiliser BigDecimal

        // --- Caractère ---
        char lettre = 'A';
        char unicode = '\u00E9';  // é
        int codeASCII = lettre;   // char est un entier : affiche 65
        System.out.println(codeASCII);

        // --- Booléen ---
        boolean estMajeur = age >= 18;
        boolean estValide = true;

        // --- Affichage ---
        System.out.println("Age : " + age);
        System.out.println("Est majeur : " + estMajeur);
        System.out.printf("Pi vaut environ %.2f%n", pi);  // formatage

        // --- Limites ---
        System.out.println("Max int : " + Integer.MAX_VALUE);    // 2147483647
        System.out.println("Min int : " + Integer.MIN_VALUE);    // -2147483648
        System.out.println("Max long : " + Long.MAX_VALUE);

        // --- Overflow (débordement) ---
        int max = Integer.MAX_VALUE;
        System.out.println(max + 1);  // Affiche -2147483648 ! (overflow silencieux)
    }
}
```

## 5. Types référence et Wrapper classes

Les types primitifs ont des équivalents objet appelés **wrapper classes** :

| Primitif | Wrapper |
|----------|---------|
| `int` | `Integer` |
| `long` | `Long` |
| `double` | `Double` |
| `boolean` | `Boolean` |
| `char` | `Character` |
| `byte` | `Byte` |
| `short` | `Short` |
| `float` | `Float` |

```java
// Autoboxing : conversion automatique primitif → wrapper
Integer nb = 42;           // équivalent à Integer.valueOf(42)
int valeur = nb;           // unboxing automatique

// Méthodes utiles des wrappers
int parsed = Integer.parseInt("123");   // String → int
String str = Integer.toString(456);    // int → String
int max = Integer.max(10, 20);         // 20
String binaire = Integer.toBinaryString(42);  // "101010"

// Comparaison : attention aux pièges !
Integer a = 127;
Integer b = 127;
System.out.println(a == b);       // true  (cache JVM pour -128 à 127)

Integer c = 128;
Integer d = 128;
System.out.println(c == d);       // false ! (objets différents)
System.out.println(c.equals(d));  // true  (toujours utiliser equals pour les objets)
```

## 6. String — La chaîne de caractères

`String` est une classe (type référence), mais elle bénéficie d'un traitement spécial en Java :

```java
public class StringDemo {
    public static void main(String[] args) {

        // Déclaration
        String nom = "Alice";
        String prenom = new String("Bob");  // rare, préférer la syntaxe littérale

        // Concaténation
        String complet = nom + " " + prenom;    // "Alice Bob"
        String complet2 = nom.concat(" ").concat(prenom);  // même résultat

        // Méthodes essentielles
        System.out.println(nom.length());           // 5
        System.out.println(nom.toUpperCase());       // "ALICE"
        System.out.println(nom.toLowerCase());       // "alice"
        System.out.println(nom.charAt(0));           // 'A'
        System.out.println(nom.substring(1));        // "lice"
        System.out.println(nom.substring(1, 3));     // "li"
        System.out.println(nom.contains("lic"));     // true
        System.out.println(nom.startsWith("Al"));    // true
        System.out.println(nom.endsWith("ce"));      // true
        System.out.println(nom.indexOf("i"));        // 2
        System.out.println(nom.replace("l", "L"));  // "ALice"
        System.out.println("  hello  ".trim());      // "hello"
        System.out.println("  hello  ".strip());     // "hello" (Java 11+, supporte Unicode)
        System.out.println(nom.isEmpty());           // false
        System.out.println("".isBlank());            // true (Java 11+)

        // Comparaison
        String s1 = "hello";
        String s2 = "hello";
        String s3 = new String("hello");

        System.out.println(s1 == s2);        // true (même référence dans le pool)
        System.out.println(s1 == s3);        // false (objets différents)
        System.out.println(s1.equals(s3));   // true (toujours utiliser equals !)
        System.out.println(s1.equalsIgnoreCase("HELLO")); // true

        // String.format et formatted (Java 15+)
        String msg = String.format("Bonjour %s, vous avez %d ans", "Alice", 30);
        String msg2 = "Bonjour %s, vous avez %d ans".formatted("Alice", 30); // Java 15+

        // Text blocks (Java 15+)
        String json = """
                {
                    "nom": "Alice",
                    "age": 30
                }
                """;
        System.out.println(json);

        // Split
        String csv = "pomme,banane,cerise";
        String[] fruits = csv.split(",");
        for (String fruit : fruits) {
            System.out.println(fruit);
        }

        // StringBuilder : pour les concaténations en boucle (performance)
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < 5; i++) {
            sb.append("item").append(i).append(", ");
        }
        System.out.println(sb.toString()); // "item0, item1, item2, item3, item4, "
    }
}
```

## 7. Déclaration de variables et portée

```java
public class Variables {

    // Variable de classe (champ statique) : portée = toute la classe
    static int compteur = 0;

    // Variable d'instance : portée = objet
    String nom;

    public static void main(String[] args) {

        // Variable locale : portée = bloc où elle est déclarée
        int x = 10;

        {
            // Bloc interne
            int y = 20;
            System.out.println(x + y);  // OK : x visible ici
        }
        // System.out.println(y);  // ERREUR de compilation : y hors portée

        // Inférence de type avec var (Java 10+)
        var message = "Bonjour";    // type inféré : String
        var nombre = 42;            // type inféré : int
        var liste = new java.util.ArrayList<String>();  // type inféré

        // Constantes : final
        final double TAUX_TVA = 0.20;
        // TAUX_TVA = 0.19;  // ERREUR : variable finale ne peut pas être modifiée

        // Constante de classe : static final (convention : MAJUSCULES_AVEC_TIRET)
        // Voir : Math.PI, Integer.MAX_VALUE
    }
}
```

## 8. Opérateurs

```java
public class Operateurs {
    public static void main(String[] args) {

        // --- Arithmétiques ---
        int a = 17, b = 5;
        System.out.println(a + b);   // 22
        System.out.println(a - b);   // 12
        System.out.println(a * b);   // 85
        System.out.println(a / b);   // 3  (division entière !)
        System.out.println(a % b);   // 2  (modulo)
        System.out.println((double) a / b);  // 3.4 (cast)

        // Incrément / décrément
        int n = 5;
        System.out.println(n++);  // 5 (post-incrément : utilise puis incrémente)
        System.out.println(n);    // 6
        System.out.println(++n);  // 7 (pré-incrément : incrémente puis utilise)

        // --- Assignation composée ---
        int x = 10;
        x += 5;   // x = x + 5 = 15
        x -= 3;   // x = x - 3 = 12
        x *= 2;   // x = x * 2 = 24
        x /= 4;   // x = x / 4 = 6
        x %= 4;   // x = x % 4 = 2

        // --- Comparaison ---
        System.out.println(a == b);  // false
        System.out.println(a != b);  // true
        System.out.println(a > b);   // true
        System.out.println(a >= b);  // true
        System.out.println(a < b);   // false
        System.out.println(a <= b);  // false

        // --- Logiques ---
        boolean t = true, f = false;
        System.out.println(t && f);  // false (ET)
        System.out.println(t || f);  // true  (OU)
        System.out.println(!t);      // false (NON)

        // Court-circuit : && et || n'évaluent pas la 2ème expression si inutile
        int zero = 0;
        if (zero != 0 && 10 / zero > 0) {  // 10/zero jamais évalué
            System.out.println("ne sera jamais affiché");
        }

        // --- Ternaire ---
        int age = 20;
        String statut = age >= 18 ? "majeur" : "mineur";
        System.out.println(statut);  // "majeur"

        // --- Bitwise (bit à bit) ---
        int flags = 0b1010;         // 10 en binaire
        int masque = 0b0110;        // 6 en binaire
        System.out.println(flags & masque);   // 0010 = 2  (AND)
        System.out.println(flags | masque);   // 1110 = 14 (OR)
        System.out.println(flags ^ masque);   // 1100 = 12 (XOR)
        System.out.println(~flags);           // complément à 1
        System.out.println(flags << 1);       // décalage gauche = * 2
        System.out.println(flags >> 1);       // décalage droite = / 2
    }
}
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Dans IntelliJ IDEA, créer un nouveau projet Java, écrire `TypesPrimitifs.java`, et exécuter en cliquant sur le bouton vert. Montrer la console de sortie avec les résultats.
> **Expliquer :** Montrer l'autocomplétion d'IntelliJ, les erreurs soulignées en rouge, et le débogueur (placer un breakpoint sur une ligne, lancer en mode Debug, observer les valeurs des variables dans le panel "Variables").
---

## 9. Conversion de types (Casting)

```java
public class Casting {
    public static void main(String[] args) {

        // --- Widening (élargissement) : automatique, sans perte ---
        int i = 100;
        long l = i;       // int → long : automatique
        double d = l;     // long → double : automatique

        // Ordre : byte → short → int → long → float → double

        // --- Narrowing (rétrécissement) : explicite, perte possible ---
        double prix = 9.99;
        int prixInt = (int) prix;   // cast explicite : perd la partie décimale
        System.out.println(prixInt); // 9 (troncature, pas arrondi !)

        long bigNumber = 3_000_000_000L;
        int smallNumber = (int) bigNumber;  // overflow ! résultat imprévisible

        // --- Conversion String ↔ primitif ---
        String s = "42";
        int parsed = Integer.parseInt(s);
        double parsedDouble = Double.parseDouble("3.14");

        String fromInt = String.valueOf(42);          // "42"
        String fromDouble = String.valueOf(3.14);     // "3.14"
        String fromBool = String.valueOf(true);       // "true"

        // --- Vérification de type ---
        Object obj = "Hello";
        if (obj instanceof String) {
            String str = (String) obj;  // cast après vérification
            System.out.println(str.length());
        }

        // Pattern matching instanceof (Java 16+)
        if (obj instanceof String str) {  // cast intégré dans instanceof
            System.out.println(str.length());
        }
    }
}
```

## 10. Entrées utilisateur avec Scanner

```java
import java.util.Scanner;

public class EntreeUtilisateur {
    public static void main(String[] args) {

        Scanner scanner = new Scanner(System.in);

        System.out.print("Entrez votre nom : ");
        String nom = scanner.nextLine();

        System.out.print("Entrez votre age : ");
        int age = scanner.nextInt();
        scanner.nextLine();  // Consommer le saut de ligne résiduel

        System.out.print("Entrez votre taille (m) : ");
        double taille = scanner.nextDouble();
        scanner.nextLine();

        System.out.printf("Bonjour %s, vous avez %d ans et mesurez %.2f m%n",
                nom, age, taille);

        // Lecture robuste avec gestion d'erreur
        System.out.print("Entrez un nombre : ");
        if (scanner.hasNextInt()) {
            int nb = scanner.nextInt();
            System.out.println("Vous avez entré : " + nb);
        } else {
            System.out.println("Ce n'est pas un entier !");
        }

        scanner.close();  // Fermer le scanner (bonne pratique)
    }
}
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Exécuter le programme `EntreeUtilisateur` dans le terminal IntelliJ, saisir des valeurs interactivement. Montrer aussi ce qui se passe si on entre un texte à la place d'un entier (InputMismatchException).
> **Expliquer :** Expliquer le flux stdin/stdout, pourquoi on doit consommer le `\n` résiduel après `nextInt()`, et pourquoi il faut fermer le scanner.
---

## Récapitulatif

| Concept | À retenir |
|---------|-----------|
| JVM | Exécute le bytecode, indépendante de la plateforme |
| JDK | Tout ce qu'il faut pour développer (inclut JRE + JVM) |
| Compilation | `javac MonFichier.java` → `MonFichier.class` |
| Exécution | `java MonClasse` (sans `.class`) |
| Types primitifs | 8 types : byte, short, int, long, float, double, char, boolean |
| String | Type référence, immuable, comparer avec `.equals()` jamais `==` |
| var | Inférence de type locale (Java 10+) |
| cast | `(type)` pour conversion rétrécissante, risque de perte |

## Exercice de la section

Créez un programme `Calculatrice.java` qui :
1. Demande deux nombres à l'utilisateur
2. Demande l'opération souhaitée (+, -, *, /)
3. Affiche le résultat formaté avec 2 décimales
4. Gère la division par zéro avec un message d'erreur approprié
