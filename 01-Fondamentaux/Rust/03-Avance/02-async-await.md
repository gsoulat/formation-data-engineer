# Rust — Async/Await : Tokio Runtime, Futures, Async Streams

## 1. Pourquoi l'asynchrone en Rust ?

```
Programmation synchrone :
Thread 1 : [requête réseau ──── attente 500ms ──── réponse] [requête DB ─── attente]

Programmation asynchrone :
Thread 1 : [requête réseau] [requête DB] [autre travail] [reçoit réseau] [reçoit DB]

→ Un seul thread peut gérer des milliers de connexions I/O simultanées
→ Particulièrement utile pour les serveurs web, les clients HTTP, les DB
```

## 2. Cargo.toml pour async

```toml
[dependencies]
tokio = { version = "1", features = ["full"] }
# ou minimal :
# tokio = { version = "1", features = ["rt", "rt-multi-thread", "macros", "time", "net"] }

# Pour HTTP
reqwest = { version = "0.11", features = ["json"] }

# Pour les streams async
futures = "0.3"
```

## 3. Premiers pas avec async/await

```rust
// async fn retourne un Future (pas la valeur directement)
async fn dire_bonjour() {
    println!("Bonjour !");
}

async fn calculer(x: i32) -> i32 {
    x * 2
}

// #[tokio::main] crée le runtime Tokio et lance la future async
#[tokio::main]
async fn main() {
    // .await exécute la future et attend le résultat
    dire_bonjour().await;

    let resultat = calculer(21).await;
    println!("{}", resultat);  // 42

    // Les futures sont LAZY : elles ne font rien sans .await
    let future = calculer(5);  // PAS encore exécuté
    let val = future.await;    // exécuté maintenant
    println!("{}", val);
}
```

## 4. tokio::time — Timers et timeouts

```rust
use tokio::time::{sleep, timeout, Duration, Instant};

async fn operation_lente(id: u32) -> String {
    sleep(Duration::from_millis(100 * id as u64)).await;
    format!("Résultat {}", id)
}

#[tokio::main]
async fn main() {
    // --- sleep ---
    let debut = Instant::now();
    sleep(Duration::from_millis(100)).await;
    println!("Après 100ms: {:?}", debut.elapsed());

    // --- Exécution séquentielle (attend l'un après l'autre) ---
    let debut = Instant::now();
    let r1 = operation_lente(1).await;  // 100ms
    let r2 = operation_lente(2).await;  // 200ms
    let r3 = operation_lente(3).await;  // 300ms
    println!("Séquentiel: {:?}", debut.elapsed());  // ~600ms
    println!("{} {} {}", r1, r2, r3);

    // --- Exécution concurrente avec join! ---
    let debut = Instant::now();
    let (r1, r2, r3) = tokio::join!(
        operation_lente(1),  // 100ms
        operation_lente(2),  // 200ms
        operation_lente(3),  // 300ms
    );
    println!("Concurrent (join!): {:?}", debut.elapsed());  // ~300ms
    println!("{} {} {}", r1, r2, r3);

    // --- Timeout ---
    match timeout(Duration::from_millis(150), operation_lente(3)).await {
        Ok(resultat)          => println!("Succès : {}", resultat),
        Err(_)                => println!("Timeout !"),
    }
    // → Timeout ! (300ms > 150ms)
}
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Exécuter le programme qui compare séquentiel (~600ms) vs concurrent avec `tokio::join!` (~300ms). Montrer la différence de temps dans le terminal. Utiliser `time cargo run` pour mesurer.
> **Expliquer :** Expliquer visuellement que `join!` permet à toutes les futures de progresser "en même temps" sur le même thread (coopérativement, pas parallèlement). Les trois opérations s'exécutent en ~300ms car elles se déroulent simultanément, chacune "dormant" pendant l'attente des autres.
---

## 5. Tâches (tokio::spawn)

```rust
use tokio::task;

async fn travail(id: u32) -> u32 {
    tokio::time::sleep(tokio::time::Duration::from_millis(50)).await;
    println!("Tâche {} terminée", id);
    id * id
}

#[tokio::main]
async fn main() {
    // spawn : lancer une tâche en arrière-plan
    let handle1 = tokio::spawn(travail(1));
    let handle2 = tokio::spawn(travail(2));
    let handle3 = tokio::spawn(travail(3));

    // Attendre les résultats
    let r1 = handle1.await.unwrap();  // JoinHandle<T>
    let r2 = handle2.await.unwrap();
    let r3 = handle3.await.unwrap();
    println!("Résultats: {}, {}, {}", r1, r2, r3);  // 1, 4, 9

    // --- spawn_blocking : pour les opérations bloquantes ---
    // (ne pas utiliser std::thread::sleep dans async !)
    let resultat = task::spawn_blocking(|| {
        // Code bloquant (CPU intensif, I/O synchrone)
        std::thread::sleep(std::time::Duration::from_millis(10));
        "résultat bloquant".to_string()
    }).await.unwrap();
    println!("{}", resultat);

    // --- Toutes les tâches avec JoinSet ---
    let mut set = task::JoinSet::new();
    for i in 0..5 {
        set.spawn(travail(i));
    }
    while let Some(res) = set.join_next().await {
        println!("Terminé: {:?}", res);
    }
}
```

## 6. Channels asynchrones

```rust
use tokio::sync::{mpsc, oneshot, broadcast};

#[tokio::main]
async fn main() {
    // --- mpsc : multiple producers, single consumer ---
    let (tx, mut rx) = mpsc::channel::<String>(32);  // buffer de 32

    // Producteur 1
    let tx1 = tx.clone();
    tokio::spawn(async move {
        tx1.send("Message 1".into()).await.unwrap();
        tx1.send("Message 2".into()).await.unwrap();
    });

    // Producteur 2
    let tx2 = tx.clone();
    tokio::spawn(async move {
        tx2.send("Message 3".into()).await.unwrap();
    });

    drop(tx);  // fermer l'émetteur original

    // Consommateur
    while let Some(msg) = rx.recv().await {
        println!("Reçu: {}", msg);
    }
    println!("Channel fermé");

    // --- oneshot : un seul envoi ---
    let (tx, rx) = oneshot::channel::<i32>();

    tokio::spawn(async move {
        tx.send(42).unwrap();
    });

    let valeur = rx.await.unwrap();
    println!("Valeur reçue: {}", valeur);

    // --- broadcast : tous les abonnés reçoivent ---
    let (tx, _rx1) = broadcast::channel::<String>(16);
    let mut rx2 = tx.subscribe();
    let mut rx3 = tx.subscribe();

    tx.send("Broadcast !".into()).unwrap();

    println!("{}", rx2.recv().await.unwrap());
    println!("{}", rx3.recv().await.unwrap());
}
```

## 7. HTTP avec reqwest

```rust
use serde::{Deserialize, Serialize};
use reqwest::Client;

#[derive(Debug, Deserialize, Serialize)]
struct Post {
    id: Option<u32>,
    title: String,
    body: String,
    user_id: u32,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let client = Client::new();

    // GET : récupérer un JSON
    let post: Post = client
        .get("https://jsonplaceholder.typicode.com/posts/1")
        .send()
        .await?
        .json::<Post>()
        .await?;
    println!("{:?}", post);

    // GET liste
    let posts: Vec<Post> = client
        .get("https://jsonplaceholder.typicode.com/posts")
        .query(&[("userId", "1")])
        .send()
        .await?
        .json()
        .await?;
    println!("{} posts pour user 1", posts.len());

    // POST : envoyer du JSON
    let nouveau = Post {
        id: None,
        title: "Mon titre".into(),
        body: "Mon contenu".into(),
        user_id: 1,
    };

    let cree: Post = client
        .post("https://jsonplaceholder.typicode.com/posts")
        .json(&nouveau)
        .send()
        .await?
        .json()
        .await?;
    println!("Créé avec id: {:?}", cree.id);

    // Requêtes concurrentes
    let urls = (1..=5).map(|i|
        format!("https://jsonplaceholder.typicode.com/posts/{}", i)
    );

    let futures: Vec<_> = urls
        .map(|url| {
            let client = client.clone();
            tokio::spawn(async move {
                client.get(&url).send().await?.json::<Post>().await
            })
        })
        .collect();

    let resultats = futures::future::join_all(futures).await;
    for res in resultats {
        match res.unwrap() {
            Ok(post)  => println!("Post: {}", post.title),
            Err(e)    => println!("Erreur: {}", e),
        }
    }

    Ok(())
}
```

## 8. Async Streams

```rust
use futures::stream::{self, StreamExt};
use tokio::time::{sleep, Duration};

// Créer un stream asynchrone
async fn compter_lentement() -> impl futures::Stream<Item = i32> {
    stream::unfold(0, |n| async move {
        if n >= 5 {
            return None;
        }
        sleep(Duration::from_millis(100)).await;
        Some((n, n + 1))
    })
}

#[tokio::main]
async fn main() {
    // Stream de nombres
    let stream = stream::iter(vec![1, 2, 3, 4, 5]);
    stream
        .filter(|&x| futures::future::ready(x % 2 == 0))
        .map(|x| x * 2)
        .for_each(|x| async move { println!("{}", x) })
        .await;

    // Stream lent
    let mut s = compter_lentement().await;
    while let Some(val) = s.next().await {
        println!("Stream: {}", val);
    }

    // Buffered : exécuter N futures en parallèle
    let resultats: Vec<i32> = stream::iter(0..10)
        .map(|i| async move {
            sleep(Duration::from_millis(10)).await;
            i * i
        })
        .buffer_unordered(4)  // max 4 en parallèle
        .collect()
        .await;
    println!("{:?}", resultats);
}
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Montrer `cargo add tokio --features full` et `cargo add reqwest --features json` dans le terminal. Montrer les sorties de Cargo qui télécharge et compile les dépendances. Ensuite lancer l'exemple `reqwest` et montrer les données JSON reçues depuis jsonplaceholder.typicode.com.
> **Expliquer :** Expliquer le runtime Tokio : c'est lui qui gère le scheduling des futures. Contraster avec Java où les threads OS sont gérés par la JVM, et avec Python asyncio. Mentionner que Tokio utilise un pool de threads (multi-thread runtime) pour les machines multi-cœurs.
---

## Récapitulatif

| Concept | Syntaxe | Description |
|---------|---------|-------------|
| Fonction async | `async fn f() -> T` | Retourne `impl Future<Output=T>` |
| Attendre | `.await` | Exécute la future |
| Runtime | `#[tokio::main]` | Initialise Tokio |
| Concurrent | `tokio::join!(f1, f2)` | Lance en parallèle, attend tous |
| Race | `tokio::select!` | Premier terminé gagne |
| Tâche | `tokio::spawn(future)` | Tâche indépendante |
| Bloquant | `spawn_blocking(|| ...)` | Code bloquant sans bloquer le runtime |
| Channel | `mpsc::channel()` | Communication entre tâches |
| Timeout | `timeout(dur, future)` | Annule si trop lent |
| Stream | `StreamExt::next()` | Itérateur asynchrone |
