# 01 — Hooks Essentiels : useEffect, useRef, useMemo, useCallback

## Introduction

Les hooks sont des fonctions spéciales qui permettent aux composants fonctionnels d'utiliser des fonctionnalités React (état, cycle de vie, etc.). Ils commencent toujours par `use`.

**Règles des hooks (à ne jamais enfreindre) :**
1. Appeler les hooks uniquement **au niveau supérieur** d'un composant (pas dans des conditions, boucles ou fonctions imbriquées)
2. Appeler les hooks uniquement dans des **composants React** ou des **hooks personnalisés**

---

## 1. useEffect — Effets de bord

`useEffect` permet d'exécuter du code en réponse au rendu d'un composant (ou de certaines valeurs). C'est ici qu'on place les appels API, les abonnements, les timers, etc.

```jsx
import { useState, useEffect } from "react";

function ExempleUseEffect() {
  const [donnees, setDonnees] = useState(null);
  const [compteur, setCompteur] = useState(0);
  const [userId, setUserId] = useState(1);

  // 1. Sans tableau de dépendances — s'exécute après CHAQUE rendu
  useEffect(() => {
    console.log("Rendu effectué");
  });

  // 2. Avec tableau vide [] — s'exécute SEULEMENT après le premier rendu (montage)
  useEffect(() => {
    console.log("Composant monté");
    // Analogue à componentDidMount en classe
  }, []);

  // 3. Avec dépendances — s'exécute quand userId change
  useEffect(() => {
    console.log(`userId a changé : ${userId}`);
    // Analogue à componentDidUpdate avec condition sur userId
  }, [userId]);

  return <button onClick={() => setUserId(id => id + 1)}>User suivant</button>;
}
```

### Cas d'usage : Appel API

```jsx
function ProfilUtilisateur({ userId }) {
  const [utilisateur, setUtilisateur] = useState(null);
  const [chargement, setChargement] = useState(true);
  const [erreur, setErreur] = useState(null);

  useEffect(() => {
    // Réinitialiser l'état quand userId change
    setChargement(true);
    setErreur(null);
    setUtilisateur(null);

    // Fonction async dans useEffect (ne pas rendre useEffect async directement)
    async function charger() {
      try {
        const response = await fetch(`https://jsonplaceholder.typicode.com/users/${userId}`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        setUtilisateur(data);
      } catch (err) {
        setErreur(err.message);
      } finally {
        setChargement(false);
      }
    }

    charger();
  }, [userId]); // Relance quand userId change

  if (chargement) return <div>Chargement du profil...</div>;
  if (erreur) return <div>Erreur : {erreur}</div>;
  if (!utilisateur) return null;

  return (
    <div>
      <h2>{utilisateur.name}</h2>
      <p>{utilisateur.email}</p>
    </div>
  );
}
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Console DevTools — créer un composant avec useEffect et différentes configurations de dépendances (sans [], avec [], avec [userId]). Montrer l'ordre d'exécution des logs. Changer userId et montrer que seul l'effect avec [userId] se relance.
> **Expliquer :** Les dépendances du useEffect sont une LISTE de valeurs que React surveille. Si l'une d'elles change entre deux rendus, React réexécute l'effect. Un tableau vide signifie "personne ne change, donc exécute une seule fois".

---

### Nettoyage (cleanup)

```jsx
function TimerComposant() {
  const [secondes, setSecondes] = useState(0);

  useEffect(() => {
    const intervalId = setInterval(() => {
      setSecondes(prev => prev + 1);
    }, 1000);

    // Fonction de nettoyage — s'exécute avant le prochain effect ET au démontage
    return () => {
      clearInterval(intervalId); // Important ! Sans ça, le timer continue après démontage
      console.log("Timer nettoyé");
    };
  }, []); // Seulement au montage

  return <p>Secondes : {secondes}</p>;
}

// Nettoyage d'un abonnement
function UsersLive({ channelId }) {
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    const socket = new WebSocket(`ws://api.example.com/channel/${channelId}`);

    socket.onmessage = (event) => {
      setMessages(prev => [...prev, JSON.parse(event.data)]);
    };

    return () => socket.close(); // Fermer la connexion WebSocket au démontage

  }, [channelId]); // Reconnecte si channelId change

  return (
    <ul>
      {messages.map((msg, i) => <li key={i}>{msg.texte}</li>)}
    </ul>
  );
}

// AbortController pour annuler les fetch() en cours
function SearchResults({ query }) {
  const [resultats, setResultats] = useState([]);

  useEffect(() => {
    if (!query) { setResultats([]); return; }

    const controller = new AbortController();

    async function rechercher() {
      try {
        const response = await fetch(`/api/search?q=${query}`, {
          signal: controller.signal, // Connecter l'AbortController
        });
        const data = await response.json();
        setResultats(data);
      } catch (err) {
        if (err.name !== "AbortError") {
          console.error("Erreur de recherche:", err);
        }
      }
    }

    rechercher();

    // Si la query change avant la fin, annuler la requête précédente
    return () => controller.abort();
  }, [query]);

  return (/* ... */);
}
```

---

## 2. useRef — Références

`useRef` retourne un objet `{ current: valeur }` qui **persiste entre les rendus** mais dont la modification ne déclenche **pas de re-rendu**.

### Accès aux éléments DOM

```jsx
import { useRef, useEffect, useState } from "react";

function ChampAutoFocus() {
  const inputRef = useRef(null); // current sera l'élément DOM après montage

  useEffect(() => {
    inputRef.current?.focus(); // Focus automatique au montage
  }, []);

  return <input ref={inputRef} placeholder="Je prends le focus automatiquement" />;
}

// Lecture de valeurs sans déclencher de re-rendu
function VideoPlayer() {
  const videoRef = useRef(null);
  const [enLecture, setEnLecture] = useState(false);

  const basculer = () => {
    const video = videoRef.current;
    if (!video) return;

    if (enLecture) {
      video.pause();
    } else {
      video.play();
    }
    setEnLecture(!enLecture);
  };

  return (
    <div>
      <video ref={videoRef} src="/video.mp4" />
      <button onClick={basculer}>
        {enLecture ? "Pause" : "Play"}
      </button>
    </div>
  );
}
```

### Stocker des valeurs persistantes (sans re-rendu)

```jsx
function Chronometre() {
  const [elapsed, setElapsed] = useState(0);
  const [enCours, setEnCours] = useState(false);

  // Stocker l'ID de l'intervalle sans déclencher de re-rendu
  const intervalRef = useRef(null);
  const debutRef = useRef(null);

  const demarrer = () => {
    if (enCours) return;
    debutRef.current = Date.now() - elapsed;
    intervalRef.current = setInterval(() => {
      setElapsed(Date.now() - debutRef.current);
    }, 10);
    setEnCours(true);
  };

  const arreter = () => {
    clearInterval(intervalRef.current);
    setEnCours(false);
  };

  const reinitialiser = () => {
    clearInterval(intervalRef.current);
    setElapsed(0);
    setEnCours(false);
  };

  return (
    <div>
      <p>{(elapsed / 1000).toFixed(2)}s</p>
      <button onClick={demarrer}>Démarrer</button>
      <button onClick={arreter}>Arrêter</button>
      <button onClick={reinitialiser}>Réinitialiser</button>
    </div>
  );
}

// Valeur précédente avec useRef
function usePrevious(valeur) {
  const ref = useRef(undefined);
  useEffect(() => {
    ref.current = valeur; // Met à jour APRÈS le rendu
  });
  return ref.current; // Retourne la valeur du rendu précédent
}

function Compteur() {
  const [count, setCount] = useState(0);
  const precedent = usePrevious(count);

  return (
    <p>
      Actuel : {count}, Précédent : {precedent ?? "N/A"}
      <button onClick={() => setCount(c => c + 1)}>+1</button>
    </p>
  );
}
```

---

## 3. useMemo — Mémoïsation de calculs

`useMemo` met en cache le résultat d'un calcul coûteux. Il recalcule uniquement quand les dépendances changent.

```jsx
import { useState, useMemo } from "react";

// Simulation d'un calcul lent
function calculCouteux(n) {
  console.log("Calcul en cours...");
  let result = 0;
  for (let i = 0; i < n * 1000000; i++) {
    result += i;
  }
  return result;
}

function ExempleUseMemo() {
  const [nombre, setNombre] = useState(5);
  const [theme, setTheme] = useState("clair");

  // ❌ Sans useMemo — recalculé à CHAQUE rendu, même si theme change
  // const valeurCalculee = calculCouteux(nombre);

  // ✅ Avec useMemo — recalculé SEULEMENT quand 'nombre' change
  const valeurCalculee = useMemo(() => {
    return calculCouteux(nombre);
  }, [nombre]); // Si 'theme' change, la valeur en cache est réutilisée

  return (
    <div style={{ background: theme === "clair" ? "#fff" : "#333" }}>
      <p>Résultat : {valeurCalculee}</p>
      <button onClick={() => setNombre(n => n + 1)}>Augmenter</button>
      <button onClick={() => setTheme(t => t === "clair" ? "sombre" : "clair")}>
        Changer thème {/* Ne devrait pas déclencher le recalcul */}
      </button>
    </div>
  );
}
```

### useMemo pour les objets et tableaux (référence stable)

```jsx
function ListeFiltree({ items, filtres }) {
  // ❌ Sans useMemo — nouvel objet à chaque rendu → les composants enfants se re-rendent inutilement
  // const resultat = { items: items.filter(i => filtres.includes(i.categorie)) };

  // ✅ Avec useMemo — même référence si items et filtres n'ont pas changé
  const resultat = useMemo(
    () => ({
      items: items.filter(i => filtres.includes(i.categorie)),
      total: items.length,
      filtre: filtres.join(", "),
    }),
    [items, filtres]
  );

  return (
    <div>
      <p>{resultat.filtre} — {resultat.items.length}/{resultat.total} items</p>
      {resultat.items.map(item => <Item key={item.id} item={item} />)}
    </div>
  );
}
```

---

## 4. useCallback — Mémoïsation de fonctions

`useCallback` retourne une version mémoïsée d'une fonction. La fonction n'est recréée que quand les dépendances changent. Principalement utile pour éviter des re-rendus en passant des fonctions en props à des composants optimisés.

```jsx
import { useState, useCallback, memo } from "react";

// React.memo — évite le re-rendu si les props n'ont pas changé
const BoutonOptimise = memo(function BoutonOptimise({ label, onClick }) {
  console.log(`Rendu de BoutonOptimise: ${label}`);
  return <button onClick={onClick}>{label}</button>;
});

function Parent() {
  const [compteur, setCompteur] = useState(0);
  const [texte, setTexte] = useState("");

  // ❌ Sans useCallback — nouvelle référence de fonction à chaque rendu
  // BoutonOptimise se re-rend inutilement même quand seul texte change
  // const incrementer = () => setCompteur(c => c + 1);

  // ✅ Avec useCallback — même référence tant que setCompteur ne change pas
  const incrementer = useCallback(
    () => setCompteur(c => c + 1),
    [] // setCompteur est stable — pas dans les dépendances
  );

  const reinitialiser = useCallback(
    () => setCompteur(0),
    []
  );

  return (
    <div>
      <input value={texte} onChange={e => setTexte(e.target.value)} />
      <p>Compteur : {compteur}</p>

      {/* BoutonOptimise ne se re-rend PAS quand texte change */}
      <BoutonOptimise label="+1" onClick={incrementer} />
      <BoutonOptimise label="Réinitialiser" onClick={reinitialiser} />
    </div>
  );
}
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** React DevTools → onglet "Profiler" → enregistrer une session → cliquer plusieurs fois sur différents boutons → arrêter l'enregistrement → montrer la flamegraph qui indique quels composants se sont re-rendus et pourquoi
> **Expliquer :** Le Profiler est l'outil de performance de React DevTools. On peut voir exactement quels composants se re-rendent, combien de temps chaque rendu prend, et POURQUOI (quel prop ou state a changé). C'est l'outil pour diagnostiquer les problèmes de performance.

---

### Quand utiliser useMemo et useCallback ?

```jsx
// GUIDELINE : Ne pas optimiser prématurément !
// useMemo et useCallback ont un coût (mémoire + calcul des dépendances)

// ✅ Utiliser useMemo quand :
// - Le calcul est vraiment lent (mesurer avec Profiler d'abord !)
// - On veut une référence stable pour éviter des re-rendus en cascade

// ✅ Utiliser useCallback quand :
// - La fonction est passée à un composant enfant optimisé avec React.memo
// - La fonction est dans les dépendances d'un useEffect

// ❌ NE PAS utiliser pour :
// - Des calculs simples (addition, accès à une propriété)
// - Des fonctions qui ne sont pas passées en prop

// Exemple de quoi ne PAS mémoïser
function Mauvais() {
  const [count, setCount] = useState(0);

  // ❌ Inutile — getDouble est simple et n'est pas passé en prop
  const getDouble = useMemo(() => count * 2, [count]);

  // ❌ Inutile — pas passé à un composant mémoïsé
  const handleClick = useCallback(() => setCount(c => c + 1), []);
}
```

---

## 5. useLayoutEffect

Similaire à `useEffect` mais s'exécute **de façon synchrone** après toutes les mutations du DOM, avant que le navigateur ne peigne l'écran.

```jsx
import { useLayoutEffect, useRef, useState } from "react";

function TooltipPositionne({ cible, texte }) {
  const tooltipRef = useRef(null);
  const [position, setPosition] = useState({ top: 0, left: 0 });

  useLayoutEffect(() => {
    // Lire les dimensions du DOM AVANT que le navigateur ne peigne
    // pour éviter le "flash" de repositionnement
    const cibleRect = cible.getBoundingClientRect();
    const tooltipRect = tooltipRef.current?.getBoundingClientRect();

    if (tooltipRect) {
      setPosition({
        top: cibleRect.bottom + 8,
        left: cibleRect.left + (cibleRect.width - tooltipRect.width) / 2,
      });
    }
  });

  return (
    <div
      ref={tooltipRef}
      style={{ position: "fixed", ...position }}
      className="tooltip"
    >
      {texte}
    </div>
  );
}

// Règle : utiliser useEffect par défaut, useLayoutEffect seulement si
// l'effet doit se passer AVANT que l'utilisateur voit l'écran (éviter le flash)
```

---

## Récapitulatif

| Hook | Usage | Déclenche re-rendu |
|---|---|---|
| `useEffect` | Effets de bord, API, timers, abonnements | Non (sauf si on appelle un setter) |
| `useRef` | Référence DOM, valeur mutable persistante | Non |
| `useMemo` | Mémoïser le résultat d'un calcul coûteux | Non |
| `useCallback` | Mémoïser une fonction (référence stable) | Non |
| `useLayoutEffect` | Lire/modifier le DOM avant le paint | Non |

**Tableau de dépendances :**

| Configuration | Comportement |
|---|---|
| Absent | S'exécute après chaque rendu |
| `[]` | S'exécute une seule fois (montage) |
| `[a, b]` | S'exécute quand `a` ou `b` change |
