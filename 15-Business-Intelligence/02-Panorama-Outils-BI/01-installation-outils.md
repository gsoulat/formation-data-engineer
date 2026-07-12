# 01 — Installation & prise en main des outils

> **Bienvenue ! C'est ici que tout commence.** Avant d'analyser la moindre donnée, il faut **équiper ton ordinateur**. Ce module te prend par la main, **clic par clic**, pour installer Python, Jupyter, VS Code, SQLite et créer tes comptes BI — que tu sois sur **Mac, Windows ou Linux**. Aucune connaissance préalable n'est requise. Si tu n'as jamais installé d'outil de développement de ta vie : **c'est exactement pour toi.**

| | |
|---|---|
| **Phase** | 0 — La Prairie · **Semaine 1** (tout premier module de la formation) |
| **Durée** | ≈ 7 h |
| **Compétences visées** | Transversale — mise en place de l'environnement de travail du Data Analyst (pré-requis de tous les modules techniques C11–C18) |
| **Pré-requis** | **Aucun.** Savoir allumer son ordinateur, cliquer, télécharger un fichier, créer une adresse e-mail. |
| **Ce qu'il te faut** | Un ordinateur (Mac, Windows ou Linux) · une connexion internet · ~10 Go d'espace disque libre · les **droits administrateur** (ton mot de passe de session) · une adresse e-mail |
| **Outils installés à la fin** | Anaconda (Python) · Jupyter · VS Code · DB Browser for SQLite · comptes Looker Studio / Power BI |

---

## Objectifs pédagogiques

À la fin de ce module, tu sauras :

1. **Installer Python** proprement via **Anaconda** (la distribution conçue pour la data) sur ton OS.
2. **Vérifier** que Python fonctionne avec une commande dans le terminal (`python --version`).
3. **Ouvrir et utiliser un terminal** : naviguer entre les dossiers (`cd`, `ls`), lancer une commande — sur Mac, Windows et Linux.
4. **Lancer Jupyter Notebook / JupyterLab**, créer un notebook et **exécuter une cellule** de code.
5. **Installer VS Code** (l'éditeur de code) et son extension Python.
6. **Installer DB Browser for SQLite**, ouvrir une base et exécuter une requête SQL simple.
7. **Créer un compte Looker Studio** (gratuit, web) et comprendre la **contrainte Power BI** selon ton OS.
8. **Installer les bibliothèques Python du parcours** : `pandas`, `numpy`, `matplotlib`, `seaborn`, `scipy`, `openpyxl`.
9. **Valider toute ton installation** avec un mini-notebook « hello data » qui charge un vrai fichier de ventes.

---

## Pourquoi c'est utile au Data Analyst

Un artisan ne commence pas sans son atelier. Le Data Analyst non plus. **Ton ordinateur correctement équipé, c'est ton atelier.** Tant qu'il n'est pas prêt, tu ne peux rien faire de concret.

- **Tu vas gagner des semaines.** Une installation ratée (mauvaise version de Python, chemin cassé, bibliothèque manquante) est la source n°1 de blocages chez les débutants. On la règle **maintenant, une bonne fois**.
- **Tu deviens autonome.** Savoir ouvrir un terminal et taper `python --version` sans paniquer, c'est déjà un réflexe de pro. Tu n'auras plus à appeler le formateur pour chaque détail.
- **C'est un savoir-faire transférable.** Installer, vérifier, dépanner un environnement : tu referas ça toute ta carrière (nouveau poste, nouveau PC, nouveau projet).

> 🧭 **Image à retenir.** Anaconda, c'est ta **caisse à outils complète livrée pré-remplie** : Python + Jupyter + les bibliothèques data, le tout dans une seule boîte. Plutôt que d'acheter chaque clé et chaque tournevis séparément (et risquer des incompatibilités), tu reçois une boîte cohérente où tout marche ensemble.

---

## Vue d'ensemble : la pile d'outils

Avant de cliquer, comprends **ce que fait chaque outil** et **dans quel ordre** on l'installe.

```
┌──────────────────────────────────────────────────────────────┐
│  1. ANACONDA  →  installe Python + Jupyter + bibliothèques     │
│       │            (le moteur de l'analyse de données)         │
│       ▼                                                        │
│  2. JUPYTER   →  pour écrire et exécuter du code par cellules   │
│       │            (ton cahier d'expériences data)            │
│       ▼                                                        │
│  3. VS CODE   →  éditeur de code (scripts, projets plus gros)   │
│       │                                                        │
│       ▼                                                        │
│  4. DB BROWSER SQLITE  →  ouvrir/interroger des bases SQL      │
│       │                                                        │
│       ▼                                                        │
│  5. COMPTES BI  →  Looker Studio (web) + Power BI (selon OS)   │
└──────────────────────────────────────────────────────────────┘
```

| Outil | À quoi ça sert | OS |
|---|---|---|
| **Anaconda** | Installe **Python** et toutes les bibliothèques data en un coup | Mac · Windows · Linux |
| **Jupyter** | Écrire du code Python **cellule par cellule**, voir les résultats tout de suite | Inclus dans Anaconda |
| **VS Code** | Éditeur de texte/code pour les fichiers `.py` et les projets | Mac · Windows · Linux |
| **DB Browser for SQLite** | Ouvrir une base de données SQLite, écrire des requêtes SQL **sans coder** | Mac · Windows · Linux |
| **Looker Studio** | Outil de **tableaux de bord** 100 % web, gratuit | Tous (navigateur) |
| **Power BI** | Outil BI standard en entreprise | ⚠️ Desktop = **Windows uniquement** |

> 💡 **Anaconda vs Miniconda.** **Anaconda** = la grosse boîte (tout est dedans, ~3-4 Go, le plus simple pour débuter → **on choisit ça**). **Miniconda** = version minimaliste (~400 Mo) où tu installes toi-même chaque bibliothèque. Si ton disque est très plein, prends Miniconda et suis l'encadré dédié au §9.

---

## Le terminal : le minimum vital ⌨️

Tu vas en avoir besoin dès l'étape suivante. Pas de panique : on n'utilise que **3 gestes**.

### C'est quoi, le terminal ?

C'est une fenêtre où tu **tapes des commandes** au lieu de cliquer. Ça paraît austère, mais c'est juste un autre moyen de parler à ton ordinateur — souvent **plus rapide et plus précis** que la souris.

### Ouvrir un terminal selon ton OS

| OS | Comment ouvrir le terminal |
|---|---|
| **🍎 Mac** | `Cmd + Espace` → tape **Terminal** → `Entrée`. (Ou : Applications → Utilitaires → Terminal.) |
| **🪟 Windows** | Menu Démarrer → tape **Anaconda Prompt** (après avoir installé Anaconda) → ouvre-le. C'est **le** terminal à utiliser dans cette formation. (Sinon : `Windows + R` → `cmd` → `Entrée`.) |
| **🐧 Linux** | `Ctrl + Alt + T`. (Ou cherche **Terminal** dans le menu des applications.) |

> 🪟 **Windows : pourquoi « Anaconda Prompt » et pas l'invite normale ?** Parce qu'Anaconda Prompt « connaît » déjà Python et conda. Avec l'invite de commande classique, tu risques l'erreur « `python` n'est pas reconnu ». **Sur Windows, prends toujours Anaconda Prompt pour cette formation.**

### Les 3 commandes à connaître

Tape une commande puis appuie sur `Entrée`. Le résultat s'affiche dessous.

| Commande | Ce qu'elle fait | Exemple |
|---|---|---|
| `pwd` | **P**rint **W**orking **D**irectory → affiche **où tu es** | `pwd` → `/Users/toi/Documents` |
| `ls` | **L**i**s**t → **liste** les fichiers/dossiers du dossier courant | `ls` |
| `cd` | **C**hange **D**irectory → **se déplace** dans un dossier | `cd Documents` |

> 🪟 **Windows (invite cmd classique) :** `pwd` n'existe pas → utilise `cd` seul pour voir où tu es, et `dir` au lieu de `ls`. **Mais dans Anaconda Prompt récent, `ls` et `pwd` marchent souvent aussi.** Sur Mac et Linux, les trois fonctionnent toujours.

**Deux raccourcis qui sauvent la vie :**
- `cd ..` → **remonte** d'un dossier (vers le dossier parent).
- `cd` (Mac/Linux) ou `cd %USERPROFILE%` (Windows) → revient à ton **dossier personnel**.

> 🧪 **Mini-exercice (2 min).** Ouvre ton terminal. Tape `pwd` (ou `cd` seul sur Windows). Puis `ls` (ou `dir`). Puis `cd Documents` et de nouveau `ls`. Tu viens de **naviguer dans ton ordinateur sans la souris**. 🎉

> ⚠️ **Si ça ne marche pas** — « commande introuvable » / « n'est pas reconnu ».
> - Vérifie l'**orthographe** (pas d'espace en trop, minuscules).
> - Sur Windows, es-tu bien dans **Anaconda Prompt** ?
> - `cd MonDossier` échoue ? Le dossier n'existe pas **à cet endroit** : fais `ls` pour voir les noms exacts (attention aux majuscules et aux accents).

---

## Installer Python via Anaconda 🐍

C'est l'étape la plus importante. Prends ton temps.

### Télécharger Anaconda

1. Va sur **[anaconda.com/download](https://www.anaconda.com/download)** dans ton navigateur.
2. Le site **détecte ton OS** et propose le bon installateur. Vérifie quand même :
   - **🍎 Mac** : choisis **Apple Silicon** si ton Mac est récent (puce M1/M2/M3/M4) ou **Intel** s'il est plus ancien. *Pour savoir : menu Pomme → « À propos de ce Mac » → ligne « Puce » ou « Processeur ».*
   - **🪟 Windows** : prends la version **64-bit** (`.exe`).
   - **🐧 Linux** : prends l'installateur **64-bit (x86)** au format `.sh`.
3. Le site peut te demander un e-mail : tu peux cliquer sur **« Skip / No thanks »** pour télécharger directement.

> 📸 *Capture décrite :* la page de téléchargement affiche un gros bouton vert/bleu **« Download »** avec, juste à côté, des icônes Windows / Apple / Linux. Le fichier fait **plusieurs centaines de Mo** — le téléchargement peut durer quelques minutes.

### Installer — 🍎 Mac

1. Ouvre le fichier téléchargé `.pkg` (dans Téléchargements).
2. Un assistant s'ouvre : clique **Continuer → Continuer → Accepter** (licence).
3. À l'étape « Type d'installation », laisse **« Installer pour moi uniquement »** (recommandé, pas de mot de passe admin nécessaire).
4. Clique **Installer**. Patiente (2-5 min). Puis **Fermer**.
5. **Ferme et rouvre** ton terminal (important : il doit recharger la config).

### Installer — 🪟 Windows

1. Double-clique le fichier `.exe` téléchargé.
2. **Next → I Agree.**
3. « Install for: » → laisse **« Just Me (recommended) »** → **Next**.
4. Garde le dossier d'installation proposé → **Next**.
5. **Écran important** « Advanced Options » :
   - Laisse **décochée** la case « Add Anaconda to my PATH » (Anaconda le déconseille — on passera par Anaconda Prompt).
   - Laisse **cochée** « Register Anaconda as my default Python ».
6. **Install** (5-10 min) → **Next → Finish** (tu peux décocher les pubs).

### Installer — 🐧 Linux

1. Ouvre un terminal, va dans le dossier du fichier téléchargé : `cd ~/Downloads` (ou `~/Téléchargements`).
2. Lance l'installateur (adapte le nom exact du fichier, utilise la touche `Tab` pour l'autocompléter) :
   ```bash
   bash Anaconda3-2024.XX-X-Linux-x86_64.sh
   ```
3. Appuie sur `Entrée` pour lire la licence, tape `yes` pour l'accepter.
4. Accepte l'emplacement proposé (`Entrée`).
5. À la question « initialize Anaconda3? » → tape **`yes`**.
6. **Ferme et rouvre** ton terminal (ou tape `source ~/.bashrc`).

### Vérifier que Python fonctionne ✅

Dans ton terminal (Anaconda Prompt sur Windows), tape :

```bash
python --version
```

Tu dois voir s'afficher quelque chose comme :

```
Python 3.12.4
```

> 🎉 **Si tu vois « Python 3.x.x », c'est gagné : Python est installé.** Le numéro exact peut varier (3.11, 3.12…), c'est normal.

Vérifie aussi que **conda** (le gestionnaire d'Anaconda) répond :

```bash
conda --version
```

→ doit afficher `conda 24.x.x` ou similaire.

> ⚠️ **Si ça ne marche pas.**
> - **« python n'est pas reconnu / command not found »** : tu n'as pas **rouvert** le terminal après l'installation → ferme-le complètement et rouvre. Sur Windows, utilise **Anaconda Prompt**, pas cmd.
> - **Mac : `python` renvoie une vieille version (2.7) ?** Essaie `python3 --version`. Le `python3` d'Anaconda est le bon. Si besoin, on corrigera le PATH avec le formateur.
> - **Toujours rien ?** Note l'erreur exacte et passe à la checklist finale + appelle le formateur. Ce n'est pas grave, ça se règle toujours.

🎥 *Besoin de voir l'installation en vidéo ? Va au §11.*

---

## Jupyter Notebook : ton cahier d'expériences 📓

Bonne nouvelle : **Jupyter est déjà installé** (il est livré avec Anaconda). On va juste apprendre à le lancer.

### Lancer Jupyter

Deux façons, choisis la plus simple :

**Option A — par le terminal (la plus fiable) :**
1. Dans ton terminal, place-toi dans le dossier où tu veux travailler, p. ex. :
   ```bash
   cd Documents
   ```
2. Lance :
   ```bash
   jupyter lab
   ```
   *(ou `jupyter notebook` si tu préfères l'interface classique)*
3. Ton **navigateur web s'ouvre tout seul** sur l'interface Jupyter. 🎉

**Option B — par Anaconda Navigator (tout en clics) :**
1. Ouvre **Anaconda Navigator** (cherche-le dans tes applications / menu Démarrer).
2. Repère la tuile **JupyterLab** → clique **« Launch »**.

> 📸 *Capture décrite :* JupyterLab s'ouvre dans le navigateur. À **gauche**, l'explorateur de fichiers (les dossiers de ton ordinateur). Au **centre**, un onglet « Launcher » avec de grandes icônes : **Notebook → Python 3**, Console, Terminal…

> ⚠️ **Ne ferme pas le terminal !** Tant que Jupyter tourne, le terminal doit rester ouvert (il fait tourner le serveur). Pour arrêter Jupyter : reviens au terminal et fais `Ctrl + C`, puis confirme avec `y`.

### Créer un notebook et exécuter une cellule

1. Dans le Launcher, clique **« Python 3 »** sous « Notebook ». Un fichier `.ipynb` vide s'ouvre.
2. Tu vois une **cellule** vide (un rectangle). Clique dedans et tape :
   ```python
   print("Bonjour, je suis prêt(e) à analyser des données !")
   2 + 2
   ```
3. **Exécute la cellule** : appuie sur **`Maj + Entrée`** (Shift+Enter). 
4. Le résultat s'affiche **juste en dessous** :
   ```
   Bonjour, je suis prêt(e) à analyser des données !
   4
   ```

> 🔑 **Le geste fondamental de Jupyter** : on écrit du code dans une cellule, on fait **`Maj + Entrée`**, le résultat apparaît dessous. On enchaîne les cellules comme les pages d'un cahier. C'est ce qui rend l'analyse de données si agréable : on voit le résultat de **chaque** étape.

5. **Renomme ton notebook** : clic droit sur l'onglet (ou menu Fichier → Rename) → `test-jupyter`.

> ⚠️ **Si ça ne marche pas.**
> - **Jupyter ne s'ouvre pas dans le navigateur** : regarde dans le terminal, il y a une ligne `http://localhost:8888/...` → copie-la dans ton navigateur.
> - **`jupyter : commande introuvable`** : Anaconda n'est pas actif → rouvre le terminal (Windows : Anaconda Prompt).
> - **La cellule affiche `... [*]` sans fin** : le code tourne encore (ou est bloqué). Menu **Kernel → Restart** si nécessaire.

---

## VS Code : l'éditeur de code 💻

Jupyter est parfait pour explorer. **VS Code** est l'éditeur où tu écriras des scripts `.py` et organiseras des projets plus gros. C'est l'éditeur le plus utilisé au monde, gratuit.

### Installer VS Code

1. Va sur **[code.visualstudio.com](https://code.visualstudio.com)**.
2. Le site détecte ton OS → clique le gros bouton **« Download »**.
   - **🍎 Mac** : tu télécharges un `.zip`. Double-clique-le, puis **glisse l'application « Visual Studio Code » dans le dossier Applications**.
   - **🪟 Windows** : lance le `.exe`. Pendant l'installation, **coche** « Ajouter à PATH » et « Ouvrir avec Code » (pratique) → Install.
   - **🐧 Linux** : télécharge le `.deb` (Ubuntu/Debian) ou `.rpm` (Fedora), puis double-clique pour installer — ou via le terminal `sudo dpkg -i le-fichier.deb`.
3. Lance VS Code.

> 📸 *Capture décrite :* au premier lancement, VS Code affiche un écran de bienvenue (« Get Started »), une **barre verticale d'icônes à gauche** (fichiers, recherche, extensions…), et un thème sombre par défaut.

### Installer l'extension Python (recommandée)

1. Dans la barre de gauche, clique l'icône **Extensions** (quatre carrés, dont un qui se détache).
2. Dans la recherche, tape **`Python`**.
3. Installe l'extension **« Python » éditée par Microsoft** (la première, avec des millions de téléchargements) → bouton **Install**.
4. (Bonus) Installe aussi **« Jupyter »** de Microsoft : ça te permet d'ouvrir tes notebooks directement dans VS Code.

> 💡 **Optionnel mais conseillé.** L'extension Python ajoute la coloration, l'auto-complétion et la détection d'erreurs. Tu n'en as pas besoin aujourd'hui, mais ça te servira vite. Si tu manques de temps, garde ça pour plus tard.

---

## SQLite + DB Browser for SQLite 🗄️

SQLite est une **base de données dans un simple fichier** (extension `.db` ou `.sqlite`). **DB Browser for SQLite** est un logiciel gratuit avec une interface graphique pour l'ouvrir et écrire des requêtes **sans coder**.

> 💡 **Et SQLite lui-même ?** Tu n'as **rien à installer** : SQLite est déjà inclus dans Python (et souvent dans ton OS). DB Browser est juste la « fenêtre » pour le manipuler facilement.

### Installer DB Browser for SQLite

1. Va sur **[sqlitebrowser.org](https://sqlitebrowser.org)** → onglet/section **« Downloads »**.
2. Selon ton OS :
   - **🪟 Windows** : télécharge l'installateur **« standard installer for 64-bit »** (`.exe`) → lance-le → Next/Install.
   - **🍎 Mac** : télécharge le `.dmg`. Ouvre-le, **glisse l'icône DB Browser dans Applications**. Au 1er lancement, si macOS bloque (« développeur non identifié ») : **clic droit sur l'app → Ouvrir → Ouvrir**.
   - **🐧 Linux** : `sudo apt install sqlitebrowser` (Ubuntu/Debian) — c'est le plus simple.
3. Lance **DB Browser for SQLite**.

### Ouvrir une base et exécuter une requête

On va utiliser une base fournie avec la formation.

1. Dans DB Browser : bouton **« Ouvrir une base de données »** (Open Database).
2. Navigue jusqu'à **`ressources/datasets/`** et ouvre **`setup.sql`**… 
   > ⚠️ `setup.sql` est un **script**, pas une base. Pour créer la base depuis ce script : menu **Fichier → Importer → Base de données depuis un fichier SQL**, choisis `setup.sql`, nomme la base `ventes.db`. *(Si une vraie base `.db` t'est fournie, ouvre-la directement.)*
3. Une fois la base ouverte, va dans l'onglet **« Exécuter le SQL »** (Execute SQL).
4. Tape cette requête simple :
   ```sql
   SELECT name FROM sqlite_master WHERE type='table';
   ```
   Puis clique sur le **triangle ▶ « Exécuter »** (ou `Ctrl/Cmd + Entrée`). Tu vois la **liste des tables** de la base.
5. Essaie maintenant une vraie requête (adapte le nom de table affiché à l'étape précédente) :
   ```sql
   SELECT * FROM ventes LIMIT 5;
   ```
   → les **5 premières lignes** de la table s'affichent en bas. 🎉

> 🔑 `SELECT * FROM table LIMIT 5` = « montre-moi 5 lignes de cette table ». C'est **la** requête réflexe pour découvrir une base inconnue.

> ⚠️ **Si ça ne marche pas.**
> - **Mac « app endommagée / développeur non identifié »** : clic droit sur l'app → **Ouvrir** (au lieu de double-clic), confirme. À ne faire qu'une fois.
> - **« no such table »** : le nom de table est faux → relance d'abord la requête `sqlite_master` (étape 4) pour voir les vrais noms.
> - **Tu ne trouves pas le dossier `ressources/`** : demande au formateur le chemin exact des fichiers de formation sur ton poste.

🎥 *Vidéo de prise en main au §11.*

---

## Installer les bibliothèques Python du parcours 📦

Anaconda installe déjà beaucoup de bibliothèques, mais assurons-nous d'avoir **exactement** celles du parcours : `pandas`, `numpy`, `matplotlib`, `seaborn`, `scipy`, `openpyxl`.

> 💡 **Une « bibliothèque » (library), c'est quoi ?** Un ensemble d'outils Python tout prêts. `pandas` = manipuler des tableaux de données. `numpy` = calcul numérique. `matplotlib`/`seaborn` = graphiques. `scipy` = statistiques. `openpyxl` = lire/écrire des fichiers Excel `.xlsx`.

### Avec conda (recommandé si tu as Anaconda)

Dans ton terminal (Anaconda Prompt sur Windows), tape **une seule ligne** :

```bash
conda install pandas numpy matplotlib seaborn scipy openpyxl
```

Conda réfléchit quelques secondes, te montre la liste de ce qu'il va installer, et demande **« Proceed ([y]/n)? »** → tape **`y`** puis `Entrée`. Patiente. À la fin : `done`. ✅

### Avec pip (si tu as Miniconda ou pas Anaconda)

```bash
pip install pandas numpy matplotlib seaborn scipy openpyxl
```

> 💡 **conda ou pip ?** Avec Anaconda, **privilégie `conda install`** (meilleure cohérence). N'utilise `pip` que si `conda` ne trouve pas un paquet. **Évite de mélanger les deux** pour un même paquet.

### Vérifier que tout est là

Lance Python en mode interactif :

```bash
python
```

Puis, dans l'invite `>>>`, tape :

```python
import pandas, numpy, matplotlib, seaborn, scipy, openpyxl
print("Toutes les bibliothèques sont OK !")
```

Si tu vois le message **sans aucune erreur rouge**, c'est parfait. Quitte Python avec `exit()`.

> ⚠️ **Si ça ne marche pas.**
> - **`ModuleNotFoundError: No module named 'seaborn'`** : la bibliothèque citée manque → relance la commande d'installation du §9.1 pour **ce** paquet (ex. `conda install seaborn`).
> - **Lenteur extrême / « solving environment » qui tourne longtemps** : c'est normal pour conda, laisse-le finir (jusqu'à plusieurs minutes).

---

## Comptes outils BI 📊

Pour la partie tableaux de bord, on a besoin de comptes. (Le module **0.2 — Panorama des outils BI** approfondit l'usage ; ici on prépare juste les accès.)

### Créer un compte Looker Studio (gratuit, web, tous OS)

Looker Studio (ex-Google Data Studio) est **100 % gratuit, dans le navigateur, sur n'importe quel OS**. C'est l'outil BI principal de la Phase 0.

1. Il te faut un **compte Google** (Gmail). Tu n'en as pas ? Crée-en un sur **[accounts.google.com](https://accounts.google.com)**.
2. Va sur **[lookerstudio.google.com](https://lookerstudio.google.com)** et connecte-toi.
3. Accepte les conditions ; Looker peut demander ton **pays** et ton **secteur** (réponds « Formation/Éducation » par exemple).
4. Tu arrives sur la page d'accueil avec **« Créer »** en haut à gauche. C'est bon, **ton compte est prêt.** 🎉

> ✅ Pas besoin de créer un rapport maintenant — on le fera dans le module 0.2.

### Power BI : la contrainte à connaître ⚠️

> **Power BI Desktop n'existe PAS sur macOS ni Linux. C'est un logiciel Windows uniquement.**

Voici quoi faire selon ton OS :

| Ton OS | Ce que tu peux faire pour Power BI |
|---|---|
| **🪟 Windows** | Télécharge **Power BI Desktop** (gratuit) depuis le Microsoft Store. Tu as la version complète. |
| **🍎 Mac** | Pas de Desktop. Utilise **Power BI Service** dans le navigateur : **[app.powerbi.com](https://app.powerbi.com)** (version web). Ou plus tard, une **VM Parallels + Windows**. |
| **🐧 Linux** | Idem Mac : **Power BI Service web** uniquement. |

> 📌 **Pour tout comprendre sur la contrainte Power BI** (pourquoi le Nord de la France le demande malgré tout, les contournements détaillés, le marché de l'emploi local) → **lis l'étude dédiée : [l'étude de marché dédiée](etude-dataviz-nord-france.md)** et le **module 0.2**.

> 🎯 **À retenir.** En Phase 0, **personne n'installe Power BI Desktop.** On apprend les concepts BI sur **Looker Studio** (qui marche pour tout le monde). Power BI viendra dans les phases avancées.

---

## Vidéos d'auto-formation 🎥

> ⚠️ Les liens marqués **🔎 (recherche)** ouvrent une recherche YouTube : choisis la vidéo la plus récente et la mieux notée correspondant à ton OS. Les liens directs ci-dessous ont été sélectionnés en français — si une vidéo a disparu, utilise la recherche associée.

| Sujet | Langue | Lien | Ce que tu y apprends |
|---|---|---|---|
| Installer Anaconda / Python (data science) | 🇫🇷 FR | [Voir](https://www.youtube.com/watch?v=t-oRdktz5JQ) | Installation d'Anaconda pour démarrer en data — pas à pas |
| Installer Anaconda sur Mac **et** Windows | 🇫🇷 FR | [Voir](https://www.youtube.com/watch?v=1IV04g6SH3E) | Couvre les deux OS — pratique si tu hésites sur ta version |
| Prise en main de Jupyter Notebook | 🇫🇷 FR | [Voir](https://www.youtube.com/watch?v=_dte_5L-exU) | Créer un notebook, exécuter des cellules — le geste de base |
| Débuter avec le terminal : commandes `cd` et `ls` | 🇫🇷 FR | [Voir (cd)](https://www.youtube.com/watch?v=khsCI-hLZXQ) · [Voir (ls)](https://www.youtube.com/watch?v=vcZJYvHVwKI) | Naviguer en ligne de commande sans stress |
| Prise en main de DB Browser for SQLite | 🇫🇷 FR | [Voir](https://www.youtube.com/watch?v=PCia6dev4mQ) | Ouvrir une base, écrire SELECT/JOIN dans l'interface |
| Installer SQLite + SQLite Browser | 🇫🇷 FR | [Voir](https://www.youtube.com/watch?v=C1I6RYr823s) | Installation et premier contact avec DB Browser |
| Installer Anaconda (autre tuto, si besoin) | 🇫🇷 FR | [🔎 Recherche](https://www.youtube.com/results?search_query=installer+anaconda+python+d%C3%A9butant+fran%C3%A7ais) | De secours, choisis selon ton OS |
| Installer VS Code + extension Python | 🇫🇷 FR | [🔎 Recherche](https://www.youtube.com/results?search_query=installer+vs+code+extension+python+d%C3%A9butant+fran%C3%A7ais) | Installer l'éditeur et l'extension Python |

---

## ✅ Checklist d'installation finale

Coche chaque case. **Tant que tout n'est pas vert, ne passe pas à la suite** (appelle le formateur sur les points bloqués).

- [ ] J'ai **téléchargé et installé Anaconda** pour mon OS.
- [ ] `python --version` affiche **Python 3.x** dans mon terminal.
- [ ] `conda --version` répond.
- [ ] Je sais **ouvrir mon terminal** et utiliser `pwd` / `ls` / `cd`.
- [ ] J'ai **lancé Jupyter** (`jupyter lab`), créé un notebook, exécuté une cellule avec `Maj + Entrée`.
- [ ] J'ai **installé VS Code** (+ extension Python, optionnel).
- [ ] J'ai **installé DB Browser for SQLite** et exécuté un `SELECT` sur une base.
- [ ] Les **6 bibliothèques** s'importent sans erreur (`pandas`, `numpy`, `matplotlib`, `seaborn`, `scipy`, `openpyxl`).
- [ ] J'ai un **compte Looker Studio** fonctionnel.
- [ ] Je connais la **contrainte Power BI** pour mon OS.
- [ ] ⭐ **Mon notebook « hello data » du §13 s'exécute jusqu'au bout** (la vraie preuve que tout marche).

---

## ⭐ Vérification finale — le notebook « hello data »

C'est **le test ultime** : si ce notebook tourne, ton atelier est opérationnel et tu es prêt(e) pour toute la formation.

### Étapes

1. Lance **JupyterLab** (`jupyter lab` dans le terminal).
2. Crée un **nouveau notebook Python 3**, nomme-le **`hello-data`**.
3. Dans la **cellule 1**, vérifie que les bibliothèques se chargent (`Maj + Entrée`) :
   ```python
   import pandas as pd
   import numpy as np
   import matplotlib.pyplot as plt
   import seaborn as sns
   print("Bibliothèques chargées. Version pandas :", pd.__version__)
   ```
4. Dans la **cellule 2**, charge le vrai fichier de ventes et affiche les premières lignes :
   ```python
   # Adapte le chemin si besoin (voir l'encadré ci-dessous)
   df = pd.read_csv("../../../ressources/datasets/ventes_magasins.csv")
   df.head()
   ```
5. Dans la **cellule 3**, regarde la taille et un mini-graphique :
   ```python
   print("Le fichier contient", df.shape[0], "lignes et", df.shape[1], "colonnes.")
   df["categorie"].value_counts().plot(kind="bar")
   plt.title("Nombre de ventes par catégorie")
   plt.show()
   ```

### Résultat attendu

- La cellule 1 affiche : `Bibliothèques chargées. Version pandas : 2.x.x`.
- La cellule 2 affiche un **tableau de 5 lignes** avec les colonnes `date, ville, type, categorie, produit, quantite, prix_unitaire, remise, montant, marge, client_id`.
- La cellule 3 affiche le **nombre de lignes/colonnes** et un **graphique à barres** des ventes par catégorie. 🎉

> 🎉 **Si tu vois le tableau ET le graphique : FÉLICITATIONS.** Ton environnement Data Analyst est 100 % opérationnel. Tu peux attaquer la formation sereinement.

> ⚠️ **Si ça ne marche pas — le chemin du fichier (`FileNotFoundError`).**
> C'est l'erreur n°1, et elle est **facile** à régler. Le chemin `../../../ressources/datasets/ventes_magasins.csv` dépend de **l'endroit d'où tu as lancé Jupyter**.
> - **Solution simple** : place une **copie** de `ventes_magasins.csv` dans le **même dossier** que ton notebook, puis remplace la ligne par :
>   ```python
>   df = pd.read_csv("ventes_magasins.csv")
>   ```
> - **Pour vérifier où Jupyter te place**, exécute dans une cellule :
>   ```python
>   import os; print(os.getcwd())   # affiche ton dossier courant
>   print(os.listdir())             # liste les fichiers visibles
>   ```
>   Puis ajuste le chemin pour atteindre `ventes_magasins.csv`.

> ⚠️ **Autres erreurs possibles.**
> - **`UnicodeDecodeError` / accents bizarres** : ajoute l'encodage → `pd.read_csv("...", encoding="utf-8")` (ou `"latin-1"` si besoin).
> - **`NameError: name 'pd' is not defined`** : tu as sauté la cellule 1 → exécute-la d'abord (l'ordre des cellules compte !).

---

## À retenir 🧠

- **Anaconda** installe **Python + Jupyter + les bibliothèques data** en une fois. On vérifie avec `python --version`.
- Le **terminal** se résume à 3 gestes : `pwd` (où suis-je), `ls` (qu'y a-t-il ici), `cd` (me déplacer). Sur **Windows**, on travaille dans **Anaconda Prompt**.
- **Jupyter** : on écrit du code dans une **cellule**, on fait **`Maj + Entrée`**, le résultat s'affiche dessous.
- **VS Code** est l'éditeur pour les scripts/projets ; l'**extension Python** est un plus.
- **DB Browser for SQLite** ouvre une base et exécute des requêtes (`SELECT * FROM table LIMIT 5`) **sans coder**.
- **Looker Studio** (gratuit, web, tous OS) est l'outil BI de départ ; **Power BI Desktop = Windows uniquement** (Mac/Linux → Power BI Service web) — détails dans l'étude Nord & le module 0.2.
- Les **6 bibliothèques** du parcours : `pandas`, `numpy`, `matplotlib`, `seaborn`, `scipy`, `openpyxl`.
- **La vraie validation = le notebook « hello data »** qui charge `ventes_magasins.csv` et affiche `.head()`. S'il tourne, ton atelier est prêt. 🚀
