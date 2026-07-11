# Exercice 01 — Rapport de Veille : Comparatif des Services OCR Cloud

## Contexte du brief (scénario B02A)

Vous êtes data engineer dans une startup française en pleine croissance. La direction vous confie une mission de veille technologique dans le cadre d'un projet d'automatisation du traitement des documents entrants (factures fournisseurs, bons de commande, contrats).

Votre responsable vous demande de produire un **rapport de veille** comparant les trois principaux services cloud d'OCR et d'extraction documentaire, afin d'éclairer la décision d'architecture pour le projet.

---

## Objectifs pédagogiques

Cet exercice vous entraîne à :

- Conduire une veille technologique structurée sur un sujet défini
- Comparer des services cloud sur des critères objectifs et pondérés
- Rédiger un rapport professionnel avec résumé exécutif et recommandations
- Utiliser les outils de veille présentés dans ce module (sources, LLMs, grille comparative)
- Respecter les contraintes RGPD dans un contexte cloud IA

---

## Sujet du rapport

**Comparatif des services d'OCR et d'extraction documentaire cloud :**
- Azure Document Intelligence (Microsoft)
- Amazon Textract (AWS)
- Google Document AI (GCP)

---

## Périmètre imposé

Votre rapport devra couvrir obligatoirement :

1. **La tâche d'extraction de factures fournisseurs** (use case principal)
2. **Les contraintes RGPD** : données fournisseurs européens (noms, adresses, IBAN, SIRET)
3. **Un volume de 300 à 500 documents PDF par mois**
4. **Une intégration Python** (votre équipe est en Python)
5. **Une infrastructure cloud neutre** (pas encore sur Azure, AWS ou GCP — déploiement initial)

---

## Livrables attendus

### Livrable 1 — Rapport de veille (document principal)

Le rapport doit respecter la structure vue dans `04-rapport-veille.md` :

```
1. Titre et métadonnées (auteur, date, période couverte)
2. Résumé exécutif (10-15 lignes maximum)
3. Contexte et périmètre (reprendre le contexte B02A)
4. Observations par service (une section par provider)
5. Analyse comparative (grille de critères pondérés)
6. Recommandations (2 à 3 recommandations hiérarchisées)
7. Sources et références (minimum 5 sources citées)
8. Limites de la veille
```

**Longueur minimale** : 4 pages (soit environ 800 à 1 200 mots hors tableaux et code)

### Livrable 2 — Grille comparative (obligatoire)

Produire un tableau comparatif des trois services sur les critères suivants (pondération libre) :

| Critère | Pondération suggérée | Notes |
|---------|---------------------|-------|
| Précision sur factures (formats FR) | 25% | Basé sur docs + tests si possible |
| Tarification au volume cible | 20% | Calculer le coût réel pour 500 docs/mois |
| Conformité RGPD (région EU, DPA) | 20% | Vérifier les engagements officiels |
| Facilité d'intégration Python | 15% | SDK, exemples, qualité de la doc |
| Modèles pré-entraînés disponibles | 10% | Richesse du catalogue |
| Maturité et support | 10% | Ancienneté, SLA, community |

### Livrable 3 — Sources utilisées

Listez **au minimum 8 sources** consultées, en précisant pour chacune :
- Le type de source (documentation officielle / blog / benchmark / newsletter / talk)
- La date de consultation
- En quoi cette source a contribué au rapport

---

## Étapes de travail recommandées

### Étape 1 — Collecte d'informations (1-2h)

Utilisez les sources présentées dans `02-sources.md` :

**Sources prioritaires à consulter :**

1. Pages officielles "What's New" / Changelog de chaque service
   - Azure : [learn.microsoft.com/azure/ai-services/document-intelligence/whats-new](https://learn.microsoft.com/azure/ai-services/document-intelligence/whats-new)
   - AWS : [docs.aws.amazon.com/textract/latest/dg/what-is.html](https://docs.aws.amazon.com/textract/latest/dg/what-is.html)
   - GCP : [cloud.google.com/document-ai/docs/release-notes](https://cloud.google.com/document-ai/docs/release-notes)

2. Pages de tarification officielles
   - Azure : [azure.microsoft.com/pricing/details/ai-document-intelligence/](https://azure.microsoft.com/pricing/details/ai-document-intelligence/)
   - AWS : [aws.amazon.com/textract/pricing/](https://aws.amazon.com/textract/pricing/)
   - GCP : [cloud.google.com/document-ai/pricing](https://cloud.google.com/document-ai/pricing)

3. Articles comparatifs récents (Hacker News, Medium, Towards Data Science)
   - Recherche suggérée sur HN : "document AI textract form recognizer 2024 2025"

4. Retours d'expérience (Reddit r/dataengineering, blog posts d'entreprises)

### Étape 2 — Organisation des notes (30 min)

Utilisez Obsidian ou Notion pour créer une note par service avec les informations collectées.
Utilisez les templates présentés dans `03-methode.md`.

### Étape 3 — Utilisation des LLMs pour accélérer (30-45 min)

Utilisez les prompts de `05-ia-outils.md` :
- **Prompt 4** (comparaison) pour générer une première ébauche de la grille comparative
- **Prompt 1** (résumé) pour résumer les articles comparatifs trouvés
- **Prompt 8** (draft) pour générer un premier draft à partir de vos notes

**Important** : Toujours vérifier les informations générées par le LLM dans les sources primaires. Indiquez dans votre rapport quelle partie a été aidée par un LLM.

### Étape 4 — Rédaction du rapport (1-2h)

Rédigez le rapport en Markdown (format `.md`) ou en PDF.
Commencez par le **résumé exécutif** (souvent le plus difficile à écrire, autant le forcer d'abord).

### Étape 5 — Relecture et vérification (30 min)

Vérifiez :
- [ ] Tous les faits sont sourcés
- [ ] Les prix sont à jour et correspondent bien au volume cible (500 docs/mois)
- [ ] Les recommendations sont spécifiques (pas juste "nous recommandons Azure")
- [ ] La partie RGPD est traitée avec les engagements contractuels (DPA)
- [ ] Le résumé exécutif tient en 10-15 lignes
- [ ] La grille comparative est complète

---

## Critères d'évaluation

| Critère | Barème | Description |
|---------|--------|-------------|
| Résumé exécutif | 3 pts | Clair, synthétique, répond à "que faire ?" |
| Observations (contenu factuel) | 5 pts | Informations à jour, sourcées, pertinentes |
| Grille comparative complète | 4 pts | Tous les critères remplis avec justification |
| Analyse et recommandations | 4 pts | Arguments solides, contextualisation au use case |
| Traitement du RGPD | 2 pts | Précis, vérifiable (DPA, régions EU) |
| Qualité des sources | 2 pts | Diversifiées, récentes, correctement citées |
| **Total** | **20 pts** | |

**Bonus :** +1 point si vous avez réellement testé l'un des services et inclus des captures ou résultats concrets.

---

## Points de vigilance RGPD — À traiter dans votre rapport

Voici les questions auxquelles votre rapport doit répondre sur le RGPD :

1. **Localisation des données** : Dans quelle(s) région(s) les données sont-elles traitées par défaut ? Est-il possible de restreindre le traitement à une région EU ?

2. **Engagements contractuels** : Chaque provider propose-t-il un Data Processing Agreement (DPA) ? Que dit ce DPA sur l'utilisation des données pour l'entraînement des modèles ?

3. **Nature des données** : Les factures fournisseurs contiennent-elles des données personnelles au sens du RGPD ? Lesquelles ? (Pensez : noms de contacts, adresses, potentiellement des données de personnes physiques comme des artisans en auto-entrepreneur)

4. **Durée de rétention** : Les providers conservent-ils les documents uploadés ? Combien de temps ?

5. **Recommandation RGPD** : Quel service offre les meilleures garanties pour ce use case ?

---

## Ressources supplémentaires pour l'exercice

### Pour les tests pratiques (optionnel)

Si vous souhaitez tester concrètement les services :

```python
# Facture de test (open source, pas de données personnelles réelles)
SAMPLE_INVOICE_URL = "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-REST-api-samples/master/curl/form-recognizer/sample-invoice.pdf"

import requests
with open("test_invoice.pdf", "wb") as f:
    f.write(requests.get(SAMPLE_INVOICE_URL).content)
```

Les trois services proposent un free tier suffisant pour des tests :
- Azure Document Intelligence : 500 pages/mois gratuites
- Amazon Textract : 1 000 pages/mois gratuites (pendant 1 an)
- Google Document AI : 1 000 pages/mois gratuites (certains processeurs)

### Documentation DPA

- Azure DPA : [microsoft.com/licensing/docs/view/Microsoft-Products-and-Services-Data-Protection-Addendum-DPA](https://www.microsoft.com/licensing/docs/view/Microsoft-Products-and-Services-Data-Protection-Addendum-DPA)
- AWS DPA : [aws.amazon.com/agreement/data-processing-addendum/](https://aws.amazon.com/agreement/data-processing-addendum/)
- GCP DPA : [cloud.google.com/terms/data-processing-addendum](https://cloud.google.com/terms/data-processing-addendum)

---

## Format de rendu

- **Format** : Markdown (`.md`) ou PDF
- **Nom du fichier** : `rapport-veille-ocr-cloud-[votre-nom].md`
- **Langue** : Français
- **Longueur** : 4 à 8 pages (hors annexes)
- **Date limite** : [À définir par le formateur]

---

## Questions fréquentes

**Q : Dois-je tester les trois services pour rédiger le rapport ?**
Non, les tests sont optionnels (bonus). Un rapport basé sur la documentation officielle, des benchmarks publiés et des articles de veille est suffisant pour atteindre la note maximale.

**Q : Puis-je utiliser un LLM pour rédiger le rapport ?**
Oui, à condition d'indiquer clairement quelle partie a été générée ou aidée par un LLM, et d'avoir vérifié toutes les informations dans des sources primaires. Un rapport entièrement généré sans vérification sera fortement pénalisé.

**Q : Les prix ont changé depuis la rédaction du cours. Comment procéder ?**
Utilisez toujours les prix officiels actuels des pages de tarification. Si les prix ont changé par rapport aux exemples du cours, c'est une bonne chose : cela montre que votre veille est à jour.

**Q : Je n'ai accès qu'à un seul provider. Puis-je quand même faire l'exercice ?**
Oui. Pour le(s) provider(s) auxquels vous n'avez pas accès, basez-vous sur la documentation, les changelogs, et les articles de veille. Indiquez clairement dans votre rapport quelles informations proviennent d'un test direct et lesquelles proviennent de sources secondaires.
