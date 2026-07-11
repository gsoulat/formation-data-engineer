# Mise en Oeuvre d'un Projet Global

> Jour 4 - Apres-midi (~3h30)

## Table des matieres

1. [Description du projet](#description-du-projet)
2. [Simulation de cas reels](#simulation-de-cas-reels)
3. [TP : Realiser un projet global en autonomie](#tp--realiser-un-projet-global-en-autonomie)

---

## Description du projet

### Contexte

Ce projet final met en pratique l'ensemble des competences acquises durant la formation Ansible. Il s'agit de deployer une infrastructure complete de production, simulant un environnement reel avec des contraintes de securite, de performance et de maintenabilite.

### Infrastructure cible

L'infrastructure a deployer comprend 4 couches :

```
                        ┌──────────────────────────────────────┐
                        │            Internet / Clients         │
                        └──────────────────┬───────────────────┘
                                           │
                        ┌──────────────────▼───────────────────┐
                        │        Load Balancer (HAProxy)        │
                        │        lb01 - 192.168.100.10          │
                        │                                       │
                        │  - Distribution du trafic HTTP        │
                        │  - Health checks sur les backends     │
                        │  - Page de statistiques               │
                        │  - Firewall (UFW)                     │
                        └──────────────────┬───────────────────┘
                                           │
                        ┌──────────────────┴───────────────────┐
                        │                                      │
            ┌───────────▼────────────┐          ┌──────────────▼───────────┐
            │   Web Server 1         │          │   Web Server 2           │
            │   Nginx + Application  │          │   Nginx + Application    │
            │   web01 - 192.168.100.11│         │   web02 - 192.168.100.12 │
            │                        │          │                          │
            │   - Nginx reverse proxy│          │   - Nginx reverse proxy  │
            │   - Application deployee│         │   - Application deployee │
            │   - Firewall (UFW)     │          │   - Firewall (UFW)       │
            └───────────┬────────────┘          └──────────────┬───────────┘
                        │                                      │
                        └──────────────────┬───────────────────┘
                                           │
                        ┌──────────────────▼───────────────────┐
                        │     Base de Donnees (MySQL/PostgreSQL)│
                        │     db01 - 192.168.100.20             │
                        │                                       │
                        │   - Base de donnees applicative        │
                        │   - Utilisateur applicatif             │
                        │   - Configuration optimisee            │
                        │   - Firewall (UFW)                     │
                        └───────────────────────────────────────┘
```

### Composants detailles

**1. Load Balancer (HAProxy) :**
- HAProxy installe et configure
- Distribution du trafic en round-robin vers les 2 serveurs web
- Health checks HTTP sur l'endpoint `/health` de chaque backend
- Page de statistiques accessible sur le port 8404
- Firewall UFW : ports 80 (HTTP) et 8404 (stats) ouverts, le reste ferme

**2. Serveurs Web (Nginx + Application) :**
- Nginx installe et configure en tant que serveur web
- Application deployee (site statique ou dynamique)
- Endpoint `/health` pour les health checks du load balancer
- Connexion a la base de donnees via le fichier de configuration
- Firewall UFW : port 80 (HTTP) ouvert uniquement depuis le load balancer et le reseau interne

**3. Base de Donnees (MySQL ou PostgreSQL) :**
- Serveur de base de donnees installe et securise
- Base de donnees applicative creee
- Utilisateur applicatif avec privileges restreints
- Bind address configure pour accepter les connexions du reseau interne
- Firewall UFW : port 3306 (ou 5432) ouvert uniquement depuis les serveurs web

**4. Firewall (UFW) sur tous les serveurs :**
- SSH (port 22) autorise depuis le reseau d'administration
- Politique par defaut : deny incoming, allow outgoing
- Regles specifiques a chaque role

---

## Simulation de cas reels

Le projet se deroule en 4 phases qui simulent des situations courantes en environnement de production.

### Phase 1 : Deploiement initial de l'infrastructure

La premiere phase consiste a deployer l'ensemble de l'infrastructure depuis zero. Le playbook principal `site.yml` orchestre le deploiement dans l'ordre correct :

1. Configuration commune de tous les serveurs (paquets de base, timezone, firewall de base, SSH)
2. Deploiement et configuration de la base de donnees
3. Deploiement des serveurs web avec l'application
4. Configuration du load balancer

L'ordre est important : la base de donnees doit etre prete avant que les serveurs web ne tentent de s'y connecter. Le load balancer doit etre configure en dernier pour ne pas envoyer de trafic vers des backends non prets.

```yaml
# playbooks/site.yml
---
- name: Phase 1 - Configuration commune
  hosts: all
  roles:
    - common

- name: Phase 1 - Base de donnees
  hosts: databases
  roles:
    - mysql

- name: Phase 1 - Serveurs web
  hosts: webservers
  roles:
    - nginx
    - app

- name: Phase 1 - Load balancer
  hosts: loadbalancers
  roles:
    - haproxy
```

### Phase 2 : Mise a jour de l'application (rolling update)

Apres le deploiement initial, une nouvelle version de l'application doit etre deployee sans interruption de service. Le rolling update traite les serveurs un par un :

1. Retirer le serveur du pool HAProxy
2. Deployer la nouvelle version
3. Verifier que le serveur repond correctement
4. Remettre le serveur dans le pool

```yaml
# playbooks/rolling-update.yml
---
- name: Phase 2 - Rolling update de l'application
  hosts: webservers
  serial: 1
  become: yes

  vars:
    app_version: "2.0.0"

  tasks:
    - name: Retirer le serveur du load balancer
      haproxy:
        state: disabled
        host: "{{ inventory_hostname }}"
        socket: /var/run/haproxy/admin.sock
        backend: http_back
      delegate_to: "{{ groups['loadbalancers'][0] }}"

    - name: Deployer la nouvelle version
      template:
        src: templates/index.html.j2
        dest: "{{ app_dir }}/index.html"
        owner: "{{ app_user }}"

    - name: Mettre a jour le fichier de configuration
      template:
        src: templates/app.conf.j2
        dest: "{{ app_dir }}/config.ini"
        owner: "{{ app_user }}"
        mode: '0600'

    - name: Recharger Nginx
      systemd:
        name: nginx
        state: reloaded

    - name: Verifier que le serveur repond
      uri:
        url: "http://localhost/health"
        status_code: 200
      retries: 10
      delay: 3

    - name: Remettre le serveur dans le load balancer
      haproxy:
        state: enabled
        host: "{{ inventory_hostname }}"
        socket: /var/run/haproxy/admin.sock
        backend: http_back
      delegate_to: "{{ groups['loadbalancers'][0] }}"
```

### Phase 3 : Ajout d'un service (monitoring avec node_exporter)

Un nouveau besoin emerge : ajouter du monitoring sur tous les serveurs en installant Prometheus Node Exporter. Ce scenario simule l'ajout d'un service transverse a une infrastructure existante.

```yaml
# playbooks/add-monitoring.yml
---
- name: Phase 3 - Installer node_exporter sur tous les serveurs
  hosts: all
  become: yes

  vars:
    node_exporter_version: "1.7.0"
    node_exporter_port: 9100

  tasks:
    - name: Creer l'utilisateur node_exporter
      user:
        name: node_exporter
        system: yes
        shell: /bin/false
        create_home: no

    - name: Telecharger node_exporter
      get_url:
        url: "https://github.com/prometheus/node_exporter/releases/download/v{{ node_exporter_version }}/node_exporter-{{ node_exporter_version }}.linux-amd64.tar.gz"
        dest: /tmp/node_exporter.tar.gz

    - name: Extraire node_exporter
      unarchive:
        src: /tmp/node_exporter.tar.gz
        dest: /tmp/
        remote_src: yes

    - name: Copier le binaire
      copy:
        src: "/tmp/node_exporter-{{ node_exporter_version }}.linux-amd64/node_exporter"
        dest: /usr/local/bin/node_exporter
        remote_src: yes
        mode: '0755'
        owner: node_exporter

    - name: Creer le service systemd
      copy:
        content: |
          [Unit]
          Description=Prometheus Node Exporter
          After=network.target

          [Service]
          User=node_exporter
          Group=node_exporter
          Type=simple
          ExecStart=/usr/local/bin/node_exporter

          [Install]
          WantedBy=multi-user.target
        dest: /etc/systemd/system/node_exporter.service
      notify: Redemarrer node_exporter

    - name: Demarrer et activer node_exporter
      systemd:
        name: node_exporter
        state: started
        enabled: yes
        daemon_reload: yes

    - name: Ouvrir le port dans le firewall
      ufw:
        rule: allow
        port: "{{ node_exporter_port }}"
        proto: tcp
        src: 192.168.100.0/24

    - name: Verifier que node_exporter repond
      uri:
        url: "http://localhost:{{ node_exporter_port }}/metrics"
        status_code: 200
      retries: 3
      delay: 5

  handlers:
    - name: Redemarrer node_exporter
      systemd:
        name: node_exporter
        state: restarted
```

### Phase 4 : Correction d'un bug de configuration

Un probleme est detecte en production : la connexion entre les serveurs web et la base de donnees utilise une mauvaise adresse IP. Ce scenario simule la correction rapide d'un bug de configuration avec verification.

```yaml
# playbooks/fix-db-connection.yml
---
- name: Phase 4 - Corriger la configuration de connexion DB
  hosts: webservers
  become: yes

  tasks:
    - name: Sauvegarder la configuration actuelle
      copy:
        src: "{{ app_dir }}/config.ini"
        dest: "{{ app_dir }}/config.ini.bak"
        remote_src: yes

    - name: Corriger l'adresse de la base de donnees
      lineinfile:
        path: "{{ app_dir }}/config.ini"
        regexp: '^host\s*='
        line: "host = {{ db_host }}"
      notify: Recharger Nginx

    - name: Verifier la connectivite vers la base de donnees
      wait_for:
        host: "{{ db_host }}"
        port: "{{ db_port }}"
        timeout: 10

    - name: Verifier que l'application repond
      uri:
        url: "http://localhost/health"
        status_code: 200
      retries: 5
      delay: 3

  handlers:
    - name: Recharger Nginx
      systemd:
        name: nginx
        state: reloaded
```

---

## TP : Realiser un projet global en autonomie

### Objectifs

- Demontrer la maitrise de tous les concepts Ansible etudies durant la formation
- Structurer un projet complet selon les bonnes pratiques
- Deployer une infrastructure multi-tier fonctionnelle
- Utiliser les roles, variables, templates Jinja2, Vault et les inventaires structures
- Mettre en oeuvre les 4 phases de simulation

### Architecture cible detaillee

```
Reseau : 192.168.100.0/24

    ┌─────────────────────────────────────────────────────────────────┐
    │                     Reseau interne                              │
    │                                                                 │
    │   ┌──────────┐     ┌──────────┐  ┌──────────┐   ┌──────────┐  │
    │   │  HAProxy │     │  Nginx   │  │  Nginx   │   │  MySQL   │  │
    │   │  lb01    │────>│  web01   │  │  web02   │   │  db01    │  │
    │   │  :80     │────>│  :80     │  │  :80     │   │  :3306   │  │
    │   │  :8404   │     │          │──│          │──>│          │  │
    │   │  :9100   │     │  :9100   │  │  :9100   │   │  :9100   │  │
    │   └──────────┘     └──────────┘  └──────────┘   └──────────┘  │
    │   .10              .11           .12             .20           │
    │                                                                 │
    │   UFW: 80,8404,    UFW: 80,     UFW: 80,       UFW: 3306,    │
    │   22,9100          22,9100      22,9100         22,9100       │
    └─────────────────────────────────────────────────────────────────┘

Ports :
  - 80     : HTTP (HAProxy frontend / Nginx)
  - 8404   : HAProxy stats
  - 3306   : MySQL
  - 9100   : Prometheus Node Exporter
  - 22     : SSH (administration)
```

### Contraintes techniques

Le projet doit obligatoirement utiliser :

1. **Roles** : minimum 5 roles (common, haproxy, nginx, app, mysql)
2. **Variables** : variables externalisees dans `group_vars` et `host_vars`
3. **Templates Jinja2** : au moins 3 templates (configuration HAProxy, virtual host Nginx, configuration applicative)
4. **Ansible Vault** : tous les secrets (mots de passe, cles) chiffres
5. **Inventaire structure** : au moins 2 environnements (production et staging)
6. **Handlers** : utilises pour le rechargement des services apres modification de configuration
7. **Tags** : pour permettre l'execution selective des parties du playbook
8. **Idempotence** : tous les playbooks doivent etre idempotents

### Phases de livraison (progressive)

Le projet se realise en 4 phases successives. Chaque phase doit etre validee avant de passer a la suivante.

---

**Phase 1 : Structure et deploiement initial (1h30)**

Livrables attendus :
- Arborescence complete du projet
- Inventaires production et staging
- Variables et secrets configures (Vault)
- 5 roles implementes
- Playbook `site.yml` fonctionnel
- L'infrastructure complete est deployee et accessible

Verification :

```bash
# Structure du projet
tree projet-global/

# Syntaxe valide
ansible-playbook playbooks/site.yml --syntax-check

# Deploiement complet
ansible-playbook playbooks/site.yml --vault-password-file .vault_pass

# Verification
curl http://192.168.100.10          # Reponse via HAProxy
curl http://192.168.100.10:8404/stats  # Stats HAProxy
```

---

**Phase 2 : Rolling update (30 min)**

Livrables attendus :
- Playbook `rolling-update.yml` fonctionnel
- Mise a jour sans interruption de service demontree
- Verification automatique apres chaque serveur

Verification :

```bash
# Lancer le rolling update
ansible-playbook playbooks/rolling-update.yml

# Pendant le rolling update, verifier la disponibilite
while true; do curl -s -o /dev/null -w "%{http_code}" http://192.168.100.10; echo; sleep 1; done
# Toutes les reponses doivent etre 200
```

---

**Phase 3 : Ajout monitoring (30 min)**

Livrables attendus :
- Playbook `add-monitoring.yml` fonctionnel
- Node Exporter installe et actif sur tous les serveurs
- Firewall mis a jour pour autoriser le port 9100

Verification :

```bash
# Installer le monitoring
ansible-playbook playbooks/add-monitoring.yml

# Verifier sur chaque serveur
curl http://192.168.100.10:9100/metrics | head -5
curl http://192.168.100.11:9100/metrics | head -5
curl http://192.168.100.12:9100/metrics | head -5
curl http://192.168.100.20:9100/metrics | head -5
```

---

**Phase 4 : Correction de bug (30 min)**

Livrables attendus :
- Playbook de correction fonctionnel
- Sauvegarde de la configuration precedente
- Verification automatique de la connectivite

Verification :

```bash
# Appliquer la correction
ansible-playbook playbooks/fix-db-connection.yml

# Verifier
curl http://192.168.100.10/health
```

---

### Livrables finaux

L'ensemble du projet doit etre livre avec la structure suivante :

```
projet-global/
├── ansible.cfg
├── requirements.yml
├── .ansible-lint
├── .vault_pass                     # (Non commite, dans .gitignore)
├── .gitignore
│
├── inventories/
│   ├── production/
│   │   ├── hosts.yml
│   │   ├── group_vars/
│   │   │   ├── all/
│   │   │   │   ├── vars.yml
│   │   │   │   └── vault.yml       # Chiffre
│   │   │   ├── webservers.yml
│   │   │   ├── databases.yml
│   │   │   └── loadbalancers.yml
│   │   └── host_vars/
│   │
│   └── staging/
│       ├── hosts.yml
│       └── group_vars/
│           └── all/
│               ├── vars.yml
│               └── vault.yml
│
├── playbooks/
│   ├── site.yml                    # Phase 1
│   ├── rolling-update.yml          # Phase 2
│   ├── add-monitoring.yml          # Phase 3
│   └── fix-db-connection.yml       # Phase 4
│
├── roles/
│   ├── common/
│   │   ├── tasks/main.yml
│   │   └── handlers/main.yml
│   ├── haproxy/
│   │   ├── tasks/main.yml
│   │   ├── templates/haproxy.cfg.j2
│   │   └── handlers/main.yml
│   ├── nginx/
│   │   ├── tasks/main.yml
│   │   ├── templates/vhost.conf.j2
│   │   └── handlers/main.yml
│   ├── app/
│   │   ├── tasks/main.yml
│   │   └── templates/
│   │       ├── index.html.j2
│   │       └── app.conf.j2
│   └── mysql/
│       ├── tasks/main.yml
│       ├── templates/my.cnf.j2
│       └── handlers/main.yml
│
└── README.md                       # Documentation du projet
```

### Criteres d'evaluation detailles

L'evaluation porte sur trois axes :

---

**Technique (50%)**

| Critere | Points | Details |
|---------|--------|---------|
| Deploiement fonctionnel | 15% | L'infrastructure complete est deployee et accessible via le load balancer |
| Roles correctement implementes | 10% | Les 5 roles sont fonctionnels, avec tasks, handlers et templates |
| Templates Jinja2 | 10% | Au moins 3 templates utilisant variables, conditions et boucles |
| Rolling update | 10% | Mise a jour sans interruption de service |
| Monitoring deploye | 5% | Node Exporter actif sur tous les serveurs |

---

**Production-ready (30%)**

| Critere | Points | Details |
|---------|--------|---------|
| Ansible Vault | 10% | Tous les secrets sont chiffres, convention `vault_` respectee |
| Firewall configure | 10% | UFW actif sur tous les serveurs avec regles adaptees a chaque role |
| Idempotence | 10% | La deuxieme execution ne produit aucun changement (changed=0) |

---

**Bonnes pratiques (20%)**

| Critere | Points | Details |
|---------|--------|---------|
| Structure du projet | 5% | Arborescence conforme aux conventions Ansible |
| Nommage | 5% | Variables prefixees par role, noms de taches descriptifs |
| Inventaires multi-environnement | 5% | Production et staging avec variables separees |
| Documentation | 5% | README du projet, commentaires dans les templates |

---

### Indications de supervision formatrice

**Pendant la Phase 1 (deploiement initial) :**
- Verifier que les apprenants structurent correctement le projet avant d'ecrire du code
- S'assurer que le Vault est initialise des le debut
- Valider que la separation des roles est respectee (un role = un service)
- Intervenir si un apprenant passe trop de temps sur un role : proposer de partir d'un role simplifie et d'iterer

**Pendant la Phase 2 (rolling update) :**
- Verifier la comprehension du mot-cle `serial`
- S'assurer que le `delegate_to` est compris
- Aide possible : fournir le squelette du playbook de rolling update

**Pendant la Phase 3 (monitoring) :**
- Laisser les apprenants chercher la documentation de node_exporter
- Verifier que les regles de firewall sont correctement ajoutees (pas remplacees)

**Pendant la Phase 4 (correction de bug) :**
- Introduire volontairement un bug dans la configuration d'un apprenant (modifier l'adresse IP de la base de donnees)
- Observer la demarche de diagnostic : utilisent-ils le mode verbose ? le module debug ?
- Verifier que la sauvegarde est effectuee avant la correction

**Points d'attention generaux :**
- Encourager l'utilisation reguliere de `--check --diff` avant chaque deploiement
- Rappeler l'importance de tester l'idempotence (executer deux fois le playbook)
- S'assurer que les apprenants ne commettent pas le fichier `.vault_pass` dans Git

---

**Retour au sommaire Jour 4 :** [../README.md](../README.md)
