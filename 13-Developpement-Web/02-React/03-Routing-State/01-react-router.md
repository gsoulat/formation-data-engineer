# 01 — React Router v6 : Navigation, useNavigate, useParams, Routes Imbriquées

## Installation

```bash
npm install react-router-dom
```

---

## 1. Configuration de base

```jsx
// src/main.jsx
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App.jsx";
import "./index.css";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </StrictMode>
);
```

```jsx
// src/App.jsx
import { Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/Layout.jsx";
import AccueilPage from "./pages/AccueilPage.jsx";
import UtilisateursPage from "./pages/UtilisateursPage.jsx";
import ProfilPage from "./pages/ProfilPage.jsx";
import SettingsPage from "./pages/SettingsPage.jsx";
import PasPage404 from "./pages/PasPage404.jsx";

function App() {
  return (
    <Routes>
      {/* Layout parent — ses children héritent du layout */}
      <Route path="/" element={<Layout />}>
        {/* Route index — affiché quand le chemin est exactement "/" */}
        <Route index element={<AccueilPage />} />

        {/* Routes imbriquées */}
        <Route path="utilisateurs" element={<UtilisateursPage />} />
        <Route path="utilisateurs/:id" element={<ProfilPage />} />
        <Route path="utilisateurs/:id/settings" element={<SettingsPage />} />

        {/* Redirection */}
        <Route path="profil" element={<Navigate to="/utilisateurs/moi" replace />} />

        {/* Route catch-all */}
        <Route path="*" element={<PasPage404 />} />
      </Route>
    </Routes>
  );
}
```

---

## 2. Layout avec `<Outlet />`

```jsx
// src/components/Layout.jsx
import { Outlet, NavLink } from "react-router-dom";

function Layout() {
  return (
    <div className="app-layout">
      <header className="app-header">
        <nav className="app-nav">
          <NavLink
            to="/"
            end  // 'end' empêche l'activation sur toutes les routes commençant par "/"
            className={({ isActive }) => isActive ? "nav-lien actif" : "nav-lien"}
          >
            Accueil
          </NavLink>

          <NavLink
            to="/utilisateurs"
            className={({ isActive }) => isActive ? "nav-lien actif" : "nav-lien"}
          >
            Utilisateurs
          </NavLink>

          {/* Style inline avec isActive */}
          <NavLink
            to="/blog"
            style={({ isActive }) => ({
              fontWeight: isActive ? "bold" : "normal",
              color: isActive ? "#4f46e5" : "inherit",
            })}
          >
            Blog
          </NavLink>
        </nav>
      </header>

      <main className="app-main">
        {/* Les routes enfants sont rendues ici */}
        <Outlet />
      </main>

      <footer>© 2025</footer>
    </div>
  );
}

export default Layout;
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Naviguer entre les pages de l'app et montrer dans React DevTools que le composant Layout ne se re-monte PAS à chaque navigation — seul le contenu de `<Outlet />` change. Montrer aussi dans l'onglet Network que les navigations côté client ne rechargent pas la page.
> **Expliquer :** C'est la différence fondamentale entre une SPA (Single Page Application) et un site traditionnel. La navigation côté client est instantanée car aucune requête HTTP n'est faite — React Router change simplement quelle route afficher dans l'Outlet.

---

## 3. useParams — Paramètres d'URL

```jsx
// src/pages/ProfilPage.jsx
import { useParams, Link } from "react-router-dom";
import { useFetch } from "../hooks/useFetch";

function ProfilPage() {
  const { id } = useParams(); // Récupère ":id" de la route "utilisateurs/:id"

  const {
    donnees: utilisateur,
    chargement,
    erreur,
  } = useFetch(`https://jsonplaceholder.typicode.com/users/${id}`);

  if (chargement) return <div>Chargement...</div>;
  if (erreur) return <div>Utilisateur non trouvé</div>;
  if (!utilisateur) return null;

  return (
    <div>
      <Link to="/utilisateurs">← Retour à la liste</Link>
      <h1>{utilisateur.name}</h1>
      <p>Email : {utilisateur.email}</p>
      <Link to={`/utilisateurs/${id}/settings`}>Paramètres</Link>
    </div>
  );
}

// Plusieurs paramètres
// Route : /produits/:categorieId/articles/:articleId
function ArticlePage() {
  const { categorieId, articleId } = useParams();
  // ...
}
```

---

## 4. useNavigate — Navigation programmatique

```jsx
import { useNavigate, Link } from "react-router-dom";

function FormulaireConnexion() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");

  const handleConnexion = async (e) => {
    e.preventDefault();
    try {
      await connexionAPI(email);
      // Naviguer après la connexion réussie
      navigate("/dashboard", { replace: true }); // replace: true évite d'ajouter à l'historique
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <form onSubmit={handleConnexion}>
      <input value={email} onChange={e => setEmail(e.target.value)} />
      <button type="submit">Connexion</button>
    </form>
  );
}

// Navigation avec état (accessible via useLocation dans la page suivante)
function ListeProduits() {
  const navigate = useNavigate();

  const voirDetail = (produit) => {
    navigate(`/produits/${produit.id}`, {
      state: {
        from: "/produits",   // D'où on vient
        nomProduit: produit.nom,  // Données supplémentaires
      },
    });
  };

  return (/* ... */);
}

// Retour en arrière
function BoutonRetour() {
  const navigate = useNavigate();
  return <button onClick={() => navigate(-1)}>Retour</button>;
  // navigate(-2) recule de 2 pages, navigate(1) avance
}
```

---

## 5. useLocation — Informations sur l'URL courante

```jsx
import { useLocation } from "react-router-dom";

function PageProduit() {
  const location = useLocation();

  console.log(location.pathname);  // "/produits/42"
  console.log(location.search);    // "?couleur=rouge&taille=L"
  console.log(location.hash);      // "#description"
  console.log(location.state);     // { from: "/produits", nomProduit: "T-shirt" }

  // Lire les paramètres de recherche (query string)
  const params = new URLSearchParams(location.search);
  const couleur = params.get("couleur"); // "rouge"
  const taille = params.get("taille");   // "L"

  return (/* ... */);
}

// useSearchParams — hook dédié pour la query string
import { useSearchParams } from "react-router-dom";

function ListeAvecFiltres() {
  const [searchParams, setSearchParams] = useSearchParams();

  const page = parseInt(searchParams.get("page") ?? "1");
  const triPar = searchParams.get("tri") ?? "date";
  const recherche = searchParams.get("q") ?? "";

  const changerPage = (nouvellePage) => {
    setSearchParams(prev => {
      prev.set("page", nouvellePage);
      return prev;
    });
  };

  const changerTri = (tri) => {
    setSearchParams({ tri, page: "1" }); // Réinitialise la page
  };

  return (
    <div>
      <input
        value={recherche}
        onChange={e => setSearchParams({ q: e.target.value, page: "1" })}
        placeholder="Rechercher..."
      />
      <select value={triPar} onChange={e => changerTri(e.target.value)}>
        <option value="date">Date</option>
        <option value="nom">Nom</option>
        <option value="prix">Prix</option>
      </select>
      {/* Pagination */}
      <button onClick={() => changerPage(page - 1)} disabled={page <= 1}>
        Précédent
      </button>
      <span>Page {page}</span>
      <button onClick={() => changerPage(page + 1)}>Suivant</button>
    </div>
  );
}
```

---

## 6. Routes protégées (authentification)

```jsx
// src/components/RouteProtegee.jsx
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../hooks/useAuth"; // Hook d'authentification

function RouteProtegee({ children, roles = [] }) {
  const { utilisateur, estAuthentifie } = useAuth();
  const location = useLocation();

  if (!estAuthentifie) {
    // Rediriger vers la connexion en mémorisant où on voulait aller
    return <Navigate to="/connexion" state={{ from: location }} replace />;
  }

  if (roles.length > 0 && !roles.includes(utilisateur.role)) {
    return <Navigate to="/acces-refuse" replace />;
  }

  return children;
}

// Utilisation dans App.jsx
<Route path="/dashboard" element={
  <RouteProtegee>
    <Dashboard />
  </RouteProtegee>
} />

<Route path="/admin" element={
  <RouteProtegee roles={["admin"]}>
    <AdminPanel />
  </RouteProtegee>
} />

// Page de connexion — redirige vers la page demandée après connexion
function PageConnexion() {
  const navigate = useNavigate();
  const location = useLocation();
  const { connexion } = useAuth();

  const destination = location.state?.from?.pathname ?? "/dashboard";

  const handleConnexion = async (credentials) => {
    await connexion(credentials);
    navigate(destination, { replace: true }); // Redirige vers la page d'origine
  };

  return (/* formulaire de connexion */);
}
```

---

## 7. Routes imbriquées avec layout secondaire

```jsx
// Architecture réelle d'une application
function App() {
  return (
    <Routes>
      {/* Routes publiques */}
      <Route path="/" element={<LayoutPublic />}>
        <Route index element={<Accueil />} />
        <Route path="connexion" element={<Connexion />} />
        <Route path="inscription" element={<Inscription />} />
      </Route>

      {/* Routes authentifiées avec layout différent */}
      <Route path="/app" element={
        <RouteProtegee>
          <LayoutApp />
        </RouteProtegee>
      }>
        <Route index element={<Navigate to="dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />

        {/* Sous-section avec son propre layout */}
        <Route path="produits" element={<LayoutProduits />}>
          <Route index element={<ListeProduits />} />
          <Route path="nouveau" element={<NouveauProduit />} />
          <Route path=":id" element={<DetailProduit />} />
          <Route path=":id/editer" element={<EditerProduit />} />
        </Route>

        {/* Routes admin */}
        <Route path="admin" element={
          <RouteProtegee roles={["admin"]}>
            <LayoutAdmin />
          </RouteProtegee>
        }>
          <Route index element={<AdminDashboard />} />
          <Route path="utilisateurs" element={<AdminUtilisateurs />} />
        </Route>
      </Route>

      {/* Route 404 */}
      <Route path="*" element={<Page404 />} />
    </Routes>
  );
}
```

---

## 8. Code splitting avec React.lazy

```jsx
import { lazy, Suspense } from "react";
import { Routes, Route } from "react-router-dom";

// Chargement lazy — le bundle de la page n'est téléchargé que si on y navigue
const Dashboard = lazy(() => import("./pages/Dashboard"));
const Produits = lazy(() => import("./pages/Produits"));
const Admin = lazy(() => import("./pages/Admin"));

function App() {
  return (
    <Suspense fallback={<PageLoader />}>  {/* Affiché pendant le chargement */}
      <Routes>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/produits" element={<Produits />} />
        <Route path="/admin" element={<Admin />} />
      </Routes>
    </Suspense>
  );
}

// Indicateur de chargement de page
function PageLoader() {
  return (
    <div style={{ display: "flex", justifyContent: "center", padding: "4rem" }}>
      <div>Chargement de la page...</div>
    </div>
  );
}
```

---

## Récapitulatif

| Hook/Composant | Utilité |
|---|---|
| `<Routes>` | Conteneur de toutes les routes |
| `<Route path="..." element={<Comp />}>` | Définir une route |
| `<Outlet />` | Afficher les routes enfants dans un layout |
| `<Link to="...">` | Lien de navigation (pas de rechargement) |
| `<NavLink>` | Lien avec état actif (classe/style conditionnel) |
| `<Navigate to="...">` | Redirection déclarative |
| `useParams()` | Lire les paramètres dynamiques d'URL (`:id`) |
| `useNavigate()` | Navigation programmatique |
| `useLocation()` | Informations sur l'URL courante |
| `useSearchParams()` | Lire/modifier la query string |
