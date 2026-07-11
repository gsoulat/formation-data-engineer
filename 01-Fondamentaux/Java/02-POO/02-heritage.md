# Java POO — Héritage : extends, super, @Override, abstract, final, instanceof

## 1. Principe de l'héritage

L'héritage permet à une classe (**sous-classe** / **classe enfant**) de réutiliser les attributs et méthodes d'une autre classe (**super-classe** / **classe parent**).

```
Animal (parent)
├── attributs : nom, age
├── méthodes  : manger(), dormir(), toString()
│
├── Chien (enfant)
│   ├── hérite de : nom, age, manger(), dormir()
│   └── ajoute    : race, aboyer()
│
└── Chat (enfant)
    ├── hérite de : nom, age, manger(), dormir()
    └── ajoute    : couleurPoil, ronronner()
```

Règle : Java n'autorise qu'un seul parent direct (**héritage simple**).

## 2. Mot-clé extends

```java
// Classe parente (super-classe)
public class Animal {

    private String nom;
    private int age;

    public Animal(String nom, int age) {
        this.nom = nom;
        this.age = age;
    }

    public String getNom() { return nom; }
    public int getAge()    { return age; }

    public void manger() {
        System.out.println(nom + " mange.");
    }

    public void dormir() {
        System.out.println(nom + " dort.");
    }

    @Override
    public String toString() {
        return getClass().getSimpleName() + "{nom='" + nom + "', age=" + age + "}";
    }
}

// Classe enfant (sous-classe)
public class Chien extends Animal {

    private String race;

    // Le constructeur de l'enfant DOIT appeler super()
    public Chien(String nom, int age, String race) {
        super(nom, age);   // appel obligatoire du constructeur parent (en 1ère ligne)
        this.race = race;
    }

    public String getRace() { return race; }

    // Méthode spécifique à Chien
    public void aboyer() {
        System.out.println(getNom() + " : Woof !");
    }

    // Redéfinition (override) de manger()
    @Override
    public void manger() {
        System.out.println(getNom() + " mange sa croquette.");
        // super.manger();  // possible d'appeler la version parent
    }

    @Override
    public String toString() {
        return super.toString().replace("}", "") + ", race='" + race + "'}";
    }
}

// Autre classe enfant
public class Chat extends Animal {

    private String couleurPoil;
    private boolean estSteriise;

    public Chat(String nom, int age, String couleurPoil) {
        super(nom, age);
        this.couleurPoil = couleurPoil;
        this.estSteriise = false;
    }

    public void ronronner() {
        System.out.println(getNom() + " : Prrr...");
    }

    @Override
    public void manger() {
        System.out.println(getNom() + " mange délicatement son pâté.");
    }
}
```

```java
public class MainAnimaux {
    public static void main(String[] args) {

        Chien rex = new Chien("Rex", 3, "Berger Allemand");
        Chat mimi = new Chat("Mimi", 5, "roux");

        // Méthodes héritées
        rex.manger();   // version redéfinie : "Rex mange sa croquette."
        rex.dormir();   // héritée de Animal : "Rex dort."
        rex.aboyer();   // spécifique à Chien : "Rex : Woof !"

        mimi.manger();   // version redéfinie
        mimi.ronronner(); // spécifique à Chat

        System.out.println(rex);   // toString() redéfini
        System.out.println(mimi);

        // Polymorphisme : variable de type Animal, objet de type Chien
        Animal monAnimal = new Chien("Buddy", 2, "Labrador");
        monAnimal.manger();  // appelle la version Chien (liaison dynamique)
        // monAnimal.aboyer();  // ERREUR : Animal ne connaît pas aboyer()

        // Tableau hétérogène
        Animal[] animaux = {
            new Chien("Fido", 4, "Caniche"),
            new Chat("Luna", 2, "noir"),
            new Chien("Max", 6, "Husky")
        };

        for (Animal a : animaux) {
            a.manger();  // chaque animal mange à sa façon (polymorphisme)
        }
    }
}
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Dans IntelliJ, créer la hiérarchie Animal/Chien/Chat. Montrer l'onglet "Structure" (Alt+7) qui affiche les méthodes héritées vs redéfinies. Montrer aussi la vue hiérarchie avec Ctrl+H sur la classe Animal.
> **Expliquer :** Expliquer le polymorphisme en montrant que `Animal[] animaux` contient des Chiens et des Chats, et que `a.manger()` appelle la bonne version selon le type réel de l'objet (liaison dynamique / late binding).
---

## 3. super — Accès au parent

```java
public class Employe {

    private String nom;
    private double salaire;

    public Employe(String nom, double salaire) {
        this.nom = nom;
        this.salaire = salaire;
    }

    public double getSalaire() { return salaire; }
    public String getNom()     { return nom; }

    public String getDescription() {
        return "Employé : " + nom + " (salaire : " + salaire + "€)";
    }

    public void afficherInfo() {
        System.out.println(getDescription());
    }
}

public class Manager extends Employe {

    private double bonus;
    private int nbSubordonnes;

    public Manager(String nom, double salaire, double bonus) {
        super(nom, salaire);    // appel constructeur parent obligatoire
        this.bonus = bonus;
        this.nbSubordonnes = 0;
    }

    // Redéfinition + appel de la version parent
    @Override
    public String getDescription() {
        // super.getDescription() récupère la description de base
        return super.getDescription() + " | Manager, bonus : " + bonus + "€";
    }

    // Salaire total = salaire base + bonus (polymorphisme)
    @Override
    public double getSalaire() {
        return super.getSalaire() + bonus;
    }

    public void ajouterSubordonne() {
        nbSubordonnes++;
    }
}

public class DirecteurGeneral extends Manager {

    private double partBenefices;

    public DirecteurGeneral(String nom, double salaire, double bonus, double partBenefices) {
        super(nom, salaire, bonus);   // appel Manager(...)
        this.partBenefices = partBenefices;
    }

    @Override
    public double getSalaire() {
        return super.getSalaire() + partBenefices;  // base + bonus + part
    }

    @Override
    public String getDescription() {
        return super.getDescription() + " | DG, part : " + partBenefices + "€";
    }
}
```

## 4. @Override — Redéfinition de méthodes

```java
public class OverrideDemo {

    // L'annotation @Override :
    // 1. Documente l'intention : "je redéfinis une méthode parent"
    // 2. Fait échouer la compilation si la méthode n'existe pas dans le parent
    //    (protection contre les fautes de frappe)

    public static class Base {
        public void methode() {
            System.out.println("Base.methode()");
        }

        public String toString() {
            return "Base";
        }
    }

    public static class Enfant extends Base {

        @Override
        public void methode() {
            System.out.println("Enfant.methode()");
        }

        // @Override
        // public void Methode() {  // ERREUR : 'Methode' n'existe pas dans Base
        //     ...
        // }

        @Override
        public String toString() {
            return "Enfant extends " + super.toString();
        }
    }

    public static void main(String[] args) {
        Base b = new Enfant();
        b.methode();        // "Enfant.methode()" — liaison dynamique
        System.out.println(b);  // "Enfant extends Base"
    }
}
```

## 5. Classes abstraites

Une classe abstraite **ne peut pas être instanciée** directement. Elle définit un contrat partiel que les sous-classes doivent compléter.

```java
// Classe abstraite : ne peut pas être instanciée directement
public abstract class Forme {

    private String couleur;

    public Forme(String couleur) {
        this.couleur = couleur;
    }

    public String getCouleur() { return couleur; }

    // Méthode abstraite : DOIT être redéfinie dans les sous-classes
    public abstract double calculerAire();
    public abstract double calculerPerimetre();

    // Méthode concrète : utilisable directement ou surchargeable
    public void afficher() {
        System.out.printf("%s %s — Aire : %.2f, Périmètre : %.2f%n",
                getCouleur(), getClass().getSimpleName(),
                calculerAire(), calculerPerimetre());
    }
}

// Sous-classe concrète : DOIT implémenter toutes les méthodes abstraites
public class Cercle extends Forme {

    private double rayon;

    public Cercle(String couleur, double rayon) {
        super(couleur);
        this.rayon = rayon;
    }

    @Override
    public double calculerAire() {
        return Math.PI * rayon * rayon;
    }

    @Override
    public double calculerPerimetre() {
        return 2 * Math.PI * rayon;
    }
}

public class Rectangle extends Forme {

    private double largeur;
    private double hauteur;

    public Rectangle(String couleur, double largeur, double hauteur) {
        super(couleur);
        this.largeur = largeur;
        this.hauteur = hauteur;
    }

    @Override
    public double calculerAire() {
        return largeur * hauteur;
    }

    @Override
    public double calculerPerimetre() {
        return 2 * (largeur + hauteur);
    }
}

public class Triangle extends Forme {

    private double a, b, c;  // trois côtés

    public Triangle(String couleur, double a, double b, double c) {
        super(couleur);
        this.a = a;
        this.b = b;
        this.c = c;
    }

    @Override
    public double calculerAire() {
        double s = (a + b + c) / 2;  // semi-périmètre
        return Math.sqrt(s * (s - a) * (s - b) * (s - c));  // Formule de Héron
    }

    @Override
    public double calculerPerimetre() {
        return a + b + c;
    }
}

public class MainFormes {
    public static void main(String[] args) {

        // Forme f = new Forme("rouge");  // ERREUR : classe abstraite !

        Forme[] formes = {
            new Cercle("rouge", 5),
            new Rectangle("bleu", 4, 6),
            new Triangle("vert", 3, 4, 5)
        };

        double aireTotal = 0;
        for (Forme f : formes) {
            f.afficher();
            aireTotal += f.calculerAire();
        }
        System.out.printf("Aire totale : %.2f%n", aireTotal);
    }
}
```

## 6. Mot-clé final

```java
// --- final sur une classe : ne peut pas être héritée ---
public final class Immuable {
    // Aucune classe ne peut faire "extends Immuable"
}

// public class Tentative extends Immuable {}  // ERREUR de compilation

// Exemples dans le JDK : String, Integer, Double, Math

// --- final sur une méthode : ne peut pas être redéfinie ---
public class Parent {
    public final void methodeSecurisee() {
        System.out.println("Cette méthode ne peut pas être redéfinie");
    }

    public void methodeNormale() {
        System.out.println("Celle-ci peut l'être");
    }
}

public class EnfantFinal extends Parent {
    // @Override
    // public void methodeSecurisee() {}  // ERREUR de compilation

    @Override
    public void methodeNormale() {
        System.out.println("Redéfinie dans l'enfant");
    }
}

// --- final sur un attribut : constante ---
public class Config {
    public static final int TIMEOUT_MS = 5000;
    public static final String URL_BASE = "https://api.example.com";

    private final int id;  // attribut d'instance final (doit être initialisé dans le constructeur)

    public Config(int id) {
        this.id = id;  // seul endroit où on peut l'initialiser
        // this.id = 2;  // ERREUR : ne peut pas être modifié ensuite
    }
}
```

## 7. instanceof et casting

```java
public class InstanceofDemo {

    public static void main(String[] args) {

        Animal[] animaux = {
            new Chien("Rex", 3, "Berger"),
            new Chat("Mimi", 2, "roux"),
            new Chien("Fido", 5, "Labrador")
        };

        for (Animal a : animaux) {

            // instanceof : vérifie le type réel de l'objet
            if (a instanceof Chien) {
                Chien chien = (Chien) a;  // downcast (Animal → Chien)
                chien.aboyer();
            } else if (a instanceof Chat) {
                Chat chat = (Chat) a;
                chat.ronronner();
            }
        }

        // Pattern matching instanceof (Java 16+) — beaucoup plus concis
        for (Animal a : animaux) {
            if (a instanceof Chien chien) {   // cast intégré
                chien.aboyer();
            } else if (a instanceof Chat chat) {
                chat.ronronner();
            }
        }

        // instanceof avec héritage
        Chien rex = new Chien("Rex", 3, "Berger");
        System.out.println(rex instanceof Chien);   // true
        System.out.println(rex instanceof Animal);  // true (Chien est-un Animal)
        System.out.println(rex instanceof Object);  // true (tout est Object)
        System.out.println(rex instanceof Chat);    // false

        // ClassCastException si le cast est incorrect
        Animal a = new Chien("Buddy", 2, "Caniche");
        try {
            Chat c = (Chat) a;  // ClassCastException à l'exécution !
        } catch (ClassCastException e) {
            System.out.println("Cast impossible : " + e.getMessage());
        }

        // Toujours vérifier avec instanceof avant de caster
        if (a instanceof Chat) {
            Chat c = (Chat) a;  // sûr
        }
    }
}
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Montrer une `ClassCastException` dans la console IntelliJ, avec le stack trace. Puis montrer la version correcte avec `instanceof` avant le cast. Aussi montrer le nouveau pattern matching `instanceof Chien chien` de Java 16.
> **Expliquer :** Expliquer la différence entre erreur de compilation (détectée par javac, safe) et erreur d'exécution (ClassCastException, à éviter absolument en production). L'utilisation de `instanceof` avant cast est une pratique défensive obligatoire.
---

## 8. La classe Object — Racine de la hiérarchie

```java
public class ObjectDemo {

    // Toutes les classes héritent implicitement de Object
    // Object fournit ces méthodes que toute classe peut redéfinir :

    // toString()  : représentation textuelle
    // equals()    : comparaison d'égalité
    // hashCode()  : code de hachage (utilisé par HashMap, HashSet)
    // getClass()  : retourne la Class de l'objet
    // clone()     : copie superficielle (nécessite Cloneable)
    // finalize()  : appelé avant la GC (déprécié)

    static class Produit {
        private String nom;
        private double prix;

        public Produit(String nom, double prix) {
            this.nom = nom;
            this.prix = prix;
        }

        // Contrat equals/hashCode : si deux objets sont equals, ils DOIVENT avoir le même hashCode
        @Override
        public boolean equals(Object o) {
            if (this == o) return true;
            if (!(o instanceof Produit)) return false;
            Produit p = (Produit) o;
            return Double.compare(p.prix, prix) == 0
                    && java.util.Objects.equals(nom, p.nom);
        }

        @Override
        public int hashCode() {
            return java.util.Objects.hash(nom, prix);
        }

        @Override
        public String toString() {
            return "Produit{" + nom + ", " + prix + "€}";
        }
    }

    public static void main(String[] args) {
        Produit p1 = new Produit("Livre", 15.99);
        Produit p2 = new Produit("Livre", 15.99);
        Produit p3 = new Produit("Stylo", 2.50);

        System.out.println(p1.equals(p2));   // true (même contenu)
        System.out.println(p1 == p2);        // false (objets différents)
        System.out.println(p1.equals(p3));   // false

        System.out.println(p1.hashCode() == p2.hashCode());  // true (même hash)

        System.out.println(p1.getClass().getName());         // nom complet
        System.out.println(p1.getClass().getSimpleName());   // "Produit"

        // java.util.Objects.toString pour éviter NPE
        Object obj = null;
        System.out.println(java.util.Objects.toString(obj, "valeur par défaut")); // "valeur par défaut"
    }
}
```

## Récapitulatif

| Concept | Syntaxe | À retenir |
|---------|---------|-----------|
| Héritage | `class B extends A` | Un seul parent direct |
| Constructeur parent | `super(args)` | Doit être la 1ère ligne |
| Appel méthode parent | `super.methode()` | Depuis une méthode redéfinie |
| Redéfinition | `@Override` | Toujours mettre l'annotation |
| Classe abstraite | `abstract class` | Non instanciable, méthodes abstraites possibles |
| Méthode abstraite | `abstract void f()` | Pas de corps, obligatoirement redéfinie |
| `final class` | `final class C` | Ne peut pas être héritée |
| `final method` | `final void f()` | Ne peut pas être redéfinie |
| `instanceof` | `obj instanceof Type` | Toujours vérifier avant de caster |
| Racine | `Object` | Toutes les classes héritent d'Object |
