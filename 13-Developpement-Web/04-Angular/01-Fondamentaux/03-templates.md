# Templates Angular — Syntaxe, Directives et Pipes

## Interpolation `{{ }}`

```html
<!-- Affichage de variables du composant -->
<h1>{{ titre }}</h1>
<p>{{ utilisateur.nom }} {{ utilisateur.prenom }}</p>

<!-- Expressions JavaScript simples (pas de statements comme if/for) -->
<p>{{ 1 + 1 }}</p>
<p>{{ 'bonjour'.toUpperCase() }}</p>
<p>{{ isConnecte ? 'Connecté' : 'Déconnecté' }}</p>
<p>{{ items.length }} article(s)</p>
<p>{{ dateNaissance | date:'dd/MM/yyyy' }}</p> <!-- avec pipe -->
```

## Property Binding `[property]`

```html
<!-- Lier une propriété DOM à une expression Angular -->
<img [src]="imageUrl" [alt]="imageDescription" />

<!-- Classe dynamique -->
<div [class]="classeCSS"></div>
<div [class.active]="isActive"></div>
<div [class.disabled]="isDisabled" [class.highlighted]="isHighlighted"></div>
<div [ngClass]="{ active: isActive, large: isLarge, 'has-error': hasError }"></div>

<!-- Style dynamique -->
<p [style.color]="couleurTexte"></p>
<p [style.fontSize.px]="taillePolice"></p>
<p [ngStyle]="{ color: couleur, 'font-size': taille + 'px' }"></p>

<!-- Attributs HTML (pas des propriétés DOM) -->
<button [attr.aria-label]="labelAccessibilite">Bouton</button>
<td [attr.colspan]="nbColonnes">Cellule</td>

<!-- Disabled -->
<button [disabled]="isLoading || !formValid">Envoyer</button>
<input [readonly]="isReadonly" />
```

## Event Binding `(event)`

```html
<!-- Événements DOM standard -->
<button (click)="onClick()">Cliquer</button>
<button (click)="onClick($event)">Avec l'objet événement</button>
<input (input)="onInput($event)" />
<input (keyup.enter)="onEnter()" />
<input (keyup.escape)="onEscape()" />
<form (submit)="onSubmit($event)">
<div (mouseover)="onHover()" (mouseleave)="onLeave()">

<!-- Événements personnalisés (@Output) -->
<app-user-card (selectionner)="onUserSelected($event)" />

<!-- Modifier l'événement -->
<!-- $event est l'objet MouseEvent, KeyboardEvent, etc. -->
```

```typescript
// Dans le composant TypeScript
onClick(event?: MouseEvent): void {
  console.log('Cliqué !', event)
}

onInput(event: Event): void {
  const input = event.target as HTMLInputElement
  console.log('Valeur:', input.value)
}

onEnter(): void {
  console.log('Entrée pressée')
}
```

## Two-way Binding `[(ngModel)]`

```html
<!-- Nécessite FormsModule importé dans le composant -->
<input [(ngModel)]="nom" placeholder="Nom" />
<!-- Equivalent à : -->
<input [value]="nom" (input)="nom = $event.target.value" />

<!-- Avec d'autres types d'inputs -->
<textarea [(ngModel)]="description"></textarea>
<select [(ngModel)]="paysCourant">
  <option *ngFor="let p of pays" [value]="p.code">{{ p.nom }}</option>
</select>
<input type="checkbox" [(ngModel)]="accepteCgu" />
```

## Nouvelle syntaxe de template (Angular 17+)

Angular 17 introduit une syntaxe plus intuitive avec `@if`, `@for`, `@switch` :

### `@if` — Conditions

```html
<!-- Nouvelle syntaxe (Angular 17+) -->
@if (utilisateur) {
  <div class="profil">
    <h2>{{ utilisateur.nom }}</h2>
    <p>{{ utilisateur.email }}</p>
  </div>
} @else if (chargement) {
  <p>Chargement...</p>
} @else {
  <p>Aucun utilisateur trouvé.</p>
}

<!-- Ancienne syntaxe (toujours valide) -->
<div *ngIf="utilisateur; else aucunUser">
  <h2>{{ utilisateur.nom }}</h2>
</div>
<ng-template #aucunUser>
  <p>Aucun utilisateur.</p>
</ng-template>
```

### `@for` — Listes

```html
<!-- Nouvelle syntaxe (Angular 17+) -->
@for (produit of produits; track produit.id) {
  <div class="produit-card">
    <h3>{{ produit.nom }}</h3>
    <p>{{ produit.prix }}€</p>
  </div>
} @empty {
  <p>Aucun produit disponible.</p>
}

<!-- Avec les variables contextuelles -->
@for (item of items; track item.id; let i = $index, let last = $last, let even = $even) {
  <div [class.dernier]="last" [class.pair]="even">
    {{ i + 1 }}. {{ item.nom }}
  </div>
}

<!-- Ancienne syntaxe *ngFor -->
<div *ngFor="let produit of produits; trackBy: trackByProduitId; let i = index">
  {{ i + 1 }}. {{ produit.nom }}
</div>
```

```typescript
// Dans le composant — trackBy améliore les performances
trackByProduitId(index: number, produit: Produit): number {
  return produit.id
}
```

### `@switch` — Switch case

```html
<!-- Nouvelle syntaxe -->
@switch (statut) {
  @case ('actif') {
    <span class="badge-vert">Actif</span>
  }
  @case ('inactif') {
    <span class="badge-rouge">Inactif</span>
  }
  @case ('en_attente') {
    <span class="badge-orange">En attente</span>
  }
  @default {
    <span class="badge-gris">Inconnu</span>
  }
}

<!-- Ancienne syntaxe ngSwitch -->
<div [ngSwitch]="statut">
  <span *ngSwitchCase="'actif'" class="badge-vert">Actif</span>
  <span *ngSwitchCase="'inactif'" class="badge-rouge">Inactif</span>
  <span *ngSwitchDefault class="badge-gris">Inconnu</span>
</div>
```

### `@defer` — Chargement différé (Angular 17+)

```html
<!-- Charger un composant lourd seulement quand il devient visible -->
@defer (on viewport) {
  <app-graphique-lourd />
} @placeholder {
  <div class="placeholder">Le graphique apparaîtra ici</div>
} @loading {
  <p>Chargement du graphique...</p>
} @error {
  <p>Impossible de charger le graphique.</p>
}

<!-- Autres triggers de @defer -->
@defer (on idle) { ... }           <!-- quand le navigateur est inactif -->
@defer (on interaction) { ... }    <!-- au premier clic/survol -->
@defer (when estConnecte) { ... }  <!-- condition booléenne -->
@defer (on timer(3s)) { ... }      <!-- après 3 secondes -->
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Éditeur de code côte à côte avec le navigateur — modifier les données dans le composant et voir le template se mettre à jour
> **Expliquer :** Modifier une valeur dans le composant TypeScript (par exemple, changer `isLoading = false` en `isLoading = true`), sauvegarder, et montrer le hot reload. Comparer la syntaxe ancienne `*ngIf` avec la nouvelle `@if` — expliquer que la nouvelle syntaxe est plus lisible et native (pas de microsyntaxe structurale).
---

## Pipes — Transformation des données

Les pipes transforment les données dans les templates sans modifier les données sources.

### Pipes built-in Angular

```html
<!-- DatePipe -->
<p>{{ date | date }}</p>
<p>{{ date | date:'dd/MM/yyyy' }}</p>
<p>{{ date | date:'dd MMMM yyyy' }}</p>
<p>{{ date | date:'shortTime' }}</p>         <!-- 14:30 -->
<p>{{ date | date:'fullDate':'':'fr' }}</p>   <!-- locale française -->

<!-- CurrencyPipe -->
<p>{{ prix | currency }}</p>                  <!-- $1,234.56 -->
<p>{{ prix | currency:'EUR':'symbol':'1.2-2' }}</p>  <!-- 1 234,56 € -->
<p>{{ prix | currency:'EUR':'code' }}</p>     <!-- EUR 1,234.56 -->

<!-- DecimalPipe (number) -->
<p>{{ 1234567 | number }}</p>                 <!-- 1,234,567 -->
<p>{{ 3.14159 | number:'1.2-3' }}</p>         <!-- 3.142 (2 à 3 décimales) -->

<!-- PercentPipe -->
<p>{{ 0.753 | percent }}</p>                  <!-- 75% -->
<p>{{ 0.753 | percent:'1.1-2' }}</p>          <!-- 75.3% -->

<!-- UpperCasePipe / LowerCasePipe / TitleCasePipe -->
<p>{{ 'bonjour monde' | uppercase }}</p>      <!-- BONJOUR MONDE -->
<p>{{ 'HELLO WORLD' | lowercase }}</p>        <!-- hello world -->
<p>{{ 'bonjour monde' | titlecase }}</p>      <!-- Bonjour Monde -->

<!-- SlicePipe -->
<p>{{ 'Bonjour' | slice:0:3 }}</p>            <!-- Bon -->
<ul>
  <li *ngFor="let item of items | slice:0:5">{{ item }}</li>
</ul>

<!-- JsonPipe (débogage) -->
<pre>{{ objet | json }}</pre>

<!-- AsyncPipe — s'abonner à un Observable/Promise dans le template -->
<p>{{ donnees$ | async }}</p>
<div *ngIf="utilisateur$ | async as user">
  <p>{{ user.nom }}</p>
</div>

<!-- Enchaîner les pipes -->
<p>{{ 'hello world' | titlecase | slice:0:5 }}</p>  <!-- Hello -->
```

### Créer un pipe personnalisé

```bash
ng generate pipe pipes/truncate
# ou ng g p pipes/truncate
```

```typescript
// src/app/pipes/truncate.pipe.ts
import { Pipe, PipeTransform } from '@angular/core'

@Pipe({
  name: 'truncate',    // Nom utilisé dans le template : {{ texte | truncate:50 }}
  standalone: true,
  pure: true,          // Pure = recalculé seulement si l'input change (défaut: true)
})
export class TruncatePipe implements PipeTransform {
  // transform est la méthode principale
  transform(valeur: string, longueur = 100, suffix = '...'): string {
    if (!valeur) return ''
    if (valeur.length <= longueur) return valeur
    return valeur.substring(0, longueur).trim() + suffix
  }
}
```

```typescript
// Pipe pour le formatage de numéro de téléphone
@Pipe({ name: 'telephone', standalone: true })
export class TelephonePipe implements PipeTransform {
  transform(tel: string): string {
    if (!tel) return ''
    const clean = tel.replace(/\D/g, '')
    if (clean.length !== 10) return tel
    return clean.match(/.{1,2}/g)!.join(' ')
    // 0612345678 → 06 12 34 56 78
  }
}
```

```typescript
// Utilisation dans le composant
@Component({
  selector: 'app-article',
  standalone: true,
  imports: [TruncatePipe, TelephonePipe],
  template: `
    <p>{{ article.contenu | truncate:200 }}</p>
    <p>{{ article.contenu | truncate:150:'[lire la suite]' }}</p>
    <p>{{ contact.telephone | telephone }}</p>
  `,
})
export class ArticleComponent {
  article = { contenu: 'Long texte...' }
  contact = { telephone: '0612345678' }
}
```

## `ng-template`, `ng-container`, `ng-content`

### `ng-container` — Grouper sans élément DOM

```html
<!-- Appliquer une directive sur plusieurs éléments sans créer de div -->
<ng-container *ngIf="isLoggedIn">
  <li>Mon profil</li>
  <li>Mes commandes</li>
  <li>Déconnexion</li>
</ng-container>

<!-- Combiner *ngFor et *ngIf sans div supplémentaire -->
<ng-container *ngFor="let item of items">
  <li *ngIf="item.visible">{{ item.nom }}</li>
</ng-container>
```

### `ng-template` — Template réutilisable

```html
<ng-template #chargement>
  <div class="spinner">Chargement en cours...</div>
</ng-template>

<ng-template #erreur let-message="message">
  <div class="alerte-erreur">{{ message }}</div>
</ng-template>

<!-- Utilisation avec ngIf et else/then -->
<div *ngIf="donnees; else chargement">
  <p>Données : {{ donnees }}</p>
</div>

<!-- Utilisation programmatique avec ngTemplateOutlet -->
<ng-container
  *ngTemplateOutlet="erreur; context: { message: 'Une erreur est survenue' }"
/>
```

### `ng-content` — Projection de contenu (Slots)

```typescript
// Composant parent — Card
@Component({
  selector: 'app-card',
  standalone: true,
  template: `
    <div class="card">
      <div class="card-header">
        <!-- ng-content avec select → projection nommée (équivalent des slots Vue) -->
        <ng-content select="[cardTitle]" />
      </div>
      <div class="card-body">
        <!-- ng-content sans select → projection du contenu par défaut -->
        <ng-content />
      </div>
      <div class="card-footer">
        <ng-content select="[cardFooter]" />
      </div>
    </div>
  `,
})
export class CardComponent {}
```

```html
<!-- Utilisation -->
<app-card>
  <!-- Projeté dans select="[cardTitle]" -->
  <h2 cardTitle>Titre de la carte</h2>

  <!-- Projeté dans le ng-content par défaut -->
  <p>Contenu principal de la carte.</p>
  <p>Peut contenir plusieurs éléments.</p>

  <!-- Projeté dans select="[cardFooter]" -->
  <div cardFooter>
    <button>Annuler</button>
    <button class="btn-primary">Valider</button>
  </div>
</app-card>
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Navigateur avec Angular DevTools ouvert, montrer l'arbre de composants imbriqués avec ng-content
> **Expliquer :** Créer un composant Card avec ng-content et utiliser l'Angular DevTools pour montrer la structure du DOM. Expliquer que ng-content est l'équivalent Angular des "slots" Vue ou des "children" React. Montrer dans l'inspecteur DOM que ng-container ne génère PAS d'élément HTML supplémentaire.
---

## Exemple complet — Table de données avec toutes les fonctionnalités

```typescript
// src/app/features/products/product-table.component.ts
import { Component, signal, computed, OnInit } from '@angular/core'
import { CommonModule, DatePipe, CurrencyPipe } from '@angular/common'
import { FormsModule } from '@angular/forms'
import { TruncatePipe } from '@/pipes/truncate.pipe'

interface Produit {
  id: number
  nom: string
  description: string
  prix: number
  stock: number
  categorie: 'electronique' | 'vetement' | 'alimentation'
  createdAt: Date
  actif: boolean
}

type ColonneTri = 'nom' | 'prix' | 'stock'
type DirectionTri = 'asc' | 'desc'

@Component({
  selector: 'app-product-table',
  standalone: true,
  imports: [CommonModule, FormsModule, TruncatePipe, DatePipe, CurrencyPipe],
  template: `
    <div class="table-container">
      <!-- Barre de contrôles -->
      <div class="controls">
        <input [(ngModel)]="recherche" placeholder="Rechercher..." />
        <select [(ngModel)]="filtreCategorie">
          <option value="">Toutes catégories</option>
          <option value="electronique">Électronique</option>
          <option value="vetement">Vêtement</option>
          <option value="alimentation">Alimentation</option>
        </select>
        <span>{{ produitsFiltres().length }} produit(s)</span>
      </div>

      <!-- Table -->
      <table>
        <thead>
          <tr>
            <th (click)="trier('nom')" [class.actif]="colonneTri === 'nom'">
              Nom {{ colonneTri === 'nom' ? (directionTri === 'asc' ? '↑' : '↓') : '' }}
            </th>
            <th>Description</th>
            <th (click)="trier('prix')" [class.actif]="colonneTri === 'prix'">
              Prix {{ colonneTri === 'prix' ? (directionTri === 'asc' ? '↑' : '↓') : '' }}
            </th>
            <th (click)="trier('stock')" [class.actif]="colonneTri === 'stock'">
              Stock
            </th>
            <th>Créé le</th>
            <th>Statut</th>
          </tr>
        </thead>
        <tbody>
          @for (produit of produitsFiltres(); track produit.id) {
            <tr [class.inactif]="!produit.actif">
              <td>{{ produit.nom }}</td>
              <td>{{ produit.description | truncate:60 }}</td>
              <td>{{ produit.prix | currency:'EUR' }}</td>
              <td [class.rupture]="produit.stock === 0">
                {{ produit.stock > 0 ? produit.stock : 'Rupture' }}
              </td>
              <td>{{ produit.createdAt | date:'dd/MM/yyyy' }}</td>
              <td>
                @switch (produit.categorie) {
                  @case ('electronique') { <span class="badge bleu">Tech</span> }
                  @case ('vetement') { <span class="badge violet">Mode</span> }
                  @case ('alimentation') { <span class="badge vert">Food</span> }
                }
              </td>
            </tr>
          } @empty {
            <tr>
              <td colspan="6" class="vide">Aucun produit trouvé.</td>
            </tr>
          }
        </tbody>
      </table>
    </div>
  `,
})
export class ProductTableComponent implements OnInit {
  produits = signal<Produit[]>([])
  recherche = ''
  filtreCategorie = ''
  colonneTri: ColonneTri = 'nom'
  directionTri: DirectionTri = 'asc'

  produitsFiltres = computed(() => {
    let result = this.produits()

    if (this.recherche.trim()) {
      const terme = this.recherche.toLowerCase()
      result = result.filter(
        (p) => p.nom.toLowerCase().includes(terme) || p.description.toLowerCase().includes(terme)
      )
    }

    if (this.filtreCategorie) {
      result = result.filter((p) => p.categorie === this.filtreCategorie)
    }

    return [...result].sort((a, b) => {
      const mult = this.directionTri === 'asc' ? 1 : -1
      const valA = a[this.colonneTri]
      const valB = b[this.colonneTri]
      if (typeof valA === 'string') return valA.localeCompare(valB as string) * mult
      return ((valA as number) - (valB as number)) * mult
    })
  })

  ngOnInit(): void {
    // Charger les données initiales
    this.produits.set([
      { id: 1, nom: 'iPhone 15', description: 'Smartphone Apple dernière génération', prix: 999, stock: 12, categorie: 'electronique', createdAt: new Date(), actif: true },
      { id: 2, nom: 'T-shirt coton', description: 'T-shirt 100% coton bio', prix: 29, stock: 0, categorie: 'vetement', createdAt: new Date(), actif: true },
      { id: 3, nom: 'Café arabica', description: 'Café en grains, origine Éthiopie', prix: 15, stock: 50, categorie: 'alimentation', createdAt: new Date(), actif: false },
    ])
  }

  trier(colonne: ColonneTri): void {
    if (this.colonneTri === colonne) {
      this.directionTri = this.directionTri === 'asc' ? 'desc' : 'asc'
    } else {
      this.colonneTri = colonne
      this.directionTri = 'asc'
    }
  }
}
```

## Résumé des syntaxes de template

| Syntaxe | Description | Exemple |
|---|---|---|
| `{{ expr }}` | Interpolation | `{{ user.name }}` |
| `[prop]` | Property binding | `[disabled]="loading"` |
| `(event)` | Event binding | `(click)="onClick()"` |
| `[(ngModel)]` | Two-way binding | `[(ngModel)]="email"` |
| `@if` | Condition | `@if (user) { ... }` |
| `@for` | Boucle | `@for (x of list; track x.id)` |
| `@switch` | Switch | `@switch (val) { @case ...}` |
| `@defer` | Lazy loading | `@defer (on viewport) { ... }` |
| `pipe` | Transformation | `{{ date \| date:'dd/MM' }}` |
| `ng-content` | Projection de contenu | `<ng-content select="[title]">` |
| `ng-container` | Groupement sans DOM | `<ng-container *ngIf>` |

**Prochaine étape :** Services et injection de dépendances →
