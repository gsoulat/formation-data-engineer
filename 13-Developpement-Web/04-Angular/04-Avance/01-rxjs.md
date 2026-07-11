# RxJS — Programmation Réactive

## Qu'est-ce que RxJS ?

RxJS (Reactive Extensions for JavaScript) est une bibliothèque de programmation réactive basée sur les **Observables**. Angular l'utilise partout : HttpClient, Router, Reactive Forms, EventEmitter...

**L'idée clé :** Traiter les données asynchrones comme des **flux** d'événements dans le temps, et les transformer avec des opérateurs.

```
// Analogie :
// Tableau classique  → données disponibles immédiatement
// Observable         → données qui arrivent dans le temps (réseau, clavier, timer...)

// Tableau : [1, 2, 3].map(x => x * 2) → [2, 4, 6] (synchrone)
// Observable : interval(1000).pipe(map(x => x * 2)) → 0, 2, 4, 6... (asynchrone)
```

## Observable, Observer, Subscription

```typescript
import { Observable, Observer, Subscription } from 'rxjs'

// Créer un Observable personnalisé
const monObservable$ = new Observable<number>((observer) => {
  // observer.next() émet une valeur
  observer.next(1)
  observer.next(2)
  observer.next(3)

  // Simulation asynchrone
  setTimeout(() => {
    observer.next(4)
    observer.complete() // Fin du flux
  }, 1000)

  // Optionnel : logique de nettoyage quand on se désabonne
  return () => {
    console.log('Observable nettoyé')
  }
})

// S'abonner — déclenche l'exécution de l'Observable
const subscription: Subscription = monObservable$.subscribe({
  next: (valeur) => console.log('Valeur reçue :', valeur),
  error: (err) => console.error('Erreur :', err),
  complete: () => console.log('Flux terminé'),
})

// Se désabonner pour éviter les fuites mémoire
subscription.unsubscribe()
```

### Convention : le `$` dans les noms

Par convention, les variables qui sont des Observables se terminent par `$` :

```typescript
const utilisateurs$ = this.http.get<User[]>('/api/users')
const clavier$ = fromEvent(document, 'keyup')
const timer$ = interval(1000)
```

## Création d'Observables

```typescript
import { of, from, interval, timer, fromEvent, Subject, BehaviorSubject } from 'rxjs'

// of() — émettre des valeurs fixes (synchrone)
of(1, 2, 3).subscribe(v => console.log(v))  // 1, 2, 3, complete

// from() — convertir un tableau, Promise, ou iterable
from([1, 2, 3]).subscribe(v => console.log(v))
from(fetch('/api/data').then(r => r.json())).subscribe(data => console.log(data))

// interval() — émettre toutes les N millisecondes
interval(1000).subscribe(n => console.log(n))  // 0, 1, 2, 3... à l'infini

// timer() — émettre une fois après un délai, ou intervalles
timer(2000).subscribe(() => console.log('2 secondes écoulées'))
timer(0, 1000).subscribe(n => console.log(n))  // commence immédiatement, puis toutes les secondes

// fromEvent() — événements DOM
fromEvent(document, 'click').subscribe((event: Event) => console.log(event))
fromEvent(inputElement, 'input').subscribe((e: Event) => {
  console.log((e.target as HTMLInputElement).value)
})
```

## Opérateurs — Le cœur de RxJS

### `map` — Transformer les valeurs

```typescript
import { of, from, interval } from 'rxjs'
import { map, filter } from 'rxjs/operators'

// map() transforme chaque valeur
of(1, 2, 3, 4, 5)
  .pipe(map((x) => x * 2))
  .subscribe(console.log)  // 2, 4, 6, 8, 10

// Transformer des objets
this.http.get<ApiResponse<User[]>>('/api/users').pipe(
  map((response) => response.data),         // Extraire le tableau
  map((users) => users.filter((u) => u.active)) // Filtrer
)
```

### `filter` — Filtrer les valeurs

```typescript
import { from } from 'rxjs'
import { filter } from 'rxjs/operators'

from([1, 2, 3, 4, 5, 6])
  .pipe(filter((x) => x % 2 === 0))
  .subscribe(console.log)  // 2, 4, 6

// Dans un contexte HTTP
this.http.get<User[]>('/api/users').pipe(
  map((users) => users.filter((u) => u.role === 'admin'))
)
```

### `switchMap` — Annuler et remplacer

`switchMap` est l'opérateur le plus important pour les appels HTTP avec paramètres changeants. Il **annule la requête précédente** si une nouvelle valeur arrive.

```typescript
import { fromEvent } from 'rxjs'
import { debounceTime, distinctUntilChanged, switchMap, map } from 'rxjs/operators'

// Recherche en temps réel — annule les requêtes précédentes
const rechercheInput = document.getElementById('recherche') as HTMLInputElement

fromEvent(rechercheInput, 'input')
  .pipe(
    map((e: Event) => (e.target as HTMLInputElement).value),
    debounceTime(400),            // Attendre 400ms de silence
    distinctUntilChanged(),        // Éviter les appels si la valeur n'a pas changé
    switchMap((terme) =>           // Annule la requête précédente si nouveau terme
      this.http.get<User[]>(`/api/users?search=${terme}`)
    )
  )
  .subscribe((users) => {
    this.users = users
  })
```

### `mergeMap` — Exécuter en parallèle

```typescript
import { from } from 'rxjs'
import { mergeMap } from 'rxjs/operators'

// mergeMap : toutes les requêtes tournent en parallèle
from([1, 2, 3, 4, 5]).pipe(
  mergeMap((id) => this.http.get<User>(`/api/users/${id}`))
).subscribe((user) => console.log(user.name))
// Les résultats peuvent arriver dans n'importe quel ordre
```

### `concatMap` — Exécuter en séquence

```typescript
import { from } from 'rxjs'
import { concatMap } from 'rxjs/operators'

// concatMap : attendre la fin avant de lancer la suivante
from([1, 2, 3]).pipe(
  concatMap((id) => this.http.post(`/api/process/${id}`, {}))
).subscribe(console.log)
// Garantit l'ordre : 1, puis 2, puis 3
```

### `combineLatest` — Combiner plusieurs flux

```typescript
import { combineLatest } from 'rxjs'
import { map } from 'rxjs/operators'

// Attendre la dernière valeur de TOUS les observables
const utilisateurs$ = this.usersService.getAll()
const produits$ = this.produitsService.getAll()
const config$ = this.configService.getConfig()

combineLatest([utilisateurs$, produits$, config$]).pipe(
  map(([utilisateurs, produits, config]) => ({
    // Construire un état combiné
    tableau: utilisateurs.filter((u) => u.active),
    nombreProduits: produits.length,
    theme: config.theme,
  }))
).subscribe((etat) => {
  this.viewState = etat
})
```

### `forkJoin` — Attendre la fin de tous

```typescript
import { forkJoin } from 'rxjs'

// forkJoin attend que TOUS les observables soient TERMINÉS puis émet une seule fois
// Idéal pour charger plusieurs ressources en parallèle au démarrage
forkJoin({
  user: this.usersService.getById(this.userId),
  posts: this.postsService.getByUserId(this.userId),
  stats: this.statsService.getUserStats(this.userId),
}).subscribe(({ user, posts, stats }) => {
  this.user = user
  this.posts = posts
  this.stats = stats
})
```

### `catchError` — Gestion des erreurs

```typescript
import { catchError, throwError, of } from 'rxjs'

this.http.get<User[]>('/api/users').pipe(
  catchError((err) => {
    console.error('Erreur HTTP :', err)

    // Option 1 : Propager l'erreur
    return throwError(() => new Error(`API Error: ${err.status}`))

    // Option 2 : Retourner une valeur de fallback (observable qui émet puis complete)
    // return of([])
  })
)
```

### `tap` — Effets de bord sans modifier le flux

```typescript
import { tap } from 'rxjs/operators'

this.http.get<User[]>('/api/users').pipe(
  tap(() => console.log('Requête envoyée')),
  tap((users) => console.log(`${users.length} utilisateurs reçus`)),
  tap({
    next: (users) => this.cache.set('users', users),
    error: (err) => this.logger.error(err),
    complete: () => console.log('Requête terminée'),
  })
)
```

### `debounceTime` et `distinctUntilChanged`

```typescript
import { fromEvent } from 'rxjs'
import { debounceTime, distinctUntilChanged, map } from 'rxjs/operators'

const input$ = fromEvent<InputEvent>(champRecherche, 'input').pipe(
  map((e) => (e.target as HTMLInputElement).value),
  debounceTime(300),          // Émettre seulement après 300ms de silence
  distinctUntilChanged(),      // Émettre seulement si la valeur a changé
  // ex: taper "a", effacer, retaper "a" → une seule émission
)
```

### `takeUntil` et `takeUntilDestroyed` — Gestion des subscriptions

```typescript
import { Component, OnInit, OnDestroy, inject } from '@angular/core'
import { Subject } from 'rxjs'
import { takeUntil } from 'rxjs/operators'
import { takeUntilDestroyed, DestroyRef } from '@angular/core/rxjs-interop'

// Méthode classique avec Subject (manuelle)
@Component({ ... })
export class ClassicComponent implements OnInit, OnDestroy {
  private destroy$ = new Subject<void>()

  ngOnInit(): void {
    interval(1000)
      .pipe(takeUntil(this.destroy$))  // Stop quand destroy$ émet
      .subscribe(console.log)
  }

  ngOnDestroy(): void {
    this.destroy$.next()   // Déclencher l'arrêt
    this.destroy$.complete()
  }
}

// Méthode moderne (Angular 16+) — recommandée
@Component({ ... })
export class ModernComponent implements OnInit {
  private destroyRef = inject(DestroyRef)

  ngOnInit(): void {
    interval(1000)
      .pipe(takeUntilDestroyed(this.destroyRef))  // Auto-cleanup
      .subscribe(console.log)
  }
}
```

## Subject — Observable + Observer

Un `Subject` est à la fois un Observable et un Observer. Il peut émettre des valeurs manuellement.

```typescript
import { Subject, BehaviorSubject, ReplaySubject } from 'rxjs'

// Subject — pas de valeur initiale, les abonnés tardifs manquent les valeurs passées
const clics$ = new Subject<MouseEvent>()
clics$.next(monEvenement)  // Émettre manuellement

// BehaviorSubject — a une valeur courante, les nouveaux abonnés reçoivent la dernière valeur
const score$ = new BehaviorSubject<number>(0)  // valeur initiale = 0
score$.getValue()   // Lire la valeur courante sans s'abonner
score$.next(10)     // Émettre une nouvelle valeur
// Un nouvel abonné reçoit immédiatement 10

// ReplaySubject — rejoue les N dernières valeurs aux nouveaux abonnés
const historique$ = new ReplaySubject<string>(5)  // mémorise les 5 dernières valeurs
```

### Pattern StateService avec BehaviorSubject

```typescript
// Service d'état avec BehaviorSubject (alternative aux Signals)
@Injectable({ providedIn: 'root' })
export class AppStateService {
  private _users$ = new BehaviorSubject<User[]>([])
  private _loading$ = new BehaviorSubject<boolean>(false)

  // Exposer en Observable read-only (pas de .next() depuis l'extérieur)
  readonly users$ = this._users$.asObservable()
  readonly loading$ = this._loading$.asObservable()

  // État dérivé avec combineLatest
  readonly userCount$ = this.users$.pipe(map((users) => users.length))
  readonly admins$ = this.users$.pipe(
    map((users) => users.filter((u) => u.role === 'admin'))
  )

  chargerUsers(): Observable<User[]> {
    this._loading$.next(true)

    return this.http.get<User[]>('/api/users').pipe(
      tap((users) => {
        this._users$.next(users)
        this._loading$.next(false)
      }),
      catchError((err) => {
        this._loading$.next(false)
        return throwError(() => err)
      })
    )
  }
}
```

## Exemple complet — Recherche en temps réel

```typescript
// src/app/features/search/search.component.ts
import { Component, OnInit, inject } from '@angular/core'
import { FormControl, ReactiveFormsModule } from '@angular/forms'
import { CommonModule, AsyncPipe } from '@angular/common'
import { HttpClient } from '@angular/common/http'
import {
  Observable,
  combineLatest,
  Subject,
  BehaviorSubject,
} from 'rxjs'
import {
  debounceTime,
  distinctUntilChanged,
  switchMap,
  map,
  startWith,
  catchError,
  of,
  tap,
  takeUntilDestroyed,
} from 'rxjs/operators'
import { DestroyRef } from '@angular/core'

interface User { id: number; name: string; email: string }

@Component({
  selector: 'app-search',
  standalone: true,
  imports: [ReactiveFormsModule, CommonModule, AsyncPipe],
  template: `
    <div class="search">
      <input [formControl]="searchCtrl" placeholder="Rechercher..." />

      @if (loading$ | async) {
        <p>Recherche en cours...</p>
      }

      @if (results$ | async; as results) {
        <p>{{ results.length }} résultat(s)</p>
        @for (user of results; track user.id) {
          <div>{{ user.name }} — {{ user.email }}</div>
        }
      }

      @if (error$ | async; as error) {
        <p class="error">{{ error }}</p>
      }
    </div>
  `,
})
export class SearchComponent {
  private http = inject(HttpClient)
  private destroyRef = inject(DestroyRef)

  searchCtrl = new FormControl('')

  private loading = new BehaviorSubject(false)
  private error = new BehaviorSubject<string | null>(null)

  loading$ = this.loading.asObservable()
  error$ = this.error.asObservable()

  results$: Observable<User[]> = this.searchCtrl.valueChanges.pipe(
    startWith(''),                          // Émettre immédiatement avec la valeur vide
    debounceTime(400),
    distinctUntilChanged(),
    tap(() => {
      this.loading.next(true)
      this.error.next(null)
    }),
    switchMap((terme) =>
      this.http
        .get<User[]>(`https://jsonplaceholder.typicode.com/users`)
        .pipe(
          map((users) =>
            terme
              ? users.filter((u) =>
                  u.name.toLowerCase().includes(terme!.toLowerCase())
                )
              : users
          ),
          tap(() => this.loading.next(false)),
          catchError((err) => {
            this.error.next('Erreur lors de la recherche')
            this.loading.next(false)
            return of([])
          })
        )
    ),
    takeUntilDestroyed(this.destroyRef)
  )
}
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Console du navigateur avec les logs des opérateurs RxJS (tap) pendant une recherche en temps réel
> **Expliquer :** Taper des lettres rapidement dans le champ de recherche. Montrer dans la console que grâce à `debounceTime(400)`, l'appel HTTP n'est fait que lorsqu'on arrête de taper. Montrer avec `switchMap` que si on tape trop vite, la requête précédente est annulée (dans l'onglet Network, les requêtes "cancelled"). C'est le comportement optimal pour une recherche — ni trop de requêtes, ni de résultats périmés.
---

## Cheat Sheet des opérateurs RxJS

| Opérateur | Description | Cas d'usage |
|---|---|---|
| `map` | Transformer chaque valeur | `users → users.filter(...)` |
| `filter` | Garder certaines valeurs | `clicks > 0` |
| `tap` | Effet de bord sans modifier | logging, cache |
| `switchMap` | Annuler + remplacer | Recherche, navigation |
| `mergeMap` | Paralléliser | Upload multiple |
| `concatMap` | Séquencer | File d'attente |
| `debounceTime` | Attendre N ms de silence | Frappe clavier |
| `distinctUntilChanged` | Ignorer les doublons | Éviter appels inutiles |
| `catchError` | Gérer les erreurs | Fallback, rethrow |
| `combineLatest` | Combiner plusieurs flux | Dashboard multi-sources |
| `forkJoin` | Attendre la fin de tous | Chargement initial |
| `takeUntil` | Arrêter à un signal | Cleanup sur destroy |
| `takeUntilDestroyed` | Arrêt automatique Angular | Cleanup moderne |
| `startWith` | Valeur initiale | Formulaires, défauts |
| `share` | Partager une subscription | Éviter les appels dupliqués |

## Résumé

- Un **Observable** est un flux de valeurs dans le temps
- On déclenche l'exécution en appelant **`.subscribe()`**
- Les **opérateurs** transforment le flux dans `.pipe()`
- **`switchMap`** est l'opérateur HTTP le plus important — annule les requêtes obsolètes
- **Toujours unsubscribe()** pour éviter les fuites mémoire → utiliser `takeUntilDestroyed`
- Un **Subject** est un Observable qu'on peut émettre manuellement
- Un **BehaviorSubject** a une valeur courante accessible sans subscription

**Félicitations — vous avez complété le cours Angular !**
Passez aux exercices pour mettre en pratique →
