# 18 — Détection du Data Drift

## Objectifs pédagogiques

À la fin de ce module, vous serez capable de :

- Comprendre ce qu'est le data drift, le concept drift et la dégradation de la qualité des données
- Identifier les différents types de drift et leurs causes
- Appliquer des tests statistiques pour détecter le drift
- Utiliser la bibliothèque Evidently AI pour générer des rapports de drift
- Intégrer la détection de drift avec MLflow
- Mettre en place un système de monitoring en production avec alertes
- Décider quand et comment réentraîner un modèle

---

## 1. Introduction — Pourquoi les modèles vieillissent-ils ?

### 1.1 Le problème du drift en production

Un modèle de machine learning est entraîné sur des données historiques. Il apprend les patterns présents dans ces données et suppose implicitement que le monde futur ressemblera au monde passé. Cette hypothèse est presque toujours fausse à long terme.

En production, les modèles sont exposés à un flux de données réelles qui évolue. Les comportements des utilisateurs changent, les marchés fluctuent, les processus métier évoluent, des événements imprévus surviennent. Le modèle, lui, ne change pas — il continue de répondre selon ce qu'il a appris.

Ce phénomène s'appelle le **data drift** : l'écart croissant entre les données d'entraînement et les données de production.

```
Distribution d'entraînement (t=0)
         ████
        ██████
       ████████
      ██████████
     ████████████
----+-----------+---- âge
    20          60

Distribution de production (t=6 mois)
                    ████
                   ██████
                  ████████
                 ██████████
                ████████████
----+-----------+------------+---- âge
    20          60            80
```

Le modèle a appris que les clients ont entre 20 et 60 ans. Mais si la population vieillit, ses prédictions deviennent moins fiables sur les nouveaux clients de 60 à 80 ans.

### 1.2 Les trois dimensions du drift

**Data Drift (dérive des données d'entrée)**
La distribution des features X change. Le modèle reçoit des données qui ressemblent de moins en moins à ce sur quoi il a été entraîné.

**Concept Drift (dérive du concept)**
La relation entre X et y change. Même si les features ont les mêmes distributions, leur relation avec la variable cible évolue. Par exemple, en détection de fraude, les fraudeurs développent de nouvelles techniques que le modèle n'a jamais vues.

**Data Quality Degradation (dégradation de la qualité)**
Les données en entrée deviennent moins fiables : valeurs manquantes qui apparaissent, valeurs aberrantes, erreurs de format, colonnes mal renseignées. Ce n'est pas un changement de distribution intentionnel — c'est un bug ou une dégradation du pipeline de données.

### 1.3 Conséquences concrètes

Sans monitoring, le drift peut passer inaperçu pendant des semaines ou des mois. Les symptômes :

- Baisse progressive des métriques métier (taux de conversion, précision des recommandations)
- Augmentation des erreurs de prédiction sur certains segments
- Confiance excessive du modèle (scores de probabilité élevés sur de mauvaises prédictions)
- Réclamations clients ou anomalies détectées par les équipes métier

Le coût de ne pas détecter le drift est souvent bien supérieur au coût de mise en place du monitoring.

---

## 2. Types de Drift

### 2.1 Covariate Shift (dérive des covariables)

Le covariate shift est le type de drift le plus fréquent. La distribution marginale des features P(X) change, mais la relation conditionnelle P(y|X) reste stable.

**Exemple concret :** Un modèle de crédit entraîné en 2020. En 2020, la majorité des demandeurs avaient entre 25 et 45 ans. En 2024, avec l'essor du crédit en ligne, une nouvelle population de 18-25 ans et de 65+ ans émerge. La façon dont l'âge prédit le risque de défaut (P(défaut|âge)) n'a pas changé, mais la distribution des âges (P(âge)) a changé.

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

# Données d'entraînement : population 25-45 ans
np.random.seed(42)
train_ages = np.random.normal(loc=35, scale=8, size=1000)
train_ages = np.clip(train_ages, 18, 65)

# Données de production : population plus large
prod_ages = np.concatenate([
    np.random.normal(loc=35, scale=8, size=600),   # ancienne population
    np.random.normal(loc=21, scale=3, size=200),   # nouveaux jeunes
    np.random.normal(loc=70, scale=5, size=200),   # nouveaux seniors
])
prod_ages = np.clip(prod_ages, 18, 85)

# Comparaison des distributions
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

axes[0].hist(train_ages, bins=30, alpha=0.7, color='blue', label='Entraînement', density=True)
axes[0].hist(prod_ages, bins=30, alpha=0.7, color='red', label='Production', density=True)
axes[0].set_title('Covariate Shift — Distribution des âges')
axes[0].set_xlabel('Âge')
axes[0].set_ylabel('Densité')
axes[0].legend()

# KDE pour une visualisation plus smooth
from scipy.stats import gaussian_kde
age_range = np.linspace(15, 90, 200)
kde_train = gaussian_kde(train_ages)
kde_prod = gaussian_kde(prod_ages)
axes[1].plot(age_range, kde_train(age_range), 'b-', linewidth=2, label='Entraînement')
axes[1].plot(age_range, kde_prod(age_range), 'r-', linewidth=2, label='Production')
axes[1].fill_between(age_range, kde_train(age_range), kde_prod(age_range),
                     alpha=0.3, color='orange', label='Zone de drift')
axes[1].set_title('KDE — Visualisation du drift')
axes[1].legend()

plt.tight_layout()
plt.savefig('covariate_shift.png', dpi=150)
plt.show()
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Exécuter le bloc de code ci-dessus et capturer le graphique généré avec les deux histogrammes et les courbes KDE montrant clairement la divergence entre distribution d'entraînement (bleue) et production (rouge), avec la zone orange de drift.
> **Expliquer :** Montrer à voix haute comment identifier visuellement le covariate shift — les pics secondaires dans la distribution de production qui n'existent pas dans l'entraînement. Insister sur le fait que les zones qui divergent sont celles où le modèle sera le moins fiable.

---

### 2.2 Prior Probability Shift (dérive de la probabilité a priori)

La distribution marginale de la cible P(y) change, mais la vraisemblance P(X|y) reste stable. Moins fréquent que le covariate shift, mais très impactant.

**Exemple :** Un modèle de détection de spam entraîné avec 10 % de spam. Si une campagne de spam massive démarre, le taux passe à 40 %. Le modèle, calibré pour 10 %, sous-estime systématiquement les probabilités de spam.

```python
# Simulation du prior probability shift
np.random.seed(42)

# Distribution des classes à l'entraînement
n_samples = 1000
train_y = np.random.choice([0, 1], size=n_samples, p=[0.90, 0.10])

# Distribution en production après shift
prod_y = np.random.choice([0, 1], size=n_samples, p=[0.60, 0.40])

print("=== Prior Probability Shift ===")
print(f"Entraînement — Classe 0: {np.mean(train_y == 0):.1%}, Classe 1: {np.mean(train_y == 1):.1%}")
print(f"Production   — Classe 0: {np.mean(prod_y == 0):.1%}, Classe 1: {np.mean(prod_y == 1):.1%}")

# Impact sur un modèle calibré pour l'entraînement
# Le seuil optimal se décale avec P(y)
from sklearn.calibration import calibration_curve

# Simulation : modèle qui score correctement selon P(X|y)
# mais est calibré sur l'ancienne prior
def simulate_scores_with_prior_shift(y_true, prior_train=0.10, prior_prod=0.40):
    """Simule les scores d'un modèle calibré sur prior_train appliqué à prior_prod"""
    scores = np.where(
        y_true == 1,
        np.random.beta(8, 2, size=len(y_true)),   # P(score|y=1) : scores élevés
        np.random.beta(2, 8, size=len(y_true))    # P(score|y=0) : scores faibles
    )
    return scores

scores_train = simulate_scores_with_prior_shift(train_y)
scores_prod = simulate_scores_with_prior_shift(prod_y)

print(f"\nScore moyen sur positifs — Entraînement: {scores_train[train_y==1].mean():.3f}")
print(f"Score moyen sur positifs — Production:   {scores_prod[prod_y==1].mean():.3f}")
print(f"\nAvec prior shift, un seuil de 0.5 ne sera plus optimal en production.")
print(f"Seuil optimal estimé en production: ~{prior_prod/(prior_prod + (1-prior_prod)):.2f}")
```

### 2.3 Concept Drift (dérive du concept)

La relation P(y|X) change. C'est le type de drift le plus difficile à détecter car les features peuvent sembler stables alors que leur sens a changé.

**Types de concept drift :**

- **Drift soudain** : changement abrupt (crise financière, pandémie, modification légale)
- **Drift graduel** : évolution lente et continue (habitudes de consommation, tendances sociales)
- **Drift récurrent** : patterns saisonniers qui reviennent (comportement d'achat)
- **Drift incrémental** : accumulation progressive de petits changements

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Simulation des 4 types de concept drift
def generate_concept_drift_data(n_points=1000, drift_type='sudden'):
    """Génère des données avec différents types de drift."""
    t = np.linspace(0, 1, n_points)
    x = np.random.normal(0, 1, n_points)

    if drift_type == 'sudden':
        # Le coefficient change brusquement à t=0.5
        coef = np.where(t < 0.5, 2.0, -1.5)
        y = coef * x + np.random.normal(0, 0.3, n_points)

    elif drift_type == 'gradual':
        # Le coefficient change graduellement
        coef = 2.0 - 3.5 * t
        y = coef * x + np.random.normal(0, 0.3, n_points)

    elif drift_type == 'recurring':
        # Pattern saisonnier
        coef = 2.0 * np.sin(2 * np.pi * t * 3)
        y = coef * x + np.random.normal(0, 0.3, n_points)

    elif drift_type == 'incremental':
        # Accumulation progressive
        coef = 2.0 * (1 - t ** 2)
        y = coef * x + np.random.normal(0, 0.3, n_points)

    return t, x, y, coef

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
drift_types = ['sudden', 'gradual', 'recurring', 'incremental']
titles = ['Drift Soudain', 'Drift Graduel', 'Drift Récurrent', 'Drift Incrémental']

for ax, dtype, title in zip(axes.flat, drift_types, titles):
    t, x, y, coef = generate_concept_drift_data(drift_type=dtype)

    # Calculer la corrélation dans des fenêtres glissantes
    window = 50
    correlations = [
        np.corrcoef(x[i:i+window], y[i:i+window])[0, 1]
        for i in range(0, len(t) - window, 10)
    ]
    t_windows = [t[i + window // 2] for i in range(0, len(t) - window, 10)]

    ax.plot(t_windows, correlations, 'b-', linewidth=2)
    ax.axhline(y=correlations[0], color='green', linestyle='--', alpha=0.5, label='Baseline')
    ax.fill_between(t_windows, correlations[0] - 0.1, correlations[0] + 0.1,
                    alpha=0.2, color='green', label='Zone stable')
    ax.set_title(title)
    ax.set_xlabel('Temps (normalisé)')
    ax.set_ylabel('Corrélation X-y')
    ax.legend(fontsize=8)
    ax.set_ylim(-1.1, 1.1)

plt.suptitle('Types de Concept Drift — Évolution de la corrélation X-y', fontsize=14)
plt.tight_layout()
plt.savefig('concept_drift_types.png', dpi=150)
plt.show()
```

---

## 3. Tests Statistiques pour la Détection du Drift

### 3.1 Test de Kolmogorov-Smirnov (KS Test)

Le test KS mesure la distance maximale entre deux fonctions de répartition empiriques (CDF). C'est le test non-paramétrique le plus utilisé pour comparer des distributions continues.

**Hypothèses :**
- H0 : les deux échantillons proviennent de la même distribution
- H1 : les distributions sont différentes

**Statistique KS :** D = max|F1(x) - F2(x)|

```python
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

# Exemple avec des features numériques
np.random.seed(42)

# Feature "revenue" — entraînement vs production
train_revenue = np.random.lognormal(mean=8, sigma=1.2, size=2000)
prod_revenue_no_drift = np.random.lognormal(mean=8, sigma=1.2, size=500)  # Pas de drift
prod_revenue_drift = np.random.lognormal(mean=8.8, sigma=1.4, size=500)   # Avec drift

# Test KS — cas sans drift
ks_stat_nodrift, ks_pvalue_nodrift = stats.ks_2samp(train_revenue, prod_revenue_no_drift)
print("=== Test KS — Sans drift ===")
print(f"Statistique KS : {ks_stat_nodrift:.4f}")
print(f"p-value        : {ks_pvalue_nodrift:.4f}")
print(f"Décision       : {'DRIFT DÉTECTÉ' if ks_pvalue_nodrift < 0.05 else 'Pas de drift significatif'}")

print()

# Test KS — cas avec drift
ks_stat_drift, ks_pvalue_drift = stats.ks_2samp(train_revenue, prod_revenue_drift)
print("=== Test KS — Avec drift ===")
print(f"Statistique KS : {ks_stat_drift:.4f}")
print(f"p-value        : {ks_pvalue_drift:.6f}")
print(f"Décision       : {'DRIFT DÉTECTÉ' if ks_pvalue_drift < 0.05 else 'Pas de drift significatif'}")

# Visualisation des CDF
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

for ax, prod_data, label, color in [
    (axes[0], prod_revenue_no_drift, 'Sans drift', 'green'),
    (axes[1], prod_revenue_drift, 'Avec drift', 'red')
]:
    sorted_train = np.sort(train_revenue)
    sorted_prod = np.sort(prod_data)
    cdf_train = np.arange(1, len(sorted_train) + 1) / len(sorted_train)
    cdf_prod = np.arange(1, len(sorted_prod) + 1) / len(sorted_prod)

    ax.plot(sorted_train, cdf_train, 'b-', linewidth=2, label='Entraînement')
    ax.plot(sorted_prod, cdf_prod, f'{color[0]}-', linewidth=2, label=f'Production ({label})')

    # Trouver et marquer la distance maximale
    from scipy.interpolate import interp1d
    f_train = interp1d(sorted_train, cdf_train, bounds_error=False, fill_value=(0, 1))
    diffs = np.abs(cdf_prod - f_train(sorted_prod))
    max_idx = np.argmax(diffs)
    ax.annotate(
        f'D = {diffs[max_idx]:.3f}',
        xy=(sorted_prod[max_idx], cdf_prod[max_idx]),
        xytext=(sorted_prod[max_idx] * 1.3, cdf_prod[max_idx] - 0.1),
        arrowprops=dict(arrowstyle='->', color='black'),
        fontsize=10
    )

    ax.set_title(f'CDF — {label}')
    ax.set_xlabel('Revenue')
    ax.set_ylabel('CDF')
    ax.legend()
    ax.set_xscale('log')

plt.tight_layout()
plt.savefig('ks_test_comparison.png', dpi=150)
plt.show()
```

### 3.2 Test du Chi-Carré

Pour les features catégorielles, le test KS ne s'applique pas. Le test du chi-carré compare les distributions de fréquences observées et attendues.

```python
from scipy.stats import chi2_contingency, chisquare

# Feature catégorielle : "segment_client"
segments = ['Premium', 'Standard', 'Budget', 'Nouveau']

# Fréquences d'entraînement (référence)
train_counts = np.array([200, 450, 280, 70])  # Total: 1000
train_probs = train_counts / train_counts.sum()

# Production — cas sans drift
prod_nodrift = np.array([52, 113, 70, 18])   # ~même proportions, n=253

# Production — cas avec drift (segment Premium en hausse)
prod_drift = np.array([95, 88, 51, 19])      # Total: 253

def chi2_drift_test(reference_counts, production_counts, alpha=0.05):
    """Test chi-carré pour détecter le drift sur une variable catégorielle."""
    n_prod = production_counts.sum()
    expected = train_probs * n_prod  # Fréquences attendues si pas de drift

    chi2_stat, p_value = chisquare(production_counts, f_exp=expected)

    result = {
        'chi2_stat': chi2_stat,
        'p_value': p_value,
        'drift_detected': p_value < alpha,
        'categories': segments,
        'observed_probs': production_counts / n_prod,
        'expected_probs': train_probs
    }
    return result

# Analyse sans drift
result_nodrift = chi2_drift_test(train_counts, prod_nodrift)
print("=== Chi-carré — Sans drift ===")
print(f"Statistique χ² : {result_nodrift['chi2_stat']:.4f}")
print(f"p-value        : {result_nodrift['p_value']:.4f}")
print(f"Décision       : {'DRIFT DÉTECTÉ' if result_nodrift['drift_detected'] else 'Stable'}")

print()

# Analyse avec drift
result_drift = chi2_drift_test(train_counts, prod_drift)
print("=== Chi-carré — Avec drift ===")
print(f"Statistique χ² : {result_drift['chi2_stat']:.4f}")
print(f"p-value        : {result_drift['p_value']:.6f}")
print(f"Décision       : {'DRIFT DÉTECTÉ' if result_drift['drift_detected'] else 'Stable'}")

print()
print("=== Détail par catégorie ===")
for seg, obs, exp in zip(segments, result_drift['observed_probs'], result_drift['expected_probs']):
    delta = obs - exp
    flag = " <-- DRIFT" if abs(delta) > 0.05 else ""
    print(f"  {seg:10s} : Observé={obs:.3f}, Attendu={exp:.3f}, Delta={delta:+.3f}{flag}")
```

### 3.3 Divergence de Jensen-Shannon (JSD)

La divergence KL (Kullback-Leibler) mesure l'asymétrie entre deux distributions mais n'est pas symétrique. La JSD est une version symétrique et bornée entre 0 et 1 (avec la racine carrée).

```python
from scipy.spatial.distance import jensenshannon
import numpy as np

def compute_jsd_for_numerical(ref_data, prod_data, n_bins=50):
    """Calcule la divergence Jensen-Shannon pour une feature numérique."""
    # Définir les bins sur l'union des deux distributions
    all_data = np.concatenate([ref_data, prod_data])
    bins = np.linspace(all_data.min(), all_data.max(), n_bins + 1)

    # Histogrammes normalisés
    ref_hist, _ = np.histogram(ref_data, bins=bins, density=False)
    prod_hist, _ = np.histogram(prod_data, bins=bins, density=False)

    # Convertir en probabilités (éviter les zéros avec smoothing)
    ref_probs = (ref_hist + 1e-10) / (ref_hist.sum() + n_bins * 1e-10)
    prod_probs = (prod_hist + 1e-10) / (prod_hist.sum() + n_bins * 1e-10)

    # JSD (scipy retourne la racine carrée)
    jsd = jensenshannon(ref_probs, prod_probs) ** 2  # Divergence (pas distance)

    return jsd

# Seuils recommandés pour la JSD
JSD_THRESHOLDS = {
    'stable':  (0.0, 0.05),    # Pas de problème
    'warning': (0.05, 0.10),   # Surveillance
    'alert':   (0.10, 0.20),   # Action recommandée
    'critical': (0.20, 1.0),   # Modèle potentiellement inutilisable
}

def interpret_jsd(jsd_value):
    for level, (low, high) in JSD_THRESHOLDS.items():
        if low <= jsd_value < high:
            return level
    return 'critical'

# Test sur plusieurs features
np.random.seed(42)

features = {
    'age': {
        'ref': np.random.normal(40, 10, 2000),
        'prod_stable': np.random.normal(40, 10, 500),
        'prod_drifted': np.random.normal(50, 15, 500),
    },
    'revenue': {
        'ref': np.random.lognormal(8, 1, 2000),
        'prod_stable': np.random.lognormal(8, 1, 500),
        'prod_drifted': np.random.lognormal(8.5, 1.3, 500),
    },
    'score_credit': {
        'ref': np.random.beta(5, 2, 2000) * 850 + 300,
        'prod_stable': np.random.beta(5, 2, 500) * 850 + 300,
        'prod_drifted': np.random.beta(2, 5, 500) * 850 + 300,
    }
}

print("=== Rapport de Drift — Jensen-Shannon Divergence ===\n")
print(f"{'Feature':<15} {'JSD Stable':>12} {'Niveau':>10} | {'JSD Drifté':>12} {'Niveau':>10}")
print("-" * 65)

for feat_name, feat_data in features.items():
    jsd_stable = compute_jsd_for_numerical(feat_data['ref'], feat_data['prod_stable'])
    jsd_drifted = compute_jsd_for_numerical(feat_data['ref'], feat_data['prod_drifted'])

    level_stable = interpret_jsd(jsd_stable)
    level_drifted = interpret_jsd(jsd_drifted)

    print(f"{feat_name:<15} {jsd_stable:>12.4f} {level_stable:>10} | {jsd_drifted:>12.4f} {level_drifted:>10}")
```

### 3.4 Population Stability Index (PSI)

Le PSI est un indicateur très utilisé dans le secteur bancaire et financier. Il quantifie la différence entre deux distributions en pourcentage de population qui s'est déplacée entre les buckets.

**Interprétation standard :**
- PSI < 0.10 : Pas de changement significatif
- 0.10 ≤ PSI < 0.25 : Changement modéré — investigation recommandée
- PSI ≥ 0.25 : Changement majeur — modèle à reconsidérer

```python
import numpy as np
import pandas as pd

def calculate_psi(reference, production, n_buckets=10, epsilon=1e-6):
    """
    Calcule le Population Stability Index (PSI).

    PSI = Σ (% prod_i - % ref_i) * ln(% prod_i / % ref_i)

    Args:
        reference: données de référence (entraînement)
        production: données de production
        n_buckets: nombre de buckets (10 recommandé)
        epsilon: valeur minimale pour éviter log(0)

    Returns:
        dict avec PSI global et détail par bucket
    """
    # Définir les buckets sur les quantiles de la référence
    quantiles = np.linspace(0, 100, n_buckets + 1)
    breakpoints = np.percentile(reference, quantiles)
    breakpoints[0] = -np.inf
    breakpoints[-1] = np.inf

    # Calculer les proportions par bucket
    ref_counts = np.histogram(reference, bins=breakpoints)[0]
    prod_counts = np.histogram(production, bins=breakpoints)[0]

    ref_probs = ref_counts / len(reference)
    prod_probs = prod_counts / len(production)

    # Éviter les zéros
    ref_probs = np.maximum(ref_probs, epsilon)
    prod_probs = np.maximum(prod_probs, epsilon)

    # Calcul PSI par bucket
    psi_buckets = (prod_probs - ref_probs) * np.log(prod_probs / ref_probs)
    psi_total = psi_buckets.sum()

    # Créer un rapport détaillé
    report = pd.DataFrame({
        'bucket': range(1, n_buckets + 1),
        'lower': breakpoints[:-1],
        'upper': breakpoints[1:],
        'ref_count': ref_counts,
        'prod_count': prod_counts,
        'ref_pct': ref_probs * 100,
        'prod_pct': prod_probs * 100,
        'psi_contribution': psi_buckets,
    })

    return psi_total, report

def psi_interpretation(psi_value):
    if psi_value < 0.10:
        return "STABLE", "Aucune action requise"
    elif psi_value < 0.25:
        return "ATTENTION", "Investigation recommandée"
    else:
        return "CRITIQUE", "Modèle à reconsidérer — réentraînement probable"

# Application sur un exemple bancaire
np.random.seed(42)

# Scores de crédit — référence (entraînement)
ref_scores = np.concatenate([
    np.random.normal(650, 50, 600),   # Population principale
    np.random.normal(750, 30, 300),   # Bons payeurs
    np.random.normal(550, 40, 100),   # Risqués
])
ref_scores = np.clip(ref_scores, 300, 850)

# Production sans drift
prod_stable = np.concatenate([
    np.random.normal(650, 50, 200),
    np.random.normal(750, 30, 100),
    np.random.normal(550, 40, 30),
])
prod_stable = np.clip(prod_stable, 300, 850)

# Production avec drift (population plus risquée)
prod_drifted = np.concatenate([
    np.random.normal(600, 60, 180),   # Décalage vers le bas
    np.random.normal(720, 40, 70),    # Moins de bons payeurs
    np.random.normal(500, 50, 80),    # Plus de risqués
])
prod_drifted = np.clip(prod_drifted, 300, 850)

# Calcul PSI
psi_stable, report_stable = calculate_psi(ref_scores, prod_stable)
psi_drifted, report_drifted = calculate_psi(ref_scores, prod_drifted)

status_stable, message_stable = psi_interpretation(psi_stable)
status_drifted, message_drifted = psi_interpretation(psi_drifted)

print("=== Rapport PSI — Score de Crédit ===\n")
print(f"Production STABLE  : PSI = {psi_stable:.4f} | {status_stable} — {message_stable}")
print(f"Production DRIFTÉE : PSI = {psi_drifted:.4f} | {status_drifted} — {message_drifted}")

print("\n=== Détail par bucket (production driftée) ===")
print(report_drifted[['bucket', 'lower', 'upper', 'ref_pct', 'prod_pct', 'psi_contribution']].to_string(
    float_format=lambda x: f'{x:.2f}', index=False
))
```

---

## 4. Evidently AI — Rapports de Drift Automatisés

### 4.1 Installation et concepts de base

Evidently est la bibliothèque Python de référence pour le monitoring de modèles ML. Elle génère des rapports visuels interactifs et des suites de tests.

```bash
pip install evidently
# Ou avec toutes les dépendances
pip install "evidently[all]"
```

**Architecture d'Evidently :**
- **Report** : rapport visuel interactif (HTML)
- **TestSuite** : ensemble de tests avec pass/fail
- **Metrics** : métriques individuelles calculées
- **Presets** : ensembles de métriques préconfigurés

### 4.2 Rapport de Drift Basique

```python
import pandas as pd
import numpy as np
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, DataQualityPreset
from evidently.metrics import (
    DatasetDriftMetric,
    DataDriftTable,
    ColumnDriftMetric
)

# Génération d'un dataset de référence
np.random.seed(42)
X, y = make_classification(
    n_samples=3000,
    n_features=10,
    n_informative=6,
    n_redundant=2,
    random_state=42
)

feature_names = [f'feature_{i}' for i in range(10)]
df_reference = pd.DataFrame(X, columns=feature_names)
df_reference['target'] = y
df_reference['segment'] = np.random.choice(
    ['A', 'B', 'C', 'D'], size=3000, p=[0.4, 0.3, 0.2, 0.1]
)

# Simulation de données de production avec drift
# Features 0, 3, 7 ont drifté
df_production = df_reference.copy().iloc[:500]
drift_noise = np.zeros((500, 10))
drift_noise[:, 0] = np.random.normal(1.5, 0.5, 500)   # Shift feature_0
drift_noise[:, 3] = np.random.normal(-1.2, 0.8, 500)  # Shift feature_3
drift_noise[:, 7] = np.random.normal(0, 2.5, 500)     # Augmentation variance feature_7

df_production[feature_names] = df_production[feature_names].values + drift_noise

# Drift dans la variable catégorielle
df_production['segment'] = np.random.choice(
    ['A', 'B', 'C', 'D'], size=500, p=[0.60, 0.15, 0.15, 0.10]  # A domine maintenant
)

# Rapport avec le preset DataDrift
report = Report(metrics=[
    DataDriftPreset(),
])

report.run(
    reference_data=df_reference,
    current_data=df_production
)

# Sauvegarde du rapport HTML
report.save_html("drift_report.html")
print("Rapport sauvegardé : drift_report.html")

# Extraction des résultats en JSON
results = report.as_dict()
drift_summary = results['metrics'][0]['result']
print(f"\n=== Résumé du Drift ===")
print(f"Nombre de features avec drift : {drift_summary['number_of_drifted_columns']}")
print(f"Nombre total de features      : {drift_summary['number_of_columns']}")
print(f"Dataset drifté                : {drift_summary['dataset_drift']}")
print(f"Share of drifted columns      : {drift_summary['share_of_drifted_columns']:.1%}")
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Après exécution du code, ouvrir `drift_report.html` dans un navigateur et capturer : (1) la vue d'ensemble avec le tableau de bord montrant le nombre de features en drift, (2) le détail d'une feature driftée (feature_0 ou feature_3) avec les distributions superposées et la statistique de test, (3) le heatmap de corrélation comparant référence et production.
> **Expliquer :** Naviguer dans le rapport interactif à voix haute. Montrer comment Evidently sélectionne automatiquement le test statistique adapté (KS pour numérique, chi-carré pour catégoriel). Insister sur la lisibilité du rapport pour les parties prenantes non-techniques.

---

### 4.3 Rapport Détaillé par Colonne

```python
from evidently.metrics import ColumnDriftMetric, ColumnDistributionMetric
from evidently.metrics import ColumnSummaryMetric, ColumnCorrelationsMetric

# Rapport focalisé sur des colonnes spécifiques
detailed_report = Report(metrics=[
    # Drift global
    DatasetDriftMetric(threshold=0.5),  # Alert si > 50% des features driftent

    # Drift par colonne avec métriques détaillées
    ColumnDriftMetric(column_name='feature_0', stattest='ks'),
    ColumnDriftMetric(column_name='feature_3', stattest='ks'),
    ColumnDriftMetric(column_name='feature_7', stattest='ks'),
    ColumnDriftMetric(column_name='segment', stattest='chisquare'),

    # Distributions
    ColumnDistributionMetric(column_name='feature_0'),
    ColumnDistributionMetric(column_name='segment'),

    # Résumé statistique
    ColumnSummaryMetric(column_name='feature_0'),
])

detailed_report.run(
    reference_data=df_reference,
    current_data=df_production
)
detailed_report.save_html("drift_report_detailed.html")

# Extraire les statistiques pour chaque feature
results = detailed_report.as_dict()

print("=== Drift par Feature ===\n")
for metric_result in results['metrics']:
    if metric_result['metric'] == 'ColumnDriftMetric':
        col_name = metric_result['result']['column_name']
        drift_detected = metric_result['result']['drift_detected']
        drift_score = metric_result['result']['drift_score']
        stattest_name = metric_result['result']['stattest_name']

        status = "DRIFT" if drift_detected else "OK"
        print(f"  {col_name:<15} | {stattest_name:<12} | score={drift_score:.4f} | [{status}]")
```

### 4.4 Test Suite avec Alertes

```python
from evidently.test_suite import TestSuite
from evidently.tests import (
    TestNumberOfDriftedColumns,
    TestShareOfDriftedColumns,
    TestColumnDrift,
    TestNumberOfMissingValues,
    TestNumberOfOutRangeValues,
)

# Définir les critères d'alerte
test_suite = TestSuite(tests=[
    # Pas plus de 20% des features peuvent drifter
    TestShareOfDriftedColumns(lt=0.20),

    # Features critiques ne doivent pas drifter
    TestColumnDrift(column_name='feature_0', stattest='ks', stattest_threshold=0.05),
    TestColumnDrift(column_name='feature_3', stattest='ks', stattest_threshold=0.05),
    TestColumnDrift(column_name='segment', stattest='chisquare', stattest_threshold=0.05),

    # Qualité des données
    TestNumberOfMissingValues(lt=10),     # Moins de 10 valeurs manquantes
    TestNumberOfOutRangeValues(column_name='feature_0', lt=5),
])

test_suite.run(
    reference_data=df_reference,
    current_data=df_production
)
test_suite.save_html("drift_tests.html")

# Vérifier les résultats
results = test_suite.as_dict()
tests_passed = sum(1 for t in results['tests'] if t['status'] == 'SUCCESS')
tests_failed = sum(1 for t in results['tests'] if t['status'] == 'FAIL')
tests_warning = sum(1 for t in results['tests'] if t['status'] == 'WARNING')

print(f"=== Résultats des Tests ===")
print(f"Tests réussis  : {tests_passed}")
print(f"Tests échoués  : {tests_failed}")
print(f"Avertissements : {tests_warning}")
print()

for test in results['tests']:
    icon = "✓" if test['status'] == 'SUCCESS' else "✗"
    print(f"  {icon} [{test['status']:<8}] {test['name']}")
    if test.get('description'):
        print(f"           → {test['description']}")

# Déclencher une alerte si des tests échouent
if tests_failed > 0:
    print(f"\n🚨 ALERTE : {tests_failed} test(s) échoué(s) — action requise !")
    # Ici on pourrait envoyer un email, créer un ticket, etc.
```

---

## 5. Intégration avec MLflow

### 5.1 Logger les Métriques de Drift dans MLflow

MLflow permet de centraliser le suivi des métriques de drift dans le temps, comme on suit les métriques de performance d'un modèle.

```python
import mlflow
import mlflow.sklearn
import pandas as pd
import numpy as np
from datetime import datetime
from evidently.report import Report
from evidently.metrics import (
    DatasetDriftMetric,
    ColumnDriftMetric,
    DataDriftTable
)
from scipy import stats
from scipy.spatial.distance import jensenshannon

def compute_drift_metrics(reference_data, production_data, numerical_cols, categorical_cols):
    """
    Calcule toutes les métriques de drift et retourne un dictionnaire
    compatible avec mlflow.log_metrics().
    """
    metrics = {}

    # 1. KS Test pour chaque feature numérique
    for col in numerical_cols:
        ks_stat, ks_pvalue = stats.ks_2samp(
            reference_data[col].dropna(),
            production_data[col].dropna()
        )
        metrics[f"drift/ks_stat/{col}"] = float(ks_stat)
        metrics[f"drift/ks_pvalue/{col}"] = float(ks_pvalue)
        metrics[f"drift/ks_detected/{col}"] = float(ks_pvalue < 0.05)

    # 2. PSI pour chaque feature numérique
    for col in numerical_cols:
        ref = reference_data[col].dropna().values
        prod = production_data[col].dropna().values

        quantiles = np.linspace(0, 100, 11)
        breakpoints = np.percentile(ref, quantiles)
        breakpoints[0] = -np.inf
        breakpoints[-1] = np.inf

        ref_hist = np.histogram(ref, bins=breakpoints)[0]
        prod_hist = np.histogram(prod, bins=breakpoints)[0]

        ref_probs = np.maximum(ref_hist / len(ref), 1e-6)
        prod_probs = np.maximum(prod_hist / len(prod), 1e-6)

        psi = np.sum((prod_probs - ref_probs) * np.log(prod_probs / ref_probs))
        metrics[f"drift/psi/{col}"] = float(psi)

    # 3. JSD pour toutes les features
    for col in numerical_cols:
        ref_bins = np.histogram(reference_data[col].dropna(), bins=50, density=True)[0] + 1e-10
        prod_bins = np.histogram(production_data[col].dropna(), bins=50, density=True)[0] + 1e-10
        ref_bins /= ref_bins.sum()
        prod_bins /= prod_bins.sum()
        jsd = float(jensenshannon(ref_bins, prod_bins) ** 2)
        metrics[f"drift/jsd/{col}"] = jsd

    # 4. Chi-carré pour les features catégorielles
    for col in categorical_cols:
        ref_freq = reference_data[col].value_counts(normalize=True)
        prod_freq = production_data[col].value_counts(normalize=True)

        # Aligner les catégories
        all_cats = set(ref_freq.index) | set(prod_freq.index)
        ref_aligned = np.array([ref_freq.get(c, 0) for c in all_cats])
        prod_aligned = np.array([prod_freq.get(c, 0) for c in all_cats])

        # Normaliser et convertir en counts
        n_prod = len(production_data[col].dropna())
        expected = ref_aligned * n_prod
        observed = prod_aligned * n_prod

        # Éviter les cellules vides
        mask = expected > 0
        if mask.sum() > 1:
            chi2, p_val = stats.chisquare(
                np.maximum(observed[mask], 0.5),
                f_exp=np.maximum(expected[mask], 0.5)
            )
            metrics[f"drift/chi2_stat/{col}"] = float(chi2)
            metrics[f"drift/chi2_pvalue/{col}"] = float(p_val)
            metrics[f"drift/chi2_detected/{col}"] = float(p_val < 0.05)

    # 5. Métriques agrégées
    drift_cols = [v for k, v in metrics.items() if '/ks_detected/' in k]
    drift_cat_cols = [v for k, v in metrics.items() if '/chi2_detected/' in k]
    all_detected = drift_cols + drift_cat_cols

    if all_detected:
        metrics['drift/share_drifted'] = float(np.mean(all_detected))
        metrics['drift/n_drifted'] = float(np.sum(all_detected))
        metrics['drift/total_features'] = float(len(all_detected))

    # 6. Métriques de qualité
    metrics['quality/missing_rate'] = float(production_data.isnull().mean().mean())
    metrics['quality/n_rows'] = float(len(production_data))

    return metrics


# Pipeline de monitoring avec MLflow
def run_drift_monitoring(
    reference_data,
    production_data,
    model_name,
    numerical_cols,
    categorical_cols,
    experiment_name="drift_monitoring",
    generate_html=True
):
    """
    Exécute un run MLflow complet de monitoring de drift.
    Enregistre toutes les métriques et artéfacts.
    """
    mlflow.set_experiment(experiment_name)

    with mlflow.start_run(run_name=f"drift_check_{datetime.now().strftime('%Y%m%d_%H%M')}"):

        # Tagger le run
        mlflow.set_tag("model_name", model_name)
        mlflow.set_tag("monitoring_type", "data_drift")
        mlflow.set_tag("n_reference_samples", len(reference_data))
        mlflow.set_tag("n_production_samples", len(production_data))

        # Calculer et logger les métriques
        print("Calcul des métriques de drift...")
        drift_metrics = compute_drift_metrics(
            reference_data, production_data,
            numerical_cols, categorical_cols
        )

        mlflow.log_metrics(drift_metrics)
        print(f"✓ {len(drift_metrics)} métriques loggées")

        # Générer le rapport Evidently
        if generate_html:
            print("Génération du rapport Evidently...")
            report = Report(metrics=[DataDriftPreset()])
            report.run(
                reference_data=reference_data[numerical_cols + categorical_cols],
                current_data=production_data[numerical_cols + categorical_cols]
            )

            report_path = f"/tmp/drift_report_{datetime.now().strftime('%Y%m%d_%H%M')}.html"
            report.save_html(report_path)

            # Logger le rapport comme artefact MLflow
            mlflow.log_artifact(report_path, "drift_reports")
            print(f"✓ Rapport HTML loggé comme artefact")

        # Décision finale
        share_drifted = drift_metrics.get('drift/share_drifted', 0)
        if share_drifted > 0.30:
            mlflow.set_tag("alert_level", "CRITICAL")
            mlflow.set_tag("recommendation", "immediate_retraining")
        elif share_drifted > 0.15:
            mlflow.set_tag("alert_level", "WARNING")
            mlflow.set_tag("recommendation", "schedule_retraining")
        else:
            mlflow.set_tag("alert_level", "OK")
            mlflow.set_tag("recommendation", "continue_monitoring")

        print(f"\n=== Résultat Final ===")
        print(f"Share of drifted features : {share_drifted:.1%}")
        print(f"Alert level               : {mlflow.get_run(mlflow.active_run().info.run_id).data.tags.get('alert_level')}")

        return drift_metrics


# Utilisation
numerical_cols = [f'feature_{i}' for i in range(10)]
categorical_cols = ['segment']

metrics_result = run_drift_monitoring(
    reference_data=df_reference,
    production_data=df_production,
    model_name="credit_scoring_v2",
    numerical_cols=numerical_cols,
    categorical_cols=categorical_cols,
    experiment_name="credit_model_monitoring"
)
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Lancer `mlflow ui` en terminal et ouvrir `http://localhost:5000`. Capturer : (1) la liste des runs de l'expérience `credit_model_monitoring` avec les tags alert_level visibles, (2) le détail d'un run avec toutes les métriques drift/* et quality/* dans le tableau de métriques, (3) l'onglet Artifacts montrant le rapport HTML Evidently loggé.
> **Expliquer :** Montrer comment MLflow permet de suivre l'évolution du drift dans le temps en comparant plusieurs runs. Expliquer l'intérêt de centraliser les métriques de drift au même endroit que les métriques de performance du modèle.

---

### 5.2 Tracking du Drift dans le Temps

```python
import mlflow
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def simulate_production_batch(reference_data, batch_date, drift_intensity=0.0):
    """
    Simule un batch de production avec un niveau de drift configurable.
    drift_intensity : 0.0 = pas de drift, 1.0 = drift maximal
    """
    n_samples = np.random.randint(200, 400)
    batch = reference_data.sample(n=n_samples, replace=True).copy()

    numerical_cols = [c for c in reference_data.columns if c.startswith('feature_')]

    # Appliquer le drift progressivement
    for i, col in enumerate(numerical_cols[:5]):  # Drift sur les 5 premières features
        shift = drift_intensity * np.random.normal(1.2, 0.3)
        noise_factor = 1 + drift_intensity * 0.5
        batch[col] = batch[col] + shift + np.random.normal(0, noise_factor, n_samples)

    batch['batch_date'] = batch_date
    return batch


def run_weekly_monitoring(reference_data, n_weeks=8, experiment_name="weekly_drift"):
    """
    Simule 8 semaines de monitoring avec drift progressif.
    """
    mlflow.set_experiment(experiment_name)
    numerical_cols = [c for c in reference_data.columns if c.startswith('feature_')]
    categorical_cols = ['segment']

    start_date = datetime(2025, 1, 1)
    monitoring_history = []

    for week in range(n_weeks):
        batch_date = start_date + timedelta(weeks=week)
        # Drift croissant à partir de la semaine 4
        drift_intensity = max(0.0, (week - 3) * 0.15)

        # Simuler le batch de production
        production_batch = simulate_production_batch(
            reference_data,
            batch_date=batch_date.strftime('%Y-%m-%d'),
            drift_intensity=drift_intensity
        )

        with mlflow.start_run(run_name=f"week_{week+1:02d}_{batch_date.strftime('%Y%m%d')}"):
            mlflow.set_tag("week", week + 1)
            mlflow.set_tag("batch_date", batch_date.strftime('%Y-%m-%d'))

            # Calculer métriques de drift (simplifié)
            from scipy import stats
            ks_scores = {}
            for col in numerical_cols:
                ks_stat, ks_pvalue = stats.ks_2samp(
                    reference_data[col], production_batch[col]
                )
                ks_scores[col] = ks_stat
                mlflow.log_metric(f"drift/ks_{col}", ks_stat, step=week)
                mlflow.log_metric(f"drift/pvalue_{col}", ks_pvalue, step=week)

            # Métriques agrégées
            n_drifted = sum(1 for v in ks_scores.values() if v > 0.1)
            share_drifted = n_drifted / len(numerical_cols)
            avg_ks = np.mean(list(ks_scores.values()))

            mlflow.log_metric("drift/n_drifted_features", n_drifted, step=week)
            mlflow.log_metric("drift/share_drifted", share_drifted, step=week)
            mlflow.log_metric("drift/avg_ks_score", avg_ks, step=week)

            # Simuler une métrique de performance (dégradation corrélée au drift)
            simulated_accuracy = 0.92 - drift_intensity * 0.15 + np.random.normal(0, 0.01)
            mlflow.log_metric("model/accuracy", simulated_accuracy, step=week)

            monitoring_history.append({
                'week': week + 1,
                'date': batch_date.strftime('%Y-%m-%d'),
                'drift_intensity': drift_intensity,
                'n_drifted': n_drifted,
                'share_drifted': share_drifted,
                'avg_ks': avg_ks,
                'accuracy': simulated_accuracy
            })

            print(f"  Semaine {week+1:2d} ({batch_date.strftime('%Y-%m-%d')}) | "
                  f"Drift: {share_drifted:.0%} | KS moyen: {avg_ks:.3f} | "
                  f"Accuracy: {simulated_accuracy:.3f}")

    return pd.DataFrame(monitoring_history)

print("=== Simulation de Monitoring Hebdomadaire ===\n")
history_df = run_weekly_monitoring(df_reference, n_weeks=8)

print("\n=== Tableau de Bord ===")
print(history_df[['week', 'date', 'share_drifted', 'avg_ks', 'accuracy']].to_string(
    float_format=lambda x: f'{x:.3f}', index=False
))
```

---

## 6. Monitoring en Production

### 6.1 Architecture d'un Système de Monitoring

Un système de monitoring de drift en production comprend plusieurs composants :

```
Flux de Données
     │
     ▼
┌─────────────────┐
│  Data Ingestion  │ ← Kafka / API / Batch
└────────┬────────┘
         │
         ▼
┌─────────────────────┐
│  Feature Store /    │ ← Sauvegarde des données de prod
│  Data Warehouse     │   pour analyse rétrospective
└────────┬────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│               Drift Detection Pipeline               │
│                                                      │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │ Statistical │  │  Evidently   │  │  MLflow    │ │
│  │   Tests     │  │   Reports    │  │  Tracking  │ │
│  └─────────────┘  └──────────────┘  └────────────┘ │
└──────────────────────────┬──────────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │   Alerting Engine      │
              │  (seuils configurés)   │
              └────────────┬───────────┘
                           │
              ┌────────────┴───────────┐
              │                        │
              ▼                        ▼
    ┌──────────────────┐    ┌──────────────────────┐
    │  Notification    │    │  Retraining Trigger  │
    │  (Slack/Email)   │    │  (CI/CD Pipeline)    │
    └──────────────────┘    └──────────────────────┘
```

### 6.2 Pipeline de Monitoring Automatisé

```python
import pandas as pd
import numpy as np
import json
import os
import logging
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Callable
from scipy import stats

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('DriftMonitor')


@dataclass
class DriftThresholds:
    """Seuils d'alerte pour la détection de drift."""
    ks_pvalue_threshold: float = 0.05       # Seuil p-value KS test
    psi_warning: float = 0.10               # PSI = avertissement
    psi_critical: float = 0.25              # PSI = critique
    jsd_warning: float = 0.05              # JSD = avertissement
    jsd_critical: float = 0.10             # JSD = critique
    max_share_drifted: float = 0.20         # Max 20% des features
    max_missing_rate: float = 0.05          # Max 5% de valeurs manquantes
    min_batch_size: int = 100               # Taille minimum du batch


@dataclass
class DriftAlert:
    """Représente une alerte de drift."""
    timestamp: str
    level: str  # 'info', 'warning', 'critical'
    feature: str
    metric: str
    value: float
    threshold: float
    message: str


class DriftMonitor:
    """
    Système de monitoring de drift en production.

    Usage:
        monitor = DriftMonitor(reference_data, thresholds)
        monitor.add_alert_handler(send_slack_notification)
        results = monitor.check(production_batch)
        if results['alert_level'] == 'critical':
            trigger_retraining()
    """

    def __init__(
        self,
        reference_data: pd.DataFrame,
        numerical_cols: List[str],
        categorical_cols: List[str],
        thresholds: Optional[DriftThresholds] = None,
        model_name: str = "model",
        output_dir: str = "/tmp/drift_monitoring"
    ):
        self.reference = reference_data
        self.numerical_cols = numerical_cols
        self.categorical_cols = categorical_cols
        self.thresholds = thresholds or DriftThresholds()
        self.model_name = model_name
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.alert_handlers: List[Callable] = []
        self._check_history = []

        logger.info(f"DriftMonitor initialisé : {model_name}")
        logger.info(f"  {len(numerical_cols)} features numériques, {len(categorical_cols)} catégorielles")

    def add_alert_handler(self, handler: Callable):
        """Ajoute un handler pour les alertes (email, Slack, etc.)"""
        self.alert_handlers.append(handler)

    def _ks_test(self, col: str, prod_data: pd.Series) -> Dict:
        ref_data = self.reference[col].dropna()
        prod_clean = prod_data.dropna()

        if len(prod_clean) < 30:
            return {'error': 'Pas assez de données'}

        ks_stat, ks_pvalue = stats.ks_2samp(ref_data, prod_clean)
        drift_detected = ks_pvalue < self.thresholds.ks_pvalue_threshold

        return {
            'test': 'ks',
            'statistic': float(ks_stat),
            'pvalue': float(ks_pvalue),
            'drift_detected': drift_detected,
            'threshold': self.thresholds.ks_pvalue_threshold
        }

    def _psi(self, col: str, prod_data: pd.Series, n_buckets: int = 10) -> Dict:
        ref = self.reference[col].dropna().values
        prod = prod_data.dropna().values

        if len(prod) < self.thresholds.min_batch_size:
            return {'error': 'Batch trop petit'}

        quantiles = np.linspace(0, 100, n_buckets + 1)
        breakpoints = np.percentile(ref, quantiles)
        breakpoints[0] = -np.inf
        breakpoints[-1] = np.inf

        ref_probs = np.maximum(
            np.histogram(ref, bins=breakpoints)[0] / len(ref), 1e-6
        )
        prod_probs = np.maximum(
            np.histogram(prod, bins=breakpoints)[0] / len(prod), 1e-6
        )

        psi = float(np.sum((prod_probs - ref_probs) * np.log(prod_probs / ref_probs)))

        if psi >= self.thresholds.psi_critical:
            level = 'critical'
        elif psi >= self.thresholds.psi_warning:
            level = 'warning'
        else:
            level = 'ok'

        return {'test': 'psi', 'value': psi, 'level': level}

    def _chi2_test(self, col: str, prod_data: pd.Series) -> Dict:
        ref_freq = self.reference[col].value_counts(normalize=True)
        prod_freq = prod_data.value_counts(normalize=True)

        all_cats = set(ref_freq.index) | set(prod_freq.index)
        n_prod = len(prod_data.dropna())

        expected = np.array([ref_freq.get(c, 1e-6) * n_prod for c in all_cats])
        observed = np.array([prod_freq.get(c, 0) * n_prod for c in all_cats])

        expected = np.maximum(expected, 0.5)
        observed = np.maximum(observed, 0)

        try:
            chi2, pvalue = stats.chisquare(observed, f_exp=expected)
            return {
                'test': 'chi2',
                'statistic': float(chi2),
                'pvalue': float(pvalue),
                'drift_detected': pvalue < self.thresholds.ks_pvalue_threshold
            }
        except Exception as e:
            return {'error': str(e)}

    def check(self, production_data: pd.DataFrame, batch_id: Optional[str] = None) -> Dict:
        """
        Effectue une vérification complète du drift sur un batch de production.

        Returns:
            dict avec 'alert_level', 'alerts', 'metrics', 'summary'
        """
        batch_id = batch_id or datetime.now().strftime('%Y%m%d_%H%M%S')
        timestamp = datetime.now().isoformat()
        alerts = []
        metrics = {}

        logger.info(f"Vérification drift — batch {batch_id} ({len(production_data)} lignes)")

        # 1. Vérification de la qualité des données
        missing_rate = production_data.isnull().mean().mean()
        metrics['missing_rate'] = float(missing_rate)

        if missing_rate > self.thresholds.max_missing_rate:
            alert = DriftAlert(
                timestamp=timestamp,
                level='warning',
                feature='all',
                metric='missing_rate',
                value=missing_rate,
                threshold=self.thresholds.max_missing_rate,
                message=f"Taux de valeurs manquantes élevé : {missing_rate:.1%}"
            )
            alerts.append(alert)

        # 2. Vérification de la taille du batch
        if len(production_data) < self.thresholds.min_batch_size:
            alert = DriftAlert(
                timestamp=timestamp,
                level='warning',
                feature='dataset',
                metric='batch_size',
                value=len(production_data),
                threshold=self.thresholds.min_batch_size,
                message=f"Batch trop petit : {len(production_data)} < {self.thresholds.min_batch_size}"
            )
            alerts.append(alert)
            logger.warning(alert.message)

        # 3. Tests sur les features numériques
        n_drifted = 0
        for col in self.numerical_cols:
            if col not in production_data.columns:
                logger.warning(f"Feature manquante en production : {col}")
                continue

            ks_result = self._ks_test(col, production_data[col])
            psi_result = self._psi(col, production_data[col])

            metrics[f'ks_stat_{col}'] = ks_result.get('statistic', -1)
            metrics[f'ks_pvalue_{col}'] = ks_result.get('pvalue', -1)
            metrics[f'psi_{col}'] = psi_result.get('value', -1)

            if ks_result.get('drift_detected'):
                n_drifted += 1
                level = 'critical' if psi_result.get('level') == 'critical' else 'warning'
                alert = DriftAlert(
                    timestamp=timestamp,
                    level=level,
                    feature=col,
                    metric='ks_test',
                    value=ks_result.get('statistic', 0),
                    threshold=self.thresholds.ks_pvalue_threshold,
                    message=f"Drift détecté sur {col} : KS={ks_result.get('statistic', 0):.3f}, "
                            f"p={ks_result.get('pvalue', 0):.4f}, PSI={psi_result.get('value', 0):.3f}"
                )
                alerts.append(alert)

        # 4. Tests sur les features catégorielles
        for col in self.categorical_cols:
            if col not in production_data.columns:
                continue

            chi2_result = self._chi2_test(col, production_data[col])
            metrics[f'chi2_stat_{col}'] = chi2_result.get('statistic', -1)
            metrics[f'chi2_pvalue_{col}'] = chi2_result.get('pvalue', -1)

            if chi2_result.get('drift_detected'):
                n_drifted += 1
                alert = DriftAlert(
                    timestamp=timestamp,
                    level='warning',
                    feature=col,
                    metric='chi2_test',
                    value=chi2_result.get('statistic', 0),
                    threshold=self.thresholds.ks_pvalue_threshold,
                    message=f"Drift catégoriel sur {col} : χ²={chi2_result.get('statistic', 0):.3f}"
                )
                alerts.append(alert)

        # 5. Décision finale
        total_features = len(self.numerical_cols) + len(self.categorical_cols)
        share_drifted = n_drifted / max(total_features, 1)
        metrics['n_drifted_features'] = n_drifted
        metrics['share_drifted'] = share_drifted

        has_critical = any(a.level == 'critical' for a in alerts)
        if has_critical or share_drifted > self.thresholds.max_share_drifted:
            alert_level = 'critical'
        elif len(alerts) > 0:
            alert_level = 'warning'
        else:
            alert_level = 'ok'

        result = {
            'batch_id': batch_id,
            'timestamp': timestamp,
            'alert_level': alert_level,
            'n_alerts': len(alerts),
            'n_drifted_features': n_drifted,
            'share_drifted': share_drifted,
            'alerts': [asdict(a) for a in alerts],
            'metrics': metrics
        }

        # Sauvegarder le résultat
        report_path = self.output_dir / f"drift_check_{batch_id}.json"
        with open(report_path, 'w') as f:
            json.dump(result, f, indent=2, default=str)

        # Déclencher les handlers d'alerte
        if alert_level in ('warning', 'critical'):
            for handler in self.alert_handlers:
                try:
                    handler(result)
                except Exception as e:
                    logger.error(f"Erreur dans le handler d'alerte : {e}")

        self._check_history.append(result)
        logger.info(f"Résultat : {alert_level.upper()} — {n_drifted}/{total_features} features driftées")

        return result


# Exemple de handler d'alerte
def log_alert(result: Dict):
    """Handler simple : log l'alerte."""
    level = result['alert_level']
    n_drifted = result['n_drifted_features']
    share = result['share_drifted']

    if level == 'critical':
        logger.critical(f"[ALERTE CRITIQUE] {n_drifted} features driftées ({share:.0%})")
    elif level == 'warning':
        logger.warning(f"[AVERTISSEMENT] {n_drifted} features driftées ({share:.0%})")


def slack_alert_handler(result: Dict):
    """
    Handler pour envoyer une alerte Slack.
    En production, utiliser requests.post() vers le webhook Slack.
    """
    level = result['alert_level']
    icons = {'ok': '✅', 'warning': '⚠️', 'critical': '🚨'}

    message = {
        "text": f"{icons.get(level, '❓')} *Drift Monitor — {level.upper()}*",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"*Batch :* `{result['batch_id']}`\n"
                        f"*Niveau :* {level.upper()}\n"
                        f"*Features driftées :* {result['n_drifted_features']} ({result['share_drifted']:.0%})\n"
                    )
                }
            }
        ]
    }

    # En production :
    # import requests
    # requests.post(SLACK_WEBHOOK_URL, json=message)
    print(f"[SLACK SIMULATION] Message envoyé : {message['text']}")


# Test du système
monitor = DriftMonitor(
    reference_data=df_reference,
    numerical_cols=numerical_cols,
    categorical_cols=categorical_cols,
    thresholds=DriftThresholds(
        ks_pvalue_threshold=0.05,
        psi_warning=0.10,
        psi_critical=0.25,
        max_share_drifted=0.20
    ),
    model_name="credit_scoring_v2"
)

monitor.add_alert_handler(log_alert)
monitor.add_alert_handler(slack_alert_handler)

# Vérification sur batch normal
print("=== Batch Normal (pas de drift) ===")
result_normal = monitor.check(
    production_data=df_reference.sample(300),
    batch_id="batch_2025_01_01"
)
print(f"Alert level : {result_normal['alert_level']}")
print(f"N alertes   : {result_normal['n_alerts']}")

print()

# Vérification sur batch avec drift
print("=== Batch Drifté ===")
result_drifted = monitor.check(
    production_data=df_production,
    batch_id="batch_2025_07_15"
)
print(f"Alert level : {result_drifted['alert_level']}")
print(f"N alertes   : {result_drifted['n_alerts']}")
if result_drifted['alerts']:
    print("\nDétail des alertes :")
    for alert in result_drifted['alerts'][:3]:
        print(f"  [{alert['level'].upper()}] {alert['message']}")
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Exécuter le code de monitoring en montrant les deux scénarios : (1) batch normal avec `alert_level: ok` et aucun log d'alerte, (2) batch drifté avec les messages de log WARNING/CRITICAL dans le terminal, les messages Slack simulés, et le fichier JSON généré dans `/tmp/drift_monitoring/`. Ouvrir le fichier JSON et montrer sa structure.
> **Expliquer :** Expliquer l'architecture du handler d'alerte et comment on brancherait un vrai webhook Slack ou un email. Montrer que le fichier JSON peut servir de base de données d'historique des checks.

---

### 6.3 Drift Check Planifié avec Schedule

```python
import schedule
import time
import threading
from datetime import datetime

def get_latest_production_batch(data_source="warehouse") -> pd.DataFrame:
    """
    Récupère le dernier batch de données de production.
    En production : connexion à une base de données, API, S3, etc.
    """
    # Simulation : on retourne un batch aléatoire
    np.random.seed(datetime.now().minute)
    n_samples = np.random.randint(150, 400)
    batch = df_reference.sample(n=n_samples, replace=True).copy()

    # Drift aléatoire pour la simulation
    if np.random.random() > 0.7:  # 30% de chance de drift
        for col in numerical_cols[:3]:
            batch[col] += np.random.normal(1.0, 0.5, n_samples)

    return batch


def scheduled_drift_check():
    """Fonction exécutée selon le planning."""
    logger.info("=== Drift Check Planifié ===")
    try:
        batch = get_latest_production_batch()
        batch_id = f"scheduled_{datetime.now().strftime('%Y%m%d_%H%M')}"

        result = monitor.check(production_data=batch, batch_id=batch_id)

        # Logger dans MLflow
        with mlflow.start_run(
            experiment_id=mlflow.get_experiment_by_name("credit_model_monitoring").experiment_id,
            run_name=batch_id
        ):
            mlflow.log_metrics(result['metrics'])
            mlflow.set_tag("alert_level", result['alert_level'])
            mlflow.set_tag("scheduled", "true")

        # Trigger retraining si critique
        if result['alert_level'] == 'critical':
            logger.critical("RETRAINING TRIGGER : drift critique détecté")
            trigger_model_retraining(result)

    except Exception as e:
        logger.error(f"Erreur lors du drift check planifié : {e}")


def trigger_model_retraining(drift_result: Dict):
    """
    Déclenche le pipeline de réentraînement.
    En production : appel à un pipeline CI/CD, Airflow DAG, etc.
    """
    logger.info("Déclenchement du pipeline de réentraînement...")
    print(f"""
    ╔══════════════════════════════════════════════════════════╗
    ║           RETRAINING PIPELINE TRIGGERED                  ║
    ║                                                          ║
    ║  Batch ID    : {drift_result['batch_id']:<40}  ║
    ║  Alert Level : {drift_result['alert_level']:<40}  ║
    ║  Drifted     : {drift_result['n_drifted_features']}/{len(numerical_cols)+len(categorical_cols):<40}  ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    # En production :
    # - Déclencher un DAG Airflow : airflow_client.trigger_dag('model_retraining')
    # - Appeler une API CI/CD : requests.post(JENKINS_URL, json={'job': 'retrain_model'})
    # - Créer un ticket JIRA automatiquement
    # - Publier un message dans une file Kafka


# Configuration du planning
# (pour un environnement de production, utiliser Airflow, Cron, ou un scheduler dédié)
print("Configuration du monitoring planifié...")
print("  → Vérification toutes les heures")
print("  → Rapport complet tous les jours à 8h")
print("  → Alerte immédiate si drift critique\n")

# schedule.every().hour.do(scheduled_drift_check)
# schedule.every().day.at("08:00").do(generate_daily_report)

# Simulation d'une seule exécution
scheduled_drift_check()
```

---

## 7. Exemples Pratiques avec Scikit-learn

### 7.1 Pipeline Complet — Détection de Fraude

```python
import pandas as pd
import numpy as np
from sklearn.datasets import make_classification
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, roc_auc_score
import mlflow
import mlflow.sklearn
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset
from scipy import stats

# 1. Génération du dataset de fraude
np.random.seed(42)

def generate_fraud_dataset(n_samples=5000, fraud_rate=0.05, drift=False):
    """Génère un dataset simulé de détection de fraude."""

    n_fraud = int(n_samples * fraud_rate)
    n_legit = n_samples - n_fraud

    # Features légitimes
    legit = {
        'montant': np.random.lognormal(4.5, 1.2, n_legit),
        'heure': np.random.choice(range(24), n_legit, p=np.array([
            0.01, 0.01, 0.01, 0.01, 0.01, 0.02, 0.04, 0.06,
            0.07, 0.07, 0.07, 0.07, 0.07, 0.07, 0.06, 0.06,
            0.06, 0.06, 0.05, 0.05, 0.04, 0.03, 0.02, 0.02
        ])),
        'nb_transactions_24h': np.random.poisson(3, n_legit),
        'distance_km': np.random.exponential(20, n_legit),
        'score_historique': np.random.beta(8, 2, n_legit) * 100,
    }

    # Features frauduleuses (patterns différents)
    fraud_shift = 2.0 if drift else 0.0  # Nouveaux patterns de fraude
    fraud = {
        'montant': np.random.lognormal(5.5 + fraud_shift * 0.5, 1.8, n_fraud),
        'heure': np.random.choice(range(24), n_fraud, p=np.ones(24) / 24),  # Uniforme
        'nb_transactions_24h': np.random.poisson(8, n_fraud),
        'distance_km': np.random.exponential(200 + fraud_shift * 50, n_fraud),
        'score_historique': np.random.beta(2, 8, n_fraud) * 100,
    }

    # Concaténation
    data = pd.DataFrame({
        col: np.concatenate([legit[col], fraud[col]])
        for col in legit.keys()
    })
    data['is_fraud'] = [0] * n_legit + [1] * n_fraud

    # Ajout de features catégorielles
    data['canal'] = np.where(
        data['is_fraud'] == 0,
        np.random.choice(['web', 'mobile', 'pos', 'atm'], n_samples, p=[0.4, 0.3, 0.2, 0.1]),
        np.random.choice(['web', 'mobile', 'pos', 'atm'], n_samples, p=[0.6, 0.3, 0.05, 0.05])
    )
    data['pays'] = np.where(
        data['is_fraud'] == 0,
        np.random.choice(['FR', 'DE', 'ES', 'IT'], n_samples, p=[0.6, 0.2, 0.1, 0.1]),
        np.random.choice(['FR', 'DE', 'ES', 'IT', 'RO', 'NG'], n_samples, p=[0.3, 0.1, 0.1, 0.1, 0.2, 0.2])
    )

    return data.sample(frac=1, random_state=42).reset_index(drop=True)


# 2. Entraînement du modèle
print("=== Entraînement du Modèle de Détection de Fraude ===\n")

train_data = generate_fraud_dataset(n_samples=5000, fraud_rate=0.05, drift=False)
X = train_data.drop(columns=['is_fraud', 'canal', 'pays'])
y = train_data['is_fraud']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

model = GradientBoostingClassifier(n_estimators=100, max_depth=4, random_state=42)
model.fit(X_train_scaled, y_train)

# Métriques d'entraînement
y_pred = model.predict(X_test_scaled)
y_proba = model.predict_proba(X_test_scaled)[:, 1]
auc = roc_auc_score(y_test, y_proba)

print(f"AUC-ROC sur test : {auc:.4f}")
print(f"\nRapport de classification :")
print(classification_report(y_test, y_pred, target_names=['Légitime', 'Fraude']))

# 3. Sauvegarder le modèle et les données de référence
with mlflow.start_run(run_name="fraud_model_v1") as run:
    mlflow.log_param("n_estimators", 100)
    mlflow.log_param("max_depth", 4)
    mlflow.log_metric("auc_roc", auc)
    mlflow.sklearn.log_model(model, "model")
    mlflow.log_text(
        train_data.describe().to_string(),
        "reference_stats.txt"
    )
    model_run_id = run.info.run_id
    print(f"\nModèle enregistré — Run ID : {model_run_id}")


# 4. Simulation de production avec drift (nouveaux types de fraude)
print("\n=== Simulation Production (6 mois après) ===\n")

prod_data_stable = generate_fraud_dataset(n_samples=500, fraud_rate=0.05, drift=False)
prod_data_drifted = generate_fraud_dataset(n_samples=500, fraud_rate=0.08, drift=True)

numerical_feat = ['montant', 'heure', 'nb_transactions_24h', 'distance_km', 'score_historique']
categorical_feat = ['canal', 'pays']

# Comparer les performances
for dataset_name, prod_data in [("Stable", prod_data_stable), ("Drifté", prod_data_drifted)]:
    X_prod = prod_data[numerical_feat]
    y_prod = prod_data['is_fraud']
    X_prod_scaled = scaler.transform(X_prod)
    y_pred_prod = model.predict(X_prod_scaled)
    y_proba_prod = model.predict_proba(X_prod_scaled)[:, 1]

    auc_prod = roc_auc_score(y_prod, y_proba_prod)

    print(f"AUC-ROC en production ({dataset_name}) : {auc_prod:.4f} {'(-{:.4f})'.format(auc - auc_prod) if auc > auc_prod else ''}")

    # Test KS sur les features critiques
    print(f"\nTest KS sur features ({dataset_name}) :")
    for feat in numerical_feat:
        ks_stat, ks_pvalue = stats.ks_2samp(train_data[feat], prod_data[feat])
        flag = " <-- DRIFT" if ks_pvalue < 0.05 else ""
        print(f"  {feat:<25} : KS={ks_stat:.3f}, p={ks_pvalue:.4f}{flag}")
    print()
```

### 7.2 Rapport de Drift Complet sur le Dataset de Fraude

```python
from evidently.report import Report
from evidently.metrics import (
    DataDriftTable,
    DatasetDriftMetric,
    ColumnDriftMetric,
    DatasetMissingValuesSummaryMetric,
)
from evidently.metric_preset import DataDriftPreset, DataQualityPreset

# Rapport complet
fraud_report = Report(metrics=[
    DataDriftPreset(),
    DataQualityPreset(),
])

# Colonnes à analyser (sans la target)
cols_to_monitor = numerical_feat + categorical_feat

fraud_report.run(
    reference_data=train_data[cols_to_monitor],
    current_data=prod_data_drifted[cols_to_monitor],
    column_mapping=None
)

fraud_report.save_html("fraud_drift_report.html")

# Extraction des résultats
fraud_results = fraud_report.as_dict()

print("=== Rapport Evidently — Dataset de Fraude ===\n")
for metric_result in fraud_results['metrics']:
    metric_name = metric_result['metric']
    if metric_name == 'DatasetDriftMetric':
        r = metric_result['result']
        print(f"Dataset Drift Détecté  : {r['dataset_drift']}")
        print(f"Features driftées      : {r['number_of_drifted_columns']} / {r['number_of_columns']}")
        print(f"Share of drift         : {r['share_of_drifted_columns']:.1%}")
    elif metric_name == 'ColumnDriftMetric':
        r = metric_result['result']
        status = "DRIFT" if r.get('drift_detected') else "OK"
        print(f"  {r['column_name']:<25} : [{status}] score={r.get('drift_score', 'N/A')}")
```

---

## 8. Réponse au Drift Détecté

### 8.1 Arbre de Décision

Quand une alerte de drift est déclenchée, la première étape est de **comprendre la cause** avant d'agir.

```
Drift Détecté
     │
     ▼
┌─────────────────────────────────┐
│ 1. Vérifier la qualité pipeline │
│    - Bug dans l'ingestion ?     │
│    - Schéma changé ?            │
│    - Encodage différent ?       │
└───────────────┬─────────────────┘
                │ Pipeline OK
                ▼
┌─────────────────────────────────┐
│ 2. Identifier le type de drift  │
│    - Features d'entrée ?        │
│    - Distribution des labels ?  │
│    - Relation X → y ?           │
└───────────────┬─────────────────┘
                │
                ▼
┌─────────────────────────────────┐
│ 3. Évaluer l'impact sur les     │
│    métriques métier             │
│    - Performance dégradée ?     │
│    - Impact business mesurable ?│
└───────────────┬─────────────────┘
                │
    ┌───────────┴────────────┐
    │                        │
    ▼                        ▼
Impact fort            Impact faible
    │                        │
    ▼                        ▼
Réentraînement       Surveillance accrue
Immédiat             + analyse
```

### 8.2 Stratégies de Réentraînement

```python
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score
import mlflow
import mlflow.sklearn

class RetrainingStrategy:
    """Stratégies de réentraînement déclenchées par le drift."""

    def __init__(self, model, scaler, reference_data, target_col='is_fraud'):
        self.model = model
        self.scaler = scaler
        self.reference_data = reference_data
        self.target_col = target_col
        self.numerical_cols = ['montant', 'heure', 'nb_transactions_24h', 'distance_km', 'score_historique']

    def full_retraining(self, new_data: pd.DataFrame, experiment_name="retraining"):
        """
        Stratégie 1 : Réentraînement complet sur toutes les données disponibles.
        Utiliser quand : drift important, nouvelle population stable détectée.
        """
        print("Stratégie : Réentraînement Complet")
        combined_data = pd.concat([self.reference_data, new_data], ignore_index=True)
        return self._train_and_log(combined_data, "full_retrain", experiment_name)

    def incremental_retraining(self, new_data: pd.DataFrame,
                               new_data_weight: float = 0.7, experiment_name="retraining"):
        """
        Stratégie 2 : Réentraînement avec pondération des nouvelles données.
        Utiliser quand : drift graduel, nouvelles données plus représentatives.
        new_data_weight : poids relatif des nouvelles données (0.5 = égal, 0.7 = favorise nouvelles)
        """
        print(f"Stratégie : Réentraînement Incrémental (poids nouvelles données: {new_data_weight})")

        n_ref = len(self.reference_data)
        n_new = len(new_data)

        # Sur-échantillonner les nouvelles données selon le poids
        ref_weight = 1.0 - new_data_weight
        target_n_new = int(n_ref * new_data_weight / ref_weight) if ref_weight > 0 else n_new * 3

        new_data_resampled = new_data.sample(
            n=min(target_n_new, n_new * 5),
            replace=True,
            random_state=42
        )
        combined = pd.concat([self.reference_data, new_data_resampled], ignore_index=True)
        return self._train_and_log(combined, f"incremental_retrain_w{new_data_weight}", experiment_name)

    def window_retraining(self, new_data: pd.DataFrame,
                          window_size: int = 2000, experiment_name="retraining"):
        """
        Stratégie 3 : Réentraînement sur une fenêtre glissante.
        Utiliser quand : drift continu, les données récentes sont les plus pertinentes.
        """
        print(f"Stratégie : Fenêtre Glissante ({window_size} échantillons)")
        combined = pd.concat([self.reference_data, new_data], ignore_index=True)
        windowed = combined.tail(window_size)
        return self._train_and_log(windowed, f"window_retrain_{window_size}", experiment_name)

    def _train_and_log(self, data: pd.DataFrame, run_name: str, experiment_name: str):
        """Pipeline d'entraînement commun."""
        mlflow.set_experiment(experiment_name)

        X = data[self.numerical_cols]
        y = data[self.target_col]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, stratify=y, random_state=42
        )

        new_scaler = StandardScaler()
        X_train_scaled = new_scaler.fit_transform(X_train)
        X_test_scaled = new_scaler.transform(X_test)

        new_model = GradientBoostingClassifier(
            n_estimators=100, max_depth=4, random_state=42
        )
        new_model.fit(X_train_scaled, y_train)

        y_proba = new_model.predict_proba(X_test_scaled)[:, 1]
        auc = roc_auc_score(y_test, y_proba)

        with mlflow.start_run(run_name=run_name):
            mlflow.log_param("n_train_samples", len(X_train))
            mlflow.log_param("strategy", run_name)
            mlflow.log_metric("auc_roc", auc)
            mlflow.sklearn.log_model(new_model, "model")

        print(f"  AUC-ROC (nouveau modèle) : {auc:.4f}")
        return new_model, new_scaler, auc


# Test des stratégies
print("=== Test des Stratégies de Réentraînement ===\n")

strategy = RetrainingStrategy(model, scaler, train_data)

# Nouvelles données labelisées (simulation : on a collecté 6 mois de prod avec labels)
new_labeled_data = generate_fraud_dataset(n_samples=1000, fraud_rate=0.08, drift=True)

for strategy_fn, kwargs in [
    (strategy.full_retraining, {}),
    (strategy.incremental_retraining, {'new_data_weight': 0.7}),
    (strategy.window_retraining, {'window_size': 2000}),
]:
    print()
    new_model, new_scaler, auc = strategy_fn(new_labeled_data, **kwargs)

    # Évaluer sur le batch drifté
    X_eval = prod_data_drifted[numerical_feat]
    y_eval = prod_data_drifted['is_fraud']
    X_eval_scaled = new_scaler.transform(X_eval)
    y_proba_eval = new_model.predict_proba(X_eval_scaled)[:, 1]
    auc_eval = roc_auc_score(y_eval, y_proba_eval)
    print(f"  AUC-ROC (évaluation production driftée) : {auc_eval:.4f}")
```

### 8.3 Checklist de Réponse au Drift

Lorsqu'une alerte de drift est déclenchée, voici les actions à mener :

**Étape 1 — Diagnostic immédiat (< 1 heure)**
- Vérifier l'intégrité du pipeline de données (logs d'ingestion, schéma)
- Confirmer que le drift est réel et non un artefact de calcul
- Évaluer si les métriques métier sont déjà impactées
- Identifier les features les plus driftées

**Étape 2 — Communication (< 4 heures)**
- Notifier l'équipe data science et les parties prenantes métier
- Ouvrir un ticket de suivi avec les métriques de drift documentées
- Si impact métier avéré : escalader selon le SLA défini

**Étape 3 — Investigation (< 24 heures)**
- Analyser la cause racine : changement de comportement, bug, nouvel événement ?
- Évaluer si le drift est temporaire (événement ponctuel) ou permanent
- Déterminer si des labels de production sont disponibles pour évaluer la performance réelle

**Étape 4 — Action (délai selon sévérité)**
- Drift bénin, temporaire → surveillance accrue, pas d'action immédiate
- Covariate shift modéré → planifier réentraînement sous 2 semaines
- Concept drift confirmé → réentraînement d'urgence avec nouvelles données
- Bug pipeline → corriger et re-traiter les données impactées

```python
# Checklist automatisée
def generate_drift_action_plan(drift_result: Dict, model_auc_baseline: float,
                                current_auc: Optional[float] = None) -> str:
    """
    Génère un plan d'action automatique basé sur les résultats de drift.
    """
    alert_level = drift_result['alert_level']
    share_drifted = drift_result['share_drifted']
    n_drifted = drift_result['n_drifted_features']
    auc_degradation = (model_auc_baseline - current_auc) if current_auc else None

    plan = [
        f"=== PLAN D'ACTION DRIFT — {datetime.now().strftime('%Y-%m-%d %H:%M')} ===",
        f"",
        f"Niveau d'alerte : {alert_level.upper()}",
        f"Features driftées : {n_drifted} ({share_drifted:.1%})",
    ]

    if auc_degradation is not None:
        plan.append(f"Dégradation AUC : {auc_degradation:.4f} ({auc_degradation/model_auc_baseline:.1%})")

    plan.extend(["", "--- ACTIONS RECOMMANDÉES ---"])

    # Actions selon le niveau
    if alert_level == 'ok':
        plan.extend([
            "✓ Pas d'action immédiate requise",
            "→ Continuer le monitoring à la fréquence normale",
        ])
    elif alert_level == 'warning':
        plan.extend([
            "⚠ Investigation recommandée",
            "→ Analyser les features driftées : " + ", ".join(
                [a['feature'] for a in drift_result['alerts'] if a['level'] == 'warning'][:5]
            ),
            "→ Vérifier les logs du pipeline d'ingestion",
            "→ Planifier réentraînement sous 2 semaines si drift persiste",
        ])
    elif alert_level == 'critical':
        plan.extend([
            "🚨 ACTION URGENTE REQUISE",
            "→ Vérifier immédiatement le pipeline de données",
            "→ Notifier l'équipe et les parties prenantes",
            "→ Évaluer l'impact sur les décisions métier en cours",
            "→ Si drift confirmé : déclencher le réentraînement d'urgence",
            "→ Considérer un rollback vers le modèle précédent si AUC < seuil",
        ])

    if auc_degradation and auc_degradation > 0.05:
        plan.extend([
            "",
            f"⚡ ALERTE PERFORMANCE : AUC dégradé de {auc_degradation:.4f}",
            "→ Rollback immédiat recommandé si > 0.10",
        ])

    return "\n".join(plan)


# Générer le plan d'action
action_plan = generate_drift_action_plan(
    drift_result=result_drifted,
    model_auc_baseline=auc,
    current_auc=0.85  # Simulé
)
print(action_plan)
```

---

## Résumé du Module

| Concept | Description | Outil/Méthode |
|---------|-------------|---------------|
| Covariate Shift | Distribution de X change | KS Test, PSI |
| Prior Probability Shift | Distribution de y change | Chi-carré, recalibration |
| Concept Drift | Relation P(y\|X) change | Fenêtres glissantes, retraining |
| Test KS | Variables numériques continues | `scipy.stats.ks_2samp` |
| Chi-carré | Variables catégorielles | `scipy.stats.chisquare` |
| JSD | Mesure symétrique de divergence | `scipy.spatial.distance.jensenshannon` |
| PSI | Standard bancaire, 10 buckets | Implémentation manuelle |
| Evidently | Rapports visuels automatisés | `DataDriftPreset`, HTML reports |
| MLflow | Tracking des métriques dans le temps | `mlflow.log_metrics` |
| Réentraînement | Réponse au drift confirmé | Full / Incremental / Window |

## Points Clés à Retenir

1. **Monitorer en continu** — Le drift n'est pas une exception, c'est la norme. Sans monitoring, votre modèle se dégrade silencieusement.

2. **Combiner plusieurs tests** — Aucun test statistique n'est parfait. Utiliser KS + PSI pour les numériques, chi-carré pour les catégorielles.

3. **Adapter les seuils au contexte** — Un PSI de 0.15 peut être critique pour un modèle de crédit, acceptable pour une recommandation de contenu.

4. **Distinguer drift des données et drift du concept** — Un drift des features ne dégrade pas toujours les performances. Le concept drift, lui, est toujours problématique.

5. **Automatiser les alertes mais maintenir le jugement humain** — Le système automatise la détection, mais la décision de réentraîner doit rester sous contrôle humain.

6. **Logger tout dans MLflow** — Avoir l'historique des métriques de drift permet de détecter des tendances avant qu'elles ne deviennent critiques.

---

## Exercices Pratiques

### Exercice 1 — Implémentation PSI
Implémenter la fonction `calculate_psi` sans regarder le cours, la tester sur le dataset `sklearn.datasets.load_breast_cancer` en simulant un drift sur 3 features.

### Exercice 2 — Rapport Evidently Complet
Utiliser le dataset `sklearn.datasets.load_wine` comme référence. Créer une version "production" avec drift sur 2 features numériques et 1 catégorielle. Générer un rapport Evidently HTML et interpréter les résultats.

### Exercice 3 — Pipeline MLflow
Créer un pipeline de monitoring qui : (1) vérifie le drift hebdomadairement, (2) log les métriques dans MLflow, (3) déclenche une alerte console si plus de 25% des features driftent. Simuler 4 semaines avec drift croissant.

### Exercice 4 — Stratégie de Réentraînement
À partir du dataset de fraude généré dans le cours, comparer les 3 stratégies de réentraînement (full, incremental, window) en termes d'AUC sur un set de validation représentant les nouvelles données driftées. Quelle stratégie donne les meilleurs résultats ?

---

*Ce cours fait partie de la formation Data Engineer — Module 08 Machine Learning.*
