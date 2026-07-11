# 01 — Build et Publication : EAS Build, App Stores

## Vue d'ensemble du processus de déploiement

```
Développement local (Expo Go)
         ↓
  Development Build (EAS Build --profile development)
         ↓
    Tests internes (EAS Build --profile preview)
         ↓
  Production Build (EAS Build --profile production)
         ↓
  Soumission automatique (EAS Submit)
         ↓
  App Store (iOS) / Google Play (Android)
```

---

## EAS — Expo Application Services

EAS est la plateforme cloud d'Expo pour builder, soumettre et mettre à jour les applications. Elle permet de builder des `.ipa` (iOS) et `.aab`/`.apk` (Android) sans avoir Xcode ou Android Studio configurés localement.

```bash
# Installer EAS CLI
npm install -g eas-cli

# Se connecter à votre compte Expo
eas login

# Vérifier la configuration
eas whoami
```

---

## Configuration du projet

### app.json — configuration complète

```json
{
  "expo": {
    "name": "Mon Application",
    "slug": "mon-application",
    "version": "1.0.0",
    "runtimeVersion": {
      "policy": "sdkVersion"
    },
    "orientation": "portrait",
    "icon": "./assets/images/icon.png",
    "scheme": "monapp",
    "userInterfaceStyle": "automatic",
    "splash": {
      "image": "./assets/images/splash.png",
      "resizeMode": "contain",
      "backgroundColor": "#ffffff"
    },
    "assetBundlePatterns": [
      "**/*"
    ],
    "ios": {
      "supportsTablet": false,
      "bundleIdentifier": "com.monentreprise.monapplication",
      "buildNumber": "1",
      "infoPlist": {
        "NSCameraUsageDescription": "Utilisé pour scanner les QR codes.",
        "NSLocationWhenInUseUsageDescription": "Utilisé pour afficher votre position."
      },
      "config": {
        "googleMapsApiKey": "VOTRE_CLE_ICI"
      }
    },
    "android": {
      "package": "com.monentreprise.monapplication",
      "versionCode": 1,
      "adaptiveIcon": {
        "foregroundImage": "./assets/images/adaptive-icon.png",
        "backgroundColor": "#ffffff"
      },
      "permissions": [
        "android.permission.CAMERA",
        "android.permission.ACCESS_FINE_LOCATION"
      ],
      "config": {
        "googleMaps": {
          "apiKey": "VOTRE_CLE_ICI"
        }
      }
    },
    "web": {
      "bundler": "metro",
      "output": "static"
    },
    "plugins": [
      "expo-router",
      "expo-camera",
      [
        "expo-notifications",
        {
          "icon": "./assets/images/notification-icon.png",
          "color": "#007AFF"
        }
      ]
    ],
    "extra": {
      "eas": {
        "projectId": "votre-project-id-eas"
      }
    }
  }
}
```

**Champs critiques :**
- `bundleIdentifier` (iOS) / `package` (Android) : reverse-domain, **immuable** une fois publié
- `buildNumber` (iOS) / `versionCode` (Android) : doit être incrémenté à chaque soumission
- `version` : version affichée aux utilisateurs (ex: "1.2.3")
- `projectId` : obtenu après `eas init`

---

## eas.json — Profils de build

```json
{
  "cli": {
    "version": ">= 5.0.0",
    "appVersionSource": "local"
  },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal",
      "ios": {
        "simulator": true
      },
      "android": {
        "buildType": "apk",
        "gradleCommand": ":app:assembleDebug"
      },
      "env": {
        "APP_ENV": "development",
        "API_URL": "http://192.168.1.100:8000"
      }
    },
    "preview": {
      "distribution": "internal",
      "ios": {
        "simulator": false
      },
      "android": {
        "buildType": "apk"
      },
      "env": {
        "APP_ENV": "staging",
        "API_URL": "https://staging-api.monapp.com"
      }
    },
    "production": {
      "ios": {
        "credentialsSource": "remote"
      },
      "android": {
        "buildType": "app-bundle",
        "credentialsSource": "remote"
      },
      "env": {
        "APP_ENV": "production",
        "API_URL": "https://api.monapp.com"
      }
    }
  },
  "submit": {
    "production": {
      "ios": {
        "appleId": "votre@apple.com",
        "ascAppId": "1234567890",
        "appleTeamId": "XXXXXXXXXX"
      },
      "android": {
        "serviceAccountKeyPath": "./service-account.json",
        "track": "internal"
      }
    }
  }
}
```

**Profils recommandés :**
- `development` : pour développer avec le Development Client (simulateur ou device)
- `preview` : APK/IPA distribué en interne via QR code pour les tests
- `production` : `.aab` (Android App Bundle) et `.ipa` signés pour les stores

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Terminal pendant un `eas build --profile preview --platform android` — montrer la progression du build : upload des sources, build sur les serveurs Expo, téléchargement de l'APK résultant. Montrer aussi le dashboard EAS (expo.dev) avec l'historique des builds
> **Expliquer :** EAS Build exécute le build dans le cloud sur des machines macOS (pour iOS) et Linux (pour Android). Pour iOS, il gère automatiquement les certificats de signature (Provisioning Profiles, Distribution Certificates) via le compte Apple Developer. Pour Android, il génère et stocke le keystore. Montrer les durées typiques : 10-20 minutes pour un premier build, moins ensuite grâce au cache.
---

## Lancer un build EAS

```bash
# Initialiser EAS dans le projet (première fois)
eas init

# Build Android (APK pour tests internes)
eas build --profile preview --platform android

# Build iOS (simulateur)
eas build --profile development --platform ios --local
# ou sur le cloud
eas build --profile preview --platform ios

# Build les deux plateformes
eas build --profile production --platform all

# Build local (nécessite Xcode/Android Studio)
eas build --profile production --platform ios --local
```

### Variables d'environnement sécurisées

```bash
# Ne jamais mettre des secrets dans eas.json ou app.json !
# Utiliser les secrets EAS :

# Ajouter un secret (stocké côté serveur Expo)
eas secret:create --scope project --name SENTRY_DSN --value "https://xxx@sentry.io/xxx"
eas secret:create --scope project --name STRIPE_KEY --value "sk_live_..."

# Lister les secrets
eas secret:list

# Utilisation dans le code (via expo-constants)
import Constants from 'expo-constants';
const sentryDsn = Constants.expoConfig?.extra?.sentryDsn;
```

---

## Icônes et Splash Screen

### Spécifications des icônes

```
icon.png (iOS + Android)
└── 1024x1024 px minimum
└── Fond plein (pas de transparence pour iOS)
└── Pas de coins arrondis (iOS les ajoute automatiquement)

adaptive-icon.png (Android uniquement)
└── 1024x1024 px
└── Zone safe : 672x672 px au centre (le reste peut être rogné)
└── Peut avoir un fond séparé (backgroundColor dans app.json)

splash.png
└── 1284x2778 px recommandé (iPhone 12 Pro Max portrait)
└── Le logo/contenu important dans les 1000x1000 px centraux
└── backgroundColor dans app.json pour les bords
```

### Générer les icônes automatiquement

```bash
# Avec l'outil Expo
npx expo-optimize

# Ou avec un outil tiers
# https://appicon.co/ — génère toutes les tailles
# https://makeappicon.com/
```

---

## Gestion des versions

```bash
# Incrémenter la version automatiquement
eas build:version:set --platform ios --version-code 2
eas build:version:set --platform android --version-code 2

# Ou dans app.json :
# ios.buildNumber → "2" (string !)
# android.versionCode → 2 (number)
# version → "1.0.1" (version utilisateur)
```

**Règles des stores :**
- `versionCode` / `buildNumber` doit augmenter à chaque soumission (même si la version utilisateur ne change pas)
- La `version` peut rester identique pour un hotfix
- Ne jamais réutiliser un `versionCode`/`buildNumber` déjà soumis

---

## EAS Submit — Soumission automatique

```bash
# Soumettre le dernier build iOS à l'App Store Connect
eas submit --platform ios

# Soumettre un build spécifique
eas submit --platform android --id BUILD_ID

# Soumettre les deux
eas submit --platform all

# Le processus de soumission EAS gère :
# - iOS : upload vers App Store Connect, TestFlight automatique
# - Android : upload vers Google Play Console (track configuré dans eas.json)
```

---

## Préparer sa soumission App Store (iOS)

### Prérequis

1. **Compte Apple Developer** : 99$/an
2. **Bundle ID** enregistré sur developer.apple.com
3. **App créée** sur App Store Connect (appstoreconnect.apple.com)
4. **Certificats** gérés automatiquement par EAS

### Informations requises pour la soumission

```
Métadonnées de l'app :
├── Nom de l'app (max 30 caractères)
├── Sous-titre (max 30 caractères)
├── Description (max 4000 caractères)
├── Mots-clés (max 100 caractères)
├── URL de support
├── URL de politique de confidentialité (OBLIGATOIRE)
├── Catégorie principale
└── Captures d'écran (obligatoires pour iPhone 6.5", 5.5")

Informations techniques :
├── Indications de contenu (évaluation d'âge)
├── Chiffrement (questions sur l'utilisation de crypto)
├── Droit de revue Apple
└── Notes pour le reviewer (contexte, compte de test...)
```

### Captures d'écran requises

```
iPhone 6.5" (iPhone 12 Pro Max) : 1284 × 2778 px — OBLIGATOIRE
iPhone 5.5" (iPhone 8 Plus) : 1242 × 2208 px — OBLIGATOIRE
iPad Pro 12.9" (3e gen+) : 2048 × 2732 px — si universelle
iPad Pro 12.9" (2e gen) : 2048 × 2732 px
```

---

## Préparer sa soumission Google Play (Android)

### Prérequis

1. **Compte Google Play Developer** : 25$ (paiement unique)
2. **App créée** sur play.google.com/console
3. **Keystore** géré automatiquement par EAS

### Informations requises

```
Fiche Play Store :
├── Titre (max 50 caractères)
├── Description courte (max 80 caractères)
├── Description complète (max 4000 caractères)
├── Icône 512x512 px
├── Bannière 1024x500 px
├── Captures d'écran (2 min, 8 max par type de device)
├── Politique de confidentialité (OBLIGATOIRE)
└── Questionnaire Sécurité des données

Tracks de publication :
├── Internal (équipe interne, max 100 testeurs)
├── Closed Testing (alpha, liste d'emails)
├── Open Testing (beta, Google Play public)
└── Production (sortie publique)
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Dashboard App Store Connect ou Google Play Console — montrer la structure d'une soumission : métadonnées, captures d'écran, historique des versions. Montrer aussi le processus de review (statut "En cours de révision" → "Approuvée")
> **Expliquer :** La review Apple (App Store) prend généralement 24-72h, parfois plus pour les nouvelles apps. Google Play est plus rapide (quelques heures à 3 jours). Les principaux motifs de rejet Apple : interface non conforme aux Human Interface Guidelines, crash au démarrage, métadonnées incomplètes, permissions non justifiées, contenu inapproprié. Google est plus permissif mais vérifie aussi la politique de confidentialité.
---

## EAS Update — Mises à jour OTA (Over-The-Air)

EAS Update permet de pousser des mises à jour JavaScript sans repasser par les stores.

**Limitation importante :** Ne peut pas modifier le code natif (nouvelles permissions, nouveaux modules natifs). Uniquement le JavaScript/TypeScript et les assets.

```bash
# Installer expo-updates
npx expo install expo-updates

# Publier une mise à jour OTA
eas update --branch production --message "Correction bug affichage profil"

# Sur le canal de preview
eas update --branch preview --message "Nouvelle fonctionnalité recherche"
```

```json
// app.json — configuration EAS Update
{
  "expo": {
    "updates": {
      "url": "https://u.expo.dev/votre-project-id",
      "enabled": true,
      "fallbackToCacheTimeout": 0,
      "checkAutomatically": "ON_LOAD"
    },
    "runtimeVersion": {
      "policy": "sdkVersion"
    }
  }
}
```

```typescript
// Vérifier les mises à jour manuellement
import * as Updates from 'expo-updates';

async function verifierMiseAJour() {
  if (__DEV__) return; // Pas de MAJ en développement

  try {
    const update = await Updates.checkForUpdateAsync();

    if (update.isAvailable) {
      await Updates.fetchUpdateAsync();
      Alert.alert(
        'Mise à jour disponible',
        'Redémarrez l\'application pour appliquer la mise à jour.',
        [
          { text: 'Plus tard' },
          { text: 'Redémarrer', onPress: () => Updates.reloadAsync() },
        ]
      );
    }
  } catch (e) {
    console.error('Erreur vérification MAJ:', e);
  }
}
```

---

## Sécurité avant publication

### Liste de vérification

```
Sécurité :
├── ✓ Aucune clé API dans le code source
├── ✓ Variables d'environnement via EAS Secrets
├── ✓ Tokens stockés dans SecureStore (pas AsyncStorage)
├── ✓ HTTPS uniquement (pas d'HTTP en production)
├── ✓ Certificate pinning si données sensibles
└── ✓ Obfuscation du JS (activée par défaut avec Hermes)

Qualité :
├── ✓ Testé sur iOS et Android
├── ✓ Testé sur petits écrans (iPhone SE) et grands (iPad)
├── ✓ Mode sombre vérifié
├── ✓ Accessibilité (VoiceOver/TalkBack) testée
├── ✓ Aucun console.log en production
└── ✓ Sentry ou équivalent configuré pour le monitoring

Légal :
├── ✓ Politique de confidentialité publiée
├── ✓ CGU si e-commerce
├── ✓ RGPD (consentement cookies/tracking si UE)
└── ✓ Permissions justifiées et minimales
```

### Retirer les console.log en production

```javascript
// babel.config.js
module.exports = function (api) {
  api.cache(true);
  return {
    presets: ['babel-preset-expo'],
    plugins: [
      // Supprimer les console.log en production
      ...(process.env.NODE_ENV === 'production'
        ? [['transform-remove-console', { exclude: ['error', 'warn'] }]]
        : []),
    ],
  };
};
```

```bash
npm install --save-dev babel-plugin-transform-remove-console
```

---

## Monitoring en production — Sentry

```bash
npx expo install @sentry/react-native sentry-expo
```

```typescript
// App.tsx
import * as Sentry from '@sentry/react-native';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  enabled: !__DEV__,  // Désactiver en développement
  tracesSampleRate: 0.2, // 20% des transactions tracées
  debug: false,
});

// Capturer une erreur manuellement
try {
  // ... code risqué
} catch (e) {
  Sentry.captureException(e);
  throw e;
}

// Ajouter du contexte utilisateur
Sentry.setUser({ id: userId, email: userEmail });

// Breadcrumb (étape du parcours)
Sentry.addBreadcrumb({
  category: 'navigation',
  message: 'Écran Profil ouvert',
  level: 'info',
});
```

---

## Récapitulatif — Checklist de déploiement

```bash
# 1. Préparer le projet
npx expo-doctor       # Vérifier la compatibilité des packages
npx expo upgrade      # Mettre à jour si nécessaire

# 2. Incrémenter les versions
# app.json : version, buildNumber (iOS), versionCode (Android)

# 3. Builder
eas build --profile production --platform all

# 4. Tester le build preview d'abord !
eas build --profile preview --platform android
# Installer l'APK et tester

# 5. Soumettre
eas submit --platform all

# 6. Après approbation : EAS Update pour les petits correctifs
eas update --branch production --message "Correction bug"
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Dashboard EAS Build (expo.dev/accounts/[username]/projects/[slug]/builds) — montrer un build réussi avec le téléchargement du fichier, les logs complets, et la durée totale. Comparer avec un build en erreur pour montrer comment lire les logs.
> **Expliquer :** Les erreurs de build les plus courantes : dépendances incompatibles avec la version du SDK Expo (toujours utiliser `npx expo install` et non `npm install` pour les packages Expo), problèmes de certificats iOS (EAS gère ça automatiquement mais peut nécessiter une interaction), erreurs de compilation des modules natifs (souvent dues à des versions incompatibles). Montrer comment utiliser `eas build:list` et `eas build:view` pour debugger.
---

## Résumé des commandes EAS

| Commande | Description |
|----------|-------------|
| `eas init` | Initialiser EAS dans le projet |
| `eas build --profile preview --platform android` | Build de test Android (APK) |
| `eas build --profile production --platform all` | Build de production (les deux) |
| `eas submit --platform ios` | Soumettre à l'App Store |
| `eas submit --platform android` | Soumettre au Play Store |
| `eas update --branch production` | Mise à jour OTA |
| `eas secret:create` | Ajouter une variable secrète |
| `eas build:list` | Historique des builds |
| `eas credentials` | Gérer les certificats/keystores |
| `eas device:create` | Enregistrer un device pour les profils de développement |
