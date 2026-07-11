# 01 — Introduction à React Native

## Qu'est-ce que React Native ?

React Native est un framework créé par Meta (Facebook) en 2015 qui permet de créer des applications mobiles **natives** pour iOS et Android en utilisant JavaScript et React. Contrairement à des solutions comme Cordova ou Ionic qui encapsulent une WebView, React Native traduit vos composants React en composants UI natifs réels.

```
Votre code JavaScript
        ↓
  Bridge / JSI (JavaScript Interface)
        ↓
  Composants natifs iOS/Android
```

**Ce que React Native N'EST PAS :**
- Ce n'est pas une WebView (contrairement à Ionic/Cordova)
- Ce n'est pas du code natif pur (Swift/Kotlin)
- Ce n'est pas React DOM (pas de `div`, `span`, `p`...)

**Ce que React Native EST :**
- Du React avec des composants mobiles (`View`, `Text`, `Image`...)
- Une couche de communication avec les APIs natives du téléphone
- Une solution véritablement multiplateforme (iOS + Android)

---

## React Native vs les alternatives

| Solution | Langage | Rendu | Performances | Accès natif |
|----------|---------|-------|--------------|-------------|
| React Native | JS/TS | Composants natifs | Bonnes | Oui (via modules) |
| Flutter | Dart | Canvas propriétaire | Excellentes | Oui |
| Ionic | JS/TS | WebView | Moyennes | Via plugins |
| Xamarin | C# | Composants natifs | Bonnes | Oui |
| Swift/Kotlin | Swift/Kotlin | Natif pur | Excellentes | Natif |

**Pourquoi choisir React Native ?**
- Vous connaissez déjà React → la courbe d'apprentissage est faible
- Partage de code entre iOS, Android et parfois le web (React Native Web)
- Large écosystème npm disponible
- Hot Reload pour un développement rapide
- Utilisé en production : Facebook, Instagram, Shopify, Discord, Airbnb (historiquement)

---

## Expo vs React Native Bare

C'est la première décision à prendre. Il existe deux façons de démarrer un projet React Native.

### Expo (recommandé pour débuter et pour la plupart des projets)

Expo est une plateforme construite au-dessus de React Native qui simplifie considérablement le développement.

**Avantages :**
- Pas besoin d'Xcode ou Android Studio pour commencer
- SDK riche : caméra, GPS, notifications, capteurs... tout inclus
- Expo Go : tester sur vrai device en scannant un QR code
- EAS (Expo Application Services) : build cloud sans configuration
- OTA updates (mise à jour sans passer par les stores)

**Inconvénients :**
- Légèrement plus lourd (SDK embarqué)
- Certains modules natifs très spécifiques ne sont pas disponibles (rare)
- Jusqu'à récemment, le mode "managed" limitait les modules natifs custom

```bash
# Créer un projet Expo
npx create-expo-app mon-application
cd mon-application
npx expo start
```

### Bare React Native (React Native CLI)

Projet React Native sans couche Expo, avec accès complet au code natif iOS/Android.

**Avantages :**
- Contrôle total sur le code natif
- Tous les modules natifs disponibles
- Taille de l'app optimisée

**Inconvénients :**
- Xcode obligatoire pour iOS (Mac uniquement)
- Android Studio obligatoire
- Configuration plus complexe
- Expo SDK non disponible nativement (certains packages peuvent être ajoutés)

```bash
# Créer un projet React Native bare
npx react-native init MonApplication
cd MonApplication
npx react-native run-ios     # Mac uniquement
npx react-native run-android
```

### Recommandation pour cette formation

On utilisera **Expo** tout au long de la formation. C'est le choix le plus productif pour 90% des projets. Si un jour vous avez besoin d'un module natif non supporté, il est possible d'éjecter vers un projet bare ou d'utiliser les "Development Builds" d'Expo.

---

## Architecture interne de React Native

Comprendre l'architecture aide à comprendre pourquoi certaines choses fonctionnent différemment du web.

### Ancienne architecture (Bridge)

```
Thread JS          Bridge (asynchrone)       Thread Natif
-----------        -------------------       ------------
JavaScript  ←───→  Sérialisation JSON  ←───→  iOS/Android
```

Le Bridge était un goulot d'étranglement : chaque communication entre JS et le natif nécessitait une sérialisation/désérialisation JSON asynchrone.

### Nouvelle architecture (JSI — JavaScript Interface)

React Native 0.71+ utilise une nouvelle architecture plus performante :

```
Thread JS          JSI (synchrone)           Thread Natif
-----------        ---------------           ------------
JavaScript  ←───→  C++ direct calls  ←───→  iOS/Android
```

- **JSI** : appels synchrones directs via C++
- **Fabric** : nouveau système de rendu
- **TurboModules** : chargement paresseux des modules natifs

Pour les développeurs, cette différence est transparente dans la majorité des cas.

---

## Metro Bundler

Metro est le bundler JavaScript de React Native, l'équivalent de Webpack/Vite pour le web.

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Terminal après `npx expo start` — montrer la sortie complète du Metro bundler avec le QR code, le menu interactif, et les logs de connexion d'un device
> **Expliquer :** Le Metro bundler surveille les fichiers, transforme le JSX/TypeScript, et sert le bundle JavaScript à l'application. Pointer les informations clés : port 8081, QR code, commandes clavier disponibles (r = reload, m = menu)
---

**Ce que fait Metro :**
1. Résout les dépendances (`import` / `require`)
2. Transforme JSX → JavaScript
3. Transforme TypeScript → JavaScript
4. Sert le bundle via HTTP (port 8081 par défaut)
5. Surveille les modifications et envoie des mises à jour (Fast Refresh)

**Commandes utiles dans le terminal Metro :**

| Touche | Action |
|--------|--------|
| `r` | Reload (recharge l'app) |
| `m` | Ouvrir le menu développeur |
| `j` | Ouvrir le debugger JavaScript |
| `a` | Ouvrir sur Android |
| `i` | Ouvrir sur iOS |

---

## Installer et configurer un projet Expo

### Étape 1 : Créer le projet

```bash
# Avec TypeScript (recommandé)
npx create-expo-app mon-app --template blank-typescript

# Ou JavaScript simple
npx create-expo-app mon-app --template blank

# Ou avec un template de navigation intégré
npx create-expo-app mon-app --template tabs
```

### Étape 2 : Structure du projet généré

```
mon-app/
├── app/                    # Si template tabs (Expo Router)
│   ├── (tabs)/
│   │   ├── index.tsx
│   │   └── explore.tsx
│   └── _layout.tsx
├── assets/                 # Images, fonts, icônes
│   ├── images/
│   │   ├── icon.png
│   │   └── splash.png
│   └── fonts/
├── components/             # Composants réutilisables
├── constants/              # Couleurs, dimensions...
├── hooks/                  # Custom hooks
├── app.json                # Configuration Expo
├── babel.config.js         # Configuration Babel
├── package.json
├── tsconfig.json           # Si TypeScript
└── App.tsx                 # Point d'entrée principal
```

### Étape 3 : Lancer le serveur de développement

```bash
cd mon-app
npx expo start
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Téléphone physique avec Expo Go ouvert — scanner le QR code depuis le terminal, montrer l'application qui se charge en direct sur le device
> **Expliquer :** Insister sur le fait que le code tourne en JS sur le device, pas dans un navigateur. Montrer que le téléphone et la machine doivent être sur le même réseau WiFi. Montrer aussi l'option "tunnel" pour les réseaux restrictifs : `npx expo start --tunnel`
---

### Étape 4 : app.json — la configuration du projet

```json
{
  "expo": {
    "name": "Mon Application",
    "slug": "mon-application",
    "version": "1.0.0",
    "orientation": "portrait",
    "icon": "./assets/images/icon.png",
    "scheme": "monapp",
    "userInterfaceStyle": "automatic",
    "splash": {
      "image": "./assets/images/splash.png",
      "resizeMode": "contain",
      "backgroundColor": "#ffffff"
    },
    "ios": {
      "supportsTablet": true,
      "bundleIdentifier": "com.monentreprise.monapplication"
    },
    "android": {
      "adaptiveIcon": {
        "foregroundImage": "./assets/images/adaptive-icon.png",
        "backgroundColor": "#ffffff"
      },
      "package": "com.monentreprise.monapplication"
    },
    "web": {
      "bundler": "metro",
      "output": "static",
      "favicon": "./assets/images/favicon.png"
    },
    "plugins": [
      "expo-router"
    ],
    "experiments": {
      "typedRoutes": true
    }
  }
}
```

**Champs importants :**
- `slug` : identifiant unique sur Expo (minuscules, tirets)
- `scheme` : pour les deep links (`monapp://...`)
- `bundleIdentifier` (iOS) / `package` (Android) : identifiant unique sur les stores, en reverse-domain notation

---

## Premier composant React Native

Voici un composant "Hello World" pour comparer React DOM et React Native :

### React (Web)
```jsx
import React from 'react';

export default function App() {
  return (
    <div style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
      <h1>Hello, World!</h1>
      <p>Bienvenue sur le web</p>
    </div>
  );
}
```

### React Native
```jsx
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default function App() {
  return (
    <View style={styles.container}>
      <Text style={styles.titre}>Hello, World!</Text>
      <Text style={styles.sous_titre}>Bienvenue sur mobile</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#fff',
  },
  titre: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  sous_titre: {
    fontSize: 16,
    color: '#666',
    marginTop: 8,
  },
});
```

**Différences clés :**
- `div` → `View`
- `h1`, `p` → `Text` (tout texte DOIT être dans `<Text>`)
- `style` est un objet JS, pas du CSS string
- `StyleSheet.create()` pour définir les styles (optimisation)
- Pas de classes CSS, pas de sélecteurs

---

## Fast Refresh (Hot Reload)

Le Fast Refresh est une fonctionnalité qui met à jour automatiquement l'application lors de la sauvegarde d'un fichier, **sans perdre l'état** des composants.

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Côte à côte — éditeur de code et device/simulateur. Modifier le texte dans App.tsx, sauvegarder, et montrer la mise à jour instantanée sur le device
> **Expliquer :** Le Fast Refresh préserve l'état (valeurs useState) lors de modifications dans le body des composants. Il fait un rechargement complet uniquement quand on modifie le module racine ou quand on change les imports. C'est un gain de productivité énorme par rapport au développement natif pur.
---

```jsx
// Modifiez ce texte et sauvegardez → mis à jour instantanément sur le device
<Text>Changez ce texte et observez le Fast Refresh !</Text>
```

**Cas où Fast Refresh rechargera complètement :**
- Modification du fichier `App.tsx` lui-même (module racine)
- Ajout/suppression d'imports
- Erreur de syntaxe corrigée
- Utilisation de `// @refresh reset` en commentaire dans le fichier

---

## TypeScript avec React Native

Expo génère par défaut des projets TypeScript. C'est fortement recommandé.

```typescript
// types.ts — définir ses types
export interface Utilisateur {
  id: number;
  nom: string;
  email: string;
  age?: number; // optionnel
}

// Props typées
interface MonComposantProps {
  titre: string;
  sousTitre?: string;
  onPress: () => void;
}

// Composant avec types
import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';

const MonComposant: React.FC<MonComposantProps> = ({
  titre,
  sousTitre,
  onPress,
}) => {
  return (
    <View style={styles.container}>
      <Text style={styles.titre}>{titre}</Text>
      {sousTitre && <Text style={styles.sousTitre}>{sousTitre}</Text>}
      <TouchableOpacity style={styles.bouton} onPress={onPress}>
        <Text style={styles.boutonTexte}>Appuyer</Text>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: 16,
  },
  titre: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  sousTitre: {
    fontSize: 14,
    color: '#666',
  },
  bouton: {
    backgroundColor: '#007AFF',
    padding: 12,
    borderRadius: 8,
    marginTop: 8,
  },
  boutonTexte: {
    color: '#fff',
    textAlign: 'center',
    fontWeight: '600',
  },
});

export default MonComposant;
```

---

## Déboguer une application React Native

### React Native Debugger / Flipper

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Ouvrir le menu développeur sur le device (secouer l'appareil ou Cmd+D sur simulateur iOS / Cmd+M sur Android) — montrer les options disponibles : "Reload", "Debug JS Remotely", "Show Inspector", "Toggle Performance Monitor"
> **Expliquer :** Le menu développeur est votre porte d'entrée au débogage. Montrer comment l'inspecteur d'éléments fonctionne (similaire aux DevTools web). Expliquer la différence entre "Debug JS Remotely" (ouvre Chrome DevTools) et Flipper (outil dédié React Native)
---

**Options de débogage disponibles :**

```
Menu développeur (secouer le téléphone ou Cmd+D/Cmd+M)
├── Reload — rechargement complet
├── Debug JS Remotely — Chrome DevTools
├── Show Element Inspector — inspecter les composants
├── Toggle Performance Monitor — FPS, JS/UI thread
├── Enable Fast Refresh
└── Settings
```

**console.log dans React Native :**
```javascript
// Visible dans le terminal Metro
console.log('Valeur:', maVariable);
console.warn('Attention:', uneValeur);
console.error('Erreur:', erreur);
```

**React DevTools :**
```bash
# Installer les React DevTools standalone
npm install -g react-devtools
react-devtools
# Puis dans l'app, secouer → "Open React DevTools"
```

---

## Résumé des commandes Expo essentielles

```bash
# Démarrer le serveur de dev
npx expo start

# Démarrer uniquement pour Android
npx expo start --android

# Démarrer uniquement pour iOS
npx expo start --ios

# Mode tunnel (réseau restreint, WiFi d'entreprise)
npx expo start --tunnel

# Vider le cache et redémarrer
npx expo start --clear

# Installer un package Expo
npx expo install expo-camera

# Vérifier la compatibilité des packages
npx expo-doctor

# Mettre à jour le SDK Expo
npx expo upgrade
```

---

## Points clés à retenir

1. React Native utilise des **composants natifs réels**, pas une WebView
2. **Expo** simplifie le développement pour la majorité des projets
3. **Metro** est le bundler qui sert votre JS au device
4. **Fast Refresh** met à jour le code en temps réel sans perdre l'état
5. `div` → `View`, texte → `<Text>`, styles via `StyleSheet.create()`
6. Tout le contenu texte **DOIT** être dans un composant `<Text>`
7. `app.json` configure les métadonnées de l'application (icône, splash, permissions...)
