# Java — Structures de Contrôle : if/else, switch, Boucles, Tableaux

## 1. Instruction if / else if / else

La structure `if/else` permet d'exécuter des blocs de code conditionnellement.

```java
public class Conditions {
    public static void main(String[] args) {

        int age = 20;

        // if simple
        if (age >= 18) {
            System.out.println("Majeur");
        }

        // if / else
        if (age >= 18) {
            System.out.println("Majeur");
        } else {
            System.out.println("Mineur");
        }

        // if / else if / else
        int note = 75;
        if (note >= 90) {
            System.out.println("Très bien");
        } else if (note >= 80) {
            System.out.println("Bien");
        } else if (note >= 70) {
            System.out.println("Assez bien");
        } else if (note >= 60) {
            System.out.println("Passable");
        } else {
            System.out.println("Insuffisant");
        }

        // if sans accolades (uniquement pour 1 instruction — déconseillé)
        if (age >= 18) System.out.println("Majeur");

        // Opérateur ternaire (inline)
        String statut = age >= 18 ? "majeur" : "mineur";

        // Conditions imbriquées
        boolean aPermis = true;
        boolean aVoiture = false;

        if (age >= 18) {
            if (aPermis) {
                if (aVoiture) {
                    System.out.println("Peut conduire");
                } else {
                    System.out.println("A le permis mais pas de voiture");
                }
            } else {
                System.out.println("Majeur mais pas de permis");
            }
        }

        // Version plus lisible avec && (ET logique)
        if (age >= 18 && aPermis && aVoiture) {
            System.out.println("Peut conduire");
        }

        // Null check — toujours tester avant d'utiliser une référence
        String nom = null;
        if (nom != null && !nom.isEmpty()) {
            System.out.println("Nom : " + nom);
        } else {
            System.out.println("Nom non défini");
        }

        // Java 14+ : switch expression comme condition
        int mois = 4;
        int nbJours = switch (mois) {
            case 1, 3, 5, 7, 8, 10, 12 -> 31;
            case 4, 6, 9, 11 -> 30;
            case 2 -> 28;
            default -> throw new IllegalArgumentException("Mois invalide : " + mois);
        };
        System.out.println("Mois " + mois + " : " + nbJours + " jours");
    }
}
```

## 2. Switch — Instruction et Expression

### Switch traditionnel (avant Java 14)

```java
public class SwitchTraditional {
    public static void main(String[] args) {

        int jour = 3;
        String nomJour;

        switch (jour) {
            case 1:
                nomJour = "Lundi";
                break;      // IMPORTANT : sans break, le code "tombe" dans le cas suivant
            case 2:
                nomJour = "Mardi";
                break;
            case 3:
                nomJour = "Mercredi";
                break;
            case 4:
                nomJour = "Jeudi";
                break;
            case 5:
                nomJour = "Vendredi";
                break;
            case 6:
            case 7:
                nomJour = "Week-end";  // cases groupés : pas de break intermédiaire
                break;
            default:
                nomJour = "Invalide";
                break;
        }
        System.out.println(nomJour);

        // Exemple de fall-through (intentionnel)
        int mois = 4;
        int nbJours;
        switch (mois) {
            case 1: case 3: case 5: case 7:
            case 8: case 10: case 12:
                nbJours = 31;
                break;
            case 4: case 6: case 9: case 11:
                nbJours = 30;
                break;
            case 2:
                nbJours = 28;
                break;
            default:
                nbJours = -1;
        }

        // Switch sur String (Java 7+)
        String couleur = "rouge";
        switch (couleur) {
            case "rouge":
                System.out.println("Stop");
                break;
            case "orange":
                System.out.println("Attention");
                break;
            case "vert":
                System.out.println("Go");
                break;
            default:
                System.out.println("Couleur inconnue");
        }
    }
}
```

### Switch expression moderne (Java 14+)

```java
public class SwitchModerne {
    public static void main(String[] args) {

        // Switch expression avec flèche -> (pas de break nécessaire)
        int jour = 3;
        String nomJour = switch (jour) {
            case 1 -> "Lundi";
            case 2 -> "Mardi";
            case 3 -> "Mercredi";
            case 4 -> "Jeudi";
            case 5 -> "Vendredi";
            case 6, 7 -> "Week-end";   // plusieurs cases en une ligne
            default -> "Invalide";
        };
        System.out.println(nomJour);  // "Mercredi"

        // Switch avec blocs (yield pour retourner une valeur)
        int nb = 5;
        String description = switch (nb) {
            case 1, 2, 3 -> "Petit";
            case 4, 5, 6 -> {
                String s = nb > 4 ? "milieu haut" : "milieu bas";
                yield "Moyen (" + s + ")";  // yield obligatoire dans un bloc
            }
            default -> "Grand";
        };
        System.out.println(description);

        // Switch sur enum (très courant)
        Saison saison = Saison.ETE;
        String activite = switch (saison) {
            case PRINTEMPS -> "Jardinage";
            case ETE -> "Natation";
            case AUTOMNE -> "Randonnée";
            case HIVER -> "Ski";
        };  // Pas de default nécessaire si toutes les valeurs enum sont couvertes
        System.out.println(activite);

        // Pattern matching dans switch (Java 21)
        Object obj = 42;
        String type = switch (obj) {
            case Integer i -> "Entier : " + i;
            case String s -> "Chaîne : " + s;
            case Double d -> "Réel : " + d;
            case null -> "Null";
            default -> "Autre type";
        };
        System.out.println(type);
    }
}

enum Saison { PRINTEMPS, ETE, AUTOMNE, HIVER }
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Montrer dans IntelliJ la différence entre l'ancien switch (avec les `break`) et le nouveau switch expression (avec `->` et sans `break`). Provoquer volontairement un fall-through dans l'ancien switch en enlevant un `break` et montrer le bug.
> **Expliquer :** Insister sur le fait que le nouveau switch expression est plus sûr car il empêche les fall-through accidentels. C'est la syntaxe à privilégier dans du code moderne.
---

## 3. Boucle while

```java
public class BoucleWhile {
    public static void main(String[] args) {

        // while : la condition est testée AVANT chaque itération
        int compteur = 0;
        while (compteur < 5) {
            System.out.println("Compteur : " + compteur);
            compteur++;  // IMPORTANT : ne pas oublier l'incrémentation !
        }

        // Boucle infinie avec break
        int n = 1;
        while (true) {
            System.out.println(n);
            n++;
            if (n > 5) break;  // sortie explicite
        }

        // Lecture jusqu'à condition (pattern courant)
        java.util.Scanner scanner = new java.util.Scanner(System.in);
        System.out.println("Entrez des nombres (0 pour arrêter) :");
        int somme = 0;
        int saisie;
        while ((saisie = scanner.nextInt()) != 0) {
            somme += saisie;
        }
        System.out.println("Somme : " + somme);

        // do-while : la condition est testée APRÈS la première itération
        // Le bloc s'exécute AU MOINS UNE FOIS
        int tentatives = 0;
        do {
            System.out.println("Tentative " + (tentatives + 1));
            tentatives++;
        } while (tentatives < 3);

        // Pattern courant do-while : menu interactif
        int choix;
        do {
            System.out.println("\n=== MENU ===");
            System.out.println("1. Option A");
            System.out.println("2. Option B");
            System.out.println("0. Quitter");
            System.out.print("Votre choix : ");
            choix = scanner.nextInt();
            switch (choix) {
                case 1 -> System.out.println("Option A choisie");
                case 2 -> System.out.println("Option B choisie");
                case 0 -> System.out.println("Au revoir !");
                default -> System.out.println("Choix invalide");
            }
        } while (choix != 0);
    }
}
```

## 4. Boucle for

```java
public class BoucleFor {
    public static void main(String[] args) {

        // for classique : for (initialisation; condition; mise à jour)
        for (int i = 0; i < 5; i++) {
            System.out.println(i);  // 0, 1, 2, 3, 4
        }

        // Décrémentation
        for (int i = 10; i > 0; i -= 2) {
            System.out.println(i);  // 10, 8, 6, 4, 2
        }

        // Plusieurs variables dans le for
        for (int i = 0, j = 10; i < j; i++, j--) {
            System.out.println(i + " - " + j);
        }

        // for avec break et continue
        for (int i = 0; i < 10; i++) {
            if (i == 3) continue;  // saute cette itération
            if (i == 7) break;     // sort de la boucle
            System.out.print(i + " ");  // 0 1 2 4 5 6
        }
        System.out.println();

        // for imbriqués : table de multiplication
        for (int i = 1; i <= 5; i++) {
            for (int j = 1; j <= 5; j++) {
                System.out.printf("%4d", i * j);
            }
            System.out.println();
        }

        // break avec label (rare mais existe)
        boucleExterne:
        for (int i = 0; i < 3; i++) {
            for (int j = 0; j < 3; j++) {
                if (i == 1 && j == 1) {
                    break boucleExterne;  // sort des deux boucles
                }
                System.out.println(i + "," + j);
            }
        }
    }
}
```

## 5. Boucle for-each (enhanced for)

```java
import java.util.Arrays;
import java.util.List;

public class BoucleForEach {
    public static void main(String[] args) {

        // for-each sur tableau
        int[] nombres = {10, 20, 30, 40, 50};
        for (int n : nombres) {
            System.out.println(n);
        }

        // for-each sur String[]
        String[] fruits = {"pomme", "banane", "cerise"};
        for (String fruit : fruits) {
            System.out.println(fruit.toUpperCase());
        }

        // for-each sur List (collections)
        List<String> villes = List.of("Paris", "Lyon", "Marseille");
        for (String ville : villes) {
            System.out.println(ville);
        }

        // Limitation : ne peut pas modifier le tableau/collection
        int[] tab = {1, 2, 3};
        for (int n : tab) {
            n = n * 2;  // ne modifie PAS le tableau !
        }
        System.out.println(Arrays.toString(tab));  // [1, 2, 3] inchangé

        // Pour modifier, utiliser un for classique avec index
        for (int i = 0; i < tab.length; i++) {
            tab[i] = tab[i] * 2;  // modifie réellement
        }
        System.out.println(Arrays.toString(tab));  // [2, 4, 6]
    }
}
```

## 6. Tableaux (Arrays)

```java
import java.util.Arrays;

public class Tableaux {
    public static void main(String[] args) {

        // --- Déclaration et initialisation ---

        // Tableau de taille fixe initialisé à 0 (ou null pour les objets)
        int[] notes = new int[5];   // [0, 0, 0, 0, 0]
        notes[0] = 15;
        notes[1] = 18;
        notes[2] = 12;
        notes[3] = 16;
        notes[4] = 9;

        // Initialisation directe avec valeurs
        int[] scores = {100, 85, 90, 75, 95};
        String[] jours = {"Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"};

        // Déclaration alternative (moins courante)
        int tableau[];  // Déconseillé, préférer int[]

        // --- Accès ---
        System.out.println(scores[0]);       // 100 (premier élément)
        System.out.println(scores[4]);       // 95 (dernier élément)
        System.out.println(scores.length);   // 5 (propriété, pas méthode)

        // --- Parcours ---
        for (int i = 0; i < scores.length; i++) {
            System.out.printf("scores[%d] = %d%n", i, scores[i]);
        }

        // --- Méthodes utiles de la classe Arrays ---
        Arrays.sort(scores);                           // tri en place
        System.out.println(Arrays.toString(scores));   // [75, 85, 90, 95, 100]

        int index = Arrays.binarySearch(scores, 90);   // 2 (après tri)
        System.out.println("Index de 90 : " + index);

        int[] copie = Arrays.copyOf(scores, scores.length);  // copie complète
        int[] partielle = Arrays.copyOfRange(scores, 1, 4);  // [85, 90, 95]

        Arrays.fill(copie, 0);                         // remplir avec une valeur
        System.out.println(Arrays.toString(copie));    // [0, 0, 0, 0, 0]

        boolean egal = Arrays.equals(scores, partielle); // false
        System.out.println(egal);

        // --- Tableaux 2D ---
        int[][] matrice = new int[3][3];
        matrice[0][0] = 1;
        matrice[1][1] = 5;
        matrice[2][2] = 9;

        // Initialisation directe
        int[][] grille = {
            {1, 2, 3},
            {4, 5, 6},
            {7, 8, 9}
        };

        // Parcours 2D
        for (int i = 0; i < grille.length; i++) {
            for (int j = 0; j < grille[i].length; j++) {
                System.out.printf("%3d", grille[i][j]);
            }
            System.out.println();
        }

        // Avec for-each
        for (int[] ligne : grille) {
            System.out.println(Arrays.toString(ligne));
        }

        // Tableaux irréguliers (jagged arrays)
        int[][] triangle = new int[3][];
        triangle[0] = new int[]{1};
        triangle[1] = new int[]{1, 2};
        triangle[2] = new int[]{1, 2, 3};

        for (int[] ligne : triangle) {
            System.out.println(Arrays.toString(ligne));
        }

        // --- Hors limites ---
        try {
            System.out.println(scores[10]);  // ArrayIndexOutOfBoundsException !
        } catch (ArrayIndexOutOfBoundsException e) {
            System.out.println("Erreur : index hors limites");
        }
    }
}
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Provoquer une `ArrayIndexOutOfBoundsException` intentionnellement en direct. Montrer le stack trace dans la console IntelliJ. Puis montrer comment corriger avec une vérification de borne.
> **Expliquer :** Expliquer ce qu'est un index out of bounds, pourquoi c'est une erreur à l'exécution (pas à la compilation), et comment la pile d'appels (stack trace) aide à localiser le problème.
---

## 7. Algorithmes classiques sur tableaux

```java
import java.util.Arrays;

public class AlgorithmesTableaux {
    public static void main(String[] args) {

        int[] tab = {64, 34, 25, 12, 22, 11, 90};

        // --- Recherche du maximum ---
        int max = tab[0];
        for (int n : tab) {
            if (n > max) max = n;
        }
        System.out.println("Max : " + max);  // 90

        // --- Somme et moyenne ---
        int somme = 0;
        for (int n : tab) {
            somme += n;
        }
        double moyenne = (double) somme / tab.length;
        System.out.printf("Somme : %d, Moyenne : %.2f%n", somme, moyenne);

        // --- Inversion ---
        int[] inverse = new int[tab.length];
        for (int i = 0; i < tab.length; i++) {
            inverse[i] = tab[tab.length - 1 - i];
        }
        System.out.println("Inversé : " + Arrays.toString(inverse));

        // Inversion en place (sans tableau auxiliaire)
        int[] arr = {1, 2, 3, 4, 5};
        int gauche = 0, droite = arr.length - 1;
        while (gauche < droite) {
            int temp = arr[gauche];
            arr[gauche] = arr[droite];
            arr[droite] = temp;
            gauche++;
            droite--;
        }
        System.out.println("Inversé en place : " + Arrays.toString(arr));

        // --- Tri à bulles (bubble sort) — pour comprendre les algorithmes ---
        int[] bubble = {64, 34, 25, 12, 22, 11, 90};
        for (int i = 0; i < bubble.length - 1; i++) {
            for (int j = 0; j < bubble.length - i - 1; j++) {
                if (bubble[j] > bubble[j + 1]) {
                    // Échange
                    int temp = bubble[j];
                    bubble[j] = bubble[j + 1];
                    bubble[j + 1] = temp;
                }
            }
        }
        System.out.println("Trié : " + Arrays.toString(bubble));
        // Note : en production, utiliser Arrays.sort() qui est bien plus rapide

        // --- Recherche linéaire ---
        int cible = 22;
        int position = -1;
        for (int i = 0; i < tab.length; i++) {
            if (tab[i] == cible) {
                position = i;
                break;
            }
        }
        System.out.println(cible + " trouvé à l'index : " + position);
    }
}
```

## 8. Récapitulatif des structures de contrôle

| Structure | Usage | Particularité |
|-----------|-------|---------------|
| `if/else` | Conditions binaires ou multiples | Utiliser `&&`, `\|\|`, `!` |
| `switch` (ancien) | Égalité sur int/String/enum | Attention au `break` |
| `switch` (Java 14+) | Idem, plus concis | `->`, pas de fall-through |
| `while` | Boucle condition avant corps | Risque boucle infinie |
| `do-while` | Boucle corps avant condition | S'exécute au moins 1 fois |
| `for` | Boucle avec compteur | Index connu |
| `for-each` | Parcours collection/tableau | Lecture seule sur les primitifs |
| `break` | Sortir d'une boucle ou d'un switch | Avec label pour boucles imbriquées |
| `continue` | Sauter l'itération courante | — |

## Exercices de la section

### Exercice 1 : FizzBuzz
Afficher les nombres de 1 à 100. Si divisible par 3, afficher "Fizz". Si par 5, "Buzz". Si par les deux, "FizzBuzz".

### Exercice 2 : Tableau de bord
Créer un tableau de 10 notes d'étudiants, puis calculer et afficher : la moyenne, la note maximale, la note minimale, et le nombre d'étudiants ayant la moyenne.

### Exercice 3 : Palindrome
Écrire un programme qui vérifie si un mot saisi est un palindrome (se lit pareil dans les deux sens).
