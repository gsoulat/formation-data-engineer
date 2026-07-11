# 03 — State et Événements : useState, Handlers, Formulaires Contrôlés

## Introduction

L'état (`state`) est ce qui rend les composants React interactifs. Contrairement aux props (données du parent), le state est **géré localement** par le composant. Quand l'état change, React **re-rend automatiquement** le composant.

---

## 1. useState — Le hook d'état

```jsx
import { useState } from "react";

function Compteur() {
  // useState retourne [valeurActuelle, fonctionPourLaModifier]
  const [compteur, setCompteur] = useState(0); // 0 est la valeur initiale

  return (
    <div>
      <p>Compteur : {compteur}</p>
      <button onClick={() => setCompteur(compteur + 1)}>+1</button>
      <button onClick={() => setCompteur(compteur - 1)}>-1</button>
      <button onClick={() => setCompteur(0)}>Réinitialiser</button>
    </div>
  );
}
```

### Règle fondamentale : ne pas muter l'état directement

```jsx
function ExemplesEtat() {
  const [nombre, setNombre] = useState(0);
  const [texte, setTexte] = useState("");
  const [actif, setActif] = useState(false);

  // ✅ Correct — utiliser la fonction setter
  const incrementer = () => setNombre(nombre + 1);
  const changerTexte = () => setTexte("nouveau texte");
  const basculer = () => setActif(!actif);

  // ❌ JAMAIS muter directement
  // nombre = nombre + 1; // Ignoré par React — pas de re-rendu !
  // actif = !actif;      // Ignoré par React !

  return (/* ... */);
}
```

### Fonction de mise à jour (updater function)

```jsx
function Compteur() {
  const [count, setCount] = useState(0);

  // ❌ Peut donner des résultats incorrects si plusieurs setCount s'exécutent
  // dans le même cycle de rendu (batching)
  const incrementerTroisFois = () => {
    setCount(count + 1); // count est toujours 0 ici (valeur capturée dans la closure)
    setCount(count + 1); // count est toujours 0 !
    setCount(count + 1); // count est toujours 0 !
    // Résultat : count = 1 (pas 3 !)
  };

  // ✅ Utiliser la forme fonctionnelle quand la nouvelle valeur dépend de l'ancienne
  const incrementerTroisFoisCorrect = () => {
    setCount(prev => prev + 1); // prev = valeur la plus récente
    setCount(prev => prev + 1); // prev = valeur précédente + 1
    setCount(prev => prev + 1); // prev = valeur précédente + 1
    // Résultat : count = 3 ✓
  };

  return (
    <div>
      <p>{count}</p>
      <button onClick={incrementerTroisFoisCorrect}>+3</button>
    </div>
  );
}
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** React DevTools → Components → sélectionner un composant avec useState → montrer que la valeur dans "Hooks > State" se met à jour en temps réel quand on clique sur les boutons. On peut même modifier la valeur directement dans DevTools.
> **Expliquer :** React DevTools permet de voir et modifier le state de n'importe quel composant en live. C'est extrêmement utile pour déboguer. On peut "forcer" un état particulier sans devoir interagir avec l'UI.

---

## 2. État avec des objets et tableaux

La règle d'or : **toujours créer un NOUVEL objet/tableau** pour les mises à jour d'état. Ne jamais muter l'état existant.

```jsx
function FormulaireProfil() {
  const [utilisateur, setUtilisateur] = useState({
    prenom: "Alice",
    nom: "Martin",
    email: "alice@example.com",
    age: 30,
  });

  // ✅ Mise à jour immutable d'une propriété
  const changerPrenom = (nouveauPrenom) => {
    setUtilisateur({
      ...utilisateur,      // Copier TOUTES les propriétés existantes
      prenom: nouveauPrenom, // Puis surcharger celle qu'on veut modifier
    });
  };

  // Pattern générique pour mettre à jour n'importe quel champ
  const changerChamp = (champ, valeur) => {
    setUtilisateur(prev => ({ ...prev, [champ]: valeur }));
  };

  return (
    <form>
      <input
        value={utilisateur.prenom}
        onChange={e => changerChamp("prenom", e.target.value)}
      />
      <input
        value={utilisateur.email}
        onChange={e => changerChamp("email", e.target.value)}
      />
    </form>
  );
}

// État avec un tableau
function ListeTodos() {
  const [todos, setTodos] = useState([
    { id: 1, texte: "Apprendre React", fait: true },
    { id: 2, texte: "Construire une app", fait: false },
  ]);

  // Ajouter un élément — ne pas utiliser push() !
  const ajouterTodo = (texte) => {
    const nouveau = { id: Date.now(), texte, fait: false };
    setTodos([...todos, nouveau]);           // ✅ Nouveau tableau
    // setTodos(todos.push(nouveau));        // ❌ Mutation directe !
  };

  // Supprimer — utiliser filter()
  const supprimerTodo = (id) => {
    setTodos(todos.filter(t => t.id !== id)); // ✅ Nouveau tableau sans l'élément
  };

  // Modifier — utiliser map()
  const toggleTodo = (id) => {
    setTodos(todos.map(t =>
      t.id === id ? { ...t, fait: !t.fait } : t // ✅ Nouveau objet pour l'élément modifié
    ));
  };

  return (
    <ul>
      {todos.map(todo => (
        <li key={todo.id}>
          <span
            style={{ textDecoration: todo.fait ? "line-through" : "none" }}
            onClick={() => toggleTodo(todo.id)}
          >
            {todo.texte}
          </span>
          <button onClick={() => supprimerTodo(todo.id)}>✕</button>
        </li>
      ))}
      <button onClick={() => ajouterTodo("Nouvelle tâche")}>Ajouter</button>
    </ul>
  );
}
```

---

## 3. Gestion des événements

```jsx
function ExemplesEvenements() {
  // Gestionnaire d'événement simple
  const handleClick = () => {
    console.log("Bouton cliqué !");
  };

  // Avec l'objet Event
  const handleClickAvecEvent = (event) => {
    console.log("Bouton:", event.target.textContent);
    console.log("Position:", event.clientX, event.clientY);
  };

  // Avec un paramètre supplémentaire (via arrow function)
  const handleSupprimer = (id) => {
    console.log("Supprimer l'item:", id);
  };

  // Prévenir le comportement par défaut
  const handleSubmit = (event) => {
    event.preventDefault(); // Empêche le rechargement de la page
    console.log("Formulaire soumis");
  };

  return (
    <div>
      {/* Attacher le gestionnaire sans l'appeler ! (pas de parenthèses) */}
      <button onClick={handleClick}>Cliquer</button>
      <button onClick={handleClickAvecEvent}>Avec Event</button>

      {/* Arrow function pour passer des paramètres */}
      <button onClick={() => handleSupprimer(42)}>Supprimer #42</button>

      {/* Inline — acceptable pour les cas simples */}
      <button onClick={() => console.log("Inline !")}>Inline</button>

      {/* Formulaire */}
      <form onSubmit={handleSubmit}>
        <button type="submit">Envoyer</button>
      </form>
    </div>
  );
}
```

### Événements courants

```jsx
function TousLesEvenements() {
  return (
    <div>
      {/* Souris */}
      <div
        onClick={(e) => console.log("clic")}
        onDoubleClick={(e) => console.log("double-clic")}
        onMouseEnter={() => console.log("entrée souris")}
        onMouseLeave={() => console.log("sortie souris")}
        onMouseMove={(e) => console.log(e.clientX, e.clientY)}
      />

      {/* Clavier */}
      <input
        onKeyDown={(e) => console.log("touche appuyée:", e.key)}
        onKeyUp={(e) => console.log("touche relâchée:", e.key)}
      />

      {/* Focus */}
      <input
        onFocus={() => console.log("focus")}
        onBlur={() => console.log("blur")}
      />

      {/* Formulaire */}
      <input onChange={(e) => console.log("valeur:", e.target.value)} />
      <form onSubmit={(e) => { e.preventDefault(); }} />

      {/* Drag & Drop */}
      <div
        draggable
        onDragStart={(e) => console.log("début drag")}
        onDrop={(e) => { e.preventDefault(); console.log("drop"); }}
        onDragOver={(e) => e.preventDefault()}
      />
    </div>
  );
}
```

---

## 4. Formulaires contrôlés

Un formulaire **contrôlé** est un formulaire dont les valeurs sont stockées dans le state React. React "contrôle" le champ — la valeur affichée vient toujours du state.

```jsx
function FormulaireInscription() {
  const [formData, setFormData] = useState({
    prenom: "",
    nom: "",
    email: "",
    motDePasse: "",
    role: "utilisateur",
    accepteConditions: false,
  });

  const [erreurs, setErreurs] = useState({});

  // Handler générique pour tous les champs
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));

    // Effacer l'erreur du champ modifié
    if (erreurs[name]) {
      setErreurs(prev => ({ ...prev, [name]: "" }));
    }
  };

  const valider = () => {
    const nouvellesErreurs = {};

    if (!formData.prenom.trim()) {
      nouvellesErreurs.prenom = "Le prénom est obligatoire";
    }
    if (!formData.email.includes("@")) {
      nouvellesErreurs.email = "Email invalide";
    }
    if (formData.motDePasse.length < 8) {
      nouvellesErreurs.motDePasse = "Minimum 8 caractères";
    }
    if (!formData.accepteConditions) {
      nouvellesErreurs.accepteConditions = "Vous devez accepter les conditions";
    }

    setErreurs(nouvellesErreurs);
    return Object.keys(nouvellesErreurs).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (valider()) {
      console.log("Formulaire valide:", formData);
      // Envoyer les données...
    }
  };

  return (
    <form onSubmit={handleSubmit} noValidate>
      {/* Champ texte */}
      <div className="champ">
        <label htmlFor="prenom">Prénom *</label>
        <input
          type="text"
          id="prenom"
          name="prenom"
          value={formData.prenom}
          onChange={handleChange}
          className={erreurs.prenom ? "erreur" : ""}
          autoComplete="given-name"
        />
        {erreurs.prenom && <span className="msg-erreur">{erreurs.prenom}</span>}
      </div>

      {/* Email */}
      <div className="champ">
        <label htmlFor="email">Email *</label>
        <input
          type="email"
          id="email"
          name="email"
          value={formData.email}
          onChange={handleChange}
          className={erreurs.email ? "erreur" : ""}
        />
        {erreurs.email && <span className="msg-erreur">{erreurs.email}</span>}
      </div>

      {/* Mot de passe */}
      <div className="champ">
        <label htmlFor="motDePasse">Mot de passe *</label>
        <input
          type="password"
          id="motDePasse"
          name="motDePasse"
          value={formData.motDePasse}
          onChange={handleChange}
          className={erreurs.motDePasse ? "erreur" : ""}
        />
        {erreurs.motDePasse && <span className="msg-erreur">{erreurs.motDePasse}</span>}
      </div>

      {/* Select */}
      <div className="champ">
        <label htmlFor="role">Rôle</label>
        <select id="role" name="role" value={formData.role} onChange={handleChange}>
          <option value="utilisateur">Utilisateur</option>
          <option value="moderateur">Modérateur</option>
          <option value="admin">Administrateur</option>
        </select>
      </div>

      {/* Checkbox */}
      <div className="champ">
        <label className="checkbox-label">
          <input
            type="checkbox"
            name="accepteConditions"
            checked={formData.accepteConditions}
            onChange={handleChange}
          />
          J'accepte les conditions d'utilisation
        </label>
        {erreurs.accepteConditions && (
          <span className="msg-erreur">{erreurs.accepteConditions}</span>
        )}
      </div>

      <button type="submit">Créer mon compte</button>
    </form>
  );
}
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Montrer la différence entre formulaire CONTRÔLÉ et NON-CONTRÔLÉ — dans un formulaire contrôlé, taper dans l'input et montrer dans React DevTools que le state se met à jour à chaque frappe. Montrer aussi que `value` sans `onChange` bloque la saisie.
> **Expliquer :** Avec `value={state}` sans `onChange`, React "verrouille" la valeur du champ (elle revient toujours à l'état). C'est intentionnel — React veut être la seule source de vérité. Pour débloquer, il FAUT ajouter onChange.

---

## 5. Lever l'état (Lifting State Up)

Quand deux composants frères ont besoin de partager le même état, on "lève" l'état vers leur parent commun.

```jsx
// ❌ Chaque composant a son propre état — ils ne se synchronisent pas
function Probleme() {
  return (
    <div>
      <Temperature scale="celsius" />    {/* Son propre état */}
      <Temperature scale="fahrenheit" /> {/* Son propre état — pas synchronisé ! */}
    </div>
  );
}

// ✅ L'état est dans le parent commun
function Convertisseur() {
  const [celsius, setCelsius] = useState(20);

  const celsiusToFahrenheit = (c) => (c * 9) / 5 + 32;
  const fahrenheitToCelsius = (f) => ((f - 32) * 5) / 9;

  const handleCelsiusChange = (valeur) => {
    setCelsius(parseFloat(valeur) || 0);
  };

  const handleFahrenheitChange = (valeur) => {
    setCelsius(fahrenheitToCelsius(parseFloat(valeur) || 0));
  };

  return (
    <div>
      <ChampTemperature
        label="Celsius"
        valeur={celsius.toFixed(1)}
        onChange={handleCelsiusChange}
      />
      <ChampTemperature
        label="Fahrenheit"
        valeur={celsiusToFahrenheit(celsius).toFixed(1)}
        onChange={handleFahrenheitChange}
      />
      <p>
        {celsius}°C = {celsiusToFahrenheit(celsius).toFixed(1)}°F
      </p>
    </div>
  );
}

function ChampTemperature({ label, valeur, onChange }) {
  return (
    <label>
      {label}:
      <input
        type="number"
        value={valeur}
        onChange={e => onChange(e.target.value)}
      />
    </label>
  );
}
```

---

## 6. Exemple complet — Panier d'achat

```jsx
// Données
const CATALOGUE = [
  { id: 1, nom: "T-shirt", prix: 29.99 },
  { id: 2, nom: "Pantalon", prix: 59.99 },
  { id: 3, nom: "Veste", prix: 99.99 },
  { id: 4, nom: "Chaussures", prix: 79.99 },
];

// Composant produit
function Produit({ produit, quantiteDansPanier, onAjouter, onRetirer }) {
  return (
    <div className="produit">
      <span>{produit.nom}</span>
      <span>{produit.prix}€</span>
      {quantiteDansPanier > 0 ? (
        <div className="controles">
          <button onClick={() => onRetirer(produit.id)}>−</button>
          <span>{quantiteDansPanier}</span>
          <button onClick={() => onAjouter(produit.id)}>+</button>
        </div>
      ) : (
        <button onClick={() => onAjouter(produit.id)}>Ajouter</button>
      )}
    </div>
  );
}

// Composant panier
function Panier({ items, onRetirer, onVider }) {
  if (items.length === 0) return <p>Panier vide</p>;

  const total = items.reduce((sum, item) => sum + item.produit.prix * item.quantite, 0);

  return (
    <div className="panier">
      <h3>Panier</h3>
      {items.map(item => (
        <div key={item.produit.id} className="panier-item">
          <span>{item.produit.nom} × {item.quantite}</span>
          <span>{(item.produit.prix * item.quantite).toFixed(2)}€</span>
          <button onClick={() => onRetirer(item.produit.id)}>−</button>
        </div>
      ))}
      <div className="total">
        <strong>Total : {total.toFixed(2)}€</strong>
      </div>
      <button onClick={onVider}>Vider le panier</button>
    </div>
  );
}

// Composant racine — state dans le parent commun
function App() {
  // panier = Map de { produitId → quantite }
  const [panier, setPanier] = useState(new Map());

  const ajouterAuPanier = (produitId) => {
    setPanier(prev => {
      const nouvelle = new Map(prev); // Copier la Map
      nouvelle.set(produitId, (nouvelle.get(produitId) ?? 0) + 1);
      return nouvelle;
    });
  };

  const retirerDuPanier = (produitId) => {
    setPanier(prev => {
      const nouvelle = new Map(prev);
      const qtActuelle = nouvelle.get(produitId) ?? 0;
      if (qtActuelle <= 1) {
        nouvelle.delete(produitId);
      } else {
        nouvelle.set(produitId, qtActuelle - 1);
      }
      return nouvelle;
    });
  };

  const viderPanier = () => setPanier(new Map());

  // Préparer les items du panier pour l'affichage
  const itemsPanier = [...panier.entries()].map(([id, quantite]) => ({
    produit: CATALOGUE.find(p => p.id === id),
    quantite,
  }));

  return (
    <div style={{ display: "flex", gap: "2rem" }}>
      <div>
        <h2>Catalogue</h2>
        {CATALOGUE.map(produit => (
          <Produit
            key={produit.id}
            produit={produit}
            quantiteDansPanier={panier.get(produit.id) ?? 0}
            onAjouter={ajouterAuPanier}
            onRetirer={retirerDuPanier}
          />
        ))}
      </div>
      <Panier
        items={itemsPanier}
        onRetirer={retirerDuPanier}
        onVider={viderPanier}
      />
    </div>
  );
}
```

---

## Récapitulatif

| Concept | Code | Règle |
|---|---|---|
| Déclarer l'état | `const [val, setVal] = useState(init)` | Ne jamais muter directement |
| Mettre à jour | `setVal(nouvelleValeur)` | Déclenche un re-rendu |
| Mise à jour fonctionnelle | `setVal(prev => prev + 1)` | Quand la valeur dépend de l'ancienne |
| Objet état | `setObj(prev => ({ ...prev, cle: val }))` | Toujours créer un nouvel objet |
| Tableau état | `setArr([...arr, nouveau])` | Toujours créer un nouveau tableau |
| Événement | `onClick={handler}` | Pas de parenthèses |
| Avec paramètre | `onClick={() => handler(id)}` | Arrow function |
| Formulaire | `value={state}` + `onChange={fn}` | Formulaire contrôlé |
| Lever l'état | Déplacer le state vers le parent commun | Pour partager entre frères |
