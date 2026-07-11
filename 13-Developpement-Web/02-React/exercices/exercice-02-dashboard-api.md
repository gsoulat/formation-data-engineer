# Exercice 02 — Dashboard avec TanStack Query et React Router

## Objectif

Construire un tableau de bord d'administration qui consomme une API REST, avec navigation, état de chargement, filtres, et mise à jour de données.

---

## Setup

```bash
npm create vite@latest dashboard-react -- --template react
cd dashboard-react
npm install react-router-dom @tanstack/react-query @tanstack/react-query-devtools
npm run dev
```

---

## Architecture

```
src/
├── api/
│   └── apiClient.js     ← Fonctions fetch centralisées
├── components/
│   ├── Layout.jsx
│   ├── StatCard.jsx
│   ├── DataTable.jsx
│   └── Spinner.jsx
├── pages/
│   ├── DashboardPage.jsx
│   ├── UsersPage.jsx
│   ├── UserDetailPage.jsx
│   └── PostsPage.jsx
├── hooks/
│   └── useSearch.js
├── App.jsx
└── main.jsx
```

---

## Partie 1 — Configuration

### `src/main.jsx`

```jsx
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import App from "./App.jsx";
import "./index.css";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,
      retry: 2,
      refetchOnWindowFocus: false, // Désactivé pour simplifier l'exercice
    },
  },
});

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <App />
      </BrowserRouter>
      <ReactQueryDevtools />
    </QueryClientProvider>
  </StrictMode>
);
```

### `src/App.jsx`

```jsx
import { Routes, Route, Navigate } from "react-router-dom";
import { lazy, Suspense } from "react";
import Layout from "./components/Layout";
import Spinner from "./components/Spinner";

const DashboardPage = lazy(() => import("./pages/DashboardPage"));
const UsersPage = lazy(() => import("./pages/UsersPage"));
const UserDetailPage = lazy(() => import("./pages/UserDetailPage"));
const PostsPage = lazy(() => import("./pages/PostsPage"));

function App() {
  return (
    <Suspense fallback={<Spinner fullPage />}>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="users" element={<UsersPage />} />
          <Route path="users/:id" element={<UserDetailPage />} />
          <Route path="posts" element={<PostsPage />} />
        </Route>
      </Routes>
    </Suspense>
  );
}

export default App;
```

---

## Partie 2 — API Client

```javascript
// src/api/apiClient.js
const BASE_URL = "https://jsonplaceholder.typicode.com";

async function get(endpoint) {
  const response = await fetch(`${BASE_URL}${endpoint}`);
  if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  return response.json();
}

async function post(endpoint, body) {
  const response = await fetch(`${BASE_URL}${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}

async function patch(endpoint, body) {
  const response = await fetch(`${BASE_URL}${endpoint}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}

async function del(endpoint) {
  const response = await fetch(`${BASE_URL}${endpoint}`, { method: "DELETE" });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return true;
}

// Fonctions API spécifiques
export const api = {
  // Utilisateurs
  getUsers: () => get("/users"),
  getUser: (id) => get(`/users/${id}`),
  getUserPosts: (id) => get(`/users/${id}/posts`),

  // Posts
  getPosts: () => get("/posts"),
  getPost: (id) => get(`/posts/${id}`),
  getPostComments: (id) => get(`/posts/${id}/comments`),
  createPost: (data) => post("/posts", data),
  updatePost: (id, data) => patch(`/posts/${id}`, data),
  deletePost: (id) => del(`/posts/${id}`),
};

// Query Keys factory
export const queryKeys = {
  users: {
    all: ["users"],
    detail: (id) => ["users", id],
    posts: (id) => ["users", id, "posts"],
  },
  posts: {
    all: ["posts"],
    detail: (id) => ["posts", id],
    comments: (id) => ["posts", id, "comments"],
  },
};
```

---

## Partie 3 — Composants UI

### `src/components/Layout.jsx`

```jsx
import { Outlet, NavLink, Link } from "react-router-dom";
import { useIsFetching } from "@tanstack/react-query";

function Layout() {
  const nombreRequetes = useIsFetching();

  return (
    <div className="layout">
      {/* Barre de progression globale */}
      {nombreRequetes > 0 && <div className="progress-bar" />}

      <aside className="sidebar">
        <div className="sidebar-brand">
          <Link to="/">📊 Dashboard</Link>
        </div>
        <nav className="sidebar-nav">
          <NavLink to="/dashboard" className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}>
            🏠 Accueil
          </NavLink>
          <NavLink to="/users" className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}>
            👥 Utilisateurs
          </NavLink>
          <NavLink to="/posts" className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}>
            📝 Articles
          </NavLink>
        </nav>
      </aside>

      <div className="main-wrapper">
        <header className="topbar">
          <div className="topbar-right">
            {nombreRequetes > 0 && (
              <span className="syncing">⏳ Synchronisation...</span>
            )}
          </div>
        </header>

        <main className="main-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

export default Layout;
```

### `src/components/StatCard.jsx`

```jsx
function StatCard({ titre, valeur, icone, couleur = "bleu", chargement = false }) {
  if (chargement) {
    return (
      <div className={`stat-card stat-card-${couleur} skeleton`}>
        <div className="skeleton-icon" />
        <div>
          <div className="skeleton-line short" />
          <div className="skeleton-line" />
        </div>
      </div>
    );
  }

  return (
    <div className={`stat-card stat-card-${couleur}`}>
      <div className="stat-icon">{icone}</div>
      <div>
        <p className="stat-titre">{titre}</p>
        <p className="stat-valeur">{valeur}</p>
      </div>
    </div>
  );
}

export default StatCard;
```

### `src/components/DataTable.jsx`

```jsx
function DataTable({ colonnes, donnees, onRowClick, chargement = false }) {
  if (chargement) {
    return (
      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>{colonnes.map(c => <th key={c.key}>{c.label}</th>)}</tr>
          </thead>
          <tbody>
            {Array.from({ length: 5 }).map((_, i) => (
              <tr key={i} className="skeleton-row">
                {colonnes.map(c => <td key={c.key}><div className="skeleton-line" /></td>)}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  return (
    <div className="table-container">
      <table className="data-table">
        <thead>
          <tr>
            {colonnes.map(c => (
              <th key={c.key} className={c.className}>{c.label}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {donnees.length === 0 ? (
            <tr>
              <td colSpan={colonnes.length} className="table-empty">
                Aucune donnée disponible
              </td>
            </tr>
          ) : (
            donnees.map((ligne, i) => (
              <tr
                key={ligne.id ?? i}
                onClick={() => onRowClick?.(ligne)}
                className={onRowClick ? "clickable" : ""}
              >
                {colonnes.map(c => (
                  <td key={c.key} className={c.className}>
                    {c.render ? c.render(ligne[c.key], ligne) : ligne[c.key]}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}

export default DataTable;
```

---

## Partie 4 — Pages

### `src/pages/DashboardPage.jsx`

```jsx
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { api, queryKeys } from "../api/apiClient";
import StatCard from "../components/StatCard";
import DataTable from "../components/DataTable";

function DashboardPage() {
  const { data: users, isLoading: loadingUsers } = useQuery({
    queryKey: queryKeys.users.all,
    queryFn: api.getUsers,
  });

  const { data: posts, isLoading: loadingPosts } = useQuery({
    queryKey: queryKeys.posts.all,
    queryFn: api.getPosts,
  });

  const derniersUsers = users?.slice(-5).reverse() ?? [];
  const derniersPosts = posts?.slice(-5).reverse() ?? [];

  const COLONNES_USERS = [
    { key: "name", label: "Nom" },
    { key: "email", label: "Email" },
    { key: "company", label: "Entreprise", render: (_, u) => u.company?.name },
  ];

  const COLONNES_POSTS = [
    { key: "id", label: "#", className: "col-id" },
    { key: "title", label: "Titre", render: t => t.length > 50 ? t.slice(0, 50) + "..." : t },
    { key: "userId", label: "Auteur", render: (id) => `Utilisateur ${id}` },
  ];

  return (
    <div className="page">
      <h1>Tableau de bord</h1>

      <div className="stats-grid">
        <StatCard
          titre="Utilisateurs"
          valeur={users?.length ?? "—"}
          icone="👥"
          couleur="bleu"
          chargement={loadingUsers}
        />
        <StatCard
          titre="Articles publiés"
          valeur={posts?.length ?? "—"}
          icone="📝"
          couleur="vert"
          chargement={loadingPosts}
        />
        <StatCard
          titre="Commentaires"
          valeur="500"
          icone="💬"
          couleur="orange"
        />
        <StatCard
          titre="Albums"
          valeur="100"
          icone="📸"
          couleur="violet"
        />
      </div>

      <div className="tables-grid">
        <section className="card">
          <div className="card-header">
            <h2>Derniers utilisateurs</h2>
            <Link to="/users" className="voir-tout">Voir tout →</Link>
          </div>
          <DataTable
            colonnes={COLONNES_USERS}
            donnees={derniersUsers}
            chargement={loadingUsers}
          />
        </section>

        <section className="card">
          <div className="card-header">
            <h2>Derniers articles</h2>
            <Link to="/posts" className="voir-tout">Voir tout →</Link>
          </div>
          <DataTable
            colonnes={COLONNES_POSTS}
            donnees={derniersPosts}
            chargement={loadingPosts}
          />
        </section>
      </div>
    </div>
  );
}

export default DashboardPage;
```

### `src/pages/UsersPage.jsx`

```jsx
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { api, queryKeys } from "../api/apiClient";
import DataTable from "../components/DataTable";

function UsersPage() {
  const navigate = useNavigate();
  const [recherche, setRecherche] = useState("");

  const { data: users = [], isLoading, error } = useQuery({
    queryKey: queryKeys.users.all,
    queryFn: api.getUsers,
  });

  const usersFiltres = users.filter(u =>
    [u.name, u.email, u.company?.name ?? ""]
      .some(val => val.toLowerCase().includes(recherche.toLowerCase()))
  );

  const COLONNES = [
    { key: "id", label: "#", className: "col-id" },
    { key: "name", label: "Nom" },
    { key: "email", label: "Email", render: (e) => <a href={`mailto:${e}`}>{e}</a> },
    { key: "phone", label: "Téléphone" },
    { key: "company", label: "Entreprise", render: (_, u) => u.company?.name },
    {
      key: "website",
      label: "Site",
      render: (w) => (
        <a href={`https://${w}`} target="_blank" rel="noopener noreferrer">
          {w}
        </a>
      ),
    },
  ];

  if (error) return <div className="erreur">Erreur : {error.message}</div>;

  return (
    <div className="page">
      <div className="page-header">
        <h1>Utilisateurs ({usersFiltres.length})</h1>
        <input
          type="search"
          placeholder="Rechercher..."
          value={recherche}
          onChange={e => setRecherche(e.target.value)}
          className="search-input"
        />
      </div>

      <div className="card">
        <DataTable
          colonnes={COLONNES}
          donnees={usersFiltres}
          chargement={isLoading}
          onRowClick={(user) => navigate(`/users/${user.id}`)}
        />
      </div>
    </div>
  );
}

export default UsersPage;
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** React Query DevTools — montrer les queries "users" et "posts" dans le panneau. Naviguer vers la page Users puis revenir au Dashboard. Montrer que les données sont servies depuis le CACHE (la query ne repart pas). Puis cliquer "Refetch" pour forcer un rechargement.
> **Expliquer :** C'est la valeur principale de TanStack Query — le cache. Sans Query, chaque visite de page déclencherait un nouveau fetch. Avec Query, si les données sont "fraîches" (staleTime pas dépassé), elles sont servies instantanément depuis le cache. C'est ce qui rend les navigations si rapides.

---

### `src/pages/UserDetailPage.jsx`

```jsx
import { useParams, Link, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api, queryKeys } from "../api/apiClient";

function UserDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const { data: user, isLoading: loadingUser } = useQuery({
    queryKey: queryKeys.users.detail(Number(id)),
    queryFn: () => api.getUser(id),
  });

  const { data: posts = [], isLoading: loadingPosts } = useQuery({
    queryKey: queryKeys.users.posts(Number(id)),
    queryFn: () => api.getUserPosts(id),
  });

  if (loadingUser) return <div>Chargement du profil...</div>;

  if (!user) return <div>Utilisateur non trouvé</div>;

  return (
    <div className="page">
      <button onClick={() => navigate(-1)} className="btn-retour">
        ← Retour
      </button>

      <div className="user-profile">
        <div className="user-avatar">
          {user.name.charAt(0).toUpperCase()}
        </div>

        <div className="user-info">
          <h1>{user.name}</h1>
          <p>@{user.username}</p>

          <div className="user-details">
            <div>
              <span>📧</span>
              <a href={`mailto:${user.email}`}>{user.email}</a>
            </div>
            <div>
              <span>📞</span>
              <span>{user.phone}</span>
            </div>
            <div>
              <span>🌐</span>
              <a href={`https://${user.website}`} target="_blank" rel="noopener noreferrer">
                {user.website}
              </a>
            </div>
            <div>
              <span>🏢</span>
              <span>{user.company?.name}</span>
            </div>
            <div>
              <span>📍</span>
              <span>{user.address?.city}, {user.address?.zipcode}</span>
            </div>
          </div>
        </div>
      </div>

      <section className="user-posts">
        <h2>Articles de {user.name} ({posts.length})</h2>
        {loadingPosts ? (
          <div>Chargement des articles...</div>
        ) : (
          <div className="posts-grid">
            {posts.map(post => (
              <article key={post.id} className="post-card-mini">
                <h3>{post.title}</h3>
                <p>{post.body.slice(0, 80)}...</p>
              </article>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

export default UserDetailPage;
```

---

## Partie 5 — Fonctionnalités bonus

### Mutation CRUD sur les posts

```jsx
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api, queryKeys } from "../api/apiClient";

function BoutonSupprimerPost({ postId }) {
  const queryClient = useQueryClient();

  const supprimer = useMutation({
    mutationFn: () => api.deletePost(postId),
    onSuccess: () => {
      queryClient.setQueryData(queryKeys.posts.all, (old) =>
        old?.filter(p => p.id !== postId) ?? []
      );
    },
    onError: (err) => alert(`Erreur : ${err.message}`),
  });

  return (
    <button
      onClick={() => supprimer.mutate()}
      disabled={supprimer.isPending}
      className="btn btn-danger"
    >
      {supprimer.isPending ? "Suppression..." : "Supprimer"}
    </button>
  );
}
```

---

## Critères de validation

| Critère | Obligatoire |
|---|---|
| Configuration React Query + Router | Oui |
| Page Dashboard avec stats | Oui |
| Page liste utilisateurs avec recherche | Oui |
| Page détail utilisateur | Oui |
| useQuery pour tous les fetches | Oui |
| Skeleton loaders | Oui |
| Navigation avec React Router | Oui |
| Lazy loading des pages | Non |
| Mutation (créer/supprimer un post) | Non |
| Optimistic updates | Non |
