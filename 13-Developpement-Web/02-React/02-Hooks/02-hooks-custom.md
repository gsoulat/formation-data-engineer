# 02 — Hooks Personnalisés : useFetch, useLocalStorage, et plus

## Introduction

Un hook personnalisé est simplement une **fonction JavaScript qui commence par `use`** et qui peut appeler d'autres hooks. Ils permettent d'extraire de la logique réutilisable hors des composants.

**Règle :** Un hook personnalisé peut appeler d'autres hooks. Une fonction ordinaire ne le peut pas.

---

## 1. Pourquoi créer des hooks personnalisés ?

```jsx
// ❌ Avant — logique dupliquée dans chaque composant
function ListeUtilisateurs() {
  const [donnees, setDonnees] = useState(null);
  const [chargement, setChargement] = useState(true);
  const [erreur, setErreur] = useState(null);

  useEffect(() => {
    fetch("/api/users")
      .then(r => r.json())
      .then(d => { setDonnees(d); setChargement(false); })
      .catch(e => { setErreur(e.message); setChargement(false); });
  }, []);

  if (chargement) return <Spinner />;
  if (erreur) return <Erreur message={erreur} />;
  return <ul>{donnees.map(u => <li key={u.id}>{u.name}</li>)}</ul>;
}

function ListeProduits() {
  // EXACTEMENT le même code copié-collé...
  const [donnees, setDonnees] = useState(null);
  const [chargement, setChargement] = useState(true);
  const [erreur, setErreur] = useState(null);
  // ... etc
}

// ✅ Après — logique extraite dans un hook réutilisable
function ListeUtilisateurs() {
  const { donnees, chargement, erreur } = useFetch("/api/users");
  if (chargement) return <Spinner />;
  if (erreur) return <Erreur message={erreur} />;
  return <ul>{donnees?.map(u => <li key={u.id}>{u.name}</li>)}</ul>;
}

function ListeProduits() {
  const { donnees, chargement, erreur } = useFetch("/api/products");
  // ...
}
```

---

## 2. useFetch — Récupérer des données

```jsx
// hooks/useFetch.js
import { useState, useEffect, useCallback } from "react";

function useFetch(url, options = {}) {
  const [etat, setEtat] = useState({
    donnees: null,
    chargement: true,
    erreur: null,
  });

  const [declencheur, setDeclencheur] = useState(0); // Pour relancer manuellement

  const relancer = useCallback(() => {
    setDeclencheur(n => n + 1);
  }, []);

  useEffect(() => {
    if (!url) {
      setEtat({ donnees: null, chargement: false, erreur: null });
      return;
    }

    const controller = new AbortController();
    setEtat(prev => ({ ...prev, chargement: true, erreur: null }));

    async function charger() {
      try {
        const response = await fetch(url, {
          ...options,
          signal: controller.signal,
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        setEtat({ donnees: data, chargement: false, erreur: null });
      } catch (err) {
        if (err.name === "AbortError") return; // Ignoré — annulation intentionnelle
        setEtat({ donnees: null, chargement: false, erreur: err.message });
      }
    }

    charger();

    return () => controller.abort();
  }, [url, declencheur]); // options exclues intentionnellement (référence instable)

  return { ...etat, relancer };
}

// Utilisation
function ProfilUtilisateur({ id }) {
  const {
    donnees: utilisateur,
    chargement,
    erreur,
    relancer,
  } = useFetch(id ? `/api/users/${id}` : null);

  if (chargement) return <div>Chargement...</div>;
  if (erreur) return (
    <div>
      <p>Erreur : {erreur}</p>
      <button onClick={relancer}>Réessayer</button>
    </div>
  );

  return (
    <div>
      <h1>{utilisateur?.name}</h1>
      <p>{utilisateur?.email}</p>
    </div>
  );
}
```

---

## 3. useLocalStorage — Persistance

```jsx
// hooks/useLocalStorage.js
import { useState, useEffect, useCallback } from "react";

function useLocalStorage(cle, valeurInitiale) {
  // Initialiser depuis localStorage (ou valeur initiale si absent)
  const [valeur, setValeur] = useState(() => {
    try {
      const item = localStorage.getItem(cle);
      return item !== null ? JSON.parse(item) : valeurInitiale;
    } catch {
      console.warn(`Erreur de lecture localStorage pour "${cle}"`);
      return valeurInitiale;
    }
  });

  // Synchroniser avec localStorage à chaque changement
  useEffect(() => {
    try {
      localStorage.setItem(cle, JSON.stringify(valeur));
    } catch {
      console.warn(`Erreur d'écriture localStorage pour "${cle}"`);
    }
  }, [cle, valeur]);

  // Supprimer la clé
  const supprimer = useCallback(() => {
    localStorage.removeItem(cle);
    setValeur(valeurInitiale);
  }, [cle, valeurInitiale]);

  return [valeur, setValeur, supprimer];
}

// Utilisation
function Preferences() {
  const [theme, setTheme, supprimerTheme] = useLocalStorage("theme", "clair");
  const [langue, setLangue] = useLocalStorage("langue", "fr");
  const [todos, setTodos] = useLocalStorage("todos", []);

  return (
    <div>
      <select value={theme} onChange={e => setTheme(e.target.value)}>
        <option value="clair">Clair</option>
        <option value="sombre">Sombre</option>
      </select>
      <button onClick={supprimerTheme}>Réinitialiser thème</button>
    </div>
  );
}
```

---

## 4. useDebounce — Délai de recherche

```jsx
// hooks/useDebounce.js
import { useState, useEffect } from "react";

function useDebounce(valeur, delaiMs = 500) {
  const [valeurDebounced, setValeurDebounced] = useState(valeur);

  useEffect(() => {
    const timer = setTimeout(() => {
      setValeurDebounced(valeur);
    }, delaiMs);

    return () => clearTimeout(timer); // Annule le timer si valeur change avant le délai

  }, [valeur, delaiMs]);

  return valeurDebounced;
}

// Utilisation
function BarreDeRecherche() {
  const [recherche, setRecherche] = useState("");
  const rechercheDebounced = useDebounce(recherche, 300);

  const { donnees: resultats, chargement } = useFetch(
    rechercheDebounced
      ? `/api/search?q=${encodeURIComponent(rechercheDebounced)}`
      : null
  );

  return (
    <div>
      <input
        value={recherche}
        onChange={e => setRecherche(e.target.value)}
        placeholder="Rechercher..."
      />
      {chargement && <Spinner />}
      {resultats?.map(item => (
        <div key={item.id}>{item.nom}</div>
      ))}
    </div>
  );
}
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Onglet Network de DevTools pendant qu'on tape dans la barre de recherche — SANS debounce (une requête par frappe) vs AVEC debounce (une seule requête 300ms après la dernière frappe)
> **Expliquer :** Sans debounce, taper "alice" (5 lettres) génère 5 requêtes : "a", "al", "ali", "alic", "alice". Seule la dernière est utile. Le debounce réduit les requêtes à 1 (ou 2 si on tape lentement). En production, c'est crucial pour ne pas surcharger l'API.

---

## 5. useToggle et useBoolean

```jsx
// hooks/useToggle.js
import { useState, useCallback } from "react";

function useToggle(valeurInitiale = false) {
  const [valeur, setValeur] = useState(valeurInitiale);

  const toggle = useCallback(() => setValeur(v => !v), []);
  const setVrai = useCallback(() => setValeur(true), []);
  const setFaux = useCallback(() => setValeur(false), []);

  return [valeur, toggle, setVrai, setFaux];
}

// Utilisation
function Modal() {
  const [ouverte, toggleModal, ouvrirModal, fermerModal] = useToggle(false);
  const [loading, toggleLoading] = useToggle(false);

  return (
    <div>
      <button onClick={ouvrirModal}>Ouvrir</button>
      {ouverte && (
        <div className="modal">
          <button onClick={fermerModal}>×</button>
          <p>Contenu de la modal</p>
        </div>
      )}
    </div>
  );
}
```

## 6. useAsync — Opérations asynchrones génériques

```jsx
// hooks/useAsync.js
import { useState, useCallback, useRef } from "react";

function useAsync(fonctionAsync) {
  const [etat, setEtat] = useState({
    statut: "idle", // "idle" | "chargement" | "succes" | "erreur"
    donnees: null,
    erreur: null,
  });

  const compteurRef = useRef(0); // Éviter les mises à jour "périmées" (stale)

  const executer = useCallback(async (...args) => {
    const id = ++compteurRef.current;
    setEtat({ statut: "chargement", donnees: null, erreur: null });

    try {
      const donnees = await fonctionAsync(...args);
      if (id === compteurRef.current) { // Ignorer si un appel plus récent existe
        setEtat({ statut: "succes", donnees, erreur: null });
      }
      return donnees;
    } catch (err) {
      if (id === compteurRef.current) {
        setEtat({ statut: "erreur", donnees: null, erreur: err });
      }
      throw err;
    }
  }, [fonctionAsync]);

  const reinitialiser = useCallback(() => {
    setEtat({ statut: "idle", donnees: null, erreur: null });
  }, []);

  return {
    ...etat,
    estIdle: etat.statut === "idle",
    estChargement: etat.statut === "chargement",
    estSucces: etat.statut === "succes",
    estErreur: etat.statut === "erreur",
    executer,
    reinitialiser,
  };
}

// Utilisation
async function creerUtilisateur(donnees) {
  const response = await fetch("/api/users", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(donnees),
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}

function FormulaireCreation() {
  const {
    executer,
    estChargement,
    estSucces,
    estErreur,
    donnees,
    erreur,
  } = useAsync(creerUtilisateur);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    await executer(Object.fromEntries(formData));
  };

  return (
    <form onSubmit={handleSubmit}>
      <input name="nom" required />
      <input name="email" type="email" required />
      <button type="submit" disabled={estChargement}>
        {estChargement ? "Création..." : "Créer"}
      </button>
      {estSucces && <p>Utilisateur créé : {donnees.nom}</p>}
      {estErreur && <p className="erreur">{erreur.message}</p>}
    </form>
  );
}
```

---

## 7. useForm — Gestion de formulaire simple

```jsx
// hooks/useForm.js
import { useState, useCallback } from "react";

function useForm(valeursInitiales, optionsValidation = {}) {
  const [valeurs, setValeurs] = useState(valeursInitiales);
  const [erreurs, setErreurs] = useState({});
  const [touche, setTouche] = useState({}); // Champs que l'utilisateur a modifiés

  const changerChamp = useCallback((e) => {
    const { name, value, type, checked } = e.target;
    const nouvelle = type === "checkbox" ? checked : value;

    setValeurs(prev => ({ ...prev, [name]: nouvelle }));
    setTouche(prev => ({ ...prev, [name]: true }));

    // Valider le champ en temps réel
    const validateurChamp = optionsValidation[name];
    if (validateurChamp) {
      const erreur = validateurChamp(nouvelle, valeurs);
      setErreurs(prev => ({ ...prev, [name]: erreur || "" }));
    }
  }, [optionsValidation, valeurs]);

  const valider = useCallback(() => {
    const nouvellesErreurs = {};
    let valide = true;

    for (const [nom, validateur] of Object.entries(optionsValidation)) {
      const erreur = validateur(valeurs[nom], valeurs);
      if (erreur) {
        nouvellesErreurs[nom] = erreur;
        valide = false;
      }
    }

    setErreurs(nouvellesErreurs);
    setTouche(Object.keys(valeurs).reduce((acc, k) => ({ ...acc, [k]: true }), {}));
    return valide;
  }, [valeurs, optionsValidation]);

  const reinitialiser = useCallback(() => {
    setValeurs(valeursInitiales);
    setErreurs({});
    setTouche({});
  }, [valeursInitiales]);

  const getProps = useCallback((nom) => ({
    name: nom,
    value: valeurs[nom] ?? "",
    onChange: changerChamp,
    className: touche[nom] && erreurs[nom] ? "erreur" : "",
  }), [valeurs, changerChamp, touche, erreurs]);

  return {
    valeurs,
    erreurs,
    touche,
    changerChamp,
    valider,
    reinitialiser,
    getProps, // Helper pour les inputs
  };
}

// Utilisation
const VALIDATIONS = {
  email: (val) => {
    if (!val) return "Email obligatoire";
    if (!val.includes("@")) return "Email invalide";
    return null;
  },
  motDePasse: (val) => {
    if (!val) return "Mot de passe obligatoire";
    if (val.length < 8) return "Minimum 8 caractères";
    return null;
  },
  confirmation: (val, tous) => {
    if (val !== tous.motDePasse) return "Les mots de passe ne correspondent pas";
    return null;
  },
};

function FormulaireInscription() {
  const { valeurs, erreurs, getProps, valider, reinitialiser } = useForm(
    { email: "", motDePasse: "", confirmation: "" },
    VALIDATIONS
  );

  const handleSubmit = (e) => {
    e.preventDefault();
    if (valider()) {
      console.log("Données valides:", valeurs);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input type="email" {...getProps("email")} placeholder="Email" />
      {erreurs.email && <span>{erreurs.email}</span>}

      <input type="password" {...getProps("motDePasse")} placeholder="Mot de passe" />
      {erreurs.motDePasse && <span>{erreurs.motDePasse}</span>}

      <input type="password" {...getProps("confirmation")} placeholder="Confirmer" />
      {erreurs.confirmation && <span>{erreurs.confirmation}</span>}

      <button type="submit">S'inscrire</button>
      <button type="button" onClick={reinitialiser}>Réinitialiser</button>
    </form>
  );
}
```

---

## 8. useIntersectionObserver — Infinite scroll et lazy loading

```jsx
// hooks/useIntersectionObserver.js
import { useEffect, useRef, useState } from "react";

function useIntersectionObserver(options = {}) {
  const ref = useRef(null);
  const [estVisible, setEstVisible] = useState(false);

  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    const observer = new IntersectionObserver(([entry]) => {
      setEstVisible(entry.isIntersecting);
    }, options);

    observer.observe(element);
    return () => observer.disconnect();
  }, [options.threshold, options.rootMargin]);

  return [ref, estVisible];
}

// Scroll infini
function ListeInfinie() {
  const [items, setItems] = useState(() =>
    Array.from({ length: 20 }, (_, i) => ({ id: i + 1, titre: `Item ${i + 1}` }))
  );
  const [chargementPlus, setChargementPlus] = useState(false);

  const [sentinelleRef, sentinelleVisible] = useIntersectionObserver({
    threshold: 0.1,
  });

  useEffect(() => {
    if (sentinelleVisible && !chargementPlus) {
      setChargementPlus(true);
      // Simuler un chargement
      setTimeout(() => {
        setItems(prev => {
          const dernierID = prev.at(-1)?.id ?? 0;
          const nouveaux = Array.from({ length: 20 }, (_, i) => ({
            id: dernierID + i + 1,
            titre: `Item ${dernierID + i + 1}`,
          }));
          return [...prev, ...nouveaux];
        });
        setChargementPlus(false);
      }, 1000);
    }
  }, [sentinelleVisible, chargementPlus]);

  return (
    <div style={{ height: "400px", overflow: "auto" }}>
      {items.map(item => (
        <div key={item.id} style={{ padding: "1rem", borderBottom: "1px solid #e2e8f0" }}>
          {item.titre}
        </div>
      ))}
      {/* Sentinelle invisible — déclencheur de chargement */}
      <div ref={sentinelleRef} style={{ height: "1px" }} />
      {chargementPlus && <div>Chargement...</div>}
    </div>
  );
}
```

---

## Récapitulatif — Hooks personnalisés courants

| Hook | Utilité | Dépendances |
|---|---|---|
| `useFetch(url)` | Appel API avec état de chargement | `useState`, `useEffect` |
| `useLocalStorage(key, val)` | Persistance dans localStorage | `useState`, `useEffect` |
| `useDebounce(val, ms)` | Délayer une valeur | `useState`, `useEffect` |
| `useToggle(init)` | Basculer un booléen | `useState`, `useCallback` |
| `useAsync(fn)` | Gérer des opérations async | `useState`, `useCallback` |
| `useForm(init, validators)` | Formulaires avec validation | `useState`, `useCallback` |
| `useIntersectionObserver` | Détecter la visibilité d'un élément | `useState`, `useEffect`, `useRef` |

**Convention de nommage :**
- Commencer par `use`
- Nom descriptif de la fonctionnalité, pas de l'implémentation
- Retourner un tuple `[valeur, setter]` ou un objet selon la complexité
