# Java — I/O Fichiers : Files, BufferedReader, NIO2 Path, try-with-resources

## 1. Deux APIs Java pour les fichiers

Java propose deux APIs pour la manipulation de fichiers :

| API | Classes principales | Version | Recommandation |
|-----|--------------------|---------|--------------------|
| **Classic I/O** | `File`, `FileReader`, `FileWriter`, `BufferedReader`... | Java 1.0+ | Encore très utilisée |
| **NIO2** | `Path`, `Files`, `Paths` | Java 7+ | **Préférer pour du nouveau code** |

## 2. NIO2 — L'API moderne (java.nio.file)

### Path — Représenter un chemin

```java
import java.nio.file.*;

public class PathDemo {
    public static void main(String[] args) {

        // Créer un Path (ne vérifie pas que le fichier existe)
        Path p1 = Path.of("/home/user/documents/rapport.txt");  // Java 11+
        Path p2 = Paths.get("/home/user/documents/rapport.txt"); // Java 7+
        Path p3 = Path.of("/home", "user", "documents", "rapport.txt"); // combiné

        // Sur Windows
        Path win = Path.of("C:\\Users\\user\\Documents\\rapport.txt");
        // Ou avec des slashes (portable)
        Path win2 = Path.of("C:/Users/user/Documents/rapport.txt");

        // Chemin relatif
        Path relatif = Path.of("documents/rapport.txt");
        Path courant  = Path.of("rapport.txt");

        // --- Infos sur le chemin ---
        System.out.println(p1.getFileName());   // rapport.txt
        System.out.println(p1.getParent());     // /home/user/documents
        System.out.println(p1.getRoot());       // /
        System.out.println(p1.getNameCount());  // 4
        System.out.println(p1.getName(0));      // home
        System.out.println(p1.getName(2));      // documents

        // Normalisation et résolution
        Path base = Path.of("/home/user");
        Path fichier = base.resolve("documents/rapport.txt");
        System.out.println(fichier);  // /home/user/documents/rapport.txt

        Path absolu = relatif.toAbsolutePath();
        System.out.println(absolu);

        // Comparaison
        System.out.println(p1.equals(p2));           // true
        System.out.println(p1.startsWith("/home"));  // true
        System.out.println(p1.endsWith("rapport.txt")); // true

        // Chemin relatif entre deux chemins
        Path from = Path.of("/home/user");
        Path to   = Path.of("/home/user/documents/rapport.txt");
        System.out.println(from.relativize(to));  // documents/rapport.txt
    }
}
```

### Files — Opérations sur les fichiers

```java
import java.nio.file.*;
import java.nio.charset.*;
import java.util.*;
import java.io.*;

public class FilesDemo {
    public static void main(String[] args) throws IOException {

        Path dossier = Path.of("test-fichiers");
        Path fichier  = dossier.resolve("exemple.txt");

        // --- Création ---
        Files.createDirectories(dossier);         // crée le dossier et ses parents
        Files.createFile(fichier);                // crée le fichier vide
        // Files.createTempFile("prefix", ".txt"); // fichier temporaire

        // --- Écriture ---
        // Écrire une String directement
        Files.writeString(fichier, "Première ligne\nDeuxième ligne\nTroisième ligne");

        // Écrire une liste de lignes
        List<String> lignes = List.of("Ligne 1", "Ligne 2", "Ligne 3");
        Files.write(fichier, lignes, StandardCharsets.UTF_8,
                    StandardOpenOption.CREATE,
                    StandardOpenOption.TRUNCATE_EXISTING);

        // Append (ajouter à la fin)
        Files.writeString(fichier, "\nLigne ajoutée", StandardOpenOption.APPEND);

        // --- Lecture ---
        // Lire tout en une String
        String contenu = Files.readString(fichier);
        System.out.println(contenu);

        // Lire toutes les lignes en List
        List<String> toutesLignes = Files.readAllLines(fichier, StandardCharsets.UTF_8);
        toutesLignes.forEach(System.out::println);

        // Lire octet par octet (binaire)
        byte[] octets = Files.readAllBytes(fichier);
        System.out.println("Taille : " + octets.length + " octets");

        // Stream de lignes (lazy, pour grands fichiers)
        try (var stream = Files.lines(fichier)) {
            stream.filter(l -> l.startsWith("Ligne"))
                  .forEach(System.out::println);
        }

        // --- Informations ---
        System.out.println(Files.exists(fichier));         // true
        System.out.println(Files.isRegularFile(fichier));  // true
        System.out.println(Files.isDirectory(dossier));    // true
        System.out.println(Files.size(fichier));           // taille en octets
        System.out.println(Files.getLastModifiedTime(fichier));

        // --- Copie et déplacement ---
        Path copie = dossier.resolve("copie.txt");
        Files.copy(fichier, copie, StandardCopyOption.REPLACE_EXISTING);

        Path destination = dossier.resolve("renomme.txt");
        Files.move(copie, destination, StandardCopyOption.REPLACE_EXISTING);

        // --- Suppression ---
        Files.delete(destination);           // lève exception si n'existe pas
        Files.deleteIfExists(destination);   // ne lève pas d'exception

        // --- Lister un dossier ---
        try (var stream = Files.list(dossier)) {
            stream.forEach(p -> System.out.println(p.getFileName()));
        }

        // Parcours récursif
        try (var walk = Files.walk(dossier)) {
            walk.filter(Files::isRegularFile)
                .filter(p -> p.toString().endsWith(".txt"))
                .forEach(System.out::println);
        }

        // --- Nettoyage ---
        Files.deleteIfExists(fichier);
        Files.deleteIfExists(dossier);
    }
}
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Dans IntelliJ, exécuter le programme `FilesDemo`, puis naviguer dans le panneau "Project" pour montrer les fichiers créés dans le dossier du projet. Ouvrir `exemple.txt` dans l'éditeur pour vérifier le contenu.
> **Expliquer :** Expliquer les `StandardOpenOption` (CREATE, APPEND, TRUNCATE_EXISTING), les `StandardCopyOption` (REPLACE_EXISTING, ATOMIC_MOVE), et l'encodage UTF-8 obligatoire pour les caractères français. Montrer aussi ce qui se passe si on essaie de lire un fichier inexistant sans vérification (`NoSuchFileException`).
---

## 3. BufferedReader et BufferedWriter — Lecture/Écriture ligne par ligne

```java
import java.io.*;
import java.nio.charset.*;
import java.nio.file.*;

public class BufferedIODemo {
    public static void main(String[] args) {

        // --- Écriture avec BufferedWriter ---
        Path fichier = Path.of("sortie.txt");

        try (BufferedWriter writer = Files.newBufferedWriter(fichier, StandardCharsets.UTF_8)) {
            writer.write("Première ligne");
            writer.newLine();  // saut de ligne portable (\n ou \r\n selon l'OS)
            writer.write("Deuxième ligne");
            writer.newLine();
            writer.write("Troisième ligne");
        } catch (IOException e) {
            System.err.println("Erreur d'écriture : " + e.getMessage());
        }

        // --- Lecture avec BufferedReader ---
        try (BufferedReader reader = Files.newBufferedReader(fichier, StandardCharsets.UTF_8)) {
            String ligne;
            int numLigne = 1;
            while ((ligne = reader.readLine()) != null) {
                System.out.printf("%3d: %s%n", numLigne++, ligne);
            }
        } catch (IOException e) {
            System.err.println("Erreur de lecture : " + e.getMessage());
        }

        // --- PrintWriter : impression formatée ---
        try (PrintWriter pw = new PrintWriter(
                Files.newBufferedWriter(Path.of("rapport.txt")))) {
            pw.println("=== Rapport ===");
            pw.printf("Date : %s%n", java.time.LocalDate.now());
            pw.printf("%-20s %10s%n", "Produit", "Quantité");
            pw.printf("%-20s %10d%n", "Clavier", 150);
            pw.printf("%-20s %10d%n", "Souris", 220);
        } catch (IOException e) {
            e.printStackTrace();
        }

        // --- FileReader / FileWriter (moins recommandé : pas de charset explicite) ---
        try (BufferedReader br = new BufferedReader(new FileReader("sortie.txt"))) {
            br.lines().forEach(System.out::println);
        } catch (IOException e) {
            e.printStackTrace();
        }

        // Nettoyage
        try {
            Files.deleteIfExists(fichier);
            Files.deleteIfExists(Path.of("rapport.txt"));
        } catch (IOException e) { e.printStackTrace(); }
    }
}
```

## 4. Lecture de fichiers CSV

```java
import java.io.*;
import java.nio.file.*;
import java.util.*;

public class CSVReader {

    record Etudiant(String nom, String prenom, int age, double note) {}

    // Lecture d'un CSV simple
    public static List<Etudiant> lireCSV(Path fichier) throws IOException {
        List<Etudiant> etudiants = new ArrayList<>();

        try (BufferedReader reader = Files.newBufferedReader(fichier)) {
            String ligne = reader.readLine();  // ignorer l'en-tête
            System.out.println("En-tête : " + ligne);

            while ((ligne = reader.readLine()) != null) {
                if (ligne.isBlank()) continue;

                String[] colonnes = ligne.split(",");
                if (colonnes.length != 4) continue;

                try {
                    etudiants.add(new Etudiant(
                        colonnes[0].trim(),
                        colonnes[1].trim(),
                        Integer.parseInt(colonnes[2].trim()),
                        Double.parseDouble(colonnes[3].trim())
                    ));
                } catch (NumberFormatException e) {
                    System.err.println("Ligne invalide : " + ligne);
                }
            }
        }
        return etudiants;
    }

    // Écriture d'un CSV
    public static void ecrireCSV(Path fichier, List<Etudiant> etudiants) throws IOException {
        try (BufferedWriter writer = Files.newBufferedWriter(fichier)) {
            writer.write("nom,prenom,age,note");
            writer.newLine();

            for (Etudiant e : etudiants) {
                writer.write(String.format("%s,%s,%d,%.2f",
                    e.nom(), e.prenom(), e.age(), e.note()));
                writer.newLine();
            }
        }
    }

    public static void main(String[] args) throws IOException {
        // Créer un fichier de test
        Path test = Path.of("etudiants.csv");
        Files.writeString(test,
            "nom,prenom,age,note\n" +
            "Dupont,Alice,22,15.5\n" +
            "Martin,Bob,21,13.0\n" +
            "Durand,Charlie,23,17.5\n"
        );

        List<Etudiant> etudiants = lireCSV(test);
        etudiants.forEach(e ->
            System.out.printf("%-10s %-10s %2d ans  note: %.1f%n",
                e.nom(), e.prenom(), e.age(), e.note())
        );

        // Calcul de la moyenne
        double moyenne = etudiants.stream()
                .mapToDouble(Etudiant::note)
                .average()
                .orElse(0);
        System.out.printf("Moyenne : %.2f%n", moyenne);

        // Écrire un CSV trié par note
        etudiants.sort(Comparator.comparingDouble(Etudiant::note).reversed());
        ecrireCSV(Path.of("etudiants_tries.csv"), etudiants);

        Files.deleteIfExists(test);
        Files.deleteIfExists(Path.of("etudiants_tries.csv"));
    }
}
```

## 5. Lecture de fichiers de configuration (Properties)

```java
import java.io.*;
import java.nio.file.*;
import java.util.*;

public class PropertiesDemo {
    public static void main(String[] args) throws IOException {

        // Créer un fichier .properties
        Path propsFile = Path.of("app.properties");
        Files.writeString(propsFile,
            "# Configuration de l'application\n" +
            "app.name=MonApplication\n" +
            "app.version=1.0.0\n" +
            "db.host=localhost\n" +
            "db.port=5432\n" +
            "db.name=ma_base\n"
        );

        // Lire les propriétés
        Properties props = new Properties();
        try (InputStream input = Files.newInputStream(propsFile)) {
            props.load(input);
        }

        System.out.println(props.getProperty("app.name"));            // "MonApplication"
        System.out.println(props.getProperty("db.port"));             // "5432"
        System.out.println(props.getProperty("absent", "défaut"));    // "défaut"

        // Modifier et sauvegarder
        props.setProperty("app.debug", "true");
        try (OutputStream output = Files.newOutputStream(propsFile)) {
            props.store(output, "Configuration mise à jour");
        }

        // Afficher toutes les propriétés
        props.forEach((k, v) -> System.out.println(k + " = " + v));

        Files.deleteIfExists(propsFile);
    }
}
```

## 6. Sérialisation JSON avec Jackson (bibliothèque externe)

```java
// Dépendance Maven :
// <dependency>
//     <groupId>com.fasterxml.jackson.core</groupId>
//     <artifactId>jackson-databind</artifactId>
//     <version>2.17.0</version>
// </dependency>

import com.fasterxml.jackson.databind.*;
import com.fasterxml.jackson.core.type.*;
import java.io.*;
import java.nio.file.*;
import java.util.*;

public class JacksonDemo {

    record Produit(String nom, double prix, int stock) {}

    public static void main(String[] args) throws Exception {
        ObjectMapper mapper = new ObjectMapper();

        // Java → JSON
        Produit produit = new Produit("Clavier", 79.99, 10);
        String json = mapper.writeValueAsString(produit);
        System.out.println(json);
        // {"nom":"Clavier","prix":79.99,"stock":10}

        // JSON → Java
        String jsonStr = """
            {"nom":"Souris","prix":29.99,"stock":25}
            """;
        Produit p = mapper.readValue(jsonStr, Produit.class);
        System.out.println(p);

        // Liste → JSON
        List<Produit> produits = List.of(
            new Produit("Clavier", 79.99, 10),
            new Produit("Souris", 29.99, 25)
        );
        String jsonListe = mapper.writerWithDefaultPrettyPrinter()
                                 .writeValueAsString(produits);
        System.out.println(jsonListe);

        // JSON → Liste
        List<Produit> listeObtenue = mapper.readValue(jsonListe,
            new TypeReference<List<Produit>>() {});
        listeObtenue.forEach(System.out::println);

        // Écriture dans un fichier
        mapper.writeValue(new File("produits.json"), produits);

        // Lecture depuis un fichier
        List<Produit> depuisFichier = mapper.readValue(
            new File("produits.json"),
            new TypeReference<List<Produit>>() {}
        );
        depuisFichier.forEach(System.out::println);

        Files.deleteIfExists(Path.of("produits.json"));
    }
}
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Montrer dans IntelliJ comment ajouter Jackson à un projet Maven via le `pom.xml`. Montrer l'autocomplétion des dépendances. Exécuter `JacksonDemo` et montrer le JSON produit dans la console. Ouvrir le fichier `produits.json` généré dans le panneau de fichiers d'IntelliJ et montrer la coloration syntaxique JSON.
> **Expliquer :** Expliquer la différence entre la sérialisation Java native (ObjectOutputStream, peu utilisée) et la sérialisation JSON avec Jackson (la norme en web/API). Mentionner que Spring Boot inclut Jackson par défaut.
---

## 7. Travailler avec les chemins de manière portable

```java
import java.nio.file.*;
import java.io.*;
import java.net.*;

public class CheminsPortables {
    public static void main(String[] args) throws Exception {

        // --- Ressources dans le classpath (dans le JAR) ---
        // Accéder aux fichiers dans src/main/resources/
        InputStream is = CheminsPortables.class
                .getClassLoader()
                .getResourceAsStream("config.properties");

        if (is != null) {
            java.util.Properties props = new java.util.Properties();
            props.load(is);
            System.out.println(props);
        }

        // --- Chemin du répertoire courant ---
        Path courant = Path.of("").toAbsolutePath();
        System.out.println("Répertoire courant : " + courant);

        // --- Dossier home de l'utilisateur ---
        Path home = Path.of(System.getProperty("user.home"));
        System.out.println("Home : " + home);

        // --- Dossier temporaire système ---
        Path tmp = Path.of(System.getProperty("java.io.tmpdir"));
        Path fichierTemp = Files.createTempFile(tmp, "app-", ".tmp");
        System.out.println("Temp : " + fichierTemp);
        Files.deleteIfExists(fichierTemp);

        // --- Séparateur de chemin ---
        System.out.println(File.separator);       // / sur Linux/Mac, \ sur Windows
        System.out.println(File.pathSeparator);   // : sur Linux/Mac, ; sur Windows

        // Path est TOUJOURS portable (gère le séparateur automatiquement)
        Path portable = Path.of("a", "b", "c", "fichier.txt");
        System.out.println(portable);  // a/b/c/fichier.txt (ou a\b\c\fichier.txt)
    }
}
```

## Récapitulatif

| Tâche | API recommandée | Exemple |
|-------|-----------------|---------|
| Lire tout un fichier | `Files.readString()` | `Files.readString(Path.of("f.txt"))` |
| Lire ligne par ligne | `Files.lines()` ou `BufferedReader` | `Files.lines(p).forEach(...)` |
| Écrire un fichier | `Files.writeString()` | `Files.writeString(p, contenu)` |
| Copier/Déplacer | `Files.copy()`, `Files.move()` | `Files.copy(src, dst, REPLACE_EXISTING)` |
| Lister un dossier | `Files.list()`, `Files.walk()` | `Files.list(p).filter(...)` |
| Ressources fermées auto | `try-with-resources` | `try (var r = ...) {}` |
| Chemin portable | `Path.of()` | `Path.of("dossier", "fichier.txt")` |
| CSV simple | `BufferedReader` + `split(",")` | Voir exemple ci-dessus |
| JSON | Jackson `ObjectMapper` | `mapper.writeValueAsString(obj)` |
