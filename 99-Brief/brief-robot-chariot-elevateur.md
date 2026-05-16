# Brief : Robot Chariot Élévateur Intelligent (Tri par couleur & forme)

## Vue d'ensemble du projet

Ce projet consiste à concevoir, construire et programmer un **robot mobile de type chariot élévateur** capable de :

1. **Reconnaître** des objets, leurs couleurs et leurs formes grâce à une caméra.
2. **Soulever** un objet avec un mécanisme de fourche motorisé.
3. **Naviguer** de manière autonome vers une zone de dépôt précise.
4. **Trier** automatiquement les objets selon leur couleur ou leur forme.

Le développement se fait **en parallèle sur deux supports** : une **simulation** (Webots) pour valider la logique sans matériel, et un **robot réel** (Raspberry Pi) pour la mise en pratique physique. Une couche d'abstraction logicielle commune permet d'écrire le code **une seule fois** pour les deux.

Le projet démarre volontairement par une **télécommande manuelle** (pilotage à la manette de jeu) afin de valider le matériel — moteurs et levage — avant d'ajouter la moindre intelligence.

```
┌─────────────────────────────────────────────────────────────────┐
│                    ARCHITECTURE FONCTIONNELLE                    │
└─────────────────────────────────────────────────────────────────┘

   ┌──────────────┐         ┌──────────────────────────────────┐
   │   Manette    │         │            ROBOT                 │
   │   de jeu     │────────▶│  ┌────────────┐  ┌────────────┐  │
   │ (Phase 1)    │  teleop │  │  Caméra    │  │  Fourche   │  │
   └──────────────┘         │  │  (vision)  │  │  (levage)  │  │
                            │  └─────┬──────┘  └─────┬──────┘  │
   ┌──────────────┐         │        │               │        │
   │   Caméra     │         │  ┌─────▼───────────────▼──────┐  │
   │ flux vidéo   │────────▶│  │   Cerveau (Raspberry Pi)   │  │
   └──────────────┘         │  │  Python : interface.py     │  │
                            │  └─────┬──────────────────────┘  │
                            │        │                         │
                            │  ┌─────▼──────┐                  │
                            │  │  Moteurs   │  (locomotion)    │
                            │  └────────────┘                  │
                            └──────────────────────────────────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              ▼                      ▼                      ▼
        ┌──────────┐           ┌──────────┐           ┌──────────┐
        │  Zone    │           │  Zone    │           │  Zone    │
        │  ROUGE   │           │  VERTE   │           │  BLEUE   │
        └──────────┘           └──────────┘           └──────────┘
            Tri automatique selon couleur / forme détectée
```

```
┌─────────────────────────────────────────────────────────────────┐
│              CYCLE DE TRI AUTONOME (objectif final)              │
└─────────────────────────────────────────────────────────────────┘

   ① Aller au poste de scan
            │
            ▼
   ② Analyser l'objet (couleur + forme + reconnaissance ML)
            │
            ▼
   ③ Soulever l'objet avec la fourche
            │
            ▼
   ④ Suivre la ligne vers la zone correspondante
            │
            ▼
   ⑤ Déposer l'objet
            │
            ▼
   ⑥ Revenir au poste de scan ──────┐
            ▲                        │
            └────────────────────────┘
```

## Objectifs pédagogiques

- Structurer un projet Python en modules avec une **couche d'abstraction** (interface commune simulation / réel).
- Piloter du **matériel** : moteurs à courant continu, servomoteurs, GPIO du Raspberry Pi.
- Lire une **manette de jeu** et mapper ses entrées vers des commandes robot.
- Mettre en œuvre la **vision par ordinateur** avec OpenCV (détection de couleur et de forme).
- Entraîner et déployer un modèle de **reconnaissance d'objets** (YOLO).
- Implémenter une **boucle de contrôle** robotique : percevoir → décider → agir.
- Développer et tester en **simulation** (Webots) avant le portage matériel.
- Versionner le projet proprement avec **Git/GitHub**.

## Prérequis

- **Python** : variables, boucles, fonctions, conditions, classes (POO de base).
- **Git/GitHub** : commits, branches.
- Notions de base d'**électronique** appréciées mais non obligatoires (le brief les introduit).
- Modules recommandés du parcours : `01-Fondamentaux/Python/`, `08-Machine-Learning/`, `09-Deep-Learning/CNN/`.

## Choix d'architecture validés

| Décision | Choix retenu | Justification |
| :--- | :--- | :--- |
| **Support de dev** | Simulation Webots **+** robot réel en parallèle | Valider la logique sans matériel, puis porter. Code écrit une seule fois grâce à l'interface commune. |
| **Télécommande** | **Manette de jeu** (Bluetooth ou USB) | Pilotage agréable et précis. Fonctionne aussi bien sur Webots (API `Joystick` intégrée) que sur le robot réel. |
| **Navigation** | **Suivi de ligne** pour le MVP | Déterministe, robuste, testable en simulation. Pas de calcul de position ni de dérive. Les marqueurs ArUco viendront en Phase 6. |
| **Reconnaissance** | OpenCV (couleur/forme) puis **YOLO** (objets) | On démarre simple et fiable, on monte vers le ML une fois le cycle de base fonctionnel. |

> **Point clé :** la **reconnaissance ML** et la **navigation** sont deux problèmes séparés. Le ML répond à « *quel objet je vois ?* » ; le suivi de ligne répond à « *comment j'atteins la zone ?* ». On peut donc viser le ML pour la vision tout en gardant une navigation simple.

## Architecture logicielle

Le secret pour développer simulation et robot réel sans tout réécrire : une **interface abstraite** commune. La logique de pilotage ne sait jamais si elle parle à un robot simulé ou réel.

```
robot/
├── interface.py       # Classe abstraite : avancer(), reculer(), tourner(),
│                      #   lever(), baisser(), lire_camera()
├── sim_robot.py       # Implémentation Webots
├── real_robot.py      # Implémentation Raspberry Pi (moteurs + servo + GPIO)
├── teleop.py          # Télécommande : lit la manette → appelle interface
├── vision.py          # Détection couleur / forme (OpenCV)
├── detection_ml.py    # Reconnaissance d'objets (YOLO)
├── line_follower.py   # Suivi de ligne autonome
├── sorter.py          # Logique de tri : couleur/forme → zone de dépôt
└── main.py            # Programme principal (orchestration du cycle)
```

## Matériel à acheter (robot réel)

> Budget indicatif total : **120 – 200 €**. Tout peut être testé d'abord en simulation (gratuit).

| Catégorie | Composant | Indication |
| :--- | :--- | :--- |
| **Cerveau** | Raspberry Pi 4 (4 Go) ou Pi 5 | Assez puissant pour OpenCV et un petit modèle YOLO. |
| | Carte microSD 32 Go (classe 10) | Système d'exploitation. |
| **Vision** | Raspberry Pi Camera Module 3 *ou* webcam USB | La caméra officielle s'intègre mieux. |
| **Locomotion** | Châssis robot 2 roues motrices + roue folle | Kits « smart car » Raspberry Pi tout faits possibles. |
| | 2 moteurs DC + roues | Souvent inclus dans le châssis. |
| | Carte de pilotage moteur (TB6612FNG ou Motor HAT) | Évite le L298N, peu efficace. |
| **Levage** | Servomoteur fort couple (ex. MG996R) | Actionne la fourche. |
| | Mécanisme de fourche | Crémaillère ou bras pivotant — pièce à concevoir/imprimer en 3D. |
| **Énergie** | Power bank USB (pour le Pi) | Alimentation stable du cerveau. |
| | Pack batteries (pour les moteurs) | Alimentation séparée des moteurs. |
| **Télécommande** | Manette de jeu Bluetooth/USB (Xbox, PS, ou générique) | Lue côté PC ou directement sur le Pi. |
| **Navigation** | Module(s) capteur suiveur de ligne infrarouge (x3 à x5) | Pour la Phase 3. |
| | Ruban adhésif noir mat + tapis clair | Tracé du circuit. |
| **Optionnel** | Carte ESP32 + extension robot | Pour la piste « hardware léger » en parallèle. |

## Pile logicielle

| Besoin | Outil |
| :--- | :--- |
| Langage | Python 3 |
| Simulation | **Webots** (gratuit, open-source) |
| Lecture manette | `pygame` (joystick) ou `inputs` / `evdev` ; API `Joystick` intégrée dans Webots |
| Pilotage GPIO (robot réel) | `gpiozero` ou la bibliothèque du Motor HAT |
| Vision | `opencv-python` |
| Reconnaissance d'objets | `ultralytics` (YOLO) ; `tflite-runtime` pour une version allégée sur Pi |
| Versionnage | Git / GitHub |

## Roadmap — 6 phases

### Phase 1 — Télécommande à la manette 🟢
*Objectif : piloter manuellement le robot — avancer, reculer, tourner, monter/descendre la fourche.*

- Mettre en place l'**interface abstraite** (`interface.py`) et les deux implémentations (`sim_robot.py`, `real_robot.py`).
- Lire les entrées de la **manette de jeu** : sticks → vitesse/direction, boutons/gâchettes → levage.
- Mapper ces entrées vers les commandes du robot dans `teleop.py`.
- **Simulation** : créer le monde Webots (robot + fourche) et piloter à la manette.
- **Robot réel** : câbler moteurs + servo, piloter à la manette.
- ✅ **Livrable :** une vidéo du robot (simulé et/ou réel) piloté à la manette, levage compris.

### Phase 2 — Vision passive 🟢
*Objectif : la caméra détecte couleur et forme, le robot reste immobile.*

- Capturer le flux caméra avec OpenCV.
- **Couleur** : conversion en espace HSV, masque, `cv2.findContours`.
- **Forme** : `cv2.approxPolyDP` pour compter les côtés (triangle, carré, cercle).
- Afficher en direct la couleur et la forme détectées.
- ✅ **Livrable :** un script qui annote le flux vidéo avec couleur + forme en temps réel.

### Phase 3 — Suivi de ligne autonome 🟡
*Objectif : le robot suit une ligne tout seul.*

- En simulation : capteurs de ligne virtuels ; sur le réel : modules infrarouges.
- Implémenter la **boucle de contrôle** : lire les capteurs → corriger la trajectoire → agir sur les moteurs.
- Régler un correcteur simple (proportionnel, puis PID si besoin).
- Gérer les intersections pour choisir une direction.
- ✅ **Livrable :** le robot parcourt un circuit en boucle sans sortir de la ligne.

### Phase 4 — Cycle de tri complet 🟡
*Objectif : intégrer toutes les briques.*

- Définir le **mapping** couleur/forme → zone de dépôt (`sorter.py`).
- Enchaîner : aller au poste de scan → analyser → soulever → suivre la ligne vers la bonne zone → déposer → revenir.
- Gérer les cas d'erreur : objet non reconnu, ligne perdue, échec de préhension.
- ✅ **Livrable :** le robot trie de façon autonome une série d'objets de couleurs/formes différentes.

### Phase 5 — Reconnaissance d'objets par ML 🔴
*Objectif : remplacer la détection couleur/forme par une vraie reconnaissance d'objets.*

- Constituer un petit **jeu de données** photo des objets à trier.
- Entraîner / affiner un modèle **YOLO** (`ultralytics`).
- Optimiser pour le Raspberry Pi (modèle léger, quantification, TFLite si besoin).
- Intégrer `detection_ml.py` dans le cycle de tri à la place de la détection OpenCV.
- ✅ **Livrable :** le robot trie selon la **classe d'objet** reconnue, pas seulement la couleur.

### Phase 6 — Navigation libre avec ArUco 🔴
*Objectif : naviguer sans lignes peintes au sol.*

- Coller des **marqueurs ArUco** repérables par la caméra (poste, zones, murs).
- Utiliser `cv2.aruco` pour estimer position et orientation du robot.
- Planifier des trajets directs entre points au lieu de suivre des lignes.
- ✅ **Livrable :** le robot rejoint n'importe quelle zone sans circuit tracé.

## Passeport de compétences

| Phase | Compétence clé | Livrable attendu |
| :--- | :--- | :--- |
| **1** | Pilotage matériel, lecture manette, architecture modulaire | Vidéo de pilotage à la manette |
| **2** | Vision par ordinateur (OpenCV) | Script d'annotation couleur/forme |
| **3** | Boucle de contrôle, régulation | Robot suiveur de ligne |
| **4** | Intégration système, machine à états | Cycle de tri autonome |
| **5** | Machine learning appliqué (YOLO) | Robot trieur par reconnaissance d'objets |
| **6** | Vision avancée, localisation | Navigation libre par marqueurs |

## Conseils & pièges à éviter

- **Commencer par la simulation** pour chaque phase : on débogue la logique gratuitement, puis on porte sur le réel.
- **Le levage est le point mécanique délicat** : prévoir un servomoteur à fort couple et, si la vraie fourche est trop complexe, simplifier d'abord (fourche basse fixe ou pince).
- **Alimenter séparément** le Raspberry Pi et les moteurs : les moteurs créent des chutes de tension qui font redémarrer le Pi.
- **Ne pas se lancer dans le ML trop tôt** : le cycle de tri doit déjà fonctionner en couleur/forme (Phase 4) avant d'ajouter YOLO (Phase 5).
- **MicroPython ≠ Python complet** : si la piste ESP32 est explorée, OpenCV et YOLO n'y tournent pas — la vision/IA reste sur le Raspberry Pi ou le PC.
- **Versionner régulièrement** : une branche par phase, des commits petits et clairs.

## Ressources

- **Webots** — simulateur de robotique gratuit et open-source : documentation officielle et tutoriels intégrés.
- **OpenCV** — documentation Python, tutoriels « color detection HSV » et « contour / shape detection ».
- **Ultralytics YOLO** — documentation pour l'entraînement et le déploiement de modèles de détection.
- **gpiozero** — bibliothèque Python simple pour piloter les GPIO du Raspberry Pi.
- **pygame** — module `joystick` pour la lecture de manette.
- Modules internes du parcours : `08-Machine-Learning/`, `09-Deep-Learning/CNN/`.
