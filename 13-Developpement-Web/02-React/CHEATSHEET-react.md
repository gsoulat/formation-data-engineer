# Cheatsheet React — Référence Rapide

## Setup & JSX

```bash
# Créer un projet
npm create vite@latest mon-app -- --template react
npm create vite@latest mon-app -- --template react-ts  # TypeScript
```

```jsx
// JSX — différences avec HTML
className="..."          // class
htmlFor="..."            // for
style={{ color: "red" }} // style = objet
autoFocus               // autofocus
<img src="..." />        // auto-fermant
{expression}            // injecter du JS
{/* commentaire */}      // commentaire JSX
<>...</>                // Fragment (pas de div wrapper)

// Rendu conditionnel
{condition && <Composant />}
{condition ? <A /> : <B />}

// Listes — key obligatoire
{items.map(item => <Item key={item.id} item={item} />)}
```

---

## Composants

```jsx
// Composant fonctionnel
function MonComposant({ prop1, prop2 = "défaut", children }) {
  return <div>{children}</div>;
}

// Spread props
<Btn {...config} extra="prop" />

// Passer du JSX comme prop
<Modal
  titre="Confirmation"
  pied={<><button>Annuler</button><button>OK</button></>}
>
  Contenu
</Modal>
```

---

## useState

```jsx
const [valeur, setValeur] = useState(initial);

// Mise à jour simple
setValeur(nouvelleValeur);

// Mise à jour fonctionnelle (si dépend de l'ancienne)
setValeur(prev => prev + 1);

// Objet — toujours créer un nouvel objet
setObj(prev => ({ ...prev, cle: nouvelleVal }));

// Tableau — ne jamais muter !
setArr(prev => [...prev, nouvelElement]);          // Ajouter
setArr(prev => prev.filter(i => i.id !== id));     // Supprimer
setArr(prev => prev.map(i => i.id === id ? {...i, ...mods} : i)); // Modifier
```

---

## useEffect

```jsx
// Toujours (après chaque rendu)
useEffect(() => { /* ... */ });

// Une fois (montage)
useEffect(() => { /* ... */ }, []);

// Quand 'dep' change
useEffect(() => { /* ... */ }, [dep]);

// Avec nettoyage
useEffect(() => {
  const timer = setInterval(fn, 1000);
  return () => clearInterval(timer); // Cleanup
}, []);

// Fetch dans useEffect
useEffect(() => {
  const ctrl = new AbortController();
  fetch(url, { signal: ctrl.signal })
    .then(r => r.json())
    .then(setData)
    .catch(err => { if (err.name !== "AbortError") setError(err); });
  return () => ctrl.abort();
}, [url]);
```

---

## useRef

```jsx
const ref = useRef(null);        // null pour les refs DOM
const ref = useRef(0);           // Valeur mutable sans re-rendu

// Attacher à un élément DOM
<input ref={ref} />
ref.current.focus();

// Valeur persistante
ref.current = intervalId;        // Ne déclenche pas de re-rendu
clearInterval(ref.current);
```

---

## useMemo & useCallback

```jsx
// useMemo — mémoïser un calcul
const resultat = useMemo(
  () => calculCouteux(data),
  [data]  // Recalcule si data change
);

// useCallback — mémoïser une fonction
const handleClick = useCallback(
  () => faire(id),
  [id]  // Recrée si id change
);

// React.memo — éviter le re-rendu d'un composant enfant
const Child = memo(function Child({ onClick }) {
  return <button onClick={onClick}>Click</button>;
});
```

---

## Hooks personnalisés

```jsx
// Pattern général
function useMonHook(param) {
  const [etat, setEtat] = useState(null);

  useEffect(() => {
    // Logique...
  }, [param]);

  return etat;
}

// useFetch simplifié
function useFetch(url) {
  const [donnees, setDonnees] = useState(null);
  const [chargement, setChargement] = useState(true);
  const [erreur, setErreur] = useState(null);

  useEffect(() => {
    fetch(url)
      .then(r => r.json())
      .then(d => { setDonnees(d); setChargement(false); })
      .catch(e => { setErreur(e.message); setChargement(false); });
  }, [url]);

  return { donnees, chargement, erreur };
}

// useLocalStorage
function useLocalStorage(cle, init) {
  const [val, setVal] = useState(() => {
    try { return JSON.parse(localStorage.getItem(cle)) ?? init; }
    catch { return init; }
  });
  useEffect(() => localStorage.setItem(cle, JSON.stringify(val)), [cle, val]);
  return [val, setVal];
}
```

---

## Context API

```jsx
// Créer
const MonContext = createContext(null);

// Provider
function MonProvider({ children }) {
  const [valeur, setValeur] = useState("défaut");
  return (
    <MonContext.Provider value={{ valeur, setValeur }}>
      {children}
    </MonContext.Provider>
  );
}

// Hook personnalisé
function useMonContext() {
  const ctx = useContext(MonContext);
  if (!ctx) throw new Error("Hors du Provider !");
  return ctx;
}

// Dans main.jsx
<MonProvider><App /></MonProvider>

// Dans n'importe quel composant
const { valeur, setValeur } = useMonContext();
```

---

## React Router v6

```jsx
// main.jsx
<BrowserRouter><App /></BrowserRouter>

// App.jsx
<Routes>
  <Route path="/" element={<Layout />}>
    <Route index element={<Accueil />} />
    <Route path="users" element={<Users />} />
    <Route path="users/:id" element={<UserDetail />} />
    <Route path="*" element={<NotFound />} />
  </Route>
</Routes>

// Layout.jsx
<nav>
  <NavLink to="/" end className={({isActive}) => isActive ? "actif" : ""}>
    Accueil
  </NavLink>
</nav>
<Outlet />  {/* Routes enfants ici */}

// Composants de navigation
import { useParams, useNavigate, useLocation, useSearchParams, Link, NavLink } from "react-router-dom";

const { id } = useParams();          // Lire :id de l'URL
const navigate = useNavigate();
navigate("/users");                   // Naviguer
navigate("/users", { replace: true }); // Sans historique
navigate(-1);                         // Retour

const location = useLocation();
const { from } = location.state ?? {};

const [params, setParams] = useSearchParams();
const page = params.get("page") ?? "1";
setParams({ page: "2" });
```

---

## TanStack Query

```jsx
// Setup
const client = new QueryClient();
<QueryClientProvider client={client}><App /></QueryClientProvider>

// Lire des données
const { data, isLoading, isError, error, refetch } = useQuery({
  queryKey: ["users"],                      // Clé de cache unique
  queryFn: () => fetch("/api/users").then(r => r.json()),
  staleTime: 5 * 60 * 1000,                // Fraîches 5min
  enabled: !!userId,                        // Conditionnel
  select: data => data.map(transform),      // Transformer
});

// Avec paramètres
useQuery({
  queryKey: ["users", userId, { filtre }],  // Inclure TOUS les paramètres
  queryFn: () => fetchUser(userId, filtre),
});

// Modifier des données
const { mutate, isPending, isError } = useMutation({
  mutationFn: (data) => fetch("/api/users", { method:"POST", body: JSON.stringify(data) }).then(r=>r.json()),
  onSuccess: () => queryClient.invalidateQueries({ queryKey: ["users"] }),
  onError: (err) => alert(err.message),
});
mutate({ nom: "Alice" }); // Déclencher

// Invalider le cache
const queryClient = useQueryClient();
queryClient.invalidateQueries({ queryKey: ["users"] }); // Refetch
queryClient.setQueryData(["users"], oldData => [...oldData, newUser]); // Modifier directement
```

---

## React Hook Form + Zod

```jsx
// Schema
const schema = z.object({
  email: z.string().email("Email invalide"),
  motDePasse: z.string().min(8, "8 caractères minimum"),
});
type FormData = z.infer<typeof schema>;

// Formulaire
const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm({
  resolver: zodResolver(schema),
  defaultValues: { email: "", motDePasse: "" },
});

const onSubmit = async (data: FormData) => { /* data est validé */ };

<form onSubmit={handleSubmit(onSubmit)}>
  <input {...register("email")} />
  {errors.email && <span>{errors.email.message}</span>}

  <input type="password" {...register("motDePasse")} />
  {errors.motDePasse && <span>{errors.motDePasse.message}</span>}

  <button disabled={isSubmitting}>
    {isSubmitting ? "..." : "Envoyer"}
  </button>
</form>
```

---

## Zustand

```jsx
import { create } from "zustand";

const useStore = create((set, get) => ({
  // État
  compteur: 0,
  items: [],

  // Actions
  incrementer: () => set(s => ({ compteur: s.compteur + 1 })),
  ajouterItem: (item) => set(s => ({ items: [...s.items, item] })),
  getTotal: () => get().items.length, // Lecture synchrone
}));

// Dans un composant — sélectionner pour éviter les re-renders inutiles
const compteur = useStore(s => s.compteur);
const incrementer = useStore(s => s.incrementer);
```

---

## Patterns courants

```jsx
// Loading state
if (isLoading) return <Spinner />;
if (error) return <ErrorMessage error={error} onRetry={refetch} />;

// Guard de null
const nom = utilisateur?.profil?.nom ?? "Anonyme";

// Conditional rendering propre
const STATUS_COMPONENTS = {
  loading: <Spinner />,
  error: <Error />,
  empty: <Empty />,
  success: <Data />,
};
return STATUS_COMPONENTS[statut];

// Debounce dans un composant
const rechercheDebounced = useDebounce(recherche, 300);
useEffect(() => {
  if (rechercheDebounced) chercher(rechercheDebounced);
}, [rechercheDebounced]);

// Lever l'état (Lifting state up)
// Si deux composants frères partagent un état → le mettre dans leur parent commun
```
