# Ansible Tower et Vagrant

> Jour 3 - Apres-midi (~3h30)

## Table des matieres

1. [Presentation d'Ansible Tower](#presentation-dansible-tower)
2. [Introduction a Vagrant](#introduction-a-vagrant)
3. [Installation d'AWX via Docker](#installation-dawx-via-docker)
4. [TP : Configurer Ansible Tower/AWX pour executer des playbooks et superviser leur execution](#tp--configurer-ansible-towerawx-pour-executer-des-playbooks-et-superviser-leur-execution)

---

## Presentation d'Ansible Tower

### Tower vs AWX

**Ansible Tower** est la version commerciale (Red Hat) d'une plateforme de gestion centralisee pour Ansible. **AWX** est son equivalent open-source, maintenu par la communaute.

| Critere | Ansible Tower | AWX |
|---------|--------------|-----|
| Licence | Commercial (Red Hat) | Open-source (Apache 2.0) |
| Support | Support Red Hat | Communaute uniquement |
| Releases | Versions stables, Long Term Support | Releases frequentes, potentiellement instables |
| Installation | RPM, Installer officiel | Docker, Kubernetes (AWX Operator) |
| Cout | Payant (par noeud gere) | Gratuit |
| Usage recommande | Production entreprise | Developpement, formation, petits deployements |

Pour la formation, nous utiliserons **AWX** qui offre les memes fonctionnalites que Tower.

### Fonctionnalites principales

#### Interface web

AWX fournit une interface graphique complete pour gerer l'ensemble de l'infrastructure Ansible :

- Tableau de bord avec vue d'ensemble de l'activite
- Visualisation des resultats d'execution en temps reel
- Historique complet de tous les jobs
- Gestion des utilisateurs et des equipes

#### RBAC (Role-Based Access Control)

Le controle d'acces base sur les roles permet de definir precisement qui peut faire quoi :

- **Admin** : acces complet a la plateforme
- **Auditor** : lecture seule sur l'ensemble de la plateforme
- **Member** : acces aux ressources de son organisation
- **Execute** : droit d'executer un job template specifique
- **Read** : droit de voir un job template specifique

```
Organisation
├── Equipe Dev
│   ├── Utilisateur A (Admin)
│   └── Utilisateur B (Execute)
└── Equipe Ops
    ├── Utilisateur C (Admin)
    └── Utilisateur D (Read)
```

#### Planification des jobs

AWX permet de planifier l'execution automatique des playbooks selon un calendrier :

- Execution ponctuelle ou recurrente (cron)
- Fenetres de maintenance
- Fuseaux horaires configurables

#### Notifications

Integration avec de nombreux canaux de notification :

- Email
- Slack
- Microsoft Teams
- Webhook personnalise
- PagerDuty

Les notifications peuvent etre declenchees sur :
- Succes d'un job
- Echec d'un job
- Debut d'un job

#### API REST

AWX expose une API REST complete pour l'automatisation et l'integration :

```bash
# Lister les job templates
curl -s -u admin:password https://awx.local/api/v2/job_templates/ | python3 -m json.tool

# Lancer un job template
curl -X POST -u admin:password \
  https://awx.local/api/v2/job_templates/1/launch/ \
  -H "Content-Type: application/json" \
  -d '{"extra_vars": {"version": "2.1.0"}}'

# Voir le statut d'un job
curl -s -u admin:password https://awx.local/api/v2/jobs/42/ | python3 -m json.tool
```

#### Gestion des inventaires

Les inventaires dans AWX peuvent etre :

- **Statiques** : definis manuellement dans l'interface
- **Dynamiques** : synchronises depuis une source externe (AWS, Azure, GCP, VMware, script personnalise)
- **Smart Inventories** : filtres dynamiques bases sur les facts des hotes

#### Gestion des credentials

AWX stocke de facon securisee les identifiants necessaires aux playbooks :

- Cles SSH
- Mots de passe machines
- Mots de passe Vault
- Tokens cloud (AWS, Azure, GCP)
- Tokens SCM (GitHub, GitLab)

Les credentials sont chiffres dans la base de donnees et ne sont jamais exposes dans les logs.

#### Workflow Templates

Les workflows permettent de chainer plusieurs job templates avec des conditions :

```
[Deployer Base de donnees] --succes--> [Deployer Application] --succes--> [Tests de smoke]
                           --echec---> [Notifier l'equipe]
                                                               --echec---> [Rollback]
```

Fonctionnalites des workflows :
- Branchement conditionnel (succes / echec / toujours)
- Convergence de plusieurs branches
- Demande d'approbation manuelle entre les etapes
- Variables partagees entre les etapes

---

## Introduction a Vagrant

### Qu'est-ce que Vagrant ?

**Vagrant** est un outil de HashiCorp pour creer et gerer des environnements de machines virtuelles de facon reproductible. Il permet de decrire une infrastructure dans un fichier texte (`Vagrantfile`) et de la provisionner automatiquement.

**Cas d'usage pour Ansible :**
- Creer rapidement des machines de test pour developper des playbooks
- Reproduire un environnement multi-machines (web, db, load balancer)
- Tester les roles Ansible avant de les deployer en production
- Creer un lab de formation complet en quelques minutes

### Syntaxe du Vagrantfile

Le `Vagrantfile` est ecrit en Ruby et decrit l'infrastructure souhaitee :

```ruby
# Vagrantfile
Vagrant.configure("2") do |config|

  # Image de base
  config.vm.box = "ubuntu/jammy64"

  # Configuration reseau
  config.vm.network "private_network", ip: "192.168.56.10"
  config.vm.network "forwarded_port", guest: 80, host: 8080

  # Ressources de la VM
  config.vm.provider "virtualbox" do |vb|
    vb.memory = "1024"
    vb.cpus = 2
    vb.name = "serveur-web"
  end

  # Dossier synchronise
  config.vm.synced_folder "./data", "/vagrant_data"

  # Provisionnement avec Ansible
  config.vm.provision "ansible" do |ansible|
    ansible.playbook = "playbooks/site.yml"
    ansible.inventory_path = "inventory/vagrant"
  end

end
```

### Providers

Vagrant supporte plusieurs providers (moteurs de virtualisation) :

- **VirtualBox** : provider par defaut, gratuit, multi-plateforme
- **Docker** : plus leger, utilise des conteneurs au lieu de VMs
- **VMware** : performant, necessite un plugin payant
- **Libvirt/KVM** : pour les systemes Linux
- **Hyper-V** : pour Windows

### Provisioners

Vagrant peut automatiser la configuration des VMs avec differents provisioners :

**Shell provisioner :**

```ruby
config.vm.provision "shell", inline: <<-SHELL
  apt-get update
  apt-get install -y nginx
SHELL
```

**Ansible provisioner (depuis l'hote) :**

```ruby
config.vm.provision "ansible" do |ansible|
  ansible.playbook = "site.yml"
  ansible.inventory_path = "inventory/vagrant"
  ansible.extra_vars = {
    env: "development"
  }
  ansible.tags = "install,config"
  ansible.verbose = "v"
end
```

**Ansible Local provisioner (depuis la VM) :**

```ruby
config.vm.provision "ansible_local" do |ansible|
  ansible.playbook = "site.yml"
  ansible.install = true  # Installe Ansible dans la VM
end
```

### Environnement multi-machines

Vagrant excelle pour creer des environnements complets avec plusieurs machines :

```ruby
# Vagrantfile multi-machines
Vagrant.configure("2") do |config|

  # Machine de controle Ansible
  config.vm.define "control" do |control|
    control.vm.box = "ubuntu/jammy64"
    control.vm.hostname = "control"
    control.vm.network "private_network", ip: "192.168.56.10"
    control.vm.provider "virtualbox" do |vb|
      vb.memory = "2048"
      vb.cpus = 2
    end
  end

  # Serveur web
  config.vm.define "web" do |web|
    web.vm.box = "ubuntu/jammy64"
    web.vm.hostname = "web"
    web.vm.network "private_network", ip: "192.168.56.11"
    web.vm.network "forwarded_port", guest: 80, host: 8080
    web.vm.provider "virtualbox" do |vb|
      vb.memory = "1024"
      vb.cpus = 1
    end
  end

  # Serveur base de donnees
  config.vm.define "db" do |db|
    db.vm.box = "ubuntu/jammy64"
    db.vm.hostname = "db"
    db.vm.network "private_network", ip: "192.168.56.12"
    db.vm.provider "virtualbox" do |vb|
      vb.memory = "1024"
      vb.cpus = 1
    end
  end

end
```

### Commandes essentielles

```bash
# Demarrer toutes les VMs
vagrant up

# Demarrer une VM specifique
vagrant up web

# Voir le statut des VMs
vagrant status

# Se connecter en SSH a une VM
vagrant ssh control
vagrant ssh web

# Arreter les VMs (sans les detruire)
vagrant halt

# Arreter une VM specifique
vagrant halt db

# Detruire toutes les VMs
vagrant destroy

# Detruire avec confirmation automatique
vagrant destroy -f

# Relancer le provisionnement sans recreer les VMs
vagrant provision

# Recharger les VMs (redemarrer + re-provisionner)
vagrant reload

# Afficher la configuration SSH (utile pour Ansible)
vagrant ssh-config
```

**Astuce pour generer un inventaire Ansible depuis Vagrant :**

```bash
# Obtenir les informations SSH
vagrant ssh-config web > ssh_config_web

# Utiliser dans ansible.cfg
# [ssh_connection]
# ssh_args = -F ssh_config_web
```

---

## Installation d'AWX via Docker

### Prerequis

- Docker et Docker Compose installes
- Minimum 4 Go de RAM disponible
- 20 Go d'espace disque
- Ports 80 et 443 disponibles

### Methode 1 : Installation avec docker-compose (recommandee pour la formation)

Cette methode utilise le projet `awx-docker-compose` qui simplifie l'installation.

#### Etape 1 : Installer les dependances

```bash
# Installer Docker
sudo apt-get update
sudo apt-get install -y docker.io docker-compose-plugin

# Ajouter l'utilisateur au groupe docker
sudo usermod -aG docker $USER
newgrp docker

# Verifier l'installation
docker --version
docker compose version
```

#### Etape 2 : Cloner le depot AWX

```bash
# Cloner le depot officiel AWX
git clone -b 23.5.1 https://github.com/ansible/awx.git
cd awx
```

#### Etape 3 : Preparer le fichier docker-compose

Creer un fichier `docker-compose.yml` pour AWX :

```yaml
# docker-compose.yml
version: '3.8'

services:
  # Base de donnees PostgreSQL
  postgres:
    image: postgres:15
    container_name: awx_postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: awx
      POSTGRES_PASSWORD: awxpostgres
      POSTGRES_DB: awx
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - awx_network

  # Cache Redis
  redis:
    image: redis:7
    container_name: awx_redis
    restart: unless-stopped
    networks:
      - awx_network

  # AWX Web (interface + API)
  awx_web:
    image: quay.io/ansible/awx:23.5.1
    container_name: awx_web
    restart: unless-stopped
    hostname: awxweb
    depends_on:
      - postgres
      - redis
    ports:
      - "8080:8052"
    environment:
      DATABASE_USER: awx
      DATABASE_PASSWORD: awxpostgres
      DATABASE_NAME: awx
      DATABASE_HOST: postgres
      DATABASE_PORT: 5432
      REDIS_HOST: redis
      REDIS_PORT: 6379
      AWX_ADMIN_USER: admin
      AWX_ADMIN_PASSWORD: password
    volumes:
      - awx_projects:/var/lib/awx/projects
      - awx_receptor:/var/lib/awx/receptor
    networks:
      - awx_network

  # AWX Task (execution des jobs)
  awx_task:
    image: quay.io/ansible/awx:23.5.1
    container_name: awx_task
    restart: unless-stopped
    hostname: awxtask
    depends_on:
      - awx_web
    command: launch_awx_task.sh
    environment:
      DATABASE_USER: awx
      DATABASE_PASSWORD: awxpostgres
      DATABASE_NAME: awx
      DATABASE_HOST: postgres
      DATABASE_PORT: 5432
      REDIS_HOST: redis
      REDIS_PORT: 6379
      SUPERVISOR_WEB_CONFIG_PATH: /etc/supervisord.conf
    volumes:
      - awx_projects:/var/lib/awx/projects
      - awx_receptor:/var/lib/awx/receptor
    networks:
      - awx_network

volumes:
  postgres_data:
  awx_projects:
  awx_receptor:

networks:
  awx_network:
    driver: bridge
```

#### Etape 4 : Lancer AWX

```bash
# Demarrer les conteneurs
docker compose up -d

# Verifier que tous les conteneurs sont en cours d'execution
docker compose ps

# Suivre les logs (attendre que l'initialisation soit terminee)
docker compose logs -f awx_web

# AWX est pret quand vous voyez :
# "AWX is now ready to accept connections"
```

#### Etape 5 : Acceder a l'interface

Ouvrir un navigateur et se rendre sur `http://localhost:8080`.

Identifiants par defaut :
- **Utilisateur** : `admin`
- **Mot de passe** : `password`

### Methode 2 : Installation avec AWX Operator sur Kubernetes

Pour les environnements plus avances, AWX peut etre deploye sur Kubernetes via l'AWX Operator. Cette methode utilise Minikube pour un deploiement local.

#### Etape 1 : Installer Minikube

```bash
# Installer Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Demarrer un cluster
minikube start --cpus=4 --memory=6g --addons=ingress
```

#### Etape 2 : Deployer l'AWX Operator

```bash
# Installer le AWX Operator via Kustomize
cat > kustomization.yaml << 'EOF'
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
  - github.com/ansible/awx-operator/config/default?ref=2.10.0

images:
  - name: quay.io/ansible/awx-operator
    newTag: 2.10.0

namespace: awx
EOF

# Creer le namespace et deployer l'operator
kubectl create namespace awx
kubectl apply -k .

# Verifier que l'operator est en cours d'execution
kubectl get pods -n awx
```

#### Etape 3 : Creer une instance AWX

```yaml
# awx-instance.yaml
apiVersion: awx.ansible.com/v1beta1
kind: AWX
metadata:
  name: awx-formation
  namespace: awx
spec:
  service_type: NodePort
  nodeport_port: 30080
  admin_user: admin
  postgres_storage_class: standard
  projects_persistence: true
  projects_storage_size: 2Gi
```

```bash
# Deployer l'instance
kubectl apply -f awx-instance.yaml -n awx

# Suivre le deploiement (peut prendre 5-10 minutes)
kubectl get pods -n awx -w

# Recuperer le mot de passe admin
kubectl get secret awx-formation-admin-password -n awx -o jsonpath='{.data.password}' | base64 -d

# Acceder a AWX
minikube service awx-formation-service -n awx
```

### Verification de l'installation

Quelle que soit la methode choisie, verifier que AWX fonctionne :

```bash
# Tester l'API
curl -s -u admin:password http://localhost:8080/api/v2/ping/ | python3 -m json.tool

# Reponse attendue :
# {
#     "ha": false,
#     "version": "23.5.1",
#     "active_node": "awxweb",
#     ...
# }
```

---

## TP : Configurer Ansible Tower/AWX pour executer des playbooks et superviser leur execution

### Objectifs

- Installer AWX dans un environnement Vagrant multi-machines
- Configurer AWX : Organisation, Inventaire, Credentials, Projet
- Creer et executer un Job Template via l'interface web
- Creer un Workflow Template chainant plusieurs jobs
- Superviser l'execution des jobs en temps reel

### Prerequis

- VirtualBox installe
- Vagrant installe
- Minimum 8 Go de RAM disponible sur la machine hote
- Connexion internet (pour telecharger les images)

### Etape 1 : Creer l'environnement Vagrant multi-machines

Creer un repertoire pour le projet :

```bash
mkdir -p awx-lab
cd awx-lab
```

Creer le `Vagrantfile` avec 3 machines :

```ruby
# Vagrantfile
Vagrant.configure("2") do |config|

  config.vm.box = "ubuntu/jammy64"

  # Noeud de controle AWX
  config.vm.define "awx" do |awx|
    awx.vm.hostname = "awx"
    awx.vm.network "private_network", ip: "192.168.56.10"
    awx.vm.network "forwarded_port", guest: 8080, host: 8080
    awx.vm.provider "virtualbox" do |vb|
      vb.memory = "4096"
      vb.cpus = 2
      vb.name = "awx-control"
    end
    awx.vm.provision "shell", inline: <<-SHELL
      apt-get update
      apt-get install -y docker.io docker-compose-plugin git
      usermod -aG docker vagrant
      systemctl enable docker
      systemctl start docker
    SHELL
  end

  # Serveur web cible
  config.vm.define "web" do |web|
    web.vm.hostname = "web"
    web.vm.network "private_network", ip: "192.168.56.11"
    web.vm.provider "virtualbox" do |vb|
      vb.memory = "1024"
      vb.cpus = 1
      vb.name = "web-target"
    end
    web.vm.provision "shell", inline: <<-SHELL
      apt-get update
      apt-get install -y python3
    SHELL
  end

  # Serveur base de donnees cible
  config.vm.define "db" do |db|
    db.vm.hostname = "db"
    db.vm.network "private_network", ip: "192.168.56.12"
    db.vm.provider "virtualbox" do |vb|
      vb.memory = "1024"
      vb.cpus = 1
      vb.name = "db-target"
    end
    db.vm.provision "shell", inline: <<-SHELL
      apt-get update
      apt-get install -y python3
    SHELL
  end

  # Configuration SSH commune
  config.vm.provision "shell", inline: <<-SHELL
    sed -i 's/PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config
    systemctl restart sshd
  SHELL

end
```

Lancer les machines :

```bash
# Demarrer toutes les VMs
vagrant up

# Verifier le statut
vagrant status

# Resultat attendu :
# awx     running (virtualbox)
# web     running (virtualbox)
# db      running (virtualbox)
```

### Etape 2 : Installer AWX sur le noeud de controle

Se connecter au noeud AWX et installer la plateforme :

```bash
# Se connecter a la VM AWX
vagrant ssh awx

# Creer le repertoire de travail
mkdir -p ~/awx-deploy && cd ~/awx-deploy
```

Creer le fichier `docker-compose.yml` sur la VM :

```bash
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15
    container_name: awx_postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: awx
      POSTGRES_PASSWORD: awxpostgres
      POSTGRES_DB: awx
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - awx_network

  redis:
    image: redis:7
    container_name: awx_redis
    restart: unless-stopped
    networks:
      - awx_network

  awx_web:
    image: quay.io/ansible/awx:23.5.1
    container_name: awx_web
    restart: unless-stopped
    hostname: awxweb
    depends_on:
      - postgres
      - redis
    ports:
      - "8080:8052"
    environment:
      DATABASE_USER: awx
      DATABASE_PASSWORD: awxpostgres
      DATABASE_NAME: awx
      DATABASE_HOST: postgres
      DATABASE_PORT: 5432
      REDIS_HOST: redis
      REDIS_PORT: 6379
      AWX_ADMIN_USER: admin
      AWX_ADMIN_PASSWORD: FormationAWX2024
    volumes:
      - awx_projects:/var/lib/awx/projects
    networks:
      - awx_network

  awx_task:
    image: quay.io/ansible/awx:23.5.1
    container_name: awx_task
    restart: unless-stopped
    hostname: awxtask
    depends_on:
      - awx_web
    command: launch_awx_task.sh
    environment:
      DATABASE_USER: awx
      DATABASE_PASSWORD: awxpostgres
      DATABASE_NAME: awx
      DATABASE_HOST: postgres
      DATABASE_PORT: 5432
      REDIS_HOST: redis
      REDIS_PORT: 6379
    volumes:
      - awx_projects:/var/lib/awx/projects
    networks:
      - awx_network

volumes:
  postgres_data:
  awx_projects:

networks:
  awx_network:
    driver: bridge
EOF

# Lancer AWX
docker compose up -d

# Attendre que tous les conteneurs soient prets
docker compose ps

# Suivre les logs jusqu'a ce que AWX soit pret
docker compose logs -f awx_web
```

Verifier l'installation depuis la machine hote :

```bash
# Depuis la machine hote (pas la VM)
curl -s -u admin:FormationAWX2024 http://localhost:8080/api/v2/ping/
```

Ouvrir `http://localhost:8080` dans un navigateur. Se connecter avec `admin` / `FormationAWX2024`.

### Etape 3 : Preparer un depot Git avec les playbooks

Creer un depot Git (sur GitHub, GitLab ou localement) contenant les playbooks a executer. Voici la structure :

```bash
# Structure du depot
ansible-awx-projet/
├── inventory/
│   └── hosts.yml
├── playbooks/
│   ├── common.yml
│   ├── webserver.yml
│   └── database.yml
└── roles/
    └── common/
        └── tasks/
            └── main.yml
```

**playbooks/common.yml :**

```yaml
---
- name: Configuration commune
  hosts: all
  become: yes

  tasks:
    - name: Mettre a jour le cache apt
      ansible.builtin.apt:
        update_cache: yes
        cache_valid_time: 3600

    - name: Installer les paquets de base
      ansible.builtin.apt:
        name:
          - vim
          - curl
          - wget
          - htop
          - tree
        state: present

    - name: Configurer le fuseau horaire
      community.general.timezone:
        name: Europe/Paris

    - name: Afficher les informations du systeme
      ansible.builtin.debug:
        msg: |
          Hostname: {{ ansible_hostname }}
          OS: {{ ansible_distribution }} {{ ansible_distribution_version }}
          IP: {{ ansible_default_ipv4.address }}
          RAM: {{ ansible_memtotal_mb }} MB
```

**playbooks/webserver.yml :**

```yaml
---
- name: Deployer le serveur web
  hosts: webservers
  become: yes

  vars:
    nginx_port: 80
    site_name: "awx-demo"

  tasks:
    - name: Installer Nginx
      ansible.builtin.apt:
        name: nginx
        state: present

    - name: Deployer la page d'accueil
      ansible.builtin.copy:
        content: |
          <!DOCTYPE html>
          <html>
          <head><title>{{ site_name }}</title></head>
          <body>
            <h1>Deploye via AWX</h1>
            <p>Serveur : {{ ansible_hostname }}</p>
            <p>Date de deploiement : {{ ansible_date_time.iso8601 }}</p>
          </body>
          </html>
        dest: /var/www/html/index.html

    - name: Demarrer Nginx
      ansible.builtin.service:
        name: nginx
        state: started
        enabled: yes

    - name: Verifier que Nginx repond
      ansible.builtin.uri:
        url: "http://localhost:{{ nginx_port }}"
        return_content: yes
      register: http_result

    - name: Afficher le resultat
      ansible.builtin.debug:
        msg: "Nginx repond avec le code {{ http_result.status }}"
```

**playbooks/database.yml :**

```yaml
---
- name: Deployer la base de donnees
  hosts: dbservers
  become: yes

  tasks:
    - name: Installer PostgreSQL
      ansible.builtin.apt:
        name:
          - postgresql
          - postgresql-contrib
        state: present

    - name: Demarrer PostgreSQL
      ansible.builtin.service:
        name: postgresql
        state: started
        enabled: yes

    - name: Verifier que PostgreSQL ecoute
      ansible.builtin.wait_for:
        port: 5432
        timeout: 10

    - name: Afficher le statut
      ansible.builtin.debug:
        msg: "PostgreSQL est actif sur {{ ansible_hostname }}:5432"
```

**inventory/hosts.yml :**

```yaml
---
all:
  children:
    webservers:
      hosts:
        web:
          ansible_host: 192.168.56.11
    dbservers:
      hosts:
        db:
          ansible_host: 192.168.56.12
  vars:
    ansible_user: vagrant
    ansible_password: vagrant
    ansible_become_password: vagrant
```

Pousser ce depot sur un service Git accessible (GitHub, GitLab).

### Etape 4 : Configurer AWX via l'interface web

Suivre ces etapes dans l'interface AWX (`http://localhost:8080`) :

#### 4a. Creer une Organisation

1. Aller dans **Access > Organizations**
2. Cliquer sur **Add**
3. Remplir :
   - **Name** : `Formation Ansible`
   - **Description** : `Organisation pour le TP AWX`
4. Cliquer sur **Save**

#### 4b. Creer les Credentials

**Credentials SSH pour les machines cibles :**

1. Aller dans **Resources > Credentials**
2. Cliquer sur **Add**
3. Remplir :
   - **Name** : `Vagrant SSH`
   - **Organization** : `Formation Ansible`
   - **Credential Type** : `Machine`
   - **Username** : `vagrant`
   - **Password** : `vagrant`
   - **Privilege Escalation Method** : `sudo`
   - **Privilege Escalation Password** : `vagrant`
4. Cliquer sur **Save**

**Credentials SCM pour le depot Git (si depot prive) :**

1. Cliquer sur **Add**
2. Remplir :
   - **Name** : `Git Credentials`
   - **Organization** : `Formation Ansible`
   - **Credential Type** : `Source Control`
   - **Username** : votre nom d'utilisateur Git
   - **Password** ou **SSH Private Key** : selon votre configuration
3. Cliquer sur **Save**

#### 4c. Creer l'Inventaire

1. Aller dans **Resources > Inventories**
2. Cliquer sur **Add > Add inventory**
3. Remplir :
   - **Name** : `Lab Vagrant`
   - **Organization** : `Formation Ansible`
4. Cliquer sur **Save**
5. Aller dans l'onglet **Hosts** et cliquer sur **Add**
6. Ajouter le premier hote :
   - **Name** : `web`
   - **Variables** :
     ```yaml
     ansible_host: 192.168.56.11
     ```
7. Ajouter le second hote :
   - **Name** : `db`
   - **Variables** :
     ```yaml
     ansible_host: 192.168.56.12
     ```
8. Aller dans l'onglet **Groups** et creer :
   - Groupe `webservers` contenant l'hote `web`
   - Groupe `dbservers` contenant l'hote `db`

#### 4d. Creer le Projet (depuis Git)

1. Aller dans **Resources > Projects**
2. Cliquer sur **Add**
3. Remplir :
   - **Name** : `Projet Formation`
   - **Organization** : `Formation Ansible`
   - **Source Control Type** : `Git`
   - **Source Control URL** : URL de votre depot (ex: `https://github.com/votre-user/ansible-awx-projet.git`)
   - **Source Control Branch** : `main`
   - **Source Control Credential** : `Git Credentials` (si depot prive)
   - Cocher **Update Revision on Launch** (synchronisation automatique avant chaque job)
4. Cliquer sur **Save**
5. Attendre que la synchronisation se termine (icone verte)

### Etape 5 : Creer et executer un Job Template

1. Aller dans **Resources > Templates**
2. Cliquer sur **Add > Add job template**
3. Remplir :
   - **Name** : `Deployer Serveur Web`
   - **Job Type** : `Run`
   - **Inventory** : `Lab Vagrant`
   - **Project** : `Projet Formation`
   - **Playbook** : `playbooks/webserver.yml`
   - **Credentials** : `Vagrant SSH`
   - **Limit** : (laisser vide pour executer sur tous les hotes du playbook)
   - **Verbosity** : `1 (Verbose)`
   - Cocher **Enable Privilege Escalation**
4. Cliquer sur **Save**

**Executer le job :**

1. Cliquer sur le bouton **Launch** (icone fusee) du job template
2. Observer l'execution en temps reel dans la vue **Output**
3. Chaque tache affiche son statut : ok (vert), changed (orange), failed (rouge)
4. A la fin, verifier le resume : nombre de taches ok, changed, failed, skipped

**Creer un second job template pour la base de donnees :**

Repeter la procedure avec :
- **Name** : `Deployer Base de Donnees`
- **Playbook** : `playbooks/database.yml`

**Et un troisieme pour la configuration commune :**

- **Name** : `Configuration Commune`
- **Playbook** : `playbooks/common.yml`

### Etape 6 : Creer un Workflow Template

Le workflow va chainer les trois jobs dans un ordre logique avec gestion des erreurs.

1. Aller dans **Resources > Templates**
2. Cliquer sur **Add > Add workflow template**
3. Remplir :
   - **Name** : `Deploiement Complet`
   - **Organization** : `Formation Ansible`
   - **Inventory** : `Lab Vagrant`
4. Cliquer sur **Save**
5. L'editeur visuel de workflow s'ouvre

**Construire le workflow :**

1. Cliquer sur **Start** puis sur le bouton **+**
2. Selectionner **Configuration Commune** > cliquer sur **Save**
3. Survoler le noeud "Configuration Commune", cliquer sur **+** (condition : **On Success**)
4. Selectionner **Deployer Base de Donnees** > cliquer sur **Save**
5. Survoler le noeud "Configuration Commune", cliquer sur **+** (condition : **On Success**)
6. Selectionner **Deployer Serveur Web** > cliquer sur **Save**

Le workflow resultant :

```
                              --succes--> [Deployer Base de Donnees]
[Configuration Commune] ---<
                              --succes--> [Deployer Serveur Web]
```

7. Cliquer sur **Save** pour enregistrer le workflow

**Executer le workflow :**

1. Cliquer sur **Launch**
2. Observer l'execution : les noeuds passent au vert au fur et a mesure
3. Les jobs "Base de Donnees" et "Serveur Web" s'executent en parallele apres le succes de "Configuration Commune"
4. Cliquer sur chaque noeud pour voir le detail de l'execution

### Etape 7 : Superviser l'execution

#### Tableau de bord

Le tableau de bord AWX (`http://localhost:8080/#/home`) affiche :

- Le nombre de jobs recents (succes/echec)
- Les hotes geres
- Les inventaires actifs
- Les projets synchronises

#### Historique des jobs

1. Aller dans **Views > Jobs**
2. Chaque job affiche : statut, date, duree, template, utilisateur
3. Cliquer sur un job pour voir le detail complet (sortie, taches, hotes)

#### Activite des hotes

1. Aller dans **Resources > Inventories > Lab Vagrant > Hosts**
2. Cliquer sur un hote pour voir l'historique des jobs executes sur cet hote
3. L'onglet **Facts** affiche les facts collectes lors de la derniere execution

### Verification finale

```bash
# Verifier que Nginx fonctionne sur le serveur web
curl http://192.168.56.11

# Verifier que PostgreSQL fonctionne sur le serveur DB
vagrant ssh db -c "sudo systemctl status postgresql"

# Lister les jobs via l'API AWX
curl -s -u admin:FormationAWX2024 http://localhost:8080/api/v2/jobs/ | python3 -m json.tool | head -50
```

### Nettoyage

```bash
# Arreter AWX (depuis la VM awx)
vagrant ssh awx -c "cd ~/awx-deploy && docker compose down"

# Detruire les VMs
vagrant destroy -f
```

### Livrables

- Un environnement Vagrant multi-machines fonctionnel (3 VMs)
- AWX installe et accessible via l'interface web
- Une Organisation, un Inventaire, des Credentials et un Projet configures dans AWX
- Trois Job Templates fonctionnels (common, webserver, database)
- Un Workflow Template chainant les trois jobs
- Capture d'ecran ou demonstration de l'execution reussie d'un workflow

### Criteres de validation

| Critere | Attendu |
|---------|---------|
| Environnement Vagrant | 3 VMs demarrees et accessibles (awx, web, db) |
| Installation AWX | Interface web accessible sur http://localhost:8080 |
| Organisation | Organisation "Formation Ansible" creee |
| Inventaire | Inventaire avec 2 hotes (web, db) et 2 groupes (webservers, dbservers) |
| Credentials | Credentials SSH fonctionnels permettant la connexion aux cibles |
| Projet | Projet synchronise depuis Git (icone verte) |
| Job Template | Au moins un job template execute avec succes |
| Workflow | Workflow chainant les 3 jobs, execute avec succes |
| Supervision | Capacite a consulter les logs d'execution et l'historique des jobs |

---

## Ressources

- [Documentation AWX](https://ansible.readthedocs.io/projects/awx/en/latest/)
- [AWX Operator GitHub](https://github.com/ansible/awx-operator)
- [Documentation Vagrant](https://developer.hashicorp.com/vagrant/docs)
- [Ansible Tower User Guide](https://docs.ansible.com/ansible-tower/latest/html/userguide/index.html)

---

**Cours precedent :** [06-Ansible-Vault](../06-Ansible-Vault/README.md)
