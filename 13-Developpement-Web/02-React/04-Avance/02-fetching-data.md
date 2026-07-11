# 02 — Fetching de Données : TanStack Query (React Query)

## Introduction

TanStack Query (anciennement React Query) est la solution recommandée pour gérer l'**état serveur** dans React : données fetchées depuis une API, avec cache, synchronisation, invalidation, et gestion des états loading/error.

---

## Installation

```bash
npm install @tanstack/react-query
# Optionnel : DevTools React Query
npm install @tanstack/react-query-devtools
```

---

## 1. Configuration

```jsx
// src/main.jsx
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,      // Données "fraîches" pendant 5 minutes
      gcTime: 10 * 60 * 1000,          // Garder en cache pendant 10 minutes
      retry: 3,                        // 3 tentatives en cas d'échec
      retryDelay: (n) => Math.min(1000 * 2 ** n, 30000), // Délai exponentiel
      refetchOnWindowFocus: true,      // Refetch quand l'onglet reprend le focus
    },
  },
});

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <App />
      </BrowserRouter>
      {/* DevTools — visible seulement en développement */}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  </StrictMode>
);
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** React Query DevTools — montrer l'interface avec la liste des queries, leur statut (fresh/stale/loading), les données en cache, et déclencher manuellement un refetch. Montrer aussi ce qui se passe quand on change d'onglet (refetchOnWindowFocus).
> **Expliquer :** React Query DevTools est l'équivalent de Postman intégré dans l'app. On voit en temps réel quelles données sont en cache, depuis combien de temps, combien de fois elles ont été fetché, etc. Indispensable pour déboguer.

---

## 2. useQuery — Fetcher des données

```jsx
import { useQuery } from "@tanstack/react-query";

// Fonction de fetch séparée (queryFn)
async function fetchUtilisateurs() {
  const response = await fetch("/api/users");
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}

function ListeUtilisateurs() {
  const {
    data,           // Données (undefined pendant chargement)
    isLoading,      // true seulement au PREMIER chargement (pas de données en cache)
    isFetching,     // true à chaque rechargement (incluant les suivants)
    isError,        // true si une erreur s'est produite
    error,          // L'objet Error
    isSuccess,      // true si les données sont disponibles
    refetch,        // Fonction pour refetch manuellement
    dataUpdatedAt,  // Timestamp de la dernière mise à jour
  } = useQuery({
    queryKey: ["utilisateurs"],     // Identifiant unique de la requête (tableau)
    queryFn: fetchUtilisateurs,     // Fonction qui retourne une Promise
  });

  if (isLoading) return <SkeletonList />;

  if (isError) return (
    <div>
      <p>Erreur : {error.message}</p>
      <button onClick={() => refetch()}>Réessayer</button>
    </div>
  );

  return (
    <div>
      {isFetching && <SpinnerMini />} {/* Indicateur de rechargement en arrière-plan */}
      <ul>
        {data.map(user => (
          <li key={user.id}>{user.name} — {user.email}</li>
        ))}
      </ul>
      <p style={{ fontSize: "0.75rem", color: "#888" }}>
        Mis à jour : {new Date(dataUpdatedAt).toLocaleTimeString()}
      </p>
    </div>
  );
}
```

### useQuery avec paramètres dynamiques

```jsx
// La queryKey DOIT inclure toutes les variables dont dépend la requête
function ProfilUtilisateur({ userId }) {
  const { data: utilisateur, isLoading } = useQuery({
    queryKey: ["utilisateurs", userId], // Clé unique par userId
    queryFn: () => fetch(`/api/users/${userId}`).then(r => r.json()),
    enabled: !!userId,                   // Ne pas fetch si userId est undefined/null
    select: (data) => ({                 // Transformer les données avant de les retourner
      ...data,
      nomComplet: `${data.prenom} ${data.nom}`,
    }),
  });

  // La requête sera automatiquement invalidée et re-fetched quand userId change
  return isLoading ? <Spinner /> : <div>{utilisateur?.nomComplet}</div>;
}

// Avec filtres et pagination
function ListeAvecFiltres({ filtre, page }) {
  const { data, isPlaceholderData } = useQuery({
    queryKey: ["produits", { filtre, page }],
    queryFn: () => fetch(`/api/produits?filtre=${filtre}&page=${page}`).then(r => r.json()),
    placeholderData: keepPreviousData, // Garder les données précédentes pendant le chargement d'une nouvelle page
  });

  return (
    <div style={{ opacity: isPlaceholderData ? 0.5 : 1 }}>
      {/* Opacité réduite pendant la transition */}
      {data?.items.map(p => <ProduitItem key={p.id} produit={p} />)}
    </div>
  );
}
```

---

## 3. useMutation — Créer, Modifier, Supprimer

```jsx
import { useMutation, useQueryClient } from "@tanstack/react-query";

function FormulaireNouvelUtilisateur() {
  const queryClient = useQueryClient();
  const [nom, setNom] = useState("");
  const [email, setEmail] = useState("");

  const mutation = useMutation({
    mutationFn: async (nouvelUtilisateur) => {
      const response = await fetch("/api/users", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(nouvelUtilisateur),
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return response.json();
    },

    // Callbacks
    onSuccess: (nouveauUser) => {
      // Invalider le cache pour forcer un refetch de la liste
      queryClient.invalidateQueries({ queryKey: ["utilisateurs"] });

      // OU : mise à jour optimiste du cache (sans refetch)
      queryClient.setQueryData(["utilisateurs"], (ancienneData) => [
        ...(ancienneData ?? []),
        nouveauUser,
      ]);

      setNom("");
      setEmail("");
    },

    onError: (erreur) => {
      alert(`Erreur : ${erreur.message}`);
    },

    onSettled: () => {
      // Toujours exécuté (succès ou erreur)
      console.log("Mutation terminée");
    },
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    mutation.mutate({ nom, email }); // Déclencher la mutation
  };

  return (
    <form onSubmit={handleSubmit}>
      <input value={nom} onChange={e => setNom(e.target.value)} placeholder="Nom" />
      <input value={email} onChange={e => setEmail(e.target.value)} placeholder="Email" />
      <button type="submit" disabled={mutation.isPending}>
        {mutation.isPending ? "Création..." : "Créer"}
      </button>
      {mutation.isError && <p className="erreur">{mutation.error.message}</p>}
      {mutation.isSuccess && <p className="succes">Utilisateur créé !</p>}
    </form>
  );
}
```

---

## 4. Mise à jour optimiste (Optimistic Updates)

```jsx
function BoutonToggleFavori({ articleId, estFavori }) {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: (id) => fetch(`/api/articles/${id}/favori`, { method: "PUT" }).then(r => r.json()),

    // AVANT la requête — mise à jour optimiste immédiate
    onMutate: async (id) => {
      // Annuler les refetchs en cours pour éviter les conflits
      await queryClient.cancelQueries({ queryKey: ["articles"] });

      // Sauvegarder le snapshot actuel
      const snapshot = queryClient.getQueryData(["articles"]);

      // Mise à jour optimiste du cache
      queryClient.setQueryData(["articles"], (old) =>
        old?.map(a => a.id === id ? { ...a, estFavori: !a.estFavori } : a)
      );

      // Retourner le snapshot pour pouvoir revenir en arrière
      return { snapshot };
    },

    // EN CAS D'ERREUR — rollback
    onError: (err, id, context) => {
      queryClient.setQueryData(["articles"], context.snapshot);
      alert("Impossible de modifier les favoris");
    },

    // À LA FIN — refetch pour synchroniser avec le serveur
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["articles"] });
    },
  });

  return (
    <button onClick={() => mutation.mutate(articleId)}>
      {estFavori ? "⭐ Favori" : "☆ Ajouter aux favoris"}
    </button>
  );
}
```

---

## 5. useInfiniteQuery — Scroll infini

```jsx
import { useInfiniteQuery } from "@tanstack/react-query";
import { useIntersectionObserver } from "../hooks/useIntersectionObserver";

async function fetchPage({ pageParam = 1 }) {
  const response = await fetch(`/api/posts?page=${pageParam}&limit=10`);
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
  // Format attendu : { items: [...], nextPage: 2 | null }
}

function ListeInfinie() {
  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading,
    isError,
  } = useInfiniteQuery({
    queryKey: ["posts"],
    queryFn: fetchPage,
    initialPageParam: 1,
    getNextPageParam: (dernierePage) => dernierePage.nextPage ?? undefined,
  });

  // Sentinelle pour déclencher le chargement
  const [sentinelleRef, estVisible] = useIntersectionObserver();

  useEffect(() => {
    if (estVisible && hasNextPage && !isFetchingNextPage) {
      fetchNextPage();
    }
  }, [estVisible, hasNextPage, isFetchingNextPage, fetchNextPage]);

  if (isLoading) return <Spinner />;
  if (isError) return <p>Erreur de chargement</p>;

  // data.pages est un tableau de pages
  const tousLesItems = data.pages.flatMap(page => page.items);

  return (
    <div>
      {tousLesItems.map(post => (
        <ArticleCard key={post.id} post={post} />
      ))}

      {/* Sentinelle invisible */}
      <div ref={sentinelleRef} />

      {isFetchingNextPage && <Spinner />}
      {!hasNextPage && <p>Tous les articles sont chargés</p>}
    </div>
  );
}
```

---

## 6. Prefetching et organisation des queries

```jsx
// Précharger des données en anticipation
function ListeProduits() {
  const queryClient = useQueryClient();
  const { data: produits } = useQuery({
    queryKey: ["produits"],
    queryFn: fetchProduits,
  });

  // Précharger le détail d'un produit au survol
  const prechargerDetail = (id) => {
    queryClient.prefetchQuery({
      queryKey: ["produits", id],
      queryFn: () => fetchProduit(id),
      staleTime: 5 * 60 * 1000,
    });
  };

  return (
    <ul>
      {produits?.map(p => (
        <li
          key={p.id}
          onMouseEnter={() => prechargerDetail(p.id)}
        >
          <Link to={`/produits/${p.id}`}>{p.nom}</Link>
        </li>
      ))}
    </ul>
  );
}

// Organiser les queryFunctions dans un fichier séparé
// src/api/utilisateursApi.js
export const utilisateursApi = {
  fetchTous: () =>
    fetch("/api/users").then(r => { if (!r.ok) throw new Error(r.status); return r.json(); }),

  fetchParId: (id) =>
    fetch(`/api/users/${id}`).then(r => { if (!r.ok) throw new Error(r.status); return r.json(); }),

  creer: (donnees) =>
    fetch("/api/users", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(donnees),
    }).then(r => { if (!r.ok) throw new Error(r.status); return r.json(); }),
};

// Organiser les queryKeys
export const utilisateursKeys = {
  all: ["utilisateurs"] as const,
  lists: () => [...utilisateursKeys.all, "list"] as const,
  detail: (id: number) => [...utilisateursKeys.all, "detail", id] as const,
};

// Utilisation
useQuery({ queryKey: utilisateursKeys.lists(), queryFn: utilisateursApi.fetchTous });
queryClient.invalidateQueries({ queryKey: utilisateursKeys.all }); // Invalide tout
```

---

## 7. État loading/error partagé

```jsx
// Afficher un état de chargement global
function EtatRequete() {
  const isFetching = useIsFetching(); // Nombre de requêtes en cours

  return isFetching > 0 ? (
    <div className="barre-progression-globale">
      <div className="progression" />
    </div>
  ) : null;
}

// Composant ErrorBoundary pour React Query
import { QueryErrorResetBoundary } from "@tanstack/react-query";
import { ErrorBoundary } from "react-error-boundary";

function AppAvecErreurs() {
  return (
    <QueryErrorResetBoundary>
      {({ reset }) => (
        <ErrorBoundary
          onReset={reset}
          fallbackRender={({ error, resetErrorBoundary }) => (
            <div>
              <h2>Une erreur est survenue</h2>
              <p>{error.message}</p>
              <button onClick={resetErrorBoundary}>Réessayer</button>
            </div>
          )}
        >
          <MonApplication />
        </ErrorBoundary>
      )}
    </QueryErrorResetBoundary>
  );
}
```

---

## Récapitulatif

| Hook | Usage | Cas d'usage |
|---|---|---|
| `useQuery` | Lire des données | GET, fetch avec cache |
| `useMutation` | Modifier des données | POST, PUT, PATCH, DELETE |
| `useInfiniteQuery` | Pagination infinie | Scroll infini, "Charger plus" |
| `useQueryClient` | Accéder au client | Invalider, prefetch, modifier le cache |
| `useIsFetching` | Requêtes en cours | Indicateur global de chargement |

**Concepts clés :**
- `queryKey` : identifiant du cache — même key = mêmes données
- `staleTime` : durée pendant laquelle les données sont considérées fraîches (pas de refetch)
- `gcTime` : durée de conservation en cache après que tous les composants abonnés se sont démontés
- `invalidateQueries` : marque des données comme périmées → refetch au prochain accès
- `setQueryData` : modifier le cache directement (mise à jour optimiste)
