# Étape 0 : Préparation de l'environnement

**Durée estimée :** 30-45 minutes  
**Difficulté :** ⭐ Facile

---

## 🎯 Objectifs de cette étape

À la fin de cette étape, vous aurez :

- ✅ Activé un trial Microsoft Fabric de 60 jours
- ✅ Créé un Workspace pour votre projet
- ✅ Configuré un repository GitHub
- ✅ Préparé votre environnement de travail

---

## 📋 Prérequis

Avant de commencer cette étape, assurez-vous d'avoir :

- 🌐 Un navigateur web moderne (Chrome, Edge, Firefox recommandés)
- 📧 Un compte Microsoft (personnel ou professionnel)
  - Si vous n'en avez pas, créez-en un gratuitement sur [account.microsoft.com](https://account.microsoft.com)
- 💻 Un compte GitHub
  - Si vous n'en avez pas, créez-en un sur [github.com](https://github.com)

---

## 🚀 Tâche 1 : Obtenir un trial Microsoft Fabric

### 1.1 - Accéder au portail Microsoft Fabric

1. **Ouvrez votre navigateur** et rendez-vous sur :
   ```
   https://app.fabric.microsoft.com
   ```

2. **Connectez-vous** avec votre compte Microsoft
   - Utilisez votre email et mot de passe
   - Si vous avez plusieurs comptes, choisissez celui que vous souhaitez utiliser pour ce projet

### 1.2 - Activer le trial Fabric

1. **Repérez l'icône de profil** en haut à droite de la page
   - C'est un cercle avec vos initiales ou votre photo

2. **Cliquez sur l'icône de profil** pour ouvrir le menu

3. **Sélectionnez "Start trial"** dans le menu déroulant
   - Si vous ne voyez pas cette option, cela signifie peut-être que vous avez déjà un trial actif

4. **Suivez les instructions à l'écran**
   - Acceptez les conditions d'utilisation
   - Confirmez l'activation du trial

5. **Vérifiez l'activation**
   - Une fois activé, vous devriez voir une mention "Trial" à côté de votre nom
   - Vous avez maintenant **60 jours d'accès gratuit** à Microsoft Fabric

> ⚠️ **Note importante** : Le trial Fabric offre une capacité limitée mais largement suffisante pour ce projet. Si votre trial expire avant la fin du projet, vous pouvez créer un nouveau compte Microsoft avec une autre adresse email.

### 1.3 - Vérification de l'accès

Pour vérifier que tout fonctionne :

1. **Cliquez sur l'icône de grille** (9 petits carrés) en haut à gauche
2. **Vous devriez voir toutes les expériences Fabric** :
   - Data Factory
   - Data Engineering
   - Data Warehouse
   - Data Science
   - Real-Time Analytics
   - Power BI

Si vous voyez toutes ces options, parfait ! Votre trial est bien activé.

---

## 🏢 Tâche 2 : Créer votre Workspace

Un Workspace dans Fabric est un espace de collaboration où vous allez créer et organiser tous vos artefacts (Lakehouses, Notebooks, Pipelines, Rapports, etc.).

### 2.1 - Naviguer vers les Workspaces

1. **Dans le menu latéral gauche**, cliquez sur **"Workspaces"**
   - C'est l'icône qui ressemble à des dossiers empilés

2. **Cliquez sur le bouton "+ New workspace"**
   - Il se trouve en haut de la liste des workspaces

### 2.2 - Configurer le Workspace

Une fenêtre de configuration s'ouvre. Remplissez les champs suivants :

1. **Name (Nom)** : `WindPowerAnalytics`
   - Vous pouvez choisir un autre nom si vous préférez
   - Le nom doit être unique dans votre organisation

2. **Description** : `Storage, processing and analysis of wind turbine data`
   - Ajoutez une description claire du projet

3. **Advanced (Avancé)** : Cliquez pour déployer cette section
   - **License mode** : Sélectionnez **"Trial"**
   - Cela garantit que vous utilisez votre capacité trial

4. **Cliquez sur "Apply"** pour créer le workspace

### 2.3 - Vérification

Une fois créé, vous devriez :

- Être automatiquement redirigé vers votre nouveau workspace vide
- Voir le nom `WindPowerAnalytics` en haut de la page
- Voir un message "This workspace is empty. Get started by adding items."

> 💡 **Conseil** : Prenez une capture d'écran de votre workspace vide. Vous pourrez la comparer à la fin du projet pour voir tout ce que vous aurez créé !

**📸 Capture d'écran à prendre :** Workspace vide avec le nom visible

---

## 🗂️ Tâche 3 : Préparer votre repository GitHub

Vous allez utiliser GitHub pour versionner vos notebooks et votre documentation.

### 3.1 - Créer un nouveau repository

1. **Connectez-vous à GitHub** : [github.com](https://github.com)

2. **Cliquez sur le bouton "+ New repository"**
   - Il se trouve en haut à droite, ou sur votre page de profil

3. **Configurez le repository** :
   - **Repository name** : `fabric-wind-power-pipeline`
   - **Description** : `Microsoft Fabric data pipeline for wind power analytics - Medallion architecture (Bronze/Silver/Gold)`
   - **Visibilité** : 
     - Choisissez **"Public"** si vous voulez le partager dans votre portfolio
     - Ou **"Private"** si vous préférez le garder privé
   - **Initialize this repository with** :
     - ✅ Cochez **"Add a README file"**
     - ✅ Sélectionnez **".gitignore"** : choisissez le template **"Python"**
     - Licence : Optionnel (vous pouvez choisir "MIT License" par exemple)

4. **Cliquez sur "Create repository"**

### 3.2 - Préparer la structure du repository

Vous allez maintenant créer la structure de dossiers pour organiser votre projet.

#### Option A : Via l'interface web GitHub (plus simple)

1. **Créez le dossier "notebooks"** :
   - Cliquez sur **"Add file" → "Create new file"**
   - Dans le champ de nom de fichier, tapez : `notebooks/.gitkeep`
   - Scrollez vers le bas et cliquez sur **"Commit new file"**

2. **Répétez l'opération** pour créer ces dossiers :
   - `documentation/.gitkeep`
   - `screenshots/.gitkeep`

> 💡 **Explication** : Le fichier `.gitkeep` est une convention pour garder les dossiers vides dans Git. Git ne suit pas les dossiers vides, donc on ajoute un fichier vide pour forcer Git à les conserver.

#### Option B : Via Git en ligne de commande (pour utilisateurs avancés)

Si vous avez Git installé localement :

```bash
# Cloner le repository
git clone https://github.com/votre-username/fabric-wind-power-pipeline.git
cd fabric-wind-power-pipeline

# Créer la structure de dossiers
mkdir -p notebooks/bronze notebooks/silver notebooks/gold
mkdir -p documentation
mkdir -p screenshots

# Créer des fichiers .gitkeep
touch notebooks/bronze/.gitkeep
touch notebooks/silver/.gitkeep
touch notebooks/gold/.gitkeep
touch documentation/.gitkeep
touch screenshots/.gitkeep

# Commiter la structure
git add .
git commit -m "chore: Initialize project structure"
git push
```

### 3.3 - Vérifier la structure

Retournez sur GitHub et vérifiez que vous avez cette structure :

```
fabric-wind-power-pipeline/
├── README.md
├── .gitignore
├── notebooks/
│   ├── bronze/
│   ├── silver/
│   └── gold/
├── documentation/
└── screenshots/
```

**📸 Capture d'écran à prendre :** Structure du repository GitHub

---

## 📝 Tâche 4 : Mettre à jour le README initial

Donnez un bon départ à votre documentation en mettant à jour le README.md.

### 4.1 - Éditer le README sur GitHub

1. **Cliquez sur le fichier "README.md"** dans votre repository

2. **Cliquez sur l'icône de crayon** (Edit this file) en haut à droite

3. **Remplacez le contenu** par le texte suivant :

```markdown
# Wind Power Analytics - Microsoft Fabric Pipeline

Pipeline de données end-to-end sur Microsoft Fabric pour l'analyse de la production d'énergie éolienne.

## 🎯 Objectifs

Ce projet implémente une architecture Medallion (Bronze/Silver/Gold) complète avec :
- Ingestion automatisée de données depuis GitHub
- Transformations PySpark et SQL
- Modèle dimensionnel (star schema)
- Orchestration avec Data Pipeline
- Visualisation dans Power BI

## 🏗️ Architecture

```
GitHub (CSV) → Bronze → Silver → Gold → Semantic Model → Power BI
```

## 📊 Technologies utilisées

- Microsoft Fabric
- Delta Lake
- PySpark
- SQL
- Power BI
- DAX

## 🚀 Statut

🔨 **En cours de développement**

---

*Projet réalisé dans le cadre d'une formation sur Microsoft Fabric*
*Date de début : 16 novembre 2025*
```

4. **Scrollez vers le bas** et cliquez sur **"Commit changes"**
   - Ajoutez un message de commit : `docs: Update README with project overview`

---

## ✅ Vérification de l'étape

Avant de passer à l'étape suivante, vérifiez que vous avez bien :

- [ ] ✅ Un trial Microsoft Fabric actif (60 jours)
- [ ] ✅ Un Workspace nommé `WindPowerAnalytics` créé dans Fabric
- [ ] ✅ Un repository GitHub `fabric-wind-power-pipeline` créé
- [ ] ✅ La structure de dossiers (notebooks, documentation, screenshots) présente dans le repo
- [ ] ✅ Le README.md mis à jour avec la description du projet
- [ ] ✅ 2 captures d'écran prises :
  - Workspace Fabric vide
  - Structure du repository GitHub

---

## 📸 Captures d'écran à conserver

Créez un dossier sur votre ordinateur pour stocker vos captures d'écran temporairement. Vous les uploaderez sur GitHub plus tard.

**Captures de cette étape :**
1. `00_fabric_trial_activated.png` - Page d'accueil Fabric avec mention "Trial"
2. `00_workspace_created.png` - Workspace WindPowerAnalytics vide
3. `00_github_repo_structure.png` - Structure du repository

---

## 🎓 Ce que vous avez appris

Dans cette étape, vous avez :

- ✅ Activé et configuré un environnement Microsoft Fabric
- ✅ Créé un Workspace pour organiser vos ressources
- ✅ Mis en place un repository GitHub avec une structure organisée
- ✅ Commencé à documenter votre projet dès le début

---

## ⚠️ Problèmes courants et solutions

### Problème 1 : "Je ne vois pas l'option Start trial"

**Cause possible :** Vous avez peut-être déjà un trial actif ou votre organisation a des restrictions.

**Solutions :**
- Vérifiez si vous avez déjà un trial actif (regardez en haut à droite)
- Essayez avec un compte Microsoft personnel différent
- Contactez votre administrateur IT si vous utilisez un compte professionnel

### Problème 2 : "Je ne peux pas créer de Workspace"

**Cause possible :** Problème de permissions ou de licence.

**Solutions :**
- Vérifiez que votre trial est bien activé
- Rafraîchissez la page et réessayez
- Déconnectez-vous et reconnectez-vous

### Problème 3 : "Git n'est pas installé sur ma machine"

**Solution :**
- Utilisez l'interface web de GitHub pour toutes les opérations (Option A)
- Ou téléchargez Git : [git-scm.com](https://git-scm.com)

---

## 🎯 Prochaine étape

Excellent travail ! Vous avez maintenant un environnement prêt pour commencer le développement.

➡️ **Passez à l'étape suivante :** [Étape 1 : Création des Lakehouses](Etape_1_Creation_Lakehouses.md)

Dans la prochaine étape, vous allez créer les 3 Lakehouses qui constituent les couches Bronze, Silver et Gold de votre architecture.

---

*Étape 0 complétée ✅*  
*Temps estimé passé : 30-45 minutes*
