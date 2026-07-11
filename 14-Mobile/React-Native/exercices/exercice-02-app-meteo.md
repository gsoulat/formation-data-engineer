# Exercice 02 — Application Météo avec API + Localisation

## Objectif

Créer une application météo complète qui récupère la position GPS de l'utilisateur, interroge une API météo publique, et affiche les prévisions avec une interface graphique riche.

## Durée estimée

**3h**

## Compétences travaillées

- Permissions de localisation (expo-location)
- Appels API REST avec fetch/axios
- Gestion des états de chargement et d'erreur
- FlatList horizontale (prévisions horaires)
- Affichage conditionnel selon les données
- Formatage des données (température, dates, icônes météo)
- SafeAreaView, gradients de fond

---

## API Météo gratuite — Open-Meteo

On utilise [Open-Meteo](https://open-meteo.com/) — **gratuite, sans clé API**.

```
URL de base : https://api.open-meteo.com/v1/forecast

Paramètres principaux :
  latitude=48.8566
  longitude=2.3522
  current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m,apparent_temperature
  hourly=temperature_2m,weather_code,precipitation_probability
  daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,sunrise,sunset
  timezone=auto
  forecast_days=7
```

**Exemple d'appel complet :**
```
https://api.open-meteo.com/v1/forecast?latitude=48.8566&longitude=2.3522&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m,apparent_temperature&hourly=temperature_2m,weather_code,precipitation_probability&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=auto&forecast_days=7
```

### Codes météo (WMO)

```typescript
// constants/weatherCodes.ts
export const DESCRIPTIONS_METEO: Record<number, string> = {
  0: 'Ciel dégagé',
  1: 'Principalement dégagé',
  2: 'Partiellement nuageux',
  3: 'Couvert',
  45: 'Brouillard',
  48: 'Brouillard givrant',
  51: 'Bruine légère',
  53: 'Bruine modérée',
  55: 'Bruine dense',
  61: 'Pluie légère',
  63: 'Pluie modérée',
  65: 'Pluie forte',
  71: 'Neige légère',
  73: 'Neige modérée',
  75: 'Neige forte',
  80: 'Averses légères',
  81: 'Averses modérées',
  82: 'Averses violentes',
  95: 'Orage',
  96: 'Orage avec grêle',
  99: 'Orage violent avec grêle',
};

export const ICONES_METEO: Record<number, string> = {
  0: '☀️',
  1: '🌤',
  2: '⛅️',
  3: '☁️',
  45: '🌫',
  48: '🌫',
  51: '🌦',
  53: '🌦',
  55: '🌧',
  61: '🌧',
  63: '🌧',
  65: '🌧',
  71: '❄️',
  73: '❄️',
  75: '❄️',
  80: '🌦',
  81: '🌧',
  82: '⛈',
  95: '⛈',
  96: '⛈',
  99: '⛈',
};

export const COULEURS_FOND: Record<number, [string, string]> = {
  0: ['#FF9500', '#FF6B00'],    // Ensoleillé — orange
  1: ['#5AC8FA', '#007AFF'],    // Dégagé — bleu clair
  2: ['#8E8E93', '#636366'],    // Nuageux — gris
  3: ['#636366', '#3A3A3C'],    // Couvert — gris foncé
  45: ['#8E8E93', '#636366'],
  61: ['#34AADC', '#007AFF'],   // Pluie — bleu
  71: ['#E5E5EA', '#C7C7CC'],   // Neige — blanc
  95: ['#5856D6', '#3634A3'],   // Orage — violet
};

export function getCouleurFond(code: number): [string, string] {
  return COULEURS_FOND[code] ?? ['#007AFF', '#0040CC'];
}
```

---

## Structure du projet

```
meteo-app/
├── App.tsx
├── src/
│   ├── api/
│   │   └── meteoService.ts      ← Appels à l'API Open-Meteo
│   ├── components/
│   │   ├── MeteoActuelle.tsx    ← Bloc météo actuelle
│   │   ├── PrevisionsHoraires.tsx ← Scroll horizontal 24h
│   │   ├── PrevisionJour.tsx    ← Une ligne de prévision journalière
│   │   ├── InfosDetail.tsx      ← Humidité, vent, etc.
│   │   └── EtatChargement.tsx   ← Spinner avec fond dégradé
│   ├── screens/
│   │   ├── MeteoScreen.tsx      ← Écran principal
│   │   └── RechercheVilleScreen.tsx ← Recherche par ville (niveau 2)
│   ├── hooks/
│   │   └── useMeteo.ts          ← Logique de récupération des données
│   ├── types/
│   │   └── meteo.ts             ← Types pour la réponse API
│   └── constants/
│       └── weatherCodes.ts      ← Descriptions et icônes
```

---

## Types TypeScript

```typescript
// src/types/meteo.ts

export interface MeteoActuelle {
  temperature: number;
  temperatureRessentie: number;
  humidite: number;
  vitesseVent: number;
  codeMeteo: number;
}

export interface PrevisionsHoraire {
  heure: string;          // ISO string
  temperature: number;
  codeMeteo: number;
  probabilitePluie: number; // 0-100
}

export interface PrevisionJournaliere {
  date: string;           // ISO string
  codeMeteo: number;
  temperatureMax: number;
  temperatureMin: number;
  precipitations: number; // mm
  lever: string;          // ISO string
  coucher: string;        // ISO string
}

export interface DonneesMeteo {
  latitude: number;
  longitude: number;
  timezone: string;
  actuelle: MeteoActuelle;
  horaires: PrevisionsHoraire[];   // 24 prochaines heures
  journalier: PrevisionJournaliere[]; // 7 prochains jours
  derniereMAJ: string;  // ISO string
}

// Réponse brute de l'API Open-Meteo (pour la transformation)
export interface ReponseOpenMeteo {
  latitude: number;
  longitude: number;
  timezone: string;
  current: {
    time: string;
    temperature_2m: number;
    apparent_temperature: number;
    relative_humidity_2m: number;
    weather_code: number;
    wind_speed_10m: number;
  };
  hourly: {
    time: string[];
    temperature_2m: number[];
    weather_code: number[];
    precipitation_probability: number[];
  };
  daily: {
    time: string[];
    weather_code: number[];
    temperature_2m_max: number[];
    temperature_2m_min: number[];
    precipitation_sum: number[];
    sunrise: string[];
    sunset: string[];
  };
}
```

---

## Service API — à compléter

```typescript
// src/api/meteoService.ts
import { DonneesMeteo, ReponseOpenMeteo } from '../types/meteo';

const BASE_URL = 'https://api.open-meteo.com/v1/forecast';

export async function fetchMeteo(
  latitude: number,
  longitude: number
): Promise<DonneesMeteo> {
  const params = new URLSearchParams({
    latitude: latitude.toString(),
    longitude: longitude.toString(),
    current: 'temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m,apparent_temperature',
    hourly: 'temperature_2m,weather_code,precipitation_probability',
    daily: 'weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,sunrise,sunset',
    timezone: 'auto',
    forecast_days: '7',
  });

  const reponse = await fetch(`${BASE_URL}?${params}`);

  if (!reponse.ok) {
    throw new Error(`Erreur API météo : ${reponse.status}`);
  }

  const data: ReponseOpenMeteo = await reponse.json();

  // TODO : Transformer la réponse brute en DonneesMeteo
  return transformerReponse(data);
}

function transformerReponse(data: ReponseOpenMeteo): DonneesMeteo {
  // TODO : Transformer les données brutes
  // Conseil : filtrer les hourly pour ne garder que les 24 prochaines heures
  // En comparant data.hourly.time[i] >= data.current.time

  return {
    latitude: data.latitude,
    longitude: data.longitude,
    timezone: data.timezone,
    actuelle: {
      temperature: Math.round(data.current.temperature_2m),
      temperatureRessentie: Math.round(data.current.apparent_temperature),
      humidite: data.current.relative_humidity_2m,
      vitesseVent: Math.round(data.current.wind_speed_10m),
      codeMeteo: data.current.weather_code,
    },
    horaires: [], // TODO
    journalier: [], // TODO
    derniereMAJ: data.current.time,
  };
}

// Recherche de ville par nom (API de géocodage Open-Meteo)
export async function rechercherVille(nom: string): Promise<Array<{
  id: number;
  name: string;
  latitude: number;
  longitude: number;
  country: string;
  admin1?: string; // Région/État
}>> {
  const reponse = await fetch(
    `https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(nom)}&count=10&language=fr&format=json`
  );
  const data = await reponse.json();
  return data.results ?? [];
}
```

---

## Hook useMeteo — à compléter

```typescript
// src/hooks/useMeteo.ts
import { useState, useEffect, useCallback } from 'react';
import * as Location from 'expo-location';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { fetchMeteo } from '../api/meteoService';
import { DonneesMeteo } from '../types/meteo';

const CLE_CACHE = '@meteo_cache';
const DUREE_CACHE_MS = 10 * 60 * 1000; // 10 minutes

interface EtatMeteo {
  donnees: DonneesMeteo | null;
  chargement: boolean;
  erreur: string | null;
  ville: string | null;
  coordonnees: { latitude: number; longitude: number } | null;
}

export function useMeteo() {
  const [etat, setEtat] = useState<EtatMeteo>({
    donnees: null,
    chargement: true,
    erreur: null,
    ville: null,
    coordonnees: null,
  });

  const chargerDepuisCache = async (): Promise<DonneesMeteo | null> => {
    try {
      const json = await AsyncStorage.getItem(CLE_CACHE);
      if (!json) return null;

      const { donnees, timestamp }: { donnees: DonneesMeteo; timestamp: number } = JSON.parse(json);

      // Vérifier la fraîcheur du cache
      if (Date.now() - timestamp > DUREE_CACHE_MS) {
        return null; // Cache expiré
      }

      return donnees;
    } catch {
      return null;
    }
  };

  const sauvegarderCache = async (donnees: DonneesMeteo) => {
    try {
      await AsyncStorage.setItem(CLE_CACHE, JSON.stringify({
        donnees,
        timestamp: Date.now(),
      }));
    } catch (e) {
      console.warn('Impossible de mettre en cache la météo:', e);
    }
  };

  const charger = useCallback(async (forcer = false) => {
    setEtat(prev => ({ ...prev, chargement: true, erreur: null }));

    try {
      // 1. Vérifier le cache (sauf si rechargement forcé)
      if (!forcer) {
        const cache = await chargerDepuisCache();
        if (cache && etat.coordonnees) {
          setEtat(prev => ({ ...prev, donnees: cache, chargement: false }));
          return;
        }
      }

      // 2. Demander la permission de localisation
      const { granted } = await Location.requestForegroundPermissionsAsync();
      if (!granted) {
        throw new Error('Permission de localisation refusée');
      }

      // 3. Obtenir la position
      const position = await Location.getCurrentPositionAsync({
        accuracy: Location.Accuracy.Balanced,
      });

      const coords = {
        latitude: position.coords.latitude,
        longitude: position.coords.longitude,
      };

      // 4. Géocodage inversé pour le nom de la ville
      const [adresse] = await Location.reverseGeocodeAsync(coords);
      const nomVille = adresse.city ?? adresse.subregion ?? adresse.region ?? 'Localisation inconnue';

      // 5. Appel API météo
      const donnees = await fetchMeteo(coords.latitude, coords.longitude);

      // 6. Sauvegarder en cache
      await sauvegarderCache(donnees);

      setEtat({
        donnees,
        chargement: false,
        erreur: null,
        ville: nomVille,
        coordonnees: coords,
      });

    } catch (e) {
      setEtat(prev => ({
        ...prev,
        chargement: false,
        erreur: e instanceof Error ? e.message : 'Erreur inconnue',
      }));
    }
  }, [etat.coordonnees]);

  useEffect(() => {
    charger();
  }, []);

  return {
    ...etat,
    actualiser: () => charger(true),
  };
}
```

---

## Composant MeteoActuelle — à implémenter

```tsx
// src/components/MeteoActuelle.tsx
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { MeteoActuelle as IMeteoActuelle } from '../types/meteo';
import { DESCRIPTIONS_METEO, ICONES_METEO } from '../constants/weatherCodes';

interface Props {
  actuelle: IMeteoActuelle;
  ville: string;
  timezone: string;
}

export function MeteoActuelle({ actuelle, ville, timezone }: Props) {
  const description = DESCRIPTIONS_METEO[actuelle.codeMeteo] ?? 'Inconnu';
  const icone = ICONES_METEO[actuelle.codeMeteo] ?? '🌡';

  const heureLocale = new Date().toLocaleTimeString('fr-FR', {
    timeZone: timezone,
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <View style={styles.container}>
      {/* Ville + heure */}
      <Text style={styles.ville}>{ville}</Text>
      <Text style={styles.heure}>{heureLocale}</Text>

      {/* Icône météo grande */}
      <Text style={styles.icone}>{icone}</Text>

      {/* Température principale */}
      <Text style={styles.temperature}>{actuelle.temperature}°</Text>
      <Text style={styles.description}>{description}</Text>

      {/* Température ressentie */}
      <Text style={styles.ressentie}>
        Ressenti {actuelle.temperatureRessentie}°
      </Text>

      {/* Détails en ligne */}
      <View style={styles.details}>
        <View style={styles.detailItem}>
          <Text style={styles.detailIcone}>💧</Text>
          <Text style={styles.detailValeur}>{actuelle.humidite}%</Text>
          <Text style={styles.detailLabel}>Humidité</Text>
        </View>
        <View style={styles.separateur} />
        <View style={styles.detailItem}>
          <Text style={styles.detailIcone}>💨</Text>
          <Text style={styles.detailValeur}>{actuelle.vitesseVent} km/h</Text>
          <Text style={styles.detailLabel}>Vent</Text>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    paddingVertical: 32,
    paddingHorizontal: 24,
  },
  ville: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
    textShadowColor: 'rgba(0,0,0,0.2)',
    textShadowOffset: { width: 0, height: 1 },
    textShadowRadius: 4,
  },
  heure: {
    fontSize: 16,
    color: 'rgba(255,255,255,0.8)',
    marginTop: 4,
    marginBottom: 20,
  },
  icone: {
    fontSize: 80,
    marginBottom: 8,
  },
  temperature: {
    fontSize: 96,
    fontWeight: '100',
    color: '#fff',
    lineHeight: 96,
  },
  description: {
    fontSize: 20,
    color: 'rgba(255,255,255,0.9)',
    marginTop: 8,
  },
  ressentie: {
    fontSize: 15,
    color: 'rgba(255,255,255,0.7)',
    marginTop: 4,
    marginBottom: 24,
  },
  details: {
    flexDirection: 'row',
    backgroundColor: 'rgba(255,255,255,0.2)',
    borderRadius: 16,
    paddingVertical: 16,
    paddingHorizontal: 32,
    gap: 32,
  },
  detailItem: {
    alignItems: 'center',
    gap: 4,
  },
  detailIcone: {
    fontSize: 22,
  },
  detailValeur: {
    fontSize: 16,
    fontWeight: '700',
    color: '#fff',
  },
  detailLabel: {
    fontSize: 12,
    color: 'rgba(255,255,255,0.7)',
  },
  separateur: {
    width: 1,
    backgroundColor: 'rgba(255,255,255,0.3)',
  },
});
```

---

## Composant PrevisionsHoraires — à implémenter

```tsx
// src/components/PrevisionsHoraires.tsx
import React from 'react';
import { View, Text, FlatList, StyleSheet } from 'react-native';
import { PrevisionsHoraire } from '../types/meteo';
import { ICONES_METEO } from '../constants/weatherCodes';

interface Props {
  horaires: PrevisionsHoraire[];
  timezone: string;
}

export function PrevisionsHoraires({ horaires, timezone }: Props) {
  const prochaines24h = horaires.slice(0, 24);

  const renderItem = ({ item, index }: { item: PrevisionsHoraire; index: number }) => {
    const heure = new Date(item.heure).toLocaleTimeString('fr-FR', {
      timeZone: timezone,
      hour: '2-digit',
      minute: '2-digit',
    });

    return (
      <View style={styles.item}>
        <Text style={styles.heure}>{index === 0 ? 'Maint.' : heure}</Text>
        <Text style={styles.icone}>{ICONES_METEO[item.codeMeteo] ?? '🌡'}</Text>
        {item.probabilitePluie > 20 && (
          <Text style={styles.pluie}>{item.probabilitePluie}%</Text>
        )}
        <Text style={styles.temperature}>{item.temperature}°</Text>
      </View>
    );
  };

  return (
    <View style={styles.container}>
      <Text style={styles.titre}>Prévisions horaires</Text>
      <FlatList
        data={prochaines24h}
        keyExtractor={(_, i) => String(i)}
        renderItem={renderItem}
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.liste}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: 'rgba(255,255,255,0.15)',
    borderRadius: 16,
    marginHorizontal: 16,
    padding: 16,
  },
  titre: {
    color: 'rgba(255,255,255,0.7)',
    fontSize: 13,
    fontWeight: '600',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    marginBottom: 12,
  },
  liste: {
    gap: 16,
  },
  item: {
    alignItems: 'center',
    gap: 4,
    minWidth: 52,
  },
  heure: {
    fontSize: 13,
    color: 'rgba(255,255,255,0.8)',
    fontWeight: '500',
  },
  icone: {
    fontSize: 24,
  },
  pluie: {
    fontSize: 11,
    color: '#5AC8FA',
    fontWeight: '600',
  },
  temperature: {
    fontSize: 15,
    color: '#fff',
    fontWeight: '600',
  },
});
```

---

## Écran principal MeteoScreen

```tsx
// src/screens/MeteoScreen.tsx
import React from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  RefreshControl,
  Text,
  TouchableOpacity,
  ActivityIndicator,
  StatusBar,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { useMeteo } from '../hooks/useMeteo';
import { MeteoActuelle } from '../components/MeteoActuelle';
import { PrevisionsHoraires } from '../components/PrevisionsHoraires';
import { getCouleurFond } from '../constants/weatherCodes';

// Installation : npx expo install expo-linear-gradient

export default function MeteoScreen() {
  const { donnees, chargement, erreur, ville, actualiser } = useMeteo();

  const couleursFond = donnees
    ? getCouleurFond(donnees.actuelle.codeMeteo)
    : ['#007AFF', '#0040CC'];

  if (erreur) {
    return (
      <SafeAreaView style={styles.centrer}>
        <Text style={styles.erreurIcone}>⚠️</Text>
        <Text style={styles.erreurTexte}>{erreur}</Text>
        <TouchableOpacity style={styles.boutonReessayer} onPress={actualiser}>
          <Text style={styles.boutonTexte}>Réessayer</Text>
        </TouchableOpacity>
      </SafeAreaView>
    );
  }

  return (
    <LinearGradient colors={couleursFond} style={styles.fond}>
      <StatusBar barStyle="light-content" />
      <SafeAreaView style={styles.safeArea}>
        <ScrollView
          style={styles.scroll}
          contentContainerStyle={styles.contenu}
          showsVerticalScrollIndicator={false}
          refreshControl={
            <RefreshControl
              refreshing={chargement}
              onRefresh={actualiser}
              tintColor="#fff"
            />
          }
        >
          {chargement && !donnees ? (
            <View style={styles.chargement}>
              <ActivityIndicator size="large" color="#fff" />
              <Text style={styles.chargementTexte}>Chargement de la météo...</Text>
            </View>
          ) : donnees ? (
            <>
              <MeteoActuelle
                actuelle={donnees.actuelle}
                ville={ville ?? 'Votre position'}
                timezone={donnees.timezone}
              />

              <PrevisionsHoraires
                horaires={donnees.horaires}
                timezone={donnees.timezone}
              />

              {/* TODO : Ajouter PrevisionsSemaine avec les 7 prochains jours */}
            </>
          ) : null}
        </ScrollView>
      </SafeAreaView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  fond: { flex: 1 },
  safeArea: { flex: 1 },
  scroll: { flex: 1 },
  contenu: { paddingBottom: 32 },
  centrer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
    gap: 16,
  },
  erreurIcone: { fontSize: 48 },
  erreurTexte: {
    fontSize: 16,
    textAlign: 'center',
    color: '#FF3B30',
  },
  boutonReessayer: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 10,
  },
  boutonTexte: { color: '#fff', fontWeight: '600' },
  chargement: {
    height: 400,
    justifyContent: 'center',
    alignItems: 'center',
    gap: 16,
  },
  chargementTexte: { color: 'rgba(255,255,255,0.8)', fontSize: 16 },
});
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Application météo en fonctionnement sur device réel — montrer la localisation automatique, le fond dégradé qui change selon les conditions météo, le scroll horizontal des prévisions horaires, et le pull-to-refresh
> **Expliquer :** Montrer dans les DevTools (Flipper ou Chrome) la requête réelle à l'API Open-Meteo et la réponse JSON brute. Comparer avec ce qu'on affiche après transformation. Expliquer le système de cache (10 minutes) pour éviter de re-requêter l'API à chaque rendu — pertinent pour une API sans clé avec des limites de requêtes.
---

## Fonctionnalités bonus

### Niveau 2 — Recherche par ville

```typescript
// Ajouter un écran RechercheVilleScreen.tsx
// Utiliser l'API de géocodage Open-Meteo :
// GET https://geocoding-api.open-meteo.com/v1/search?name=Paris&count=10&language=fr

// Sauvegarder la ville sélectionnée dans AsyncStorage
// Permettre de basculer entre "Ma position" et "Ville enregistrée"
```

### Niveau 3 — Widget et notifications

```typescript
// Notification locale : alerte météo si pluie prévue dans les 2h
// Vérifier les probabilités de pluie dans hourly
// Si probabilitePluie > 70% dans les 2 prochaines heures →
//   planifier une notification : "🌧 Pluie probable dans 2h, pensez à votre parapluie"
```

---

## Commandes pour démarrer

```bash
npx create-expo-app meteo-app --template blank-typescript
cd meteo-app

npx expo install expo-location
npx expo install expo-linear-gradient
npx expo install @react-native-async-storage/async-storage
npx expo install react-native-safe-area-context
npm install @react-navigation/native @react-navigation/native-stack
npx expo install react-native-screens

npx expo start
```

---

## Critères d'évaluation

| Critère | Points |
|---------|--------|
| Permission GPS demandée correctement | 1 |
| Appel API réussi avec les bonnes données | 3 |
| Météo actuelle affichée (température, description, icône) | 2 |
| Prévisions horaires en scroll horizontal | 2 |
| Gestion des états (chargement, erreur, données) | 2 |
| Fond dégradé adapté aux conditions météo | 1 |
| Pull-to-refresh | 1 |
| Mise en cache 10 minutes (AsyncStorage) | 2 |
| Interface soignée avec les couleurs adaptées | 2 |
| TypeScript correct | 2 |
| Bonus : Recherche par ville | +2 |
| Bonus : Prévisions 7 jours | +1 |
| Bonus : Notification pluie | +2 |

**Total : 18 points (+ 5 bonus)**

---

## Solution de la fonction transformerReponse

```typescript
function transformerReponse(data: ReponseOpenMeteo): DonneesMeteo {
  const tempsActuel = new Date(data.current.time).getTime();

  // Filtrer les horaires pour les 24 prochaines heures
  const indexActuel = data.hourly.time.findIndex(
    t => new Date(t).getTime() >= tempsActuel
  );

  const horaires = data.hourly.time
    .slice(indexActuel, indexActuel + 24)
    .map((heure, i) => ({
      heure,
      temperature: Math.round(data.hourly.temperature_2m[indexActuel + i]),
      codeMeteo: data.hourly.weather_code[indexActuel + i],
      probabilitePluie: data.hourly.precipitation_probability[indexActuel + i] ?? 0,
    }));

  const journalier = data.daily.time.map((date, i) => ({
    date,
    codeMeteo: data.daily.weather_code[i],
    temperatureMax: Math.round(data.daily.temperature_2m_max[i]),
    temperatureMin: Math.round(data.daily.temperature_2m_min[i]),
    precipitations: data.daily.precipitation_sum[i] ?? 0,
    lever: data.daily.sunrise[i],
    coucher: data.daily.sunset[i],
  }));

  return {
    latitude: data.latitude,
    longitude: data.longitude,
    timezone: data.timezone,
    actuelle: {
      temperature: Math.round(data.current.temperature_2m),
      temperatureRessentie: Math.round(data.current.apparent_temperature),
      humidite: data.current.relative_humidity_2m,
      vitesseVent: Math.round(data.current.wind_speed_10m),
      codeMeteo: data.current.weather_code,
    },
    horaires,
    journalier,
    derniereMAJ: data.current.time,
  };
}
```
