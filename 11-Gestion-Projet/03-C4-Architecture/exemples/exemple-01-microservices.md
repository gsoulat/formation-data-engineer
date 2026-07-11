# Exemple 01 — Architecture Microservices en C4

## Présentation du système

**Système :** Plateforme e-commerce **ShopFlow** avec une architecture microservices.

Le système est composé de plusieurs services indépendants communiquant via une API Gateway et un broker de messages Kafka.

---

## Niveau 1 — Diagramme de Contexte

```plantuml
@startuml ShopFlow-Contexte

!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml

title Diagramme de Contexte — ShopFlow E-Commerce

LAYOUT_WITH_LEGEND()

Person(client, "Client", "Achète des produits\nvia le site web ou l'application mobile.")

Person(vendeur, "Vendeur", "Gère son catalogue produits,\nses stocks et ses commandes.")

Person(admin, "Administrateur", "Gère la plateforme,\nles utilisateurs et les litiges.")

System(shopflow, "ShopFlow", "Plateforme e-commerce permettant\nl'achat, la vente et la gestion de commandes.")

System_Ext(stripe, "Stripe", "Traitement des paiements\net gestion des remboursements.")

System_Ext(sendgrid, "SendGrid", "Envoi des emails transactionnels\n(confirmation, livraison, factures).")

System_Ext(colissimo, "Colissimo / Chronopost", "Génération des étiquettes d'expédition\net suivi des colis.")

System_Ext(google, "Google SSO", "Authentification via\ncompte Google.")

Rel(client, shopflow, "Navigue, commande, paye", "HTTPS")
Rel(vendeur, shopflow, "Gère catalogue et commandes", "HTTPS")
Rel(admin, shopflow, "Administration", "HTTPS")

Rel(shopflow, stripe, "Traite les paiements", "API HTTPS")
Rel(shopflow, sendgrid, "Envoie les emails", "API HTTPS")
Rel(shopflow, colissimo, "Génère les étiquettes", "API HTTPS")
Rel(shopflow, google, "Authentifie les utilisateurs", "OAuth 2.0")

@enduml
```

---

## Niveau 2 — Diagramme de Conteneurs

```plantuml
@startuml ShopFlow-Conteneurs

!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml

title Diagramme de Conteneurs — ShopFlow E-Commerce

LAYOUT_WITH_LEGEND()

Person(client, "Client", "")
Person(vendeur, "Vendeur", "")

System_Ext(stripe, "Stripe", "Paiement")
System_Ext(sendgrid, "SendGrid", "Email")
System_Ext(colissimo, "Colissimo", "Livraison")

System_Boundary(shopflow, "ShopFlow") {

    Container(webapp, "Application Web", "React, TypeScript", "SPA client — navigation,\nrecherche, panier, commande.")

    Container(mobileApp, "Application Mobile", "React Native", "Application iOS/Android\npour les clients.")

    Container(apiGateway, "API Gateway", "Nginx + Kong", "Point d'entrée unique.\nRouting, auth, rate limiting.")

    Container(authService, "Auth Service", "Python, FastAPI", "Gestion de l'authentification\nJWT et OAuth 2.0.")

    Container(catalogService, "Catalog Service", "Go", "Gestion du catalogue produits,\ncatégories, attributs, recherche.")

    Container(orderService, "Order Service", "Python, FastAPI", "Gestion des commandes :\npanier, validation, paiement, suivi.")

    Container(inventoryService, "Inventory Service", "Python, FastAPI", "Gestion des stocks\npar vendeur et entrepôt.")

    Container(notificationService, "Notification Service", "Node.js", "Envoi des notifications\nEmail, SMS, Push.")

    Container(shippingService, "Shipping Service", "Python, FastAPI", "Génération des étiquettes\net suivi des livraisons.")

    ContainerQueue(kafka, "Apache Kafka", "Kafka 3.6", "Bus d'événements asynchrone\nentre les services.")

    ContainerDb(authDb, "Auth DB", "PostgreSQL", "Utilisateurs, sessions, OAuth tokens.")
    ContainerDb(catalogDb, "Catalog DB", "PostgreSQL", "Produits, catégories, images.")
    ContainerDb(orderDb, "Order DB", "PostgreSQL", "Commandes, paiements, historique.")
    ContainerDb(inventoryDb, "Inventory DB", "PostgreSQL", "Stocks, mouvements, alertes.")
    ContainerDb(searchEngine, "Moteur de recherche", "Elasticsearch", "Index de recherche full-text\ndes produits.")
    ContainerDb(cache, "Cache", "Redis", "Sessions, paniers temporaires,\ncache des pages produits.")
}

' Clients → Gateway
Rel(client, webapp, "Utilise", "HTTPS")
Rel(client, mobileApp, "Utilise", "HTTPS/WebSocket")
Rel(vendeur, webapp, "Gère son catalogue", "HTTPS")
Rel(webapp, apiGateway, "Appels API", "HTTPS / REST")
Rel(mobileApp, apiGateway, "Appels API", "HTTPS / REST")

' Gateway → Services
Rel(apiGateway, authService, "Authentification", "HTTP")
Rel(apiGateway, catalogService, "Catalogue", "HTTP")
Rel(apiGateway, orderService, "Commandes", "HTTP")
Rel(apiGateway, inventoryService, "Stocks", "HTTP")
Rel(apiGateway, shippingService, "Livraison", "HTTP")

' Services → Bases de données
Rel(authService, authDb, "Lit/Écrit", "SQL")
Rel(authService, cache, "Sessions", "Redis")
Rel(catalogService, catalogDb, "Lit/Écrit", "SQL")
Rel(catalogService, searchEngine, "Index", "HTTP")
Rel(orderService, orderDb, "Lit/Écrit", "SQL")
Rel(inventoryService, inventoryDb, "Lit/Écrit", "SQL")

' Événements Kafka
Rel(orderService, kafka, "Publie : order.created, order.paid", "Kafka")
Rel(inventoryService, kafka, "Consomme : order.paid", "Kafka")
Rel(notificationService, kafka, "Consomme : order.*, inventory.*", "Kafka")
Rel(shippingService, kafka, "Consomme : order.paid", "Kafka")

' Services → Externes
Rel(orderService, stripe, "Traite le paiement", "API HTTPS")
Rel(notificationService, sendgrid, "Envoie les emails", "API HTTPS")
Rel(shippingService, colissimo, "Génère étiquette", "API HTTPS")
Rel(authService, google, "OAuth 2.0", "HTTPS")

@enduml
```

---

## Niveau 2 — Vue dynamique : flux de commande

Ce diagramme montre la séquence d'événements lors d'une commande client.

```plantuml
@startuml ShopFlow-Flux-Commande

!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Dynamic.puml

title Flux de commande — ShopFlow

LAYOUT_WITH_LEGEND()

Person(client, "Client", "")
Container(webapp, "Application Web", "React", "")
Container(apiGateway, "API Gateway", "Kong", "")
Container(orderService, "Order Service", "FastAPI", "")
Container(inventoryService, "Inventory Service", "FastAPI", "")
ContainerQueue(kafka, "Kafka", "Broker", "")
Container(notifService, "Notification Service", "Node.js", "")
System_Ext(stripe, "Stripe", "Paiement")
System_Ext(sendgrid, "SendGrid", "Email")

RelIndex(1, client, webapp, "Valide le panier")
RelIndex(2, webapp, apiGateway, "POST /orders")
RelIndex(3, apiGateway, orderService, "POST /orders")
RelIndex(4, orderService, inventoryService, "Vérifie le stock disponible")
RelIndex(5, orderService, stripe, "Traite le paiement")
RelIndex(6, orderService, kafka, "Publie : order.paid")
RelIndex(7, kafka, inventoryService, "Consomme : order.paid → décrémente stock")
RelIndex(8, kafka, notifService, "Consomme : order.paid")
RelIndex(9, notifService, sendgrid, "Envoie email de confirmation")
RelIndex(10, notifService, client, "Envoie notification push")

@enduml
```

---

## Niveau 3 — Composants Order Service

```plantuml
@startuml ShopFlow-Composants-OrderService

!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml

title Diagramme de Composants — Order Service (FastAPI)

LAYOUT_WITH_LEGEND()

Person(client, "Client via API Gateway", "")
ContainerDb(orderDb, "Order DB", "PostgreSQL", "")
ContainerQueue(kafka, "Apache Kafka", "", "")
Container_Ext(stripe, "Stripe", "API Paiement", "")
Container_Ext(inventoryService, "Inventory Service", "FastAPI", "")

System_Boundary(orderService, "Order Service") {

    Component(orderRouter, "Order Router", "FastAPI Router", "/orders, /orders/{id}, /orders/{id}/cancel")

    Component(cartRouter, "Cart Router", "FastAPI Router", "/cart, /cart/items")

    Component(authDep, "Auth Dependency", "FastAPI Depends", "Vérifie le JWT sur chaque requête.")

    Component(orderUseCase, "Order Use Cases", "Python", "Logique métier : créer, payer,\nannuler une commande.")

    Component(cartUseCase, "Cart Use Cases", "Python", "Gestion du panier :\najouter, supprimer, calculer le total.")

    Component(paymentAdapter, "Payment Adapter", "Python", "Abstraction de Stripe.\nGère le paiement et les remboursements.")

    Component(inventoryAdapter, "Inventory Adapter", "Python, httpx", "Client HTTP vers Inventory Service.\nVérifie la disponibilité du stock.")

    Component(eventPublisher, "Event Publisher", "Python, aiokafka", "Publie les événements Kafka\n(order.created, order.paid, order.cancelled).")

    Component(orderRepo, "Order Repository", "Python, SQLAlchemy", "Accès aux données de commande\nen base PostgreSQL.")
}

Rel(client, orderRouter, "POST /orders, GET /orders/{id}", "HTTPS")
Rel(client, cartRouter, "POST /cart/items, GET /cart", "HTTPS")
Rel(orderRouter, authDep, "Vérifie l'auth")
Rel(cartRouter, authDep, "Vérifie l'auth")
Rel(orderRouter, orderUseCase, "Délègue")
Rel(cartRouter, cartUseCase, "Délègue")
Rel(orderUseCase, paymentAdapter, "Déclenche le paiement")
Rel(orderUseCase, inventoryAdapter, "Vérifie le stock")
Rel(orderUseCase, eventPublisher, "Publie les événements")
Rel(orderUseCase, orderRepo, "Lit/Écrit la commande")
Rel(cartUseCase, orderRepo, "Lit/Écrit le panier")
Rel(paymentAdapter, stripe, "API REST", "HTTPS")
Rel(inventoryAdapter, inventoryService, "HTTP", "HTTP/JSON")
Rel(eventPublisher, kafka, "Publie", "AMQP / Kafka Protocol")
Rel(orderRepo, orderDb, "SQL", "JDBC")

@enduml
```

---

## Observations sur cet exemple

**Pourquoi Kafka pour les événements ?**
Plusieurs services réagissent au même événement `order.paid` (Inventory décrémente le stock, Notification envoie l'email, Shipping génère l'étiquette). Kafka permet le fan-out sans couplage direct entre les services. → Voir ADR-0004.

**Pourquoi une API Gateway ?**
Centraliser l'authentification, le rate limiting et le routing évite de dupliquer cette logique dans chaque microservice.

**Pourquoi PostgreSQL séparé par service ?**
Chaque service possède sa propre base — c'est le pattern "Database per service" des microservices. Cela garantit l'isolation et l'indépendance des déploiements.
