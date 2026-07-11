# Formation React Native

## Objectifs de la formation

Cette formation vous permettra de construire des applications mobiles multiplateformes (iOS et Android) avec React Native et Expo. Vous partirez de zéro pour arriver à publier une vraie application sur les stores.

## Prérequis

- JavaScript ES6+ (destructuring, async/await, modules)
- Bases de React (composants, hooks useState/useEffect, props)
- Node.js et npm/yarn installés
- Un smartphone iOS ou Android pour tester avec Expo Go

## Programme

| Module | Contenu | Durée estimée |
|--------|---------|---------------|
| Fondamentaux | Introduction, composants core, styles | 4h |
| Navigation | Stack, Tabs, Drawer | 2h |
| Données | API REST, stockage local | 3h |
| Natif | Permissions, caméra, GPS, notifications | 3h |
| Déploiement | EAS Build, stores | 2h |
| Exercices | Todo app, App météo | 4h |

**Total estimé : 18h de formation**

## Structure des fichiers

```
React-Native/
├── README.md                         ← Ce fichier
├── CHEATSHEET-react-native.md        ← Référence rapide
├── Fondamentaux/
│   ├── 01-introduction.md
│   ├── 02-composants-core.md
│   └── 03-styles.md
├── Navigation/
│   ├── 01-stack-navigation.md
│   └── 02-tab-drawer.md
├── Donnees/
│   ├── 01-api-fetch.md
│   └── 02-stockage-local.md
├── Natif/
│   ├── 01-permissions.md
│   └── 02-composants-natifs.md
├── Deploiement/
│   └── 01-build-publication.md
└── exercices/
    ├── exercice-01-todo-mobile.md
    └── exercice-02-app-meteo.md
```

## Outils à installer avant la formation

### Sur votre machine de développement

```bash
# Node.js (version 18 ou 20 LTS recommandée)
node --version

# Expo CLI global (optionnel mais pratique)
npm install -g expo-cli

# EAS CLI pour les builds
npm install -g eas-cli
```

### Sur votre smartphone

Télécharger **Expo Go** depuis :
- App Store (iOS)
- Google Play Store (Android)

### Optionnel — Simulateurs

- **iOS** : Xcode (Mac uniquement) — disponible sur l'App Store macOS
- **Android** : Android Studio avec un AVD (Android Virtual Device)

## Philosophie de la formation

React Native vous permet d'écrire **une seule codebase JavaScript/TypeScript** qui tourne sur iOS et Android. Le framework traduit vos composants React en composants natifs réels — ce n'est pas une WebView.

**Expo** simplifie considérablement l'expérience développeur, surtout pour débuter. On utilisera Expo tout au long de cette formation.

## Ressources officielles

- [Documentation React Native](https://reactnative.dev/docs/getting-started)
- [Documentation Expo](https://docs.expo.dev)
- [React Navigation](https://reactnavigation.org/docs/getting-started)
- [Expo SDK API Reference](https://docs.expo.dev/versions/latest/)
