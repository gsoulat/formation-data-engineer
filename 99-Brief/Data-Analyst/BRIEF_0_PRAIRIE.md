# Brief : Répliquer un tableau de bord de ventes retail avec Looker Studio (Phase 0 — La Prairie)

## Informations

| Critère | Valeur |
|---------|--------|
| **Durée** | 2 à 3 jours |
| **Niveau** | Débutant — mission de découverte |
| **Modalité** | Individuel |
| **Outils** | Looker Studio (alternative : Power BI), tableur |
| **Prérequis** | [Cours Business Intelligence](../../15-Business-Intelligence/) — aucun prérequis technique (pas de code) |

## Description rapide

Vous rejoignez une PME e-commerce des Hauts-de-France. Votre première mission : reproduire fidèlement un tableau de bord modèle fourni par votre tuteur, à partir d'un jeu de ventes réel. Objectif : vous familiariser avec un outil de BI (Looker Studio), comprendre ce qu'est un indicateur clé (KPI) et choisir des visualisations lisibles et accessibles. Vous travaillez seul, sans installer de logiciel. Vous livrez le lien partagé de votre tableau de bord, une courte note décrivant vos KPI, et un dossier de rendu documenté. Pas de code, pas d'analyse libre : ici, on apprend en imitant un exemple de qualité.

## Objectifs pédagogiques

À l'issue de ce brief, vous serez capable de :

- **Identifier les indicateurs clés (KPI)** attendus par une direction et expliquer, pour chacun, sa définition et son mode de calcul à partir des colonnes d'un jeu de données.
- **Choisir des visualisations pertinentes et accessibles** : associer chaque type de graphique à l'intention de lecture (évolution, comparaison, répartition) et respecter des bases d'accessibilité (contrastes, titres explicites).
- **Construire un tableau de bord avec un outil de BI** (Looker Studio) : connecter une source, produire des cartes de chiffres clés et des graphiques, ajouter un filtre interactif.
- **Cadrer une mission** : reformuler un besoin métier, préciser ce qui est dans le périmètre et dresser un inventaire de ce qui est à reproduire.
- **Rechercher méthodiquement une solution** : retrouver l'origine d'un écart de chiffre et mobiliser la documentation ou des tutoriels face à un blocage.

## Contexte

**L'entreprise et son problème.** « Ch'ti Comptoir » est une PME e-commerce installée à Roubaix, dans les Hauts-de-France. Elle vend du mobilier, des fournitures de bureau et du matériel high-tech à des particuliers et à des professionnels partout en France. L'entreprise a grandi vite : aujourd'hui une dizaine de salariés, plusieurs milliers de commandes par an. Le problème, c'est que la direction pilote encore « au feeling ». Chaque lundi, la gérante ouvre un gros fichier de ventes exporté de l'outil de commande et fait défiler les lignes pour « voir comment ça va ». Personne ne sait, d'un coup d'œil, quel est le chiffre d'affaires du mois, quelle région rapporte le plus, ni quelle catégorie de produits dégage vraiment de la marge. Les décisions (quelles promos lancer, quelles régions relancer) se prennent sans tableau de bord fiable, ce qui fait perdre du temps et de l'argent.

Pour changer cela, la gérante a fait appel à un consultant BI qui a construit un tableau de bord modèle dans Looker Studio. Ce modèle est exactement ce que l'entreprise veut voir chaque semaine. Mais le consultant part, et l'entreprise veut être autonome. Votre tuteur vous confie donc une mission de prise en main : reproduire ce tableau de bord modèle à l'identique, pour comprendre comment il est construit, avant de pouvoir un jour en créer de nouveaux.

**La question centrale.** Tout le tableau de bord répond à une seule question métier, simple et concrète : « Comment se portent les ventes de Ch'ti Comptoir, et quelles régions, catégories et segments de clients tirent l'activité ? » Gardez cette question en tête à chaque étape : chaque chiffre et chaque graphique que vous reproduisez doit aider la gérante à y répondre en moins d'une minute.

**La source de données.** Vous travaillez sur un jeu de ventes retail public et réel, le « Superstore Dataset », largement utilisé en formation BI. Il contient 9 994 lignes de commandes (une ligne = un produit commandé), avec des colonnes prêtes à l'emploi : date de commande (Order Date), région (Region), État/ville, catégorie et sous-catégorie de produit (Category, Sub-Category), segment de client (Segment : Consumer, Corporate, Home Office), montant des ventes (Sales), quantité (Quantity), remise (Discount) et profit (Profit). Format : un fichier CSV unique, environ 2 Mo, aucune authentification requise.

- Jeu de données : Superstore Dataset — https://www.kaggle.com/datasets/vivek468/superstore-dataset-final
- Téléchargement : bouton « Download » sur la page Kaggle (compte gratuit requis) ; le fichier s'appelle généralement `Sample - Superstore.csv` ou `Superstore.csv`

> Note de scénarisation : ce jeu est en dollars et concerne un marché US ; pour la mission, on fait comme si c'était les ventes de Ch'ti Comptoir (vous pouvez raisonner en « euros » sans rien recalculer). L'important est la démarche, pas la devise.

**Ce qui est attendu.** Vous ne partez pas d'une page blanche. Votre tuteur vous remet un tableau de bord modèle (capture d'écran annotée + lien Looker Studio en lecture seule). Votre travail : reproduire ce modèle le plus fidèlement possible avec le jeu de données fourni. Le modèle comporte typiquement : un bandeau de cartes de chiffres clés (chiffre d'affaires total, profit total, nombre de commandes, panier moyen), un graphique d'évolution du chiffre d'affaires dans le temps, une comparaison des ventes par région, une répartition par catégorie de produits, un classement des sous-catégories les plus rentables, et un filtre interactif (par exemple par région ou par période).

On attend de vous une réplique fidèle, pas une création originale : mêmes indicateurs, mêmes types de graphiques, même logique de lecture. La valeur pédagogique est ici dans l'imitation soignée. Vous devrez quand même comprendre ce que vous reproduisez : être capable d'expliquer ce qu'est chacun des indicateurs (par exemple : « le panier moyen, c'est le chiffre d'affaires divisé par le nombre de commandes ») et pourquoi tel graphique convient à telle donnée. Aucune analyse libre, aucune nouvelle métrique inventée, aucun nettoyage de données complexe n'est demandé : le jeu est déjà propre.

## Modalités pédagogiques

Projet individuel, 2 à 3 jours, organisé en trois phases. Vous suivez un tableau de bord modèle : votre liberté est volontairement réduite, car l'objectif de cette mission de découverte est de reproduire un exemple de qualité pour acquérir les bons réflexes. Chaque phase produit un résultat visible.

### Phase 1 — Cadrage et lecture du modèle, SANS outil (J1, matin)

Avant de toucher à Looker Studio, posez le décor sur papier ou dans un document texte. Relisez la question centrale et reformulez-la avec vos mots : que cherche concrètement la gérante de Ch'ti Comptoir ? Ouvrez ensuite le tableau de bord modèle fourni et observez-le comme un détective. Quels sont les chiffres clés affichés en haut ? Combien y en a-t-il ? À votre avis, comment chacun est-il calculé à partir des colonnes du CSV (par exemple, le chiffre d'affaires correspond-il à la somme de la colonne Sales) ? Quels types de graphiques voyez-vous, et quelle donnée chacun représente-t-il : une évolution dans le temps, une comparaison entre régions, une répartition par catégorie ? Pourquoi, selon vous, le consultant a-t-il choisi une courbe pour le temps et des barres pour comparer les régions plutôt que l'inverse ? Listez aussi le ou les filtres présents. À la fin de cette phase, vous devez avoir un inventaire écrit : la liste des KPI à reproduire (avec votre hypothèse de calcul pour chacun) et la liste des graphiques (avec leur type et la donnée associée). C'est votre feuille de route. Ouvrez enfin le CSV dans un tableur pour repérer où se trouve chaque colonne dont vous aurez besoin.

### Phase 2 — Reproduction du tableau de bord (J1 après-midi à J2)

Connectez le fichier CSV à Looker Studio (connecteur « Importer un fichier » / Google Sheets). Reproduisez le modèle élément par élément, en suivant votre inventaire de la phase 1. Commencez par le bandeau de cartes de chiffres clés (scorecards), puis ajoutez les graphiques un par un. Pour chaque élément, comparez en permanence votre écran au modèle : les chiffres correspondent-ils ? Le type de graphique est-il le même ? Si un chiffre diffère de celui du modèle, c'est un signal : votre champ, votre agrégation (somme, moyenne, comptage) ou votre filtre est sans doute mal réglé. Comment retrouver d'où vient l'écart de façon méthodique, sans tout refaire au hasard ? Ajoutez enfin le ou les filtres interactifs pour que la gérante puisse, par exemple, n'afficher qu'une région. Vérifiez que cliquer sur le filtre met bien à jour tous les graphiques.

### Phase 3 — Accessibilité, finitions et rendu (J3, ou fin de J2)

Reprenez votre tableau de bord avec l'œil d'un utilisateur. Les titres sont-ils explicites (un titre par graphique, pas de « Graphique 1 ») ? Les couleurs sont-elles suffisamment contrastées pour être lisibles par une personne malvoyante, conformément aux recommandations WCAG ? Évitez de transmettre une information uniquement par la couleur ; vérifiez le contraste entre le texte et le fond. La devise et les nombres sont-ils formatés proprement ? Rédigez ensuite votre courte note de rendu : pour chaque KPI, indiquez sa définition et son mode de calcul, et joignez une capture de votre tableau de bord à côté du modèle pour montrer la ressemblance. Préparez enfin votre dossier de rendu (dépôt GitHub ou dossier partagé) avec un README. Réglez le partage du lien Looker Studio en « lecture pour toute personne disposant du lien » et testez-le dans une fenêtre de navigation privée : si le lien ne s'ouvre pas, personne ne pourra évaluer votre travail.

## Modalités d'évaluation

L'évaluation se fait en fin de Phase 0, en deux volets, sur la base de votre rendu et d'un court échange oral individuel.

- **Démonstration du tableau de bord (70 %).** Vous présentez votre tableau de bord Looker Studio en direct face au formateur (environ 10 minutes de démonstration). Vous montrez le bandeau de chiffres clés, chaque graphique, et l'usage du filtre interactif. Le formateur compare votre réplique au modèle fourni : fidélité des KPI, exactitude des chiffres, pertinence et lisibilité des visualisations, fonctionnement du filtre, respect des bonnes pratiques d'accessibilité (titres clairs, contrastes).

- **Oral de compréhension (30 %).** Échange d'environ 5 à 10 minutes. Vous expliquez ce que représente chaque KPI et comment il se calcule à partir des colonnes du jeu de données, et vous justifiez le choix de chaque type de graphique (pourquoi une courbe pour le temps, des barres pour comparer les régions). Le formateur peut vous demander de modifier un filtre en direct ou de retrouver d'où viendrait un écart de chiffre. Cet oral vérifie que vous avez compris ce que vous avez reproduit, et pas seulement copié.

Durées indicatives : 10 min de démonstration + 5 à 10 min de questions, soit environ 20 minutes par apprenant.

**Clause de validation partielle.** Un apprenant dont le tableau de bord est incomplet (par exemple certains graphiques manquants) mais qui démontre, à l'oral, une compréhension juste des KPI, du choix des visualisations et de l'usage de l'outil, peut valider partiellement les acquis de la mission. À l'inverse, un tableau de bord visuellement complet mais que l'apprenant ne sait pas expliquer ne suffit pas à valider la compréhension attendue. Les capacités de cadrage et de recherche méthodique sont évaluées via l'inventaire de cadrage (Phase 1) et la méthode décrite pour retrouver les écarts.

## Livrables attendus

Trois livrables, regroupés dans un dépôt GitHub public (ou, à défaut, un dossier de rendu partagé).

- **Le lien partagé du tableau de bord Looker Studio**, réglé en accès « lecture pour toute personne disposant du lien ». Le lien doit être collé dans le README et testé en navigation privée. Sans lien fonctionnel, la démonstration ne peut être évaluée.

- **Une courte note de rendu** (PDF ou Markdown, 1 à 3 pages) contenant : la reformulation de la question centrale ; la liste des KPI reproduits avec, pour chacun, sa définition et son mode de calcul (champ source + agrégation utilisée, par exemple « Chiffre d'affaires = somme de Sales ») ; la liste des graphiques avec leur type et la donnée représentée ; une ou deux captures d'écran de votre tableau de bord placées à côté du modèle fourni pour montrer la ressemblance ; quelques lignes sur les vérifications d'accessibilité réalisées (titres, contrastes).

- **Un dépôt GitHub public** (ou dossier partagé) avec un README structuré :
  - Description du projet (contexte Ch'ti Comptoir + question centrale)
  - Outil utilisé (Looker Studio) et source de données (lien Kaggle)
  - Lien cliquable vers le tableau de bord Looker Studio
  - Liste des KPI et des graphiques reproduits
  - Auteur

Le dépôt contient au minimum le README et la note de rendu (avec ses captures). Le fichier CSV n'a pas à être versionné : indiquez seulement le lien de la source. Aucun code n'est attendu pour cette mission.

## Critères de performance

**Identifier les indicateurs clés à calculer**
- Les KPI reproduits correspondent à ceux du tableau de bord modèle (CA total, profit, nombre de commandes, panier moyen). OUI / NON
- Pour chaque KPI, l'apprenant donne une définition correcte et son mode de calcul (champ source + agrégation). OUI / NON
- Les valeurs des KPI affichées correspondent aux valeurs attendues du jeu de données. OUI / NON

**Choisir des visualisations pertinentes et accessibles**
- Les types de graphiques reproduits correspondent à ceux du modèle (courbe pour le temps, barres pour les comparaisons, etc.). OUI / NON
- Chaque graphique porte un titre explicite et représente la donnée attendue. OUI / NON
- Les visualisations respectent des bases d'accessibilité : contrastes suffisants, information non portée uniquement par la couleur. OUI / NON

**Créer des tableaux de bord avec un outil de BI**
- Le jeu de données est correctement connecté à Looker Studio et le tableau de bord s'affiche. OUI / NON
- Le ou les filtres interactifs fonctionnent et mettent à jour les graphiques. OUI / NON
- Le lien partagé est accessible en lecture par une personne externe (testé en navigation privée). OUI / NON

**Définir le périmètre de la mission**
- L'apprenant reformule la question centrale et liste ce qui est dans / hors du périmètre de la mission. OUI / NON
- L'inventaire de cadrage (KPI + graphiques à reproduire) est présent et cohérent. OUI / NON

**Rechercher méthodiquement des pistes de résolution**
- L'apprenant décrit une démarche pour retrouver l'origine d'un écart de chiffre (champ, agrégation, filtre). OUI / NON
- L'apprenant mobilise la documentation ou les tutoriels pour résoudre un blocage. OUI / NON

## Ressources

- [Cours Business Intelligence](../../15-Business-Intelligence/) — métier de Data Analyst et fondamentaux BI
- Documentation officielle Looker Studio (Google) : https://support.google.com/looker-studio
- Démarrage rapide Looker Studio (créer un premier rapport) : https://support.google.com/looker-studio/answer/9171315
- Connecter un fichier CSV / Google Sheets à Looker Studio : https://support.google.com/looker-studio/answer/6295297
- Jeu de données Superstore (Kaggle) : https://www.kaggle.com/datasets/vivek468/superstore-dataset-final
- Alternative Power BI (si l'apprenant est sous Windows) — démarrage : https://learn.microsoft.com/fr-fr/power-bi/fundamentals/desktop-getting-started
- Comprendre les contrastes de couleurs (WCAG) — vérificateur de contraste WebAIM : https://webaim.org/resources/contrastchecker/
- Règles WCAG 2.1 en français (synthèse) : https://www.w3.org/Translations/WCAG21-fr/
