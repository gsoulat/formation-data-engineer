# Java — Méthodes : Définition, Surcharge, Récursion, Varargs

## 1. Pourquoi des méthodes ?

Les méthodes permettent de :
- **Réutiliser** du code sans le dupliquer
- **Découper** un problème complexe en sous-problèmes
- **Tester** chaque partie indépendamment
- **Nommer** des opérations pour rendre le code lisible

Règle d'or : **une méthode = une responsabilité** (principe de responsabilité unique).

## 2. Anatomie d'une méthode

```java
public class Methodes {

    // Syntaxe :
    // [modificateurs] typeRetour nomMethode([paramètres]) [throws Exception] {
    //     corps
    //     [return valeur;]
    // }

    // Méthode sans retour (void) ni paramètre
    public static void direBonjour() {
        System.out.println("Bonjour !");
    }

    // Méthode avec retour et paramètre
    public static double calculerAire(double rayon) {
        return Math.PI * rayon * rayon;
    }

    // Méthode avec plusieurs paramètres
    public static double calculerIMC(double poids, double taille) {
        return poids / (taille * taille);
    }

    // Méthode retournant un boolean
    public static boolean estPremier(int n) {
        if (n < 2) return false;
        for (int i = 2; i <= Math.sqrt(n); i++) {
            if (n % i == 0) return false;
        }
        return true;
    }

    // Méthode retournant un String
    public static String categorieIMC(double imc) {
        if (imc < 18.5)       return "Insuffisance pondérale";
        else if (imc < 25.0)  return "Poids normal";
        else if (imc < 30.0)  return "Surpoids";
        else                  return "Obésité";
    }

    public static void main(String[] args) {

        // Appel de méthodes
        direBonjour();

        double aire = calculerAire(5.0);
        System.out.printf("Aire du cercle : %.2f%n", aire);

        double imc = calculerIMC(70, 1.75);
        System.out.printf("IMC : %.1f → %s%n", imc, categorieIMC(imc));

        System.out.println(estPremier(17));  // true
        System.out.println(estPremier(18));  // false

        // Les primitifs sont passés par valeur (copie)
        int x = 5;
        doubler(x);
        System.out.println(x);  // 5, inchangé !

        // Les tableaux/objets sont passés par référence (de la copie)
        int[] tab = {1, 2, 3};
        doublerTableau(tab);
        System.out.println(java.util.Arrays.toString(tab));  // [2, 4, 6] modifié !
    }

    // Passage par valeur : la modification ne sort pas de la méthode
    public static void doubler(int n) {
        n = n * 2;  // ne modifie pas la variable appelante
    }

    // Le tableau lui-même n'est pas copié, on reçoit la référence
    public static void doublerTableau(int[] tab) {
        for (int i = 0; i < tab.length; i++) {
            tab[i] = tab[i] * 2;  // modifie le vrai tableau
        }
    }
}
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Dans le débogueur IntelliJ, placer un breakpoint dans `doubler()` et dans `doublerTableau()`. Montrer dans le panel "Variables" que dans le premier cas `x` reste à 5 après l'appel, et dans le second cas le tableau est bien modifié.
> **Expliquer :** Expliquer la différence entre passage par valeur (primitifs) et passage par référence (tableaux et objets). C'est un point souvent mal compris par les débutants.
---

## 3. Portée des variables et shadowing

```java
public class Portee {

    static int x = 10;  // variable de classe

    public static void methodeA() {
        int y = 20;  // variable locale à methodeA
        System.out.println(x);  // 10 : accessible (variable de classe)
        System.out.println(y);  // 20
    }

    public static void methodeB() {
        // System.out.println(y);  // ERREUR : y n'existe pas ici
        System.out.println(x);  // 10

        // Shadowing : variable locale masque la variable de classe
        int x = 100;  // masque le x de classe
        System.out.println(x);  // 100 (locale)
    }

    public static void main(String[] args) {
        methodeA();
        methodeB();

        // Variable de classe toujours accessible
        System.out.println(x);  // 10 (non modifiée par methodeB)
    }
}
```

## 4. Surcharge de méthodes (Overloading)

La surcharge permet d'avoir plusieurs méthodes avec le **même nom** mais des **paramètres différents**.

```java
public class Surcharge {

    // Même nom, paramètres différents (type ou nombre)
    public static int additionner(int a, int b) {
        System.out.println("additionner(int, int)");
        return a + b;
    }

    public static double additionner(double a, double b) {
        System.out.println("additionner(double, double)");
        return a + b;
    }

    public static int additionner(int a, int b, int c) {
        System.out.println("additionner(int, int, int)");
        return a + b + c;
    }

    public static double additionner(int a, double b) {
        System.out.println("additionner(int, double)");
        return a + b;
    }

    // Surcharge utile : afficher différents types
    public static void afficher(int n) {
        System.out.println("Entier : " + n);
    }

    public static void afficher(double d) {
        System.out.println("Réel : " + d);
    }

    public static void afficher(String s) {
        System.out.println("Chaîne : " + s);
    }

    public static void afficher(int[] tab) {
        System.out.println("Tableau : " + java.util.Arrays.toString(tab));
    }

    public static void main(String[] args) {
        // Java choisit automatiquement la bonne version selon les arguments
        System.out.println(additionner(1, 2));         // int, int → 3
        System.out.println(additionner(1.5, 2.5));     // double, double → 4.0
        System.out.println(additionner(1, 2, 3));      // int, int, int → 6
        System.out.println(additionner(1, 2.5));       // int, double → 3.5

        afficher(42);
        afficher(3.14);
        afficher("hello");
        afficher(new int[]{1, 2, 3});

        // Ambiguïté → erreur de compilation
        // additionner(1L, 2L);  // Aucune méthode pour (long, long) → promotion vers double
    }
}
```

### Règles de surcharge

```java
public class ReglesOverload {

    // VALIDE : types différents
    public static void test(int a) {}
    public static void test(String a) {}

    // VALIDE : nombre de paramètres différent
    public static void test(int a, int b) {}

    // VALIDE : ordre des types différent
    public static void test(int a, String b) {}
    public static void test(String a, int b) {}

    // INVALIDE : seul le type de retour diffère → erreur de compilation
    // public static int test(int a) { return a; }
    // public static double test(int a) { return a; }

    // INVALIDE : nom des paramètres seuls → erreur de compilation
    // public static void test(int x) {}   // déjà déclaré ci-dessus
    // public static void test(int y) {}

}
```

## 5. Récursion

Une méthode est récursive quand elle s'appelle elle-même. Elle doit toujours avoir :
1. Un **cas de base** (condition d'arrêt)
2. Un **appel récursif** qui se rapproche du cas de base

```java
public class Recursion {

    // --- Factorielle ---
    // n! = n × (n-1)! avec 0! = 1
    public static long factorielle(int n) {
        // Cas de base
        if (n <= 1) return 1;
        // Appel récursif
        return n * factorielle(n - 1);
    }
    // factorielle(5) = 5 × factorielle(4)
    //                = 5 × 4 × factorielle(3)
    //                = 5 × 4 × 3 × factorielle(2)
    //                = 5 × 4 × 3 × 2 × factorielle(1)
    //                = 5 × 4 × 3 × 2 × 1 = 120

    // --- Fibonacci ---
    // fib(n) = fib(n-1) + fib(n-2) avec fib(0)=0, fib(1)=1
    public static int fibonacci(int n) {
        if (n <= 0) return 0;
        if (n == 1) return 1;
        return fibonacci(n - 1) + fibonacci(n - 2);
        // Attention : très lent pour les grands n (exponentiel) → utiliser memoization
    }

    // Fibonacci avec mémoïsation (programmation dynamique)
    private static long[] memo = new long[100];
    public static long fibonacciMemo(int n) {
        if (n <= 0) return 0;
        if (n == 1) return 1;
        if (memo[n] != 0) return memo[n];  // résultat déjà calculé
        memo[n] = fibonacciMemo(n - 1) + fibonacciMemo(n - 2);
        return memo[n];
    }

    // --- Puissance ---
    public static double puissance(double base, int exposant) {
        if (exposant == 0) return 1;
        if (exposant < 0) return 1.0 / puissance(base, -exposant);
        return base * puissance(base, exposant - 1);
    }

    // --- Somme d'un tableau ---
    public static int somme(int[] tab, int index) {
        if (index == tab.length) return 0;  // cas de base
        return tab[index] + somme(tab, index + 1);
    }

    // --- Palindrome récursif ---
    public static boolean estPalindrome(String s) {
        if (s.length() <= 1) return true;  // cas de base
        if (s.charAt(0) != s.charAt(s.length() - 1)) return false;
        return estPalindrome(s.substring(1, s.length() - 1));
    }

    // --- Tour de Hanoï ---
    // Déplacer n disques de 'source' vers 'destination' via 'auxiliaire'
    public static void hanoi(int n, char source, char destination, char auxiliaire) {
        if (n == 0) return;  // cas de base
        hanoi(n - 1, source, auxiliaire, destination);
        System.out.printf("Déplacer disque %d de %c vers %c%n", n, source, destination);
        hanoi(n - 1, auxiliaire, destination, source);
    }

    public static void main(String[] args) {
        System.out.println("5! = " + factorielle(5));      // 120
        System.out.println("10! = " + factorielle(10));    // 3628800

        System.out.println("fib(10) = " + fibonacci(10));  // 55
        System.out.println("fib(40) = " + fibonacciMemo(40));  // 102334155 (rapide)

        System.out.println("2^10 = " + (int) puissance(2, 10));  // 1024

        int[] tab = {1, 2, 3, 4, 5};
        System.out.println("Somme = " + somme(tab, 0));  // 15

        System.out.println(estPalindrome("radar"));   // true
        System.out.println(estPalindrome("java"));    // false
        System.out.println(estPalindrome("level"));   // true

        System.out.println("\nTour de Hanoï (3 disques) :");
        hanoi(3, 'A', 'C', 'B');
    }
}
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Débogueur IntelliJ avec `factorielle(4)`. Placer un breakpoint dans la méthode, montrer la pile d'appels (call stack) dans le panel "Frames" qui montre les appels imbriqués. Avancer pas à pas pour voir comment la récursion se "dépile".
> **Expliquer :** Expliquer la pile d'exécution (call stack), ce qui se passe pour des valeurs trop grandes (StackOverflowError), et la différence de performance entre fibonacci naïf et memoïsé.
---

## 6. Varargs (nombre variable d'arguments)

```java
public class Varargs {

    // Varargs : le paramètre est traité comme un tableau
    // Doit être le DERNIER paramètre de la méthode
    public static int somme(int... nombres) {
        int total = 0;
        for (int n : nombres) {
            total += n;
        }
        return total;
    }

    // Mélange paramètre normal + varargs
    public static void afficherMessage(String titre, String... lignes) {
        System.out.println("=== " + titre + " ===");
        for (String ligne : lignes) {
            System.out.println("- " + ligne);
        }
    }

    // Varargs de types quelconques
    public static double moyenne(double... valeurs) {
        if (valeurs.length == 0) return 0;
        double total = 0;
        for (double v : valeurs) total += v;
        return total / valeurs.length;
    }

    // Varargs de type Object (accepte tout)
    public static String concatener(Object... elements) {
        StringBuilder sb = new StringBuilder();
        for (Object e : elements) {
            sb.append(e).append(" ");
        }
        return sb.toString().trim();
    }

    public static void main(String[] args) {

        // Appel sans argument
        System.out.println(somme());           // 0

        // Appel avec un argument
        System.out.println(somme(5));           // 5

        // Appel avec plusieurs arguments
        System.out.println(somme(1, 2, 3));     // 6
        System.out.println(somme(1, 2, 3, 4, 5));  // 15

        // Appel avec un tableau existant
        int[] tab = {10, 20, 30};
        System.out.println(somme(tab));         // 60

        // Mélange paramètres
        afficherMessage("Courses", "Lait", "Pain", "Fromage");
        afficherMessage("TODO");  // lignes vide = OK

        System.out.println(moyenne(10, 20, 30, 40));  // 25.0

        System.out.println(concatener("Bonjour", 42, true, 3.14));
        // "Bonjour 42 true 3.14"

        // Varargs et surcharge : attention aux ambiguïtés
        // test(1, 2) → choisit test(int, int) si disponible (plus spécifique)
        tester(1, 2);      // appelle tester(int, int)
        tester(1, 2, 3);   // appelle tester(int...)
    }

    public static void tester(int a, int b) {
        System.out.println("tester(int, int) : " + a + ", " + b);
    }

    public static void tester(int... valeurs) {
        System.out.println("tester(int...) : " + java.util.Arrays.toString(valeurs));
    }
}
```

## 7. Méthodes utilitaires de la bibliothèque Math

```java
public class MathDemo {
    public static void main(String[] args) {

        // Constantes
        System.out.println(Math.PI);   // 3.141592653589793
        System.out.println(Math.E);    // 2.718281828459045

        // Valeur absolue
        System.out.println(Math.abs(-5));    // 5
        System.out.println(Math.abs(-3.7));  // 3.7

        // Arrondi
        System.out.println(Math.round(3.5));  // 4 (arrondi à l'entier le plus proche)
        System.out.println(Math.floor(3.9));  // 3.0 (arrondi vers le bas)
        System.out.println(Math.ceil(3.1));   // 4.0 (arrondi vers le haut)

        // Min / Max
        System.out.println(Math.min(10, 20));  // 10
        System.out.println(Math.max(10, 20));  // 20

        // Puissance et racine
        System.out.println(Math.pow(2, 10));   // 1024.0
        System.out.println(Math.sqrt(144));    // 12.0
        System.out.println(Math.cbrt(27));     // 3.0 (racine cubique)

        // Logarithme
        System.out.println(Math.log(Math.E));  // 1.0 (log naturel)
        System.out.println(Math.log10(100));   // 2.0 (log base 10)

        // Trigonométrie (angles en radians)
        System.out.println(Math.sin(Math.PI / 2));  // 1.0
        System.out.println(Math.cos(0));             // 1.0
        System.out.printf("sin(30°) = %.4f%n", Math.sin(Math.toRadians(30)));  // 0.5

        // Aléatoire (entre 0.0 inclus et 1.0 exclu)
        double rand = Math.random();
        System.out.println(rand);

        // Entier aléatoire entre min et max inclus
        int min = 1, max = 6;
        int de = (int) (Math.random() * (max - min + 1)) + min;
        System.out.println("Dé : " + de);

        // Préférer java.util.Random ou ThreadLocalRandom pour plus de contrôle
        java.util.Random rng = new java.util.Random();
        System.out.println(rng.nextInt(100));      // [0, 99]
        System.out.println(rng.nextInt(1, 101));   // [1, 100] (Java 17+)
        System.out.println(rng.nextDouble());      // [0.0, 1.0[
        System.out.println(rng.nextBoolean());
    }
}
```

## 8. Bonne pratiques pour les méthodes

```java
public class BonnesPratiques {

    // ✓ Nom en camelCase, verbe d'action, explicite
    public static double calculerTaxe(double prixHT, double tauxTVA) {
        return prixHT * tauxTVA;
    }

    // ✗ Nom trop court, pas clair
    public static double calc(double p, double t) {
        return p * t;
    }

    // ✓ Méthode courte, une seule responsabilité
    public static boolean estAdulte(int age) {
        return age >= 18;
    }

    // ✓ Early return pour réduire l'imbrication
    public static String classerNote(int note) {
        if (note < 0 || note > 20) return "Note invalide";
        if (note < 10) return "Insuffisant";
        if (note < 14) return "Assez bien";
        if (note < 16) return "Bien";
        return "Très bien";
    }

    // ✗ Imbrication excessive (hard to read)
    public static String classerNoteMauvais(int note) {
        if (note >= 0 && note <= 20) {
            if (note >= 10) {
                if (note >= 14) {
                    if (note >= 16) {
                        return "Très bien";
                    } else {
                        return "Bien";
                    }
                } else {
                    return "Assez bien";
                }
            } else {
                return "Insuffisant";
            }
        } else {
            return "Note invalide";
        }
    }

    // ✓ Documenter avec Javadoc
    /**
     * Calcule le prix TTC à partir du prix HT.
     *
     * @param prixHT   Le prix hors taxes (doit être positif)
     * @param tauxTVA  Le taux de TVA (ex: 0.20 pour 20%)
     * @return Le prix toutes taxes comprises
     * @throws IllegalArgumentException si prixHT est négatif
     */
    public static double calculerPrixTTC(double prixHT, double tauxTVA) {
        if (prixHT < 0) {
            throw new IllegalArgumentException("Le prix HT ne peut pas être négatif");
        }
        return prixHT * (1 + tauxTVA);
    }

    public static void main(String[] args) {
        System.out.println(classerNote(15));  // "Bien"
        System.out.println(calculerPrixTTC(100, 0.20));  // 120.0

        try {
            calculerPrixTTC(-10, 0.20);
        } catch (IllegalArgumentException e) {
            System.out.println("Erreur : " + e.getMessage());
        }
    }
}
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Dans IntelliJ, montrer la génération automatique de Javadoc : placer le curseur avant une méthode et taper `/**` puis Entrée. IntelliJ génère automatiquement le squelette avec les tags `@param` et `@return`.
> **Expliquer :** Expliquer l'importance de la documentation, comment générer la Javadoc HTML avec `javadoc` en ligne de commande, et comment IntelliJ affiche la Javadoc au survol d'une méthode (Ctrl+Q ou F1).
---

## 9. Méthodes de la classe Arrays et Collections (avant-goût)

```java
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.ArrayList;

public class UtilsDemo {
    public static void main(String[] args) {

        // Arrays.sort() — tri d'un tableau
        int[] nombres = {5, 2, 8, 1, 9, 3};
        Arrays.sort(nombres);
        System.out.println(Arrays.toString(nombres));  // [1, 2, 3, 5, 8, 9]

        // Arrays.sort() sur une partie du tableau
        int[] partiel = {5, 2, 8, 1, 9, 3};
        Arrays.sort(partiel, 1, 4);  // tri de l'index 1 à 3 inclus
        System.out.println(Arrays.toString(partiel));  // [5, 1, 2, 8, 9, 3]

        // Collections.sort() — tri d'une List
        List<String> noms = new ArrayList<>(List.of("Zeynep", "Alice", "Bob", "Charlie"));
        Collections.sort(noms);
        System.out.println(noms);  // [Alice, Bob, Charlie, Zeynep]

        // Tri avec Comparator (lambda — vu plus tard)
        noms.sort((a, b) -> a.length() - b.length());  // tri par longueur
        System.out.println(noms);  // [Bob, Alice, Zeynep, Charlie]

        // Collections.reverse()
        Collections.reverse(noms);
        System.out.println(noms);  // [Charlie, Zeynep, Alice, Bob]

        // Collections.shuffle() — mélange aléatoire
        Collections.shuffle(noms);
        System.out.println(noms);  // ordre aléatoire
    }
}
```

## Récapitulatif

| Concept | Syntaxe | À retenir |
|---------|---------|-----------|
| Méthode statique | `public static type nom(params)` | Liée à la classe, pas à un objet |
| Void | `public static void nom()` | Ne retourne rien |
| Retour multiple | Impossible directement | Retourner un tableau ou un objet |
| Surcharge | Même nom, params différents | Le type de retour seul ne suffit pas |
| Récursion | S'appelle elle-même | Toujours un cas de base ! |
| Varargs | `int... nums` | Dernier paramètre, traité comme tableau |
| Passage params | Primitifs = copie, Objets = référence copiée | Important pour comprendre les mutations |

## Exercices de la section

### Exercice 1 : Calculatrice avec méthodes
Refactoriser la calculatrice du chapitre précédent en créant des méthodes séparées : `additionner`, `soustraire`, `multiplier`, `diviser`. Chaque méthode retourne un `double` et lance une exception si nécessaire.

### Exercice 2 : Récursion — Flocon de Koch
Implémenter (en texte ASCII) une démonstration de la structure récursive du flocon de Koch en affichant `*` répété selon un niveau de récursion donné.

### Exercice 3 : Varargs — Logger
Créer une méthode `log(String niveau, String... messages)` qui affiche les messages précédés du niveau (`[INFO]`, `[WARN]`, `[ERROR]`) avec un timestamp.
