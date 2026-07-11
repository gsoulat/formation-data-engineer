# 02 — Composants : Props, Children, Prop Types

## Introduction

Les composants sont les blocs de construction de React. Comprendre comment passer des données entre composants via les props est fondamental. Ce chapitre couvre aussi la composition avec `children` et la validation des types de props.

---

## 1. Props — Propriétés des composants

Les props sont des données passées d'un composant parent à un composant enfant. Elles sont **en lecture seule** dans l'enfant.

```jsx
// Composant recevant des props
function CarteProduit(props) {
  return (
    <article>
      <h2>{props.nom}</h2>
      <p>{props.description}</p>
      <strong>{props.prix}€</strong>
    </article>
  );
}

// Utilisation — on passe les props comme des attributs HTML
function App() {
  return (
    <CarteProduit
      nom="Laptop Pro"
      description="Un ordinateur puissant"
      prix={999}
    />
  );
}
```

### Destructuring des props (recommandé)

```jsx
// Au lieu de props.nom, props.prix...
// On destructure directement dans la signature
function CarteProduit({ nom, description, prix, image, disponible }) {
  return (
    <article className={`carte ${disponible ? "disponible" : "epuise"}`}>
      {image && <img src={image} alt={nom} />}
      <h2>{nom}</h2>
      <p>{description}</p>
      <div className="carte-footer">
        <strong className="prix">{prix}€</strong>
        <span className="statut">
          {disponible ? "En stock" : "Épuisé"}
        </span>
      </div>
    </article>
  );
}

// Avec valeurs par défaut
function Bouton({ texte = "Cliquer", couleur = "blue", taille = "moyen", onClick }) {
  return (
    <button
      className={`btn btn-${couleur} btn-${taille}`}
      onClick={onClick}
    >
      {texte}
    </button>
  );
}

// Utilisation avec et sans valeurs par défaut
<Bouton />                                    // texte="Cliquer", couleur="blue"
<Bouton texte="Valider" couleur="green" />   // surcharge les défauts
<Bouton texte="Supprimer" couleur="red" />
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** React DevTools → sélectionner un composant CarteProduit dans l'arbre → montrer le panneau "Props" sur la droite avec toutes les props et leurs valeurs. Modifier une valeur dans DevTools et montrer la mise à jour en temps réel.
> **Expliquer :** Les props sont l'API publique du composant. Tout ce qu'on veut configurer depuis l'extérieur doit passer par les props. Les composants bien conçus ont des props claires et documentées.

---

### Spread des props

```jsx
// Passer un objet de props avec le spread
const produitData = {
  nom: "Clavier Mécanique",
  description: "Switches Cherry MX Blue",
  prix: 120,
  disponible: true,
};

<CarteProduit {...produitData} />
// Équivalent à :
// <CarteProduit nom="Clavier Mécanique" description="..." prix={120} disponible={true} />

// Pattern utile pour les composants "pass-through"
function BoutonPrimaire({ children, ...autresProps }) {
  // autresProps contient toutes les props passées (ex: onClick, disabled, type...)
  return (
    <button className="btn btn-primary" {...autresProps}>
      {children}
    </button>
  );
}

<BoutonPrimaire onClick={handleClick} disabled={isLoading} type="submit">
  Envoyer
</BoutonPrimaire>
```

---

## 2. Children — Composition de composants

La prop `children` représente le contenu passé entre les balises ouvrante et fermante du composant.

```jsx
// Composant qui affiche ses children
function Carte({ titre, children }) {
  return (
    <div className="carte">
      {titre && <h2 className="carte-titre">{titre}</h2>}
      <div className="carte-corps">
        {children}
      </div>
    </div>
  );
}

// Utilisation
<Carte titre="Mon profil">
  <p>Nom: Alice</p>
  <p>Email: alice@example.com</p>
  <button>Modifier</button>
</Carte>

// Les children peuvent être n'importe quoi
<Carte titre="Statistiques">
  <GraphiqueBar donnees={[1,2,3,4,5]} />
</Carte>

<Carte>  {/* Sans titre */}
  Juste du texte
</Carte>
```

### Composants de mise en page (Layout Components)

```jsx
// Layout principal
function PageLayout({ children }) {
  return (
    <div className="page">
      <header className="page-header">
        <nav>Navigation</nav>
      </header>
      <main className="page-main">
        {children}
      </main>
      <footer className="page-footer">
        © 2025 Mon Site
      </footer>
    </div>
  );
}

// Layout avec plusieurs zones nommées
function PageDeuxColonnes({ sidebar, main, titre }) {
  return (
    <div className="deux-colonnes">
      <h1>{titre}</h1>
      <div className="layout">
        <aside className="sidebar">{sidebar}</aside>
        <section className="contenu">{main}</section>
      </div>
    </div>
  );
}

// Utilisation
<PageDeuxColonnes
  titre="Tableau de bord"
  sidebar={
    <ul>
      <li>Dashboard</li>
      <li>Profil</li>
    </ul>
  }
  main={<DashboardContent />}
/>
```

### Patterns de composition avancés

```jsx
// Composant avec slots nommés
function Modal({ titre, children, pied }) {
  return (
    <div className="modal-overlay">
      <div className="modal">
        <div className="modal-entete">
          <h2>{titre}</h2>
        </div>
        <div className="modal-corps">
          {children}
        </div>
        {pied && (
          <div className="modal-pied">
            {pied}
          </div>
        )}
      </div>
    </div>
  );
}

<Modal
  titre="Confirmer la suppression"
  pied={
    <>
      <button onClick={annuler}>Annuler</button>
      <button onClick={confirmer} className="danger">Supprimer</button>
    </>
  }
>
  <p>Êtes-vous sûr de vouloir supprimer cet élément ?</p>
  <p>Cette action est irréversible.</p>
</Modal>

// Compound Components Pattern
function Accordion({ children }) {
  return <div className="accordion">{children}</div>;
}

function AccordionItem({ titre, children }) {
  const [ouvert, setOuvert] = useState(false);
  return (
    <div className="accordion-item">
      <button onClick={() => setOuvert(o => !o)}>
        {titre} {ouvert ? "▼" : "▶"}
      </button>
      {ouvert && <div className="accordion-contenu">{children}</div>}
    </div>
  );
}

Accordion.Item = AccordionItem; // Attacher le sous-composant

// Utilisation élégante
<Accordion>
  <Accordion.Item titre="Section 1">
    <p>Contenu de la section 1</p>
  </Accordion.Item>
  <Accordion.Item titre="Section 2">
    <p>Contenu de la section 2</p>
  </Accordion.Item>
</Accordion>
```

---

## 3. Types de données acceptés par les props

```jsx
function ExempleToutesProps({
  // Primitifs
  texte,           // string
  nombre,          // number
  actif,           // boolean
  rien,            // null / undefined

  // Objets et tableaux
  utilisateur,     // object
  items,           // array

  // Fonctions (callbacks)
  onClick,         // function () => void
  onChange,        // function (valeur) => void
  onChargement,    // function (données) => void

  // JSX
  icone,           // JSX element (ex: <StarIcon />)
  children,        // Contenu entre les balises

  // Enum (union de strings)
  variante,        // "primaire" | "secondaire" | "danger"

  // Avec défaut
  taille = "moyen",
}) {
  return (
    <div>
      <span>{texte}</span>
      <span>{nombre}</span>
      {actif && <span>Actif</span>}
      {icone}
      <button onClick={onClick} className={`btn btn-${variante}`}>
        {children}
      </button>
    </div>
  );
}

// Utilisation
<ExempleToutesProps
  texte="Bonjour"
  nombre={42}
  actif
  utilisateur={{ nom: "Alice" }}
  items={[1, 2, 3]}
  onClick={() => console.log("clic")}
  icone={<StarIcon />}
  variante="primaire"
>
  Contenu du bouton
</ExempleToutesProps>
```

---

## 4. PropTypes — Validation (JavaScript)

```jsx
import PropTypes from "prop-types"; // npm install prop-types

function CarteProduit({ nom, prix, description, categories, onAchat, image }) {
  return (
    <article className="carte">
      {image && <img src={image} alt={nom} />}
      <h2>{nom}</h2>
      <p>{description}</p>
      <ul>{categories.map(c => <li key={c}>{c}</li>)}</ul>
      <strong>{prix}€</strong>
      <button onClick={onAchat}>Ajouter au panier</button>
    </article>
  );
}

// Définir les types attendus
CarteProduit.propTypes = {
  nom: PropTypes.string.isRequired,          // String obligatoire
  prix: PropTypes.number.isRequired,         // Number obligatoire
  description: PropTypes.string,             // String optionnelle
  categories: PropTypes.arrayOf(PropTypes.string).isRequired, // Tableau de strings
  onAchat: PropTypes.func.isRequired,        // Fonction obligatoire
  image: PropTypes.string,                   // String optionnelle

  // Union de types
  taille: PropTypes.oneOf(["petit", "moyen", "grand"]),

  // Objet avec une forme spécifique
  auteur: PropTypes.shape({
    id: PropTypes.number.isRequired,
    nom: PropTypes.string.isRequired,
  }),

  // Tableau d'objets
  tags: PropTypes.arrayOf(PropTypes.shape({
    id: PropTypes.number.isRequired,
    label: PropTypes.string.isRequired,
  })),
};

// Valeurs par défaut
CarteProduit.defaultProps = {
  description: "Aucune description disponible",
  categories: [],
  image: null,
};
```

---

## 5. TypeScript avec les props (recommandé)

Si vous utilisez TypeScript (template `react-ts`), les PropTypes ne sont pas nécessaires :

```tsx
// Définir le type des props avec TypeScript
interface CarteProduitProps {
  nom: string;
  prix: number;
  description?: string;          // Optionnel avec ?
  categories: string[];
  onAchat: () => void;
  image?: string;
  variante?: "standard" | "premium" | "solde";
  auteur?: {
    id: number;
    nom: string;
  };
}

// Le composant — TypeScript vérifie les props à la compilation
function CarteProduit({
  nom,
  prix,
  description = "Aucune description",
  categories,
  onAchat,
  image,
  variante = "standard",
}: CarteProduitProps) {
  return (
    <article className={`carte carte-${variante}`}>
      {image && <img src={image} alt={nom} />}
      <h2>{nom}</h2>
      <p>{description}</p>
      <ul>{categories.map(c => <li key={c}>{c}</li>)}</ul>
      <strong>{prix}€</strong>
      <button onClick={onAchat}>Ajouter au panier</button>
    </article>
  );
}

// Utilisation — TS erreur si une prop obligatoire manque
<CarteProduit
  nom="Laptop"
  prix={999}
  categories={["informatique"]}
  onAchat={() => console.log("acheté")}
/>
```

---

## 6. Concevoir des composants réutilisables

### Principe de responsabilité unique

```jsx
// ❌ Composant trop gros — fait tout
function PageUtilisateur() {
  // Fetch des données
  // Gère l'état du formulaire
  // Affiche le profil
  // Gère la navigation
  // etc.
}

// ✅ Composants bien découpés
function PageUtilisateur() {
  return (
    <div>
      <ProfilHeader utilisateur={utilisateur} />
      <UtilisateurStats stats={stats} />
      <ProjetsList projets={projets} />
      <FormulaireModification onSave={handleSave} />
    </div>
  );
}
```

### Les niveaux de composants

```jsx
// Niveau 1 — Composants primitifs (boutons, inputs, badges)
function Badge({ texte, couleur = "gris" }) {
  return <span className={`badge badge-${couleur}`}>{texte}</span>;
}

function Avatar({ src, alt, taille = 40 }) {
  return (
    <img
      src={src || `https://ui-avatars.com/api/?name=${alt}`}
      alt={alt}
      width={taille}
      height={taille}
      style={{ borderRadius: "50%", objectFit: "cover" }}
    />
  );
}

// Niveau 2 — Composants composés (utilisent les primitifs)
function MembreEquipe({ membre }) {
  return (
    <div className="membre">
      <Avatar src={membre.avatar} alt={membre.nom} taille={50} />
      <div>
        <strong>{membre.nom}</strong>
        <Badge texte={membre.role} couleur={membre.role === "lead" ? "bleu" : "gris"} />
      </div>
    </div>
  );
}

// Niveau 3 — Composants de page (orchestrent les niveaux 1 et 2)
function PageEquipe({ membres }) {
  return (
    <section>
      <h1>Notre équipe</h1>
      <div className="grille-equipe">
        {membres.map(m => <MembreEquipe key={m.id} membre={m} />)}
      </div>
    </section>
  );
}
```

---

## 7. Exemple complet — Design System minimaliste

```jsx
// Variantes et tailles via props
function Bouton({
  children,
  variante = "primaire",
  taille = "moyen",
  desactive = false,
  chargement = false,
  iconeGauche,
  iconesDroite,
  onClick,
  type = "button",
  ...autresProps
}) {
  const classes = [
    "btn",
    `btn-${variante}`,
    `btn-${taille}`,
    desactive && "btn-desactive",
    chargement && "btn-chargement",
  ].filter(Boolean).join(" ");

  return (
    <button
      type={type}
      className={classes}
      disabled={desactive || chargement}
      onClick={onClick}
      {...autresProps}
    >
      {chargement ? (
        <span className="spinner" aria-label="Chargement..." />
      ) : (
        <>
          {iconeGauche && <span className="icone-gauche">{iconeGauche}</span>}
          <span>{children}</span>
          {iconesDroite && <span className="icone-droite">{iconesDroite}</span>}
        </>
      )}
    </button>
  );
}

// Utilisation
<Bouton variante="primaire" taille="grand" onClick={envoyer}>
  Envoyer le formulaire
</Bouton>

<Bouton variante="danger" iconeGauche="🗑️" onClick={supprimer}>
  Supprimer
</Bouton>

<Bouton chargement={isLoading} desactive={isLoading}>
  {isLoading ? "Envoi..." : "Valider"}
</Bouton>
```

---

## Récapitulatif

| Concept | Syntaxe | Note |
|---|---|---|
| Props | `<Btn texte="OK" />` | Lecture seule dans l'enfant |
| Déstructuring | `function Btn({ texte, onClick })` | Recommandé |
| Valeur par défaut | `{ couleur = "bleu" }` | En ES6 |
| Spread props | `{...config}` ou `{...autresProps}` | Pass-through |
| Children | `{children}` dans le JSX | Contenu entre balises |
| PropTypes | `Composant.propTypes = {}` | JS seulement |
| TypeScript | `interface Props {}` | Recommandé |
