# Java — Exceptions : try/catch/finally, Checked vs Unchecked, Custom Exceptions

## 1. Qu'est-ce qu'une exception ?

Une **exception** est un événement anormal qui survient pendant l'exécution d'un programme et interrompt le flux normal d'exécution. Java utilise un mécanisme de gestion d'exceptions robuste basé sur des objets.

```
Throwable
├── Error            — Erreurs JVM graves (ne pas attraper)
│   ├── OutOfMemoryError
│   ├── StackOverflowError
│   └── AssertionError
│
└── Exception        — Exceptions gérables
    ├── RuntimeException       — UNCHECKED (pas d'obligation de gérer)
    │   ├── NullPointerException
    │   ├── ArrayIndexOutOfBoundsException
    │   ├── ClassCastException
    │   ├── ArithmeticException       (division par zéro)
    │   ├── NumberFormatException
    │   ├── IllegalArgumentException
    │   ├── IllegalStateException
    │   └── UnsupportedOperationException
    │
    └── IOException            — CHECKED (obligation de gérer)
        ├── FileNotFoundException
        ├── SQLException
        └── ParseException
```

## 2. try / catch / finally — Syntaxe de base

```java
import java.io.*;

public class TryCatch {
    public static void main(String[] args) {

        // --- try / catch simple ---
        try {
            int resultat = 10 / 0;          // ArithmeticException
            System.out.println(resultat);    // jamais exécuté
        } catch (ArithmeticException e) {
            System.out.println("Division par zéro : " + e.getMessage());
        }

        // --- Plusieurs catch ---
        String[] tab = {"hello", "world", null};
        try {
            for (int i = 0; i < 5; i++) {    // ArrayIndexOutOfBoundsException possible
                System.out.println(tab[i].toUpperCase());  // NullPointerException possible
            }
        } catch (ArrayIndexOutOfBoundsException e) {
            System.out.println("Index hors limites : " + e.getMessage());
        } catch (NullPointerException e) {
            System.out.println("Référence null trouvée");
        } catch (Exception e) {
            // Attrape toutes les exceptions restantes (toujours en dernier)
            System.out.println("Exception inattendue : " + e.getMessage());
        }

        // --- Multi-catch (Java 7+) ---
        try {
            String s = null;
            int n = Integer.parseInt(s);     // NumberFormatException
        } catch (NumberFormatException | NullPointerException e) {
            System.out.println("Erreur de parsing ou null : " + e.getClass().getSimpleName());
        }

        // --- finally : toujours exécuté ---
        java.util.Scanner scanner = null;
        try {
            scanner = new java.util.Scanner(System.in);
            // opérations avec scanner
        } catch (Exception e) {
            System.out.println("Erreur : " + e.getMessage());
        } finally {
            if (scanner != null) {
                scanner.close();  // toujours fermer la ressource
            }
            System.out.println("finally toujours exécuté, même si exception ou return");
        }

        // --- try sans catch (avec finally seulement) ---
        try {
            System.out.println("Code qui peut échouer");
        } finally {
            System.out.println("Nettoyage dans finally");
        }
    }
}
```

## 3. Checked vs Unchecked Exceptions

```java
import java.io.*;
import java.nio.file.*;

public class CheckedUnchecked {

    // --- CHECKED : le compilateur FORCE la gestion ---
    // Méthode 1 : attraper l'exception
    public static String lireFichier_v1(String path) {
        try {
            return Files.readString(Path.of(path));
        } catch (IOException e) {
            System.out.println("Impossible de lire : " + e.getMessage());
            return null;
        }
    }

    // Méthode 2 : propager l'exception avec throws
    public static String lireFichier_v2(String path) throws IOException {
        return Files.readString(Path.of(path));
        // L'appelant DOIT gérer IOException
    }

    // Propagation en chaîne
    public static void traiter(String path) throws IOException {
        String contenu = lireFichier_v2(path);  // propagé
        System.out.println(contenu.substring(0, 100));
    }

    // --- UNCHECKED : pas d'obligation ---
    public static int diviser(int a, int b) {
        // Pas besoin de declare ArithmeticException (unchecked)
        if (b == 0) throw new IllegalArgumentException("Le diviseur ne peut pas être 0");
        return a / b;
    }

    public static void main(String[] args) {
        // Appel de méthode checked : OBLIGÉ de gérer
        try {
            String contenu = lireFichier_v2("fichier.txt");
        } catch (IOException e) {
            System.out.println("Fichier introuvable");
        }

        // Appel de méthode unchecked : pas obligatoire (mais recommandé)
        System.out.println(diviser(10, 2));  // 5
        // diviser(10, 0);  // IllegalArgumentException si on appelle sans vérification

        // Exception enchaînée (chaining)
        try {
            lireFichier_v2("inexistant.txt");
        } catch (IOException e) {
            // Envelopper dans une RuntimeException pour éviter de propager checked
            throw new RuntimeException("Erreur de lecture du fichier de config", e);
            // Le paramètre 'e' est la cause originale : accessible via getCause()
        }
    }
}
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Dans IntelliJ, écrire `Files.readString(Path.of("test.txt"))` sans try/catch. Montrer l'erreur de compilation rouge "Unhandled exception: java.io.IOException". Utiliser le quick-fix IntelliJ (Alt+Entrée) pour ajouter automatiquement le try/catch.
> **Expliquer :** Expliquer la différence entre checked (le compilateur oblige à gérer) et unchecked (facultatif mais recommandé). Insister sur le fait que les checked exceptions représentent des erreurs "attendues" (fichier absent, réseau indisponible), et les unchecked représentent des bugs de programmation.
---

## 4. Exceptions personnalisées

```java
// Exception non vérifiée (hérite de RuntimeException)
public class SoldeInsuffisantException extends RuntimeException {

    private final double montantDemande;
    private final double soldeActuel;

    public SoldeInsuffisantException(double montantDemande, double soldeActuel) {
        super(String.format(
            "Solde insuffisant : demande %.2f€, disponible %.2f€",
            montantDemande, soldeActuel));
        this.montantDemande = montantDemande;
        this.soldeActuel    = soldeActuel;
    }

    public double getMontantDemande() { return montantDemande; }
    public double getSoldeActuel()    { return soldeActuel; }
}

// Exception vérifiée (hérite de Exception)
public class CompteInexistantException extends Exception {

    private final String numeroCompte;

    public CompteInexistantException(String numero) {
        super("Compte introuvable : " + numero);
        this.numeroCompte = numero;
    }

    // Constructeur avec cause
    public CompteInexistantException(String numero, Throwable cause) {
        super("Compte introuvable : " + numero, cause);
        this.numeroCompte = numero;
    }

    public String getNumeroCompte() { return numeroCompte; }
}

// Hiérarchie d'exceptions métier
public class AppException extends RuntimeException {
    public AppException(String message) { super(message); }
    public AppException(String message, Throwable cause) { super(message, cause); }
}

public class ValidationException extends AppException {
    private final String champ;
    private final Object valeur;

    public ValidationException(String champ, Object valeur, String message) {
        super("Validation échouée pour '" + champ + "' (valeur: " + valeur + "): " + message);
        this.champ  = champ;
        this.valeur = valeur;
    }

    public String getChamp()  { return champ; }
    public Object getValeur() { return valeur; }
}

public class NotFoundException extends AppException {
    public NotFoundException(String ressource, Object id) {
        super(ressource + " introuvable avec l'id : " + id);
    }
}
```

```java
// Utilisation des exceptions personnalisées
public class ServiceBancaire {

    private java.util.Map<String, Double> comptes = new java.util.HashMap<>();

    public void creerCompte(String numero, double soldeInitial) {
        if (numero == null || numero.isBlank()) {
            throw new ValidationException("numero", numero, "ne peut pas être vide");
        }
        if (soldeInitial < 0) {
            throw new ValidationException("soldeInitial", soldeInitial, "doit être positif");
        }
        comptes.put(numero, soldeInitial);
    }

    public double consulterSolde(String numero) throws CompteInexistantException {
        Double solde = comptes.get(numero);
        if (solde == null) {
            throw new CompteInexistantException(numero);
        }
        return solde;
    }

    public void virer(String source, String dest, double montant)
            throws CompteInexistantException {

        double soldeSource = consulterSolde(source);  // propagée
        Double soldeDest   = comptes.get(dest);
        if (soldeDest == null) {
            throw new CompteInexistantException(dest);
        }

        if (montant > soldeSource) {
            throw new SoldeInsuffisantException(montant, soldeSource);  // unchecked
        }

        comptes.put(source, soldeSource - montant);
        comptes.put(dest, soldeDest + montant);
    }

    public static void main(String[] args) {
        ServiceBancaire service = new ServiceBancaire();

        try {
            service.creerCompte("C001", 1000);
            service.creerCompte("C002", 500);

            System.out.println("Solde C001 : " + service.consulterSolde("C001"));

            service.virer("C001", "C002", 200);
            System.out.println("Après virement de 200€ :");
            System.out.println("C001 : " + service.consulterSolde("C001"));
            System.out.println("C002 : " + service.consulterSolde("C002"));

            // Virement impossible (solde insuffisant)
            service.virer("C001", "C002", 10000);

        } catch (CompteInexistantException e) {
            System.out.println("Compte introuvable : " + e.getNumeroCompte());
        } catch (SoldeInsuffisantException e) {
            System.out.printf("Erreur : demande %.2f€, disponible %.2f€%n",
                e.getMontantDemande(), e.getSoldeActuel());
        } catch (ValidationException e) {
            System.out.println("Validation : " + e.getMessage());
        }

        // Tester la validation
        try {
            service.creerCompte("", 100);  // ValidationException
        } catch (ValidationException e) {
            System.out.println(e.getMessage());
        }
    }
}
```

## 5. throw et throws

```java
public class ThrowDemo {

    // throws : déclare que la méthode peut lancer ces exceptions (checked)
    public static void validerAge(int age) throws IllegalArgumentException {
        if (age < 0 || age > 150) {
            throw new IllegalArgumentException("Age invalide : " + age);
        }
    }

    // throws multiple
    public static void traiterFichier(String path)
            throws java.io.IOException, IllegalArgumentException {
        if (path == null) throw new IllegalArgumentException("Path ne peut pas être null");
        // ... traitement fichier (peut lancer IOException)
    }

    // Re-throw : attraper, enrichir, et relancer
    public static int lireEntier(String s) {
        try {
            return Integer.parseInt(s);
        } catch (NumberFormatException e) {
            throw new IllegalArgumentException(
                "'" + s + "' n'est pas un entier valide", e);  // cause originale conservée
        }
    }

    public static void main(String[] args) {
        // throw crée et lance l'exception
        try {
            validerAge(-5);
        } catch (IllegalArgumentException e) {
            System.out.println(e.getMessage());  // "Age invalide : -5"
        }

        try {
            lireEntier("abc");
        } catch (IllegalArgumentException e) {
            System.out.println(e.getMessage());
            System.out.println("Cause : " + e.getCause().getMessage());
        }

        // L'exception peut traverser plusieurs niveaux d'appels
        try {
            methodeA();
        } catch (RuntimeException e) {
            System.out.println("Attrapée dans main");
            e.printStackTrace();  // affiche le stack trace complet
        }
    }

    static void methodeA() { methodeB(); }
    static void methodeB() { methodeC(); }
    static void methodeC() {
        throw new RuntimeException("Lancée depuis methodeC");
    }
}
```

## 6. try-with-resources (Java 7+)

```java
import java.io.*;
import java.nio.file.*;

public class TryWithResources {
    public static void main(String[] args) {

        // Avant Java 7 : gestion manuelle des ressources
        BufferedReader reader = null;
        try {
            reader = new BufferedReader(new FileReader("fichier.txt"));
            String ligne;
            while ((ligne = reader.readLine()) != null) {
                System.out.println(ligne);
            }
        } catch (IOException e) {
            e.printStackTrace();
        } finally {
            if (reader != null) {
                try {
                    reader.close();  // peut aussi lancer IOException !
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }

        // Avec try-with-resources : fermeture automatique (implémente AutoCloseable)
        try (BufferedReader br = new BufferedReader(new FileReader("fichier.txt"))) {
            String ligne;
            while ((ligne = br.readLine()) != null) {
                System.out.println(ligne);
            }
        } catch (IOException e) {
            System.out.println("Fichier introuvable : " + e.getMessage());
        }
        // br.close() est appelé AUTOMATIQUEMENT, même en cas d'exception

        // Plusieurs ressources (fermées dans l'ordre inverse d'ouverture)
        try (
            FileInputStream fis = new FileInputStream("source.txt");
            FileOutputStream fos = new FileOutputStream("dest.txt")
        ) {
            byte[] buffer = new byte[1024];
            int nbOctets;
            while ((nbOctets = fis.read(buffer)) != -1) {
                fos.write(buffer, 0, nbOctets);
            }
        } catch (IOException e) {
            System.out.println("Erreur de copie : " + e.getMessage());
        }

        // Implémenter AutoCloseable pour ses propres ressources
        try (MaRessource r = new MaRessource("connexion-db")) {
            r.utiliser();
        } catch (Exception e) {
            System.out.println("Erreur : " + e.getMessage());
        }
        // "Fermeture de connexion-db" affiché automatiquement
    }
}

class MaRessource implements AutoCloseable {
    private final String nom;

    public MaRessource(String nom) {
        this.nom = nom;
        System.out.println("Ouverture de " + nom);
    }

    public void utiliser() {
        System.out.println("Utilisation de " + nom);
    }

    @Override
    public void close() {
        System.out.println("Fermeture de " + nom);
    }
}
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Dans IntelliJ, montrer un `FileNotFoundException` en ouvrant un fichier inexistant. Montrer le stack trace dans la console. Puis corriger avec `try-with-resources`. Montrer aussi la fenêtre "Run → Debug" avec l'exception mise en surbrillance.
> **Expliquer :** Expliquer l'importance des try-with-resources pour éviter les fuites de ressources (file handles, connexions DB, etc.). Montrer que sans `finally` approprié, les ressources peuvent rester ouvertes même après une exception.
---

## 7. Bonnes pratiques

```java
public class BonnesPratiquesExceptions {

    // ✓ Capturer l'exception la plus spécifique possible
    public static void bonExemple(String s) {
        try {
            int n = Integer.parseInt(s);
        } catch (NumberFormatException e) {  // ✓ spécifique
            System.out.println("Pas un nombre");
        }
    }

    // ✗ Ne jamais attraper Exception ou Throwable silencieusement
    public static void mauvaisExemple(String s) {
        try {
            int n = Integer.parseInt(s);
        } catch (Exception e) {  // ✗ trop large
            // ✗ corps vide : l'erreur est avalée silencieusement !
        }
    }

    // ✓ Logger l'exception
    public static void avecLogging(String s) {
        try {
            int n = Integer.parseInt(s);
        } catch (NumberFormatException e) {
            System.err.println("Erreur de parsing : " + e.getMessage());
            // En production : logger.error("Erreur de parsing", e);
        }
    }

    // ✓ Ne pas utiliser les exceptions pour le contrôle de flux
    // ✗ Version anti-pattern
    public static boolean contientElementMauvais(int[] tab, int valeur) {
        try {
            for (int i = 0; ; i++) {
                if (tab[i] == valeur) return true;
            }
        } catch (ArrayIndexOutOfBoundsException e) {
            return false;
        }
    }

    // ✓ Version correcte
    public static boolean contientElement(int[] tab, int valeur) {
        for (int n : tab) {
            if (n == valeur) return true;
        }
        return false;
    }

    // ✓ Toujours préserver la cause originale
    public static void avecCause() throws RuntimeException {
        try {
            throw new java.io.IOException("Erreur réseau");
        } catch (java.io.IOException e) {
            throw new RuntimeException("Impossible de récupérer les données", e);
            //                                                                  ↑ cause conservée
        }
    }
}
```

## Récapitulatif

| Concept | À retenir |
|---------|-----------|
| `try/catch` | Entoure le code risqué, attrape l'exception |
| `finally` | Toujours exécuté (nettoyage de ressources) |
| `try-with-resources` | Fermeture automatique (AutoCloseable) |
| Checked | Hérite d'Exception, compilation oblige à gérer |
| Unchecked | Hérite de RuntimeException, facultatif |
| `throw` | Lance une exception |
| `throws` | Déclare les exceptions propagées |
| Exception personnalisée | Hériter de RuntimeException ou Exception |
| Chaining | Conserver la cause avec `new Ex(msg, cause)` |
| Anti-pattern | Exception vide, catch(Exception), flux par exceptions |
