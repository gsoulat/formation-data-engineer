# 01 — Permissions : Caméra, Localisation, Notifications

## Pourquoi les permissions ?

Sur iOS et Android, les applications doivent demander explicitement l'autorisation de l'utilisateur pour accéder aux fonctionnalités sensibles du device : caméra, microphone, localisation, contacts, photos, notifications...

**Principes fondamentaux :**
1. Les permissions ne peuvent être demandées qu'au **moment où l'utilisateur en a besoin** (pas au lancement)
2. Sur iOS, une permission refusée est **définitive** dans l'app — l'utilisateur doit aller dans les Réglages
3. Sur Android (API 23+), les permissions peuvent être redemandées
4. Toujours proposer une **explication** avant de demander (pourquoi l'app a besoin de cette permission)

```
Flux recommandé :
1. L'utilisateur touche "Accéder à la caméra"
2. Vérifier si la permission est déjà accordée
3. Si non → expliquer pourquoi (custom UI)
4. Demander la permission système
5. Si refusée → afficher un message + lien vers les Réglages
```

---

## expo-permissions (SDK Expo)

Expo centralise les permissions via son SDK. Chaque module (`expo-camera`, `expo-location`...) exporte ses propres hooks de permissions.

```bash
npx expo install expo-camera expo-location expo-notifications
```

---

## Permissions Caméra

```tsx
import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Alert, Linking } from 'react-native';
import { Camera, useCameraPermissions } from 'expo-camera';

export default function DemandePermissionCamera() {
  const [permission, requestPermission] = useCameraPermissions();

  const handleDemanderPermission = async () => {
    if (permission?.canAskAgain === false) {
      // Permission définitivement refusée → rediriger vers les Réglages
      Alert.alert(
        'Permission requise',
        'Veuillez autoriser l\'accès à la caméra dans les Réglages.',
        [
          { text: 'Annuler', style: 'cancel' },
          { text: 'Ouvrir les Réglages', onPress: () => Linking.openSettings() },
        ]
      );
      return;
    }

    const resultat = await requestPermission();

    if (!resultat.granted) {
      Alert.alert(
        'Caméra refusée',
        'Sans accès à la caméra, cette fonctionnalité n\'est pas disponible.'
      );
    }
  };

  // Permission encore inconnue (en cours de résolution)
  if (!permission) {
    return <View />;
  }

  // Permission accordée → afficher la caméra
  if (permission.granted) {
    return <CameraInterface />;
  }

  // Permission non accordée → demander
  return (
    <View style={styles.container}>
      <Text style={styles.icone}>📸</Text>
      <Text style={styles.titre}>Accès à la caméra</Text>
      <Text style={styles.description}>
        Pour prendre des photos et scanner des codes, l'application a besoin
        d'accéder à votre caméra.
      </Text>
      <TouchableOpacity style={styles.bouton} onPress={handleDemanderPermission}>
        <Text style={styles.boutonTexte}>Autoriser l'accès</Text>
      </TouchableOpacity>
    </View>
  );
}

// États de la permission
// permission.status : 'undetermined' | 'granted' | 'denied'
// permission.granted : boolean
// permission.canAskAgain : boolean (false si refusée définitivement sur iOS)
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Sur iPhone réel — montrer la boîte de dialogue système iOS de demande de permission caméra ("MonApp veut accéder à votre appareil photo"), puis l'état dans les Réglages iOS → Confidentialité → Appareil Photo. Montrer aussi ce qui se passe quand on refuse puis qu'on essaie de ré-ouvrir la caméra.
> **Expliquer :** iOS n'affiche la boîte de dialogue système **qu'une seule fois**. Si l'utilisateur refuse, `canAskAgain` devient `false` et la seule solution est Réglages → MonApp → Appareil Photo. Sur Android, la boîte peut réapparaître plusieurs fois. Insister sur l'importance d'une UI explicative AVANT la demande système pour maximiser le taux d'acceptation.
---

## Permissions Localisation

```tsx
import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Alert, Linking } from 'react-native';
import * as Location from 'expo-location';

export default function DemandePermissionLocalisation() {
  const [statusFG, requestFG] = Location.useForegroundPermissions();
  const [statusBG, requestBG] = Location.useBackgroundPermissions();

  const demanderForeground = async () => {
    const { granted, canAskAgain } = await requestFG();

    if (!granted) {
      if (!canAskAgain) {
        Alert.alert(
          'Permission refusée',
          'Activez la localisation dans Réglages → MonApp → Localisation',
          [
            { text: 'Annuler' },
            { text: 'Réglages', onPress: () => Linking.openSettings() },
          ]
        );
      }
    }
  };

  const demanderBackground = async () => {
    // D'abord, la permission foreground est obligatoire
    if (!statusFG?.granted) {
      Alert.alert('Étape préalable', 'Veuillez d\'abord autoriser la localisation.');
      return;
    }
    await requestBG();
  };

  return (
    <View style={styles.container}>
      <Text style={styles.titre}>Permissions de localisation</Text>

      {/* Localisation en avant-plan */}
      <View style={styles.bloc}>
        <Text style={styles.label}>Localisation (pendant l'utilisation)</Text>
        <Text style={[styles.statut, statusFG?.granted ? styles.accorde : styles.refuse]}>
          {statusFG?.granted ? '✓ Accordée' : '✗ Non accordée'}
        </Text>
        <TouchableOpacity style={styles.bouton} onPress={demanderForeground}>
          <Text style={styles.boutonTexte}>Demander</Text>
        </TouchableOpacity>
      </View>

      {/* Localisation en arrière-plan (iOS : "Toujours") */}
      <View style={styles.bloc}>
        <Text style={styles.label}>Localisation en arrière-plan</Text>
        <Text style={[styles.statut, statusBG?.granted ? styles.accorde : styles.refuse]}>
          {statusBG?.granted ? '✓ Accordée' : '✗ Non accordée'}
        </Text>
        <TouchableOpacity
          style={[styles.bouton, !statusFG?.granted && styles.desactive]}
          onPress={demanderBackground}
          disabled={!statusFG?.granted}
        >
          <Text style={styles.boutonTexte}>Demander (arrière-plan)</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}
```

### Obtenir la position

```typescript
import * as Location from 'expo-location';

// Position actuelle (one-shot)
async function obtenirPosition() {
  const { granted } = await Location.getForegroundPermissionsAsync();
  if (!granted) throw new Error('Permission localisation refusée');

  // accuracy : Location.Accuracy.Lowest (1) à Location.Accuracy.BestForNavigation (6)
  const position = await Location.getCurrentPositionAsync({
    accuracy: Location.Accuracy.Balanced, // Bon compromis vitesse/précision
  });

  return {
    latitude: position.coords.latitude,
    longitude: position.coords.longitude,
    altitude: position.coords.altitude,
    precision: position.coords.accuracy, // En mètres
    vitesse: position.coords.speed,      // En m/s
    timestamp: position.timestamp,
  };
}

// Suivi de position en temps réel
async function suivrePosition(callback: (pos: Location.LocationObject) => void) {
  const abonnement = await Location.watchPositionAsync(
    {
      accuracy: Location.Accuracy.High,
      timeInterval: 5000,     // Minimum 5 secondes entre les mises à jour
      distanceInterval: 10,   // Ou minimum 10 mètres de déplacement
    },
    callback
  );

  // Retourner la fonction de nettoyage
  return () => abonnement.remove();
}

// Géocodage inversé (coordonnées → adresse)
async function adresseDepuisCoordonnees(lat: number, lon: number) {
  const [adresse] = await Location.reverseGeocodeAsync({ latitude: lat, longitude: lon });
  return {
    rue: adresse.street,
    ville: adresse.city,
    codePostal: adresse.postalCode,
    pays: adresse.country,
    adresseComplete: `${adresse.street}, ${adresse.postalCode} ${adresse.city}`,
  };
}

// Exemple d'utilisation dans un composant
export function CartePosition() {
  const [position, setPosition] = useState<Location.LocationObject | null>(null);
  const [adresse, setAdresse] = useState<string>('');

  useEffect(() => {
    let cleanup: (() => void) | undefined;

    const demarrer = async () => {
      try {
        const { granted } = await Location.requestForegroundPermissionsAsync();
        if (!granted) return;

        // Position initiale
        const pos = await Location.getCurrentPositionAsync({
          accuracy: Location.Accuracy.Balanced,
        });
        setPosition(pos);

        // Géocodage
        const addr = await adresseDepuisCoordonnees(
          pos.coords.latitude,
          pos.coords.longitude
        );
        setAdresse(addr.adresseComplete);

        // Suivi
        cleanup = await suivrePosition(setPosition);
      } catch (e) {
        console.error('Erreur localisation:', e);
      }
    };

    demarrer();
    return () => cleanup?.();
  }, []);

  return (
    <View style={{ padding: 16 }}>
      {position ? (
        <>
          <Text>Lat : {position.coords.latitude.toFixed(6)}</Text>
          <Text>Lon : {position.coords.longitude.toFixed(6)}</Text>
          <Text>Précision : ±{position.coords.accuracy?.toFixed(0)}m</Text>
          <Text>Adresse : {adresse}</Text>
        </>
      ) : (
        <ActivityIndicator />
      )}
    </View>
  );
}
```

---

## Permissions Notifications

```tsx
import * as Notifications from 'expo-notifications';
import { useEffect, useRef } from 'react';

// Configuration globale des notifications (dans App.tsx)
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,   // Afficher une alerte visuelle
    shouldPlaySound: true,   // Jouer un son
    shouldSetBadge: true,    // Mettre à jour le badge de l'icône
  }),
});

// Demander la permission
async function demanderPermissionNotifications(): Promise<boolean> {
  const { status: existant } = await Notifications.getPermissionsAsync();

  if (existant === 'granted') return true;

  const { status } = await Notifications.requestPermissionsAsync({
    ios: {
      allowAlert: true,
      allowSound: true,
      allowBadge: true,
      allowAnnouncements: true,
    },
  });

  return status === 'granted';
}

// Obtenir le token push (pour les notifications distantes)
async function obtenirTokenPush(): Promise<string | null> {
  const accorde = await demanderPermissionNotifications();
  if (!accorde) return null;

  // Nécessite un projectId Expo (dans app.json)
  const token = await Notifications.getExpoPushTokenAsync({
    projectId: 'votre-project-id-expo', // Trouvé dans app.json → expo.extra.eas.projectId
  });

  return token.data;
  // Format : ExponentPushToken[xxxxxxxxxxxxxxxxxxxxxx]
  // À envoyer à votre backend pour les notifications distantes
}

// Hook de gestion des notifications
export function useNotifications() {
  const notificationListener = useRef<Notifications.Subscription>();
  const responseListener = useRef<Notifications.Subscription>();

  useEffect(() => {
    // Notification reçue en avant-plan
    notificationListener.current = Notifications.addNotificationReceivedListener(
      (notification) => {
        console.log('Notification reçue:', notification.request.content);
      }
    );

    // L'utilisateur a tapé sur la notification
    responseListener.current = Notifications.addNotificationResponseReceivedListener(
      (response) => {
        const data = response.notification.request.content.data;
        console.log('Notification tappée, data:', data);
        // Naviguer vers l'écran correspondant
        // navigation.navigate('Detail', { id: data.articleId });
      }
    );

    return () => {
      notificationListener.current?.remove();
      responseListener.current?.remove();
    };
  }, []);
}
```

### Notifications locales planifiées

```typescript
import * as Notifications from 'expo-notifications';

// Notification immédiate
async function notifierImmediatement(titre: string, corps: string, data?: object) {
  await Notifications.scheduleNotificationAsync({
    content: {
      title: titre,
      body: corps,
      data: data ?? {},
      sound: 'default',
      badge: 1,
    },
    trigger: null, // null = immédiat
  });
}

// Notification dans 5 secondes
async function notifierDans5Secondes() {
  await Notifications.scheduleNotificationAsync({
    content: {
      title: 'Rappel !',
      body: 'N\'oubliez pas votre rendez-vous dans 30 minutes.',
    },
    trigger: {
      seconds: 5,
    },
  });
}

// Notification quotidienne à 9h
async function notifierQuotidien() {
  await Notifications.scheduleNotificationAsync({
    content: {
      title: 'Bonne journée !',
      body: 'Consultez les nouvelles du jour.',
    },
    trigger: {
      hour: 9,
      minute: 0,
      repeats: true,
    },
  });
}

// Notification à une date précise
async function notifierADate(date: Date, message: string) {
  await Notifications.scheduleNotificationAsync({
    content: {
      title: 'Rappel',
      body: message,
    },
    trigger: {
      date: date,
    },
  });
}

// Annuler toutes les notifications planifiées
async function annulerTout() {
  await Notifications.cancelAllScheduledNotificationsAsync();
}

// Annuler une notification spécifique
async function annuler(identifiant: string) {
  await Notifications.cancelScheduledNotificationAsync(identifiant);
}

// Obtenir toutes les notifications planifiées
async function listerPlanifiees() {
  return Notifications.getAllScheduledNotificationsAsync();
}
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Sur device réel — montrer la permission système iOS de notifications ("MonApp souhaite vous envoyer des notifications"), puis déclencher une notification locale depuis l'app, montrer la notification qui apparaît dans le centre de notifications même quand l'app est en arrière-plan
> **Expliquer :** Les simulateurs iOS et Android peuvent afficher des notifications locales. Cependant les notifications distantes (push) nécessitent un device réel car elles passent par les serveurs APNs (Apple) ou FCM (Google/Firebase). Montrer la différence entre notification reçue en avant-plan (interceptée par `addNotificationReceivedListener`) et en arrière-plan (apparaît comme une notification système standard).
---

## Autres permissions courantes

```typescript
// Permissions pour les modules moins courants

// Contacts
import * as Contacts from 'expo-contacts';
const { status } = await Contacts.requestPermissionsAsync();
const { data: contacts } = await Contacts.getContactsAsync({
  fields: [Contacts.Fields.Name, Contacts.Fields.PhoneNumbers],
});

// Microphone (pour l'enregistrement audio)
import { Audio } from 'expo-av';
const { status } = await Audio.requestPermissionsAsync();

// Bibliothèque photos
import * as MediaLibrary from 'expo-media-library';
const { status } = await MediaLibrary.requestPermissionsAsync();

// Stocker une image dans la galerie
await MediaLibrary.saveToLibraryAsync(uriLocaleImage);

// Calendrier
import * as Calendar from 'expo-calendar';
const { status } = await Calendar.requestCalendarPermissionsAsync();
```

---

## Déclaration des permissions dans app.json

Sur iOS et Android, certaines permissions doivent être déclarées **à l'avance** dans la configuration, même avant de les demander à l'exécution.

```json
{
  "expo": {
    "ios": {
      "infoPlist": {
        "NSCameraUsageDescription": "L'application utilise la caméra pour scanner des QR codes et prendre des photos.",
        "NSLocationWhenInUseUsageDescription": "La localisation est utilisée pour afficher les points d'intérêt proches de vous.",
        "NSLocationAlwaysAndWhenInUseUsageDescription": "La localisation en arrière-plan permet de vous notifier des offres quand vous êtes à proximité.",
        "NSMicrophoneUsageDescription": "Le microphone est utilisé pour l'enregistrement de messages vocaux.",
        "NSPhotoLibraryUsageDescription": "L'accès aux photos permet de choisir une image de profil.",
        "NSContactsUsageDescription": "L'accès aux contacts permet d'inviter vos proches.",
        "NSFaceIDUsageDescription": "Face ID est utilisé pour sécuriser l'accès à vos données.",
        "NSUserNotificationsUsageDescription": "Les notifications vous alertent des nouvelles activités."
      }
    },
    "android": {
      "permissions": [
        "CAMERA",
        "ACCESS_FINE_LOCATION",
        "ACCESS_COARSE_LOCATION",
        "ACCESS_BACKGROUND_LOCATION",
        "RECORD_AUDIO",
        "READ_EXTERNAL_STORAGE",
        "WRITE_EXTERNAL_STORAGE",
        "READ_CONTACTS",
        "VIBRATE",
        "RECEIVE_BOOT_COMPLETED"
      ]
    }
  }
}
```

**Règle iOS :** La description (`NSXxxUsageDescription`) doit être explicite et claire — Apple la vérifie lors de la revue de l'app. Une description générique comme "Utilisé pour les fonctionnalités de l'app" entraîne un rejet.

---

## Vérification de l'état des permissions au lancement

```typescript
// hooks/usePermissions.ts
import { useEffect, useState } from 'react';
import * as Location from 'expo-location';
import { useCameraPermissions } from 'expo-camera';
import * as Notifications from 'expo-notifications';

interface PermissionsState {
  camera: boolean;
  location: boolean;
  notifications: boolean;
}

export function usePermissions() {
  const [permissions, setPermissions] = useState<PermissionsState>({
    camera: false,
    location: false,
    notifications: false,
  });

  const verifier = async () => {
    const [camera, location, notifications] = await Promise.all([
      Camera.getCameraPermissionsAsync(),
      Location.getForegroundPermissionsAsync(),
      Notifications.getPermissionsAsync(),
    ]);

    setPermissions({
      camera: camera.granted,
      location: location.granted,
      notifications: notifications.granted,
    });
  };

  useEffect(() => {
    verifier();
  }, []);

  return { permissions, verifier };
}
```

---

## Récapitulatif — Bonnes pratiques

1. Demander les permissions **au bon moment** (contextuel, pas au démarrage)
2. Toujours **expliquer** pourquoi avant de demander
3. Gérer le cas `canAskAgain === false` → rediriger vers les Réglages
4. Déclarer toutes les permissions dans `app.json` avant le build
5. Sur iOS, les descriptions doivent être **claires et spécifiques**
6. Tester sur **device réel** (certaines permissions ne fonctionnent pas sur simulateur)
7. Les permissions biométriques (Face ID, Touch ID) nécessitent `expo-local-authentication`
