# Exercice 1 — Système de Gestion de Bibliothèque (POO)

## Objectif

Concevoir et implémenter un système de gestion de bibliothèque en appliquant les principes de la POO : classes, héritage, interfaces, encapsulation, génériques.

## Durée estimée : 3 à 4 heures

---

## Partie 1 — Modélisation des entités (45 min)

### 1.1 Interface `Empruntable`

Créez l'interface `Empruntable` avec les méthodes :
- `boolean estDisponible()` : retourne true si l'ouvrage peut être emprunté
- `void emprunter(String emprunteur)` : marque l'ouvrage comme emprunté
- `void retourner()` : marque l'ouvrage comme disponible
- `String getEmprunteurActuel()` : retourne null si disponible, sinon le nom

### 1.2 Classe abstraite `Document`

```java
// À compléter
public abstract class Document implements Empruntable {
    // Attributs communs à tous les documents :
    // - id (String, généré automatiquement : "DOC-XXXX")
    // - titre (String)
    // - auteur (String)
    // - anneePublication (int)
    // - emprunteur (String, null si disponible)

    // Constructeur protégé
    // Getters
    // Implémentation de Empruntable
    // Méthode abstraite : String getType()
    // toString() générique
}
```

### 1.3 Sous-classes concrètes

Implémentez ces trois classes qui étendent `Document` :

**`Livre`** :
- Attributs supplémentaires : `isbn` (String), `nbPages` (int)
- `getType()` retourne `"Livre"`
- `toString()` inclut ISBN et nombre de pages

**`Revue`** :
- Attributs supplémentaires : `numeroEdition` (int), `periodicite` (String : "mensuelle", "trimestrielle"...)
- `getType()` retourne `"Revue"`
- Un emprunt d'une revue dure moins longtemps (surcharger le comportement)

**`DVD`** :
- Attributs supplémentaires : `dureeMinutes` (int), `realisateur` (String)
- `getType()` retourne `"DVD"`

---

## Partie 2 — Gestion des membres (30 min)

### 2.1 Classe `Membre`

```java
public class Membre {
    // Attributs :
    // - id (int, auto-incrémenté via static)
    // - nom (String)
    // - prenom (String)
    // - email (String)
    // - documentsEmpruntes (List<Document>)
    // - LIMITE_EMPRUNTS (static final int = 5)

    // Méthodes :
    // - emprunterDocument(Document d) : vérifie la limite et l'empruntabilité
    // - retournerDocument(Document d)
    // - getDocumentsEmpruntes() : copie défensive (List non modifiable)
    // - peutEmprunter() : boolean
    // - toString() avec liste des emprunts en cours
}
```

---

## Partie 3 — Catalogue générique (45 min)

### 3.1 Classe `Catalogue<T extends Document>`

```java
public class Catalogue<T extends Document> {
    // Attributs :
    // - documents (List<T>)
    // - nom (String)

    // Méthodes :
    // - ajouter(T document)
    // - retirer(String id) : boolean
    // - trouverParId(String id) : Optional<T>
    // - rechercherParTitre(String motCle) : List<T>
    // - rechercherParAuteur(String auteur) : List<T>
    // - listerDisponibles() : List<T>
    // - listerEmpruntes() : List<T>
    // - compter() : int
    // - compterDisponibles() : int
    // - afficherStatistiques()
}
```

---

## Partie 4 — Système de bibliothèque (45 min)

### 4.1 Classe `Bibliotheque`

```java
public class Bibliotheque {
    private Catalogue<Document> catalogue;
    private List<Membre> membres;
    private String nom;

    // Méthodes :
    // - inscrireMembre(String nom, String prenom, String email) : Membre
    // - ajouterDocument(Document doc)
    // - emprunter(int idMembre, String idDocument) : boolean (avec vérifications)
    // - retourner(int idMembre, String idDocument) : boolean
    // - rechercherDocuments(String motCle) : List<Document>
    // - getMembresAvecEmprunts() : List<Membre>
    // - getDocumentsEnRetard() : List<Document> (bonus)
    // - genererRapport() : String
}
```

---

## Partie 5 — Programme principal (30 min)

Écrivez une classe `MainBibliotheque` qui :

1. Crée une bibliothèque "Médiathèque de Paris"
2. Ajoute au catalogue :
   - 5 livres (dont 2 du même auteur)
   - 3 revues
   - 2 DVDs
3. Inscrit 3 membres
4. Effectue des emprunts :
   - Membre 1 emprunte 2 livres et 1 DVD
   - Membre 2 emprunte 1 revue
   - Tente d'emprunter un document déjà emprunté → message d'erreur
5. Effectue un retour
6. Affiche le rapport complet

---

## Critères d'évaluation

| Critère | Points |
|---------|--------|
| Interface `Empruntable` correctement définie | 2 |
| Classe abstraite `Document` avec bonne encapsulation | 3 |
| Les 3 sous-classes concrètes | 3 |
| Classe `Membre` avec contrainte d'emprunt | 3 |
| Catalogue générique fonctionnel | 4 |
| Classe `Bibliotheque` complète | 3 |
| Gestion des cas limites (null, déjà emprunté, limite...) | 2 |
| **Total** | **20** |

---

## Correction indicative — Structure des classes

```java
// Empruntable.java
public interface Empruntable {
    boolean estDisponible();
    void emprunter(String emprunteur);
    void retourner();
    String getEmprunteurActuel();
}

// Document.java
public abstract class Document implements Empruntable {
    private static int compteur = 1;

    private final String id;
    private final String titre;
    private final String auteur;
    private final int anneePublication;
    private String emprunteur;

    protected Document(String titre, String auteur, int anneePublication) {
        this.id = String.format("DOC-%04d", compteur++);
        this.titre = titre;
        this.auteur = auteur;
        this.anneePublication = anneePublication;
        this.emprunteur = null;
    }

    @Override
    public boolean estDisponible() { return emprunteur == null; }

    @Override
    public void emprunter(String nom) {
        if (!estDisponible()) throw new IllegalStateException("Déjà emprunté par " + emprunteur);
        this.emprunteur = nom;
    }

    @Override
    public void retourner() { this.emprunteur = null; }

    @Override
    public String getEmprunteurActuel() { return emprunteur; }

    public String getId()       { return id; }
    public String getTitre()    { return titre; }
    public String getAuteur()   { return auteur; }
    public int    getAnnee()    { return anneePublication; }

    public abstract String getType();

    @Override
    public String toString() {
        return String.format("[%s] %s - %s (%d) [%s]",
            id, titre, auteur, anneePublication,
            estDisponible() ? "DISPONIBLE" : "Emprunté par " + emprunteur);
    }
}

// Livre.java
public class Livre extends Document {
    private final String isbn;
    private final int nbPages;

    public Livre(String titre, String auteur, int annee, String isbn, int nbPages) {
        super(titre, auteur, annee);
        this.isbn = isbn;
        this.nbPages = nbPages;
    }

    @Override public String getType() { return "Livre"; }

    @Override
    public String toString() {
        return super.toString() + String.format(" — ISBN: %s, %d pages", isbn, nbPages);
    }
}

// Membre.java
public class Membre {
    private static int compteur = 1;
    private static final int LIMITE_EMPRUNTS = 5;

    private final int id;
    private final String nom;
    private final String prenom;
    private final String email;
    private final List<Document> documentsEmpruntes;

    public Membre(String nom, String prenom, String email) {
        this.id = compteur++;
        this.nom = nom;
        this.prenom = prenom;
        this.email = email;
        this.documentsEmpruntes = new ArrayList<>();
    }

    public boolean peutEmprunter() { return documentsEmpruntes.size() < LIMITE_EMPRUNTS; }

    public boolean emprunterDocument(Document doc) {
        if (!peutEmprunter()) {
            System.out.println("Limite d'emprunts atteinte (" + LIMITE_EMPRUNTS + ")");
            return false;
        }
        if (!doc.estDisponible()) {
            System.out.println("Document déjà emprunté : " + doc.getTitre());
            return false;
        }
        doc.emprunter(nom + " " + prenom);
        documentsEmpruntes.add(doc);
        return true;
    }

    public boolean retournerDocument(Document doc) {
        if (documentsEmpruntes.remove(doc)) {
            doc.retourner();
            return true;
        }
        return false;
    }

    public List<Document> getDocumentsEmpruntes() {
        return Collections.unmodifiableList(documentsEmpruntes);
    }

    public int getId()      { return id; }
    public String getNom()  { return nom + " " + prenom; }
}

// Catalogue.java
public class Catalogue<T extends Document> {
    private final List<T> documents = new ArrayList<>();
    private final String nom;

    public Catalogue(String nom) { this.nom = nom; }

    public void ajouter(T doc) { documents.add(doc); }

    public Optional<T> trouverParId(String id) {
        return documents.stream().filter(d -> d.getId().equals(id)).findFirst();
    }

    public List<T> rechercherParTitre(String motCle) {
        return documents.stream()
            .filter(d -> d.getTitre().toLowerCase().contains(motCle.toLowerCase()))
            .collect(java.util.stream.Collectors.toList());
    }

    public List<T> listerDisponibles() {
        return documents.stream().filter(Document::estDisponible)
            .collect(java.util.stream.Collectors.toList());
    }

    public void afficherStatistiques() {
        System.out.println("=== " + nom + " ===");
        System.out.println("Total : " + documents.size());
        System.out.println("Disponibles : " + listerDisponibles().size());
        System.out.println("Empruntés : " + (documents.size() - listerDisponibles().size()));
    }
}
```
