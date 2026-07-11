# 02 — Composants Natifs : Caméra, GPS, Notifications, Image Picker

## Vue d'ensemble des modules Expo

Expo SDK fournit des modules qui encapsulent les APIs natives iOS/Android. Cette approche évite d'avoir à écrire du Swift/Kotlin tout en donnant accès aux fonctionnalités natives réelles.

```bash
# Installer tous les modules de ce chapitre
npx expo install expo-camera expo-location expo-notifications
npx expo install expo-image-picker expo-av expo-barcode-scanner
npx expo install expo-sensors expo-haptics expo-clipboard
```

---

## expo-camera — Caméra complète

```bash
npx expo install expo-camera
```

### Composant Camera de base

```tsx
import React, { useState, useRef } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Alert,
} from 'react-native';
import { CameraView, useCameraPermissions, CameraType } from 'expo-camera';
import * as MediaLibrary from 'expo-media-library';

export default function AppareilPhoto() {
  const [face, setFace] = useState<CameraType>('back');
  const [flash, setFlash] = useState<'off' | 'on' | 'auto'>('off');
  const [prise, setPrise] = useState(false);
  const [permission, requestPermission] = useCameraPermissions();
  const cameraRef = useRef<CameraView>(null);

  if (!permission?.granted) {
    return (
      <View style={styles.permissionContainer}>
        <Text style={styles.permissionTexte}>
          Accès à la caméra requis
        </Text>
        <TouchableOpacity style={styles.bouton} onPress={requestPermission}>
          <Text style={styles.boutonTexte}>Autoriser</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const prendrephoto = async () => {
    if (!cameraRef.current || prise) return;
    setPrise(true);

    try {
      const photo = await cameraRef.current.takePictureAsync({
        quality: 0.8,         // 0 (minimum) à 1 (maximum)
        base64: false,        // true pour obtenir le base64
        exif: true,           // Inclure les métadonnées EXIF
        skipProcessing: false, // true = plus rapide mais qualité réduite
      });

      // photo.uri — chemin local temporaire
      // photo.width, photo.height — dimensions
      // photo.base64 — si demandé

      Alert.alert(
        'Photo prise !',
        `${photo.width}x${photo.height} px`,
        [
          { text: 'Annuler' },
          {
            text: 'Sauvegarder',
            onPress: async () => {
              const { granted } = await MediaLibrary.requestPermissionsAsync();
              if (granted) {
                await MediaLibrary.saveToLibraryAsync(photo.uri);
                Alert.alert('Sauvegardé', 'Photo enregistrée dans votre galerie');
              }
            },
          },
        ]
      );
    } catch (e) {
      Alert.alert('Erreur', 'Impossible de prendre la photo');
    } finally {
      setPrise(false);
    }
  };

  return (
    <View style={styles.container}>
      <CameraView
        ref={cameraRef}
        style={styles.camera}
        facing={face}
        flash={flash}
      >
        {/* Contrôles superposés */}
        <View style={styles.controles}>
          {/* Flash */}
          <TouchableOpacity
            style={styles.boutonControle}
            onPress={() => setFlash(f => f === 'off' ? 'on' : f === 'on' ? 'auto' : 'off')}
          >
            <Text style={styles.icone}>
              {flash === 'off' ? '⚡️✗' : flash === 'on' ? '⚡️' : '⚡️A'}
            </Text>
          </TouchableOpacity>

          {/* Retourner la caméra */}
          <TouchableOpacity
            style={styles.boutonControle}
            onPress={() => setFace(f => f === 'back' ? 'front' : 'back')}
          >
            <Text style={styles.icone}>🔄</Text>
          </TouchableOpacity>
        </View>

        {/* Bouton de capture */}
        <View style={styles.capture}>
          <TouchableOpacity
            style={[styles.boutonCapture, prise && styles.boutonCaptureActif]}
            onPress={prendrephoto}
            disabled={prise}
          >
            <View style={styles.boutonCaptureInterne} />
          </TouchableOpacity>
        </View>
      </CameraView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#000' },
  permissionContainer: {
    flex: 1, justifyContent: 'center', alignItems: 'center', padding: 32
  },
  permissionTexte: { fontSize: 18, marginBottom: 16, textAlign: 'center' },
  camera: { flex: 1 },
  controles: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    padding: 20,
    paddingTop: 50,
  },
  boutonControle: {
    backgroundColor: 'rgba(0,0,0,0.4)',
    borderRadius: 30,
    width: 50,
    height: 50,
    alignItems: 'center',
    justifyContent: 'center',
  },
  icone: { fontSize: 18 },
  capture: {
    flex: 1,
    justifyContent: 'flex-end',
    alignItems: 'center',
    paddingBottom: 40,
  },
  boutonCapture: {
    width: 80,
    height: 80,
    borderRadius: 40,
    borderWidth: 4,
    borderColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
  },
  boutonCaptureActif: { opacity: 0.6 },
  boutonCaptureInterne: {
    width: 66,
    height: 66,
    borderRadius: 33,
    backgroundColor: '#fff',
  },
  bouton: {
    backgroundColor: '#007AFF', padding: 16, borderRadius: 10,
  },
  boutonTexte: { color: '#fff', fontWeight: '600', fontSize: 16 },
});
```

### Scanner de QR Code

```tsx
import { CameraView, useCameraPermissions } from 'expo-camera';
import { useState } from 'react';

export default function ScannerQR() {
  const [permission, requestPermission] = useCameraPermissions();
  const [scanne, setScanne] = useState(false);
  const [resultat, setResultat] = useState<string | null>(null);

  const handleScan = (scanResult: { data: string; type: string }) => {
    if (scanne) return; // Éviter les scans multiples
    setScanne(true);
    setResultat(scanResult.data);

    // Vibration feedback
    // Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);

    setTimeout(() => setScanne(false), 2000); // Reset après 2s
  };

  if (!permission?.granted) {
    return <TouchableOpacity onPress={requestPermission}><Text>Autoriser</Text></TouchableOpacity>;
  }

  return (
    <View style={{ flex: 1 }}>
      <CameraView
        style={{ flex: 1 }}
        onBarcodeScanned={scanne ? undefined : handleScan}
        barcodeScannerSettings={{
          barcodeTypes: ['qr', 'ean13', 'ean8', 'code128', 'code39'],
        }}
      >
        {/* Viseur */}
        <View style={styles.viseur}>
          <View style={styles.coin_TL} />
          <View style={styles.coin_TR} />
          <View style={styles.coin_BL} />
          <View style={styles.coin_BR} />
        </View>
      </CameraView>

      {resultat && (
        <View style={styles.resultat}>
          <Text style={styles.resultatTexte}>Résultat : {resultat}</Text>
        </View>
      )}
    </View>
  );
}
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Device réel avec la caméra active — montrer le live preview, prendre une photo, et la retrouver dans la galerie Photos. Montrer aussi le scanner QR en action sur un QR code imprimé ou affiché sur un autre écran.
> **Expliquer :** La caméra ne fonctionne PAS sur simulateur iOS/Android — il faut un device réel. Le simulateur iOS affiche une image de remplacement statique. Sur Android Emulator, une image de test peut être configurée. Pour les tests sans device, Expo Go sur téléphone physique suffit.
---

## expo-image-picker — Bibliothèque photos

Plus simple que la caméra pour laisser l'utilisateur choisir une image existante.

```tsx
import React, { useState } from 'react';
import {
  View, Image, TouchableOpacity, Text, StyleSheet, Alert
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';

export default function SelecteurImage() {
  const [image, setImage] = useState<string | null>(null);

  const ouvrirGalerie = async () => {
    // Demander la permission d'accès aux photos
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permission requise', 'Accès à la galerie photos nécessaire');
      return;
    }

    const resultat = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images, // Images uniquement
      allowsEditing: true,   // Permettre le recadrage
      aspect: [1, 1],        // Ratio 1:1 pour le recadrage
      quality: 0.8,
      base64: false,
      exif: false,

      // Sélection multiple (iOS 14+, Android)
      // allowsMultipleSelection: true,
      // selectionLimit: 5,
    });

    if (!resultat.canceled && resultat.assets[0]) {
      setImage(resultat.assets[0].uri);
      // resultat.assets[0] :
      // uri, width, height, type, fileName, fileSize, base64, exif
    }
  };

  const ouvrirCamera = async () => {
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permission requise', 'Accès à la caméra nécessaire');
      return;
    }

    const resultat = await ImagePicker.launchCameraAsync({
      allowsEditing: true,
      aspect: [4, 3],
      quality: 0.9,
    });

    if (!resultat.canceled && resultat.assets[0]) {
      setImage(resultat.assets[0].uri);
    }
  };

  const choisirSource = () => {
    Alert.alert('Photo de profil', 'Choisir une source', [
      { text: 'Galerie', onPress: ouvrirGalerie },
      { text: 'Appareil photo', onPress: ouvrirCamera },
      { text: 'Annuler', style: 'cancel' },
    ]);
  };

  return (
    <View style={styles.container}>
      <TouchableOpacity style={styles.avatarConteneur} onPress={choisirSource}>
        {image ? (
          <Image source={{ uri: image }} style={styles.avatar} />
        ) : (
          <View style={styles.avatarVide}>
            <Text style={styles.avatarIcone}>📷</Text>
            <Text style={styles.avatarTexte}>Choisir une photo</Text>
          </View>
        )}
        {image && (
          <View style={styles.badgeModifier}>
            <Text style={styles.badgeTexte}>✏️</Text>
          </View>
        )}
      </TouchableOpacity>

      {image && (
        <TouchableOpacity onPress={() => setImage(null)}>
          <Text style={styles.supprimer}>Supprimer la photo</Text>
        </TouchableOpacity>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    padding: 24,
  },
  avatarConteneur: {
    position: 'relative',
  },
  avatar: {
    width: 120,
    height: 120,
    borderRadius: 60,
  },
  avatarVide: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: '#f0f0f0',
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 2,
    borderColor: '#ddd',
    borderStyle: 'dashed',
    gap: 4,
  },
  avatarIcone: { fontSize: 32 },
  avatarTexte: { fontSize: 11, color: '#999', textAlign: 'center' },
  badgeModifier: {
    position: 'absolute',
    bottom: 4,
    right: 4,
    backgroundColor: '#007AFF',
    width: 32,
    height: 32,
    borderRadius: 16,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 2,
    borderColor: '#fff',
  },
  badgeTexte: { fontSize: 14 },
  supprimer: {
    color: '#FF3B30',
    marginTop: 16,
    fontSize: 14,
  },
});
```

### Uploader une image vers un serveur

```typescript
// Uploader avec FormData
async function uploaderImage(uri: string, endpoint: string): Promise<string> {
  const formData = new FormData();

  // Sur React Native, les URIs locales se gèrent différemment du web
  formData.append('photo', {
    uri: uri,
    type: 'image/jpeg',
    name: 'photo.jpg',
  } as any);

  formData.append('userId', '123');

  const reponse = await fetch(endpoint, {
    method: 'POST',
    body: formData,
    headers: {
      'Content-Type': 'multipart/form-data',
      'Authorization': `Bearer ${token}`,
    },
  });

  const data = await reponse.json();
  return data.imageUrl; // URL publique retournée par le serveur
}
```

---

## expo-location — GPS complet

```tsx
import React, { useState, useEffect, useCallback } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ActivityIndicator } from 'react-native';
import * as Location from 'expo-location';
import MapView, { Marker, Circle } from 'react-native-maps'; // Nécessite expo install

interface PositionInfo {
  latitude: number;
  longitude: number;
  altitude: number | null;
  precision: number | null;
  adresse: string;
}

export default function CarteLocalisation() {
  const [permission, requestPermission] = Location.useForegroundPermissions();
  const [position, setPosition] = useState<PositionInfo | null>(null);
  const [chargement, setChargement] = useState(false);

  const localiser = useCallback(async () => {
    if (!permission?.granted) {
      await requestPermission();
      return;
    }

    setChargement(true);
    try {
      const pos = await Location.getCurrentPositionAsync({
        accuracy: Location.Accuracy.High,
      });

      // Géocodage inversé
      const [adresseObj] = await Location.reverseGeocodeAsync({
        latitude: pos.coords.latitude,
        longitude: pos.coords.longitude,
      });

      setPosition({
        latitude: pos.coords.latitude,
        longitude: pos.coords.longitude,
        altitude: pos.coords.altitude,
        precision: pos.coords.accuracy,
        adresse: [
          adresseObj.street,
          adresseObj.postalCode,
          adresseObj.city,
          adresseObj.country,
        ].filter(Boolean).join(', '),
      });
    } catch (e) {
      console.error('Erreur GPS:', e);
    } finally {
      setChargement(false);
    }
  }, [permission]);

  return (
    <View style={styles.container}>
      {position && (
        // react-native-maps (requiert un dev build)
        // <MapView
        //   style={styles.carte}
        //   initialRegion={{
        //     latitude: position.latitude,
        //     longitude: position.longitude,
        //     latitudeDelta: 0.005,
        //     longitudeDelta: 0.005,
        //   }}
        // >
        //   <Marker coordinate={position} title="Ma position" />
        //   <Circle
        //     center={position}
        //     radius={position.precision ?? 100}
        //     fillColor="rgba(0, 122, 255, 0.15)"
        //     strokeColor="rgba(0, 122, 255, 0.5)"
        //   />
        // </MapView>

        // Sans MapView (mode texte uniquement)
        <View style={styles.infoGPS}>
          <Text style={styles.adresse}>{position.adresse}</Text>
          <Text style={styles.coordonnees}>
            {position.latitude.toFixed(5)}, {position.longitude.toFixed(5)}
          </Text>
          {position.altitude && (
            <Text style={styles.detail}>Altitude : {position.altitude.toFixed(0)} m</Text>
          )}
          {position.precision && (
            <Text style={styles.detail}>Précision : ±{position.precision.toFixed(0)} m</Text>
          )}
        </View>
      )}

      <TouchableOpacity
        style={[styles.bouton, chargement && styles.boutonCharge]}
        onPress={localiser}
        disabled={chargement}
      >
        {chargement ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.boutonTexte}>
            {position ? 'Actualiser ma position' : '📍 Me localiser'}
          </Text>
        )}
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16 },
  infoGPS: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 8,
    elevation: 3,
    gap: 4,
  },
  adresse: { fontSize: 16, fontWeight: '600', color: '#1a1a1a' },
  coordonnees: { fontSize: 13, color: '#666', fontFamily: 'monospace' },
  detail: { fontSize: 13, color: '#999' },
  bouton: {
    backgroundColor: '#007AFF',
    padding: 16,
    borderRadius: 10,
    alignItems: 'center',
  },
  boutonCharge: { backgroundColor: '#aaa' },
  boutonTexte: { color: '#fff', fontWeight: '700', fontSize: 16 },
});
```

---

## expo-notifications — Notifications avancées

```tsx
import React, { useEffect, useRef, useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Alert, FlatList } from 'react-native';
import * as Notifications from 'expo-notifications';

// Configuration des catégories d'actions (boutons dans les notifications)
async function configurerCategories() {
  await Notifications.setNotificationCategoryAsync('message', [
    {
      identifier: 'repondre',
      buttonTitle: 'Répondre',
      options: { opensAppToForeground: false },
      textInput: {
        submitButtonTitle: 'Envoyer',
        placeholder: 'Votre message...',
      },
    },
    {
      identifier: 'marquer_lu',
      buttonTitle: 'Marquer comme lu',
      options: { opensAppToForeground: false, isDestructive: false },
    },
  ]);
}

export default function NotificationsScreen() {
  const [notificationsPlanifiees, setNp] = useState<Notifications.NotificationRequest[]>([]);
  const responseListener = useRef<Notifications.Subscription>();

  useEffect(() => {
    configurerCategories();

    // Réponse aux actions de notifications (boutons)
    responseListener.current = Notifications.addNotificationResponseReceivedListener(response => {
      const action = response.actionIdentifier;
      const notification = response.notification;

      if (action === 'repondre') {
        const texte = (response as any).userText;
        console.log('Réponse:', texte);
      } else if (action === 'marquer_lu') {
        console.log('Marqué comme lu');
      } else {
        // Tap sur la notification elle-même
        console.log('Notification tappée:', notification.request.content.data);
      }
    });

    chargerPlanifiees();

    return () => responseListener.current?.remove();
  }, []);

  const chargerPlanifiees = async () => {
    const liste = await Notifications.getAllScheduledNotificationsAsync();
    setNp(liste);
  };

  const planifierTest = async () => {
    await Notifications.scheduleNotificationAsync({
      content: {
        title: '💬 Nouveau message',
        body: 'Alice : "Tu es disponible ce soir ?"',
        data: { type: 'message', senderId: '42' },
        categoryIdentifier: 'message',
        sound: 'default',
      },
      trigger: { seconds: 3 },
    });
    Alert.alert('Planifié', 'Notification dans 3 secondes — mettez l\'app en arrière-plan');
    chargerPlanifiees();
  };

  const planifierRappelHebdo = async () => {
    await Notifications.scheduleNotificationAsync({
      content: {
        title: '📚 Rappel de formation',
        body: 'Votre session hebdomadaire commence dans 30 minutes',
      },
      trigger: {
        weekday: 2, // Lundi (1=dimanche, 2=lundi... 7=samedi)
        hour: 9,
        minute: 30,
        repeats: true,
      },
    });
    Alert.alert('Rappel hebdomadaire configuré !', 'Tous les lundis à 9h30');
    chargerPlanifiees();
  };

  const annulerTout = async () => {
    await Notifications.cancelAllScheduledNotificationsAsync();
    chargerPlanifiees();
  };

  return (
    <View style={styles.container}>
      <Text style={styles.titre}>Centre de Notifications</Text>

      <View style={styles.actions}>
        <TouchableOpacity style={styles.bouton} onPress={planifierTest}>
          <Text style={styles.boutonTexte}>Test dans 3s</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.bouton} onPress={planifierRappelHebdo}>
          <Text style={styles.boutonTexte}>Rappel hebdo</Text>
        </TouchableOpacity>

        <TouchableOpacity style={[styles.bouton, styles.boutonDanger]} onPress={annulerTout}>
          <Text style={styles.boutonTexte}>Tout annuler</Text>
        </TouchableOpacity>
      </View>

      <Text style={styles.sousTitre}>
        {notificationsPlanifiees.length} notification(s) planifiée(s)
      </Text>

      <FlatList
        data={notificationsPlanifiees}
        keyExtractor={item => item.identifier}
        renderItem={({ item }) => (
          <View style={styles.notif}>
            <Text style={styles.notifTitre}>{item.content.title}</Text>
            <Text style={styles.notifCorps}>{item.content.body}</Text>
          </View>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16 },
  titre: { fontSize: 24, fontWeight: 'bold', marginBottom: 16 },
  actions: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginBottom: 16 },
  bouton: { backgroundColor: '#007AFF', padding: 12, borderRadius: 8 },
  boutonDanger: { backgroundColor: '#FF3B30' },
  boutonTexte: { color: '#fff', fontWeight: '600' },
  sousTitre: { fontSize: 14, color: '#666', marginBottom: 8 },
  notif: {
    backgroundColor: '#fff',
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
    borderLeftWidth: 3,
    borderLeftColor: '#007AFF',
  },
  notifTitre: { fontWeight: '600', fontSize: 15 },
  notifCorps: { color: '#666', marginTop: 2 },
});
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Device réel avec une notification planifiée — mettre l'app en arrière-plan, attendre que la notification apparaisse dans le centre de notifications iOS/Android, tapper dessus et montrer que l'app s'ouvre sur le bon écran
> **Expliquer :** Les notifications locales fonctionnent sur simulateur mais les notifications **push** (depuis un serveur) nécessitent un device réel. Montrer le flux complet : votre backend appelle l'API Expo Push (`https://exp.host/--/api/v2/push/send`) avec le token du device, Expo relaie vers APNs (Apple) ou FCM (Google), qui délivrent au device. Le token Expo Push n'est valide que sur un device réel.
---

## expo-sensors — Accéléromètre et autres capteurs

```tsx
import { Accelerometer, Gyroscope, Barometer } from 'expo-sensors';
import { useState, useEffect } from 'react';

export function NiveauBulle() {
  const [data, setData] = useState({ x: 0, y: 0, z: 0 });
  const [abonnement, setAbonnement] = useState(null);

  const abonner = () => {
    // Fréquence de mise à jour en ms
    Accelerometer.setUpdateInterval(100); // 10 fois/seconde

    const sub = Accelerometer.addListener(donnees => {
      setData(donnees);
    });
    setAbonnement(sub);
  };

  const desabonner = () => {
    abonnement?.remove();
    setAbonnement(null);
  };

  useEffect(() => {
    abonner();
    return desabonner;
  }, []);

  // Calculer l'inclinaison
  const angleX = Math.atan2(data.y, data.z) * (180 / Math.PI);
  const angleY = Math.atan2(data.x, data.z) * (180 / Math.PI);
  const estPlat = Math.abs(angleX) < 5 && Math.abs(angleY) < 5;

  return (
    <View style={{ padding: 20, alignItems: 'center' }}>
      <Text style={{ fontSize: 20, color: estPlat ? 'green' : 'red' }}>
        {estPlat ? '✓ Niveau' : '⚠ Incliné'}
      </Text>
      <Text>X: {data.x.toFixed(3)}</Text>
      <Text>Y: {data.y.toFixed(3)}</Text>
      <Text>Z: {data.z.toFixed(3)}</Text>
      <Text>Angle X: {angleX.toFixed(1)}°</Text>
      <Text>Angle Y: {angleY.toFixed(1)}°</Text>
    </View>
  );
}
```

---

## expo-haptics — Retour haptique

Les vibrations tactiles améliorent l'UX sur iOS (Taptic Engine) et Android.

```typescript
import * as Haptics from 'expo-haptics';

// Impact (lors d'une sélection)
await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);   // Léger
await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);  // Moyen
await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy);   // Fort

// Notification (succès, erreur, avertissement)
await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning);

// Sélection (scroll d'un picker, sélection d'une option)
await Haptics.selectionAsync();

// Exemples d'utilisation contextuelle
const supprimerItem = async (id: string) => {
  await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
  // Puis la logique de suppression...
};

const erreurFormulaire = async () => {
  await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
};

const changerValeurSlider = async () => {
  await Haptics.selectionAsync(); // Feedback discret pendant le drag
};
```

---

## expo-av — Audio et vidéo

```typescript
import { Audio, Video } from 'expo-av';

// Configurer le mode audio
await Audio.setAudioModeAsync({
  playsInSilentModeIOS: true,        // Jouer même en mode silencieux iOS
  allowsRecordingIOS: false,
  staysActiveInBackground: false,
  shouldDuckAndroid: true,           // Baisser le volume des autres apps
});

// Jouer un son
const { sound } = await Audio.Sound.createAsync(
  require('../assets/sounds/notification.mp3'),
  { shouldPlay: true }
);
await sound.playAsync();

// Toujours décharger le son quand terminé
sound.setOnPlaybackStatusUpdate(status => {
  if (status.isLoaded && status.didJustFinish) {
    sound.unloadAsync();
  }
});

// Son depuis une URL
const { sound: soundDistant } = await Audio.Sound.createAsync(
  { uri: 'https://example.com/audio.mp3' },
  { shouldPlay: false }
);

// Contrôles
await soundDistant.playAsync();
await soundDistant.pauseAsync();
await soundDistant.stopAsync();
await soundDistant.setPositionAsync(5000); // Aller à 5 secondes
const status = await soundDistant.getStatusAsync(); // position, duration, etc.

// Nettoyage (important pour éviter les fuites mémoire)
await soundDistant.unloadAsync();
```

---

## expo-clipboard — Presse-papier

```typescript
import * as Clipboard from 'expo-clipboard';

// Copier du texte
await Clipboard.setStringAsync('Texte copié !');

// Lire le presse-papier
const texte = await Clipboard.getStringAsync();

// Vérifier si quelque chose est dans le presse-papier
const disponible = await Clipboard.hasStringAsync();

// Bouton de copie pratique
export function BoutonCopier({ texte }: { texte: string }) {
  const [copie, setCopie] = useState(false);

  const copier = async () => {
    await Clipboard.setStringAsync(texte);
    setCopie(true);
    setTimeout(() => setCopie(false), 2000);
  };

  return (
    <TouchableOpacity onPress={copier} style={styles.boutonCopie}>
      <Text style={styles.boutonCopieTexte}>
        {copie ? '✓ Copié !' : '📋 Copier'}
      </Text>
    </TouchableOpacity>
  );
}
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Comparaison simulateur vs device réel — montrer que la caméra ne fonctionne pas sur simulateur (image statique ou erreur), puis la même fonctionnalité opérationnelle sur un vrai iPhone/Android
> **Expliquer :** Liste des fonctionnalités qui nécessitent un device réel : caméra (photos/vidéo réelles), GPS (position réelle), Haptics (vibrations physiques), Bluetooth, NFC, capteurs biométriques. Sur simulateur, les GPS retournent des coordonnées fixes (Apple Park pour iOS Simulator), les notifications push ne fonctionnent pas. Pour le développement Expo Go suffit, mais pour les tests de production il faut un Development Build ou une build classique.
---

## Récapitulatif des modules Expo

| Module | Usage principal | Device requis |
|--------|----------------|---------------|
| `expo-camera` | Caméra, QR code | Oui |
| `expo-image-picker` | Galerie, caméra simplifiée | Caméra : oui |
| `expo-location` | GPS, géocodage | Non (simulateur OK) |
| `expo-notifications` | Notifs locales/push | Push : oui |
| `expo-sensors` | Accéléromètre, gyroscope | Préférable |
| `expo-haptics` | Vibrations | Oui (silencieux sinon) |
| `expo-av` | Audio, vidéo | Non |
| `expo-clipboard` | Presse-papier | Non |
| `expo-barcode-scanner` | Scan codes-barres | Oui |
