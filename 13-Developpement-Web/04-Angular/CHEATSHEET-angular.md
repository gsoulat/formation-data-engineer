# Cheatsheet Angular 17+

## CLI — Commandes essentielles

```bash
ng new mon-app --style=scss --standalone
ng serve --open
ng build
ng test

ng g c components/mon-composant        # Composant
ng g s services/mon-service            # Service
ng g guard guards/auth                 # Guard
ng g interceptor interceptors/auth     # Intercepteur
ng g pipe pipes/truncate               # Pipe
ng g interface models/user             # Interface
```

## Structure d'un composant

```typescript
@Component({
  selector: 'app-mon-composant',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  templateUrl: './mon-composant.component.html',
  styleUrl: './mon-composant.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MonComposantComponent implements OnInit, OnDestroy {
  // Signals
  data = signal<User[]>([])
  loading = signal(false)
  filtred = computed(() => this.data().filter(u => u.active))

  // Injection
  private service = inject(MonService)
  private destroyRef = inject(DestroyRef)

  ngOnInit(): void { this.charger() }

  charger(): void {
    this.loading.set(true)
    this.service.getAll()
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (items) => { this.data.set(items); this.loading.set(false) },
        error: (err) => { console.error(err); this.loading.set(false) },
      })
  }
}
```

## @Input / @Output

```typescript
// Enfant
@Input({ required: true }) user!: User
@Input() disabled = false
@Output() selectionner = new EventEmitter<User>()

// Nouveau style (Input Signals, Angular 17.1+)
readonly user = input.required<User>()
readonly disabled = input(false)

// Utilisation parent
<app-card [user]="monUser" [disabled]="false" (selectionner)="onSelect($event)" />
```

## Lifecycle hooks

```typescript
ngOnInit()          // ← API calls ici
ngOnChanges(changes: SimpleChanges)
ngAfterViewInit()   // ← ViewChild ici
ngOnDestroy()       // ← Cleanup ici
```

## Syntaxe de template (Angular 17+)

```html
<!-- Interpolation -->
{{ expression }}   [property]="expr"   (event)="fn()"   [(ngModel)]="prop"

<!-- Conditions -->
@if (condition) { ... } @else if (...) { ... } @else { ... }

<!-- Listes -->
@for (item of items; track item.id) { ... } @empty { <p>Vide</p> }

<!-- Switch -->
@switch (val) { @case ('a') { ... } @default { ... } }

<!-- Lazy loading -->
@defer (on viewport) { <app-lourd /> } @placeholder { ... }

<!-- Ancienne syntaxe (toujours valide) -->
*ngIf="condition"   *ngFor="let x of items; trackBy: fn"
[ngClass]="{ active: bool }"   [ngStyle]="{ color: 'red' }"
```

## Services et DI

```typescript
@Injectable({ providedIn: 'root' })
export class MonService {
  private http = inject(HttpClient)
  private _state = signal<User[]>([])
  readonly state = this._state.asReadonly()

  getAll(): Observable<User[]> {
    return this.http.get<User[]>('/api/users').pipe(
      tap(users => this._state.set(users))
    )
  }
}

// Injection dans un composant
private service = inject(MonService)
```

## Signals (Angular 16+)

```typescript
import { signal, computed, effect } from '@angular/core'

const count = signal(0)           // valeur réactive
count.set(5)                      // définir
count.update(n => n + 1)          // modifier
count()                           // lire

const doubled = computed(() => count() * 2)   // dérivé, mis en cache

effect(() => {
  console.log('count =', count()) // effet auto
})

// Dans un service — exposer en lecture seule
private _data = signal<User[]>([])
readonly data = this._data.asReadonly()
readonly count = computed(() => this._data().length)
```

## HttpClient

```typescript
// app.config.ts
provideHttpClient(withFetch(), withInterceptors([authInterceptor]))

// Service
this.http.get<User[]>('/api/users')
this.http.post<User>('/api/users', body)
this.http.put<User>('/api/users/1', body)
this.http.delete<void>('/api/users/1')

// Paramètres
const params = new HttpParams().set('page', '1').set('size', '10')
this.http.get('/api', { params })

// Observer dans le composant
this.service.getAll()
  .pipe(takeUntilDestroyed(this.destroyRef))
  .subscribe({ next: (data) => ..., error: (err) => ... })

// Ou dans le template avec async pipe
users$ = this.service.getAll()
// template: <p *ngFor="let u of users$ | async">{{ u.name }}</p>
```

## Intercepteur

```typescript
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const auth = inject(AuthService)
  const token = auth.getToken()

  const reqClone = token
    ? req.clone({ headers: req.headers.set('Authorization', `Bearer ${token}`) })
    : req

  return next(reqClone).pipe(
    catchError((err: HttpErrorResponse) => {
      if (err.status === 401) inject(Router).navigate(['/login'])
      return throwError(() => err)
    })
  )
}
```

## Router

```typescript
// Routes
{ path: 'users', loadComponent: () => import('./user-list.component') }
{ path: 'users/:id', component: UserDetailComponent, canActivate: [authGuard] }
{ path: '**', redirectTo: '404' }

// Navigation
<a routerLink="/users">Lien</a>
<a [routerLink]="['/users', id]" routerLinkActive="active">Lien</a>
<router-outlet />

const router = inject(Router)
router.navigate(['/users', id])
router.navigate(['/search'], { queryParams: { q: terme } })

const route = inject(ActivatedRoute)
const id = route.snapshot.params['id']
const page = route.snapshot.queryParams['page']

// Guard
export const authGuard: CanActivateFn = (route, state) => {
  const auth = inject(AuthService)
  return auth.isLoggedIn() || inject(Router).createUrlTree(['/login'])
}
```

## Reactive Forms

```typescript
private fb = inject(FormBuilder)

form = this.fb.group({
  email: ['', [Validators.required, Validators.email]],
  password: ['', [Validators.required, Validators.minLength(8)]],
  age: [null, [Validators.min(0), Validators.max(150)]],
})

// Template
<form [formGroup]="form" (ngSubmit)="onSubmit()">
  <input formControlName="email" />
  @if (form.get('email')?.errors?.['required'] && form.get('email')?.touched) {
    <span>Requis</span>
  }
  <button [disabled]="form.invalid">Envoyer</button>
</form>

// Valeurs
form.value               // { email: '', password: '' }
form.get('email')!.value // lecture
form.patchValue({ email: 'test@test.com' })
form.setValue({ email: '', password: '' })  // TOUS les champs
form.markAllAsTouched()
form.reset()
```

## Pipes built-in

```html
{{ date | date:'dd/MM/yyyy' }}          <!-- DatePipe -->
{{ prix | currency:'EUR' }}             <!-- CurrencyPipe -->
{{ 0.75 | percent }}                    <!-- PercentPipe -->
{{ 'hello' | uppercase }}               <!-- UpperCasePipe -->
{{ texte | slice:0:100 }}               <!-- SlicePipe -->
{{ obj | json }}                        <!-- JsonPipe (debug) -->
{{ obs$ | async }}                      <!-- AsyncPipe -->
```

## RxJS — Opérateurs clés

```typescript
import { map, filter, switchMap, mergeMap, tap, catchError,
         debounceTime, distinctUntilChanged, combineLatest, forkJoin,
         takeUntilDestroyed } from 'rxjs'

source$.pipe(
  map(x => x * 2),
  filter(x => x > 0),
  debounceTime(400),
  distinctUntilChanged(),
  switchMap(v => this.http.get(`/api?q=${v}`)),   // Annule la requête précédente
  catchError(err => of([])),                       // Fallback en cas d'erreur
  takeUntilDestroyed(this.destroyRef),             // Auto-unsubscribe
).subscribe(data => this.data.set(data))

// Parallèle
forkJoin([users$, posts$]).subscribe(([users, posts]) => { ... })
combineLatest([a$, b$]).subscribe(([a, b]) => { ... })
```

## Gotchas et bonnes pratiques

```typescript
// ✅ Toujours unsubscribe avec takeUntilDestroyed
obs$.pipe(takeUntilDestroyed(this.destroyRef)).subscribe(...)

// ✅ Utiliser le async pipe quand possible (unsubscribe auto)
// template: {{ users$ | async }}

// ✅ Signals plutôt que BehaviorSubject pour l'état local
private _count = signal(0)  // plus simple que new BehaviorSubject(0)

// ✅ inject() plutôt que constructor
private service = inject(MonService)  // vs constructor(private s: MonService)

// ✅ Lazy load toutes les routes
loadComponent: () => import('./comp').then(m => m.MonComponent)

// ❌ Ne pas subscribe dans subscribe
// ❌ Ne pas mutar l'état directement depuis un composant (passer par le service)
// ❌ Oublier de déclarer un composant dans imports[] d'un standalone component
```
