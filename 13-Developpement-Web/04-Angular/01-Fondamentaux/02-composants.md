# Composants Angular

## Anatomie d'un composant Angular

Un composant Angular se compose de 3 à 4 fichiers :

```
user-card/
├── user-card.component.ts       # Logique TypeScript + métadonnées
├── user-card.component.html     # Template HTML
├── user-card.component.scss     # Styles CSS scoped
└── user-card.component.spec.ts  # Tests unitaires
```

### Créer avec la CLI

```bash
ng generate component components/user-card
# ou raccourci :
ng g c components/user-card
```

## Le décorateur `@Component`

```typescript
// src/app/components/user-card/user-card.component.ts
import { Component, Input, Output, EventEmitter, OnInit } from '@angular/core'
import { CommonModule } from '@angular/common'
import { RouterModule } from '@angular/router'
import { User } from '@/models/user.model'

@Component({
  // OBLIGATOIRE: le sélecteur CSS utilisé dans les templates parents
  selector: 'app-user-card',

  // Standalone Component (Angular 17+ recommandé)
  standalone: true,

  // Modules/composants importés (nécessaires pour NgFor, NgIf, routerLink, etc.)
  imports: [CommonModule, RouterModule],

  // Template inline (pour les petits composants)
  // template: `<div>{{ user.name }}</div>`,

  // Ou fichier externe (recommandé pour les vrais projets)
  templateUrl: './user-card.component.html',
  styleUrl: './user-card.component.scss',

  // Stratégie de détection de changements (OnPush = performances optimisées)
  // changeDetection: ChangeDetectionStrategy.OnPush,
})
export class UserCardComponent implements OnInit {
  // @Input() — données reçues du composant parent
  @Input({ required: true }) user!: User
  @Input() afficherEmail = true   // valeur par défaut

  // @Output() — événements émis vers le parent
  @Output() selectionner = new EventEmitter<User>()
  @Output() supprimer = new EventEmitter<number>()

  // Propriété calculée
  get initialesNom(): string {
    return this.user.name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .substring(0, 2)
  }

  // Cycle de vie
  ngOnInit(): void {
    console.log('UserCardComponent initialisé avec :', this.user)
  }

  // Méthodes
  onSelectionner(): void {
    this.selectionner.emit(this.user)
  }

  onSupprimer(event: MouseEvent): void {
    event.stopPropagation()                    // Ne pas déclencher le clic parent
    this.supprimer.emit(this.user.id)
  }
}
```

```html
<!-- user-card.component.html -->
<div class="user-card" (click)="onSelectionner()">
  <div class="avatar">{{ initialesNom }}</div>

  <div class="info">
    <h3>{{ user.name }}</h3>
    <p *ngIf="afficherEmail" class="email">{{ user.email }}</p>
    <span class="badge" [class]="'badge-' + user.role">{{ user.role }}</span>
  </div>

  <button class="btn-supprimer" (click)="onSupprimer($event)">×</button>
</div>
```

## `@Input` — Passage de données parent → enfant

### Syntaxes disponibles

```typescript
import { Component, Input, input } from '@angular/core'

// Syntaxe classique (décorateur)
@Input() titre: string = ''
@Input({ required: true }) userId!: number    // ! = non-null assertion (requis)
@Input('labelExterne') labelInterne: string = '' // alias de nom

// Nouveau : Input Signals (Angular 17.1+)
// Plus intégré avec le nouveau système de réactivité
readonly titre = input<string>('')            // optionnel avec défaut
readonly userId = input.required<number>()    // requis
```

### Transformer les inputs

```typescript
import { Component, Input } from '@angular/core'

@Component({ selector: 'app-exemple', standalone: true, template: '' })
export class ExempleComponent {
  // Transformer la valeur reçue
  @Input({ transform: (valeur: string) => valeur.toLowerCase() })
  email: string = ''

  // booleanAttribute — transforme "true"/"false" strings en booléens
  // (utile pour les attributs HTML qui sont des strings)
  @Input({ transform: booleanAttribute })
  disabled: boolean = false

  // numberAttribute — transforme en nombre
  @Input({ transform: numberAttribute })
  maxItems: number = 10
}
```

### Détecter les changements d'Input

```typescript
import { Component, Input, OnChanges, SimpleChanges } from '@angular/core'

@Component({ selector: 'app-data', standalone: true, template: '' })
export class DataComponent implements OnChanges {
  @Input() userId!: number

  data: any = null

  // Appelé à chaque fois qu'un @Input change
  ngOnChanges(changes: SimpleChanges): void {
    if (changes['userId']) {
      const { previousValue, currentValue, firstChange } = changes['userId']
      console.log(`userId changé: ${previousValue} → ${currentValue}`)

      if (!firstChange) {
        // Recharger les données quand userId change
        this.chargerDonnees(currentValue)
      }
    }
  }

  async chargerDonnees(id: number): Promise<void> {
    const response = await fetch(`/api/users/${id}`)
    this.data = await response.json()
  }
}
```

## `@Output` et `EventEmitter` — Enfant → Parent

```typescript
// Composant enfant
import { Component, Output, EventEmitter } from '@angular/core'

interface FormData {
  nom: string
  email: string
}

@Component({
  selector: 'app-user-form',
  standalone: true,
  template: `
    <form (ngSubmit)="soumettre()">
      <input [(ngModel)]="formData.nom" name="nom" placeholder="Nom" />
      <input [(ngModel)]="formData.email" name="email" placeholder="Email" />
      <button type="submit">Enregistrer</button>
      <button type="button" (click)="annuler()">Annuler</button>
    </form>
  `,
})
export class UserFormComponent {
  @Output() enregistrer = new EventEmitter<FormData>()
  @Output() annulerEvent = new EventEmitter<void>()

  formData: FormData = { nom: '', email: '' }

  soumettre(): void {
    if (this.formData.nom && this.formData.email) {
      this.enregistrer.emit(this.formData)
      this.formData = { nom: '', email: '' }  // Reset
    }
  }

  annuler(): void {
    this.annulerEvent.emit()
  }
}
```

```typescript
// Composant parent
@Component({
  selector: 'app-parent',
  standalone: true,
  imports: [UserFormComponent],
  template: `
    <h2>Utilisateurs ({{ users.length }})</h2>

    <app-user-form
      (enregistrer)="ajouterUtilisateur($event)"
      (annulerEvent)="fermerFormulaire()"
    />
  `,
})
export class ParentComponent {
  users: FormData[] = []

  ajouterUtilisateur(data: FormData): void {
    this.users.push(data)
    console.log('Nouvel utilisateur :', data)
  }

  fermerFormulaire(): void {
    console.log('Formulaire annulé')
  }
}
```

## Lifecycle Hooks — Cycle de vie

Angular appelle des méthodes spéciales à chaque étape du cycle de vie d'un composant.

```typescript
import {
  Component,
  OnInit,
  OnChanges,
  DoCheck,
  AfterContentInit,
  AfterContentChecked,
  AfterViewInit,
  AfterViewChecked,
  OnDestroy,
  Input,
  SimpleChanges,
} from '@angular/core'
import { Subscription } from 'rxjs'

@Component({
  selector: 'app-lifecycle-demo',
  standalone: true,
  template: '<p>{{ donnee }}</p>',
})
export class LifecycleDemoComponent
  implements
    OnInit,
    OnChanges,
    DoCheck,
    AfterContentInit,
    AfterContentChecked,
    AfterViewInit,
    AfterViewChecked,
    OnDestroy
{
  @Input() userId!: number

  donnee: string = ''
  private abonnement!: Subscription

  // 1. Appelé à chaque changement d'@Input (AVANT ngOnInit au premier rendu)
  ngOnChanges(changes: SimpleChanges): void {
    console.log('ngOnChanges:', changes)
  }

  // 2. Appelé UNE FOIS après la première initialisation
  // C'est ICI qu'on fait les appels API initiaux
  ngOnInit(): void {
    console.log('ngOnInit: composant initialisé')
    this.chargerDonnees()
  }

  // 3. Appelé à chaque cycle de détection de changements (souvent!)
  // Utiliser avec précaution — peut être appelé très souvent
  ngDoCheck(): void {
    // Détection personnalisée
  }

  // 4. Après initialisation du contenu projeté (ng-content)
  ngAfterContentInit(): void {
    console.log('ngAfterContentInit: ng-content projeté')
  }

  // 5. Après chaque vérification du contenu projeté
  ngAfterContentChecked(): void { }

  // 6. Après initialisation des vues enfants — accès complet au DOM
  ngAfterViewInit(): void {
    console.log('ngAfterViewInit: vue enfant initialisée')
    // Accéder aux ViewChild ici (PAS dans ngOnInit)
  }

  // 7. Après chaque vérification des vues
  ngAfterViewChecked(): void { }

  // 8. Juste avant la destruction du composant
  // OBLIGATOIRE pour nettoyer les subscriptions RxJS et éviter les fuites mémoire
  ngOnDestroy(): void {
    console.log('ngOnDestroy: nettoyage')
    this.abonnement?.unsubscribe()
    // clearInterval, removeEventListener, etc.
  }

  private async chargerDonnees(): Promise<void> {
    const response = await fetch(`/api/users/${this.userId}`)
    const user = await response.json()
    this.donnee = user.name
  }
}
```

### Hooks les plus utilisés

| Hook | Quand | Utilisation typique |
|---|---|---|
| `ngOnInit` | Une fois après initialisation | Appels API, subscriptions |
| `ngOnChanges` | À chaque changement d'@Input | Réagir aux nouvelles valeurs |
| `ngOnDestroy` | Avant destruction | Nettoyer subscriptions, timers |
| `ngAfterViewInit` | Après init du DOM enfant | Accéder aux ViewChild |

## `@ViewChild` et `@ContentChild`

### `@ViewChild` — Accéder à un enfant du template

```typescript
import { Component, ViewChild, AfterViewInit, ElementRef } from '@angular/core'
import { FormsModule } from '@angular/forms'

@Component({
  selector: 'app-focus-demo',
  standalone: true,
  imports: [FormsModule],
  template: `
    <input #champNom type="text" placeholder="Votre nom" />
    <app-enfant #composantEnfant />
    <button (click)="focusInput()">Focus</button>
  `,
})
export class FocusDemoComponent implements AfterViewInit {
  // Accéder à un élément DOM natif
  @ViewChild('champNom') champNomRef!: ElementRef<HTMLInputElement>

  // Accéder à un composant enfant (instance du composant)
  @ViewChild('composantEnfant') enfantRef!: EnfantComponent

  // Disponible UNIQUEMENT après ngAfterViewInit (pas dans ngOnInit!)
  ngAfterViewInit(): void {
    this.champNomRef.nativeElement.focus()
    this.enfantRef.methodePublique()
  }

  focusInput(): void {
    this.champNomRef.nativeElement.focus()
    this.champNomRef.nativeElement.select()
  }
}
```

### `@ContentChild` — Accéder au contenu projeté (ng-content)

```typescript
import { Component, ContentChild, AfterContentInit } from '@angular/core'

@Component({
  selector: 'app-carte',
  standalone: true,
  template: `
    <div class="carte">
      <div class="header">
        <!-- Le contenu projeté par ng-content -->
        <ng-content select="[slot='header']" />
      </div>
      <div class="body">
        <ng-content />
      </div>
    </div>
  `,
})
export class CarteComponent implements AfterContentInit {
  @ContentChild('titre') titreRef!: ElementRef

  ngAfterContentInit(): void {
    console.log('Titre projeté :', this.titreRef?.nativeElement?.textContent)
  }
}
```

```html
<!-- Utilisation avec ng-content -->
<app-carte>
  <h2 slot="header" #titre>Titre de la carte</h2>
  <p>Corps de la carte — projeté dans le ng-content par défaut</p>
</app-carte>
```

## `ChangeDetectionStrategy.OnPush` — Optimisation

```typescript
import { Component, ChangeDetectionStrategy, Input } from '@angular/core'

@Component({
  selector: 'app-optimised',
  standalone: true,
  // OnPush : Angular ne re-render ce composant que si :
  // 1. Une @Input change (référence différente)
  // 2. Un événement DOM dans ce composant est déclenché
  // 3. Un Observable s'y termine (avec | async pipe)
  // 4. markForCheck() est appelé manuellement
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `<p>{{ utilisateur.name }}</p>`,
})
export class OptimisedComponent {
  @Input() utilisateur!: { id: number; name: string }

  // ATTENTION avec OnPush : muter l'objet ne déclenche PAS de re-render
  // Il faut créer un NOUVEL objet (immutabilité)
  // ❌ this.utilisateur.name = 'Bob'  → pas de re-render
  // ✅ this.utilisateur = { ...this.utilisateur, name: 'Bob' }  → re-render
}
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Angular DevTools dans le navigateur (F12 → onglet Angular) avec l'arbre des composants
> **Expliquer :** Installer Angular DevTools (extension Chrome). Ouvrir l'onglet Angular dans DevTools. Montrer l'arbre des composants, les @Input visibles pour chaque composant. Cliquer sur un composant et modifier une valeur d'Input directement dans le panneau. Montrer comment profiler les performances avec l'onglet "Profiler" d'Angular DevTools.
---

## Exemple complet — Liste d'utilisateurs avec interaction

```typescript
// src/app/features/users/user-list.component.ts
import { Component, signal, computed } from '@angular/core'
import { CommonModule } from '@angular/common'
import { FormsModule } from '@angular/forms'

interface User {
  id: number
  name: string
  email: string
  role: 'admin' | 'user'
  active: boolean
}

@Component({
  selector: 'app-user-list',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="user-list">
      <div class="controls">
        <input
          [(ngModel)]="recherche"
          placeholder="Rechercher..."
          class="search-input"
        />
        <span>{{ usersFiltres().length }} utilisateur(s)</span>
      </div>

      <div class="user-grid">
        @for (user of usersFiltres(); track user.id) {
          <div class="user-card" [class.inactive]="!user.active">
            <span class="initiales">{{ getInitiales(user.name) }}</span>
            <div class="info">
              <strong>{{ user.name }}</strong>
              <small>{{ user.email }}</small>
              <span class="badge" [class]="'role-' + user.role">
                {{ user.role }}
              </span>
            </div>
            <div class="actions">
              <button (click)="toggleActive(user)">
                {{ user.active ? 'Désactiver' : 'Activer' }}
              </button>
              <button (click)="supprimer(user.id)" class="btn-danger">
                Supprimer
              </button>
            </div>
          </div>
        } @empty {
          <p class="empty-state">Aucun utilisateur trouvé.</p>
        }
      </div>
    </div>
  `,
})
export class UserListComponent {
  // Signals (Angular 17+)
  users = signal<User[]>([
    { id: 1, name: 'Alice Dupont', email: 'alice@ex.com', role: 'admin', active: true },
    { id: 2, name: 'Bob Martin', email: 'bob@ex.com', role: 'user', active: true },
    { id: 3, name: 'Clara Petit', email: 'clara@ex.com', role: 'user', active: false },
  ])

  recherche = ''  // valeur ngModel

  // Computed signal — recalculé quand users() ou recherche change
  usersFiltres = computed(() => {
    const terme = this.recherche.toLowerCase().trim()
    if (!terme) return this.users()
    return this.users().filter(
      (u) =>
        u.name.toLowerCase().includes(terme) ||
        u.email.toLowerCase().includes(terme),
    )
  })

  getInitiales(name: string): string {
    return name.split(' ').map((n) => n[0]).join('').substring(0, 2).toUpperCase()
  }

  toggleActive(user: User): void {
    // Avec Signals : update crée un nouvel tableau (immutabilité)
    this.users.update((users) =>
      users.map((u) => (u.id === user.id ? { ...u, active: !u.active } : u))
    )
  }

  supprimer(id: number): void {
    this.users.update((users) => users.filter((u) => u.id !== id))
  }
}
```

## Résumé

| Concept | Description | Décorateur/API |
|---|---|---|
| Composant | Brique UI avec template | `@Component` |
| Input | Données parent → enfant | `@Input()` |
| Output | Événements enfant → parent | `@Output() + EventEmitter` |
| ViewChild | Accès DOM / composant enfant | `@ViewChild()` |
| ContentChild | Accès contenu projeté | `@ContentChild()` |
| Projection | Injection de contenu | `<ng-content>` |
| OnPush | Optimisation re-renders | `ChangeDetectionStrategy.OnPush` |
| Signals | Réactivité moderne | `signal()`, `computed()` |

**Prochaine étape :** La syntaxe de template Angular — directives, pipes →
