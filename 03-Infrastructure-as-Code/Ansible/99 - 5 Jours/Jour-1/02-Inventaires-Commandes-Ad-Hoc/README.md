# Inventaires et Commandes Ad Hoc

> Jour 1 - Apres-midi (~3h30)

## Table des matieres

1. [Introduction aux inventaires d'hotes geres](#introduction-aux-inventaires-dhôtes-gérés)
2. [Utilisation des commandes ad hoc](#utilisation-des-commandes-ad-hoc)
3. [TP : Configurer un inventaire et executer des commandes ad hoc](#tp--configurer-un-inventaire-et-exécuter-des-commandes-ad-hoc)

---

## Introduction aux inventaires d'hotes geres

L'**inventaire** est le point de depart de toute automatisation Ansible. Il definit la liste des machines (hosts) que Ansible va gerer, comment s'y connecter, et comment les organiser logiquement.

### Inventaire statique

Un inventaire statique est un fichier texte dans lequel on declare manuellement les machines cibles. Ansible supporte deux formats principaux : **INI** et **YAML**.

#### Format INI

Le format INI est le format historique. Il est simple et rapide a ecrire.

```ini
# inventory.ini

# Hosts sans groupe (appartiendront au groupe "ungrouped")
serveur-standalone.example.com

# Groupe webservers
[webservers]
web1 ansible_host=192.168.56.10 ansible_user=ubuntu
web2 ansible_host=192.168.56.11 ansible_user=ubuntu
web3 ansible_host=192.168.56.12 ansible_user=ubuntu

# Groupe databases
[databases]
db1 ansible_host=192.168.56.20 ansible_user=ubuntu
db2 ansible_host=192.168.56.21 ansible_user=ubuntu

# Groupe loadbalancers
[loadbalancers]
lb1 ansible_host=192.168.56.30 ansible_user=ubuntu

# Variables de groupe
[webservers:vars]
http_port=80
nginx_version=1.24

[databases:vars]
mysql_port=3306

# Variables globales
[all:vars]
ansible_python_interpreter=/usr/bin/python3
ansible_ssh_private_key_file=~/.ssh/ansible_key
```

**Utilisation des ranges pour simplifier l'ecriture :**

```ini
[webservers]
web[01:10].example.com        # web01.example.com a web10.example.com

[databases]
db-[a:c].example.com          # db-a, db-b, db-c
```

#### Format YAML

Le format YAML est le format moderne et recommande pour les inventaires complexes. Il offre une meilleure lisibilite et une structure hierarchique naturelle.

```yaml
# inventory.yml
all:
  vars:
    ansible_python_interpreter: /usr/bin/python3
    ansible_ssh_private_key_file: ~/.ssh/ansible_key

  hosts:
    serveur-standalone.example.com:

  children:
    webservers:
      hosts:
        web1:
          ansible_host: 192.168.56.10
          ansible_user: ubuntu
        web2:
          ansible_host: 192.168.56.11
          ansible_user: ubuntu
        web3:
          ansible_host: 192.168.56.12
          ansible_user: ubuntu
      vars:
        http_port: 80
        nginx_version: "1.24"

    databases:
      hosts:
        db1:
          ansible_host: 192.168.56.20
          ansible_user: ubuntu
        db2:
          ansible_host: 192.168.56.21
          ansible_user: ubuntu
      vars:
        mysql_port: 3306

    loadbalancers:
      hosts:
        lb1:
          ansible_host: 192.168.56.30
          ansible_user: ubuntu
```

### Inventaire dynamique

Un inventaire dynamique genere la liste des machines **a la volee** en interrogeant une source externe (API cloud, CMDB, base de donnees, etc.). C'est indispensable dans les environnements cloud ou les instances sont creees et detruites en permanence.

#### Concept

Un inventaire dynamique est un script executable qui repond a deux arguments :

- `--list` : retourne l'ensemble de l'inventaire au format JSON
- `--host <hostname>` : retourne les variables d'un host specifique

**Format de sortie attendu (`--list`) :**

```json
{
  "_meta": {
    "hostvars": {
      "web1": {
        "ansible_host": "10.0.1.10",
        "ansible_user": "ubuntu"
      }
    }
  },
  "webservers": {
    "hosts": ["web1", "web2"],
    "vars": {
      "http_port": 80
    }
  },
  "databases": {
    "hosts": ["db1"]
  }
}
```

#### Script Python d'inventaire dynamique

```python
#!/usr/bin/env python3
"""Inventaire dynamique simple pour Ansible."""

import json
import sys


def get_inventory():
    """Retourne l'inventaire complet."""
    return {
        "_meta": {
            "hostvars": {
                "web1": {
                    "ansible_host": "192.168.56.10",
                    "ansible_user": "ubuntu"
                },
                "web2": {
                    "ansible_host": "192.168.56.11",
                    "ansible_user": "ubuntu"
                },
                "db1": {
                    "ansible_host": "192.168.56.20",
                    "ansible_user": "ubuntu"
                }
            }
        },
        "webservers": {
            "hosts": ["web1", "web2"],
            "vars": {
                "http_port": 80
            }
        },
        "databases": {
            "hosts": ["db1"],
            "vars": {
                "mysql_port": 3306
            }
        }
    }


def get_host(hostname):
    """Retourne les variables d'un host specifique."""
    inventory = get_inventory()
    return inventory["_meta"]["hostvars"].get(hostname, {})


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--list":
        print(json.dumps(get_inventory(), indent=2))
    elif len(sys.argv) == 3 and sys.argv[1] == "--host":
        print(json.dumps(get_host(sys.argv[2]), indent=2))
    else:
        print(f"Usage: {sys.argv[0]} --list | --host <hostname>")
        sys.exit(1)
```

```bash
# Rendre le script executable
chmod +x dynamic_inventory.py

# Tester le script
./dynamic_inventory.py --list
./dynamic_inventory.py --host web1

# Utiliser avec Ansible
ansible all -i dynamic_inventory.py -m ping
```

#### Plugins d'inventaire cloud (AWS, Azure, GCP)

Les plugins d'inventaire sont la methode moderne et recommandee pour les inventaires dynamiques cloud. Ils s'installent via les collections Ansible.

**Plugin AWS EC2 :**

```bash
# Installer la collection AWS
ansible-galaxy collection install amazon.aws
```

```yaml
# inventory/aws_ec2.yml
plugin: amazon.aws.aws_ec2
regions:
  - eu-west-1
filters:
  instance-state-name: running
  tag:Environment: production
keyed_groups:
  - key: tags.Role
    prefix: role
hostnames:
  - tag:Name
  - private-ip-address
compose:
  ansible_host: public_ip_address
  ansible_user: "'ubuntu'"
```

**Plugin Azure :**

```bash
ansible-galaxy collection install azure.azcollection
```

```yaml
# inventory/azure_rm.yml
plugin: azure.azcollection.azure_rm
auth_source: auto
include_vm_resource_groups:
  - my-resource-group
keyed_groups:
  - key: tags.Role
    prefix: role
  - key: location
    prefix: loc
compose:
  ansible_host: public_ipv4_addresses[0]
  ansible_user: "'azureuser'"
```

**Plugin GCP :**

```bash
ansible-galaxy collection install google.cloud
```

```yaml
# inventory/gcp_compute.yml
plugin: google.cloud.gcp_compute
projects:
  - my-gcp-project
filters:
  - status = RUNNING
keyed_groups:
  - key: labels.role
    prefix: role
compose:
  ansible_host: networkInterfaces[0].accessConfigs[0].natIP
  ansible_user: "'ubuntu'"
```

### Groupes et groupes enfants (children)

Les groupes permettent d'organiser les machines par fonction, environnement, localisation, ou tout autre critere logique. Les groupes enfants (children) permettent de creer des hierarchies.

**Format INI :**

```ini
[webservers]
web1
web2

[databases]
db1
db2

[loadbalancers]
lb1

# Groupes enfants avec :children
[production:children]
webservers
databases
loadbalancers

[frontend:children]
webservers
loadbalancers

[backend:children]
databases

# Variables du groupe parent
[production:vars]
environment=production
monitoring_enabled=true
```

**Format YAML :**

```yaml
all:
  children:
    webservers:
      hosts:
        web1:
        web2:
    databases:
      hosts:
        db1:
        db2:
    loadbalancers:
      hosts:
        lb1:

    # Groupes enfants
    production:
      children:
        webservers:
        databases:
        loadbalancers:
      vars:
        environment: production
        monitoring_enabled: true

    frontend:
      children:
        webservers:
        loadbalancers:

    backend:
      children:
        databases:
```

**Groupes implicites :** Ansible cree automatiquement deux groupes :

- `all` : contient tous les hosts
- `ungrouped` : contient les hosts qui n'appartiennent a aucun groupe explicite

### Patterns de selection

Les patterns permettent de cibler des sous-ensembles de l'inventaire.

```bash
# Tous les hosts
ansible all -m ping

# Un groupe specifique
ansible webservers -m ping

# Plusieurs groupes (union / OR)
ansible 'webservers:databases' -m ping

# Intersection (AND) : hosts dans webservers ET production
ansible 'webservers:&production' -m ping

# Exclusion (NOT) : webservers SAUF web1
ansible 'webservers:!web1' -m ping

# Combinaisons
ansible 'webservers:databases:!db2' -m ping

# Wildcards
ansible 'web*' -m ping

# Regex
ansible '~web[0-9]+' -m ping

# Index dans un groupe
ansible 'webservers[0]' -m ping       # Premier host
ansible 'webservers[0:1]' -m ping     # Deux premiers hosts
```

### group_vars et host_vars

La structure recommandee pour organiser les variables est d'utiliser des repertoires `group_vars/` et `host_vars/` a cote de l'inventaire.

```
projet-ansible/
├── ansible.cfg
├── inventory/
│   ├── production.yml
│   ├── group_vars/
│   │   ├── all.yml            # Variables pour tous les hosts
│   │   ├── webservers.yml     # Variables du groupe webservers
│   │   └── databases.yml      # Variables du groupe databases
│   └── host_vars/
│       ├── web1.yml           # Variables specifiques a web1
│       └── db1.yml            # Variables specifiques a db1
```

```yaml
# inventory/group_vars/all.yml
ansible_python_interpreter: /usr/bin/python3
ntp_server: ntp.example.com
dns_servers:
  - 8.8.8.8
  - 8.8.4.4
```

```yaml
# inventory/group_vars/webservers.yml
http_port: 80
https_port: 443
nginx_worker_processes: auto
```

```yaml
# inventory/group_vars/databases.yml
mysql_port: 3306
mysql_max_connections: 500
backup_enabled: true
```

```yaml
# inventory/host_vars/web1.yml
nginx_worker_processes: 8
ssl_certificate: /etc/ssl/certs/web1.crt
```

**Ordre de precedence des variables (de la plus basse a la plus haute) :**

1. `group_vars/all`
2. `group_vars/<nom_du_groupe>`
3. `host_vars/<nom_du_host>`
4. Variables d'inventaire (group vars)
5. Variables d'inventaire (host vars)
6. Variables de playbook (`vars`, `vars_files`)
7. Variables de task
8. Extra vars (`-e`)

### Commandes utiles pour explorer un inventaire

```bash
# Lister tous les hosts
ansible-inventory -i inventory.yml --list

# Afficher l'arborescence des groupes
ansible-inventory -i inventory.yml --graph

# Afficher les variables d'un host
ansible-inventory -i inventory.yml --host web1

# Lister les hosts d'un pattern
ansible webservers -i inventory.yml --list-hosts

# Verifier un pattern complexe
ansible 'webservers:&production' -i inventory.yml --list-hosts
```

---

## Utilisation des commandes ad hoc

Les commandes ad hoc permettent d'executer des taches ponctuelles sur un ou plusieurs hosts sans ecrire de playbook. Elles sont ideales pour les operations rapides de diagnostic, de maintenance ou de verification.

### Syntaxe generale

```
ansible <pattern> -i <inventaire> -m <module> -a "<arguments>" [options]
```

**Elements de la commande :**

| Element | Description |
|---------|-------------|
| `<pattern>` | Cible (host, groupe, pattern) |
| `-i <inventaire>` | Fichier d'inventaire (optionnel si configure dans `ansible.cfg`) |
| `-m <module>` | Module Ansible a utiliser |
| `-a "<arguments>"` | Arguments du module |
| `-f <nombre>` | Nombre de forks (parallelisme) |
| `-b` / `--become` | Executer avec elevation de privileges (sudo) |
| `-K` | Demander le mot de passe sudo |
| `-v` / `-vvv` | Mode verbose |

### Modules courants pour les commandes ad hoc

#### Module `ping`

Verifie la connectivite Ansible (pas un ping ICMP). Teste que l'on peut se connecter au host, que Python est disponible, et que le module peut s'executer.

```bash
# Ping tous les hosts
ansible all -m ping

# Ping un groupe
ansible webservers -m ping

# Ping un host specifique
ansible web1 -m ping
```

**Sortie attendue :**

```
web1 | SUCCESS => {
    "changed": false,
    "ping": "pong"
}
```

#### Module `command`

Execute une commande sur les hosts distants. C'est le module par defaut (pas besoin de `-m command`). Ne passe **pas** par le shell : pas de pipes, redirections ou variables d'environnement.

```bash
# Afficher le hostname
ansible all -m command -a "hostname"

# Equivalent (command est le module par defaut)
ansible all -a "hostname"

# Afficher l'uptime
ansible all -a "uptime"

# Verifier l'espace disque
ansible all -a "df -h"

# Lister les processus
ansible all -a "ps aux"
```

#### Module `shell`

Execute une commande **via le shell** (`/bin/sh`). Supporte les pipes, redirections, variables d'environnement et toutes les fonctionnalites du shell.

```bash
# Commande avec pipe
ansible all -m shell -a "ps aux | grep nginx"

# Redirection
ansible all -m shell -a "echo 'test' > /tmp/test.txt"

# Variables d'environnement
ansible all -m shell -a "echo $HOME"

# Commandes chainees
ansible all -m shell -a "cd /var/log && tail -5 syslog"
```

#### Module `copy`

Copie un fichier depuis le control node vers les managed nodes.

```bash
# Copier un fichier
ansible all -m copy -a "src=/etc/hosts dest=/tmp/hosts"

# Copier avec permissions specifiques
ansible webservers -m copy -a "src=index.html dest=/var/www/html/index.html owner=www-data group=www-data mode=0644"

# Creer un fichier avec du contenu
ansible all -m copy -a "content='Hello Ansible\n' dest=/tmp/hello.txt"
```

#### Module `file`

Gere les fichiers et repertoires (creation, suppression, permissions, liens symboliques).

```bash
# Creer un repertoire
ansible all -m file -a "path=/opt/app state=directory mode=0755"

# Creer un fichier vide
ansible all -m file -a "path=/tmp/marker state=touch"

# Supprimer un fichier
ansible all -m file -a "path=/tmp/test.txt state=absent"

# Modifier les permissions
ansible all -m file -a "path=/var/log/app.log owner=www-data group=www-data mode=0644"

# Creer un lien symbolique
ansible all -m file -a "src=/opt/app/current dest=/opt/app/latest state=link"
```

#### Module `setup`

Collecte les facts (informations systeme) d'un host. Tres utile pour le diagnostic.

```bash
# Collecter tous les facts
ansible web1 -m setup

# Filtrer les facts
ansible web1 -m setup -a "filter=ansible_distribution*"
ansible web1 -m setup -a "filter=ansible_memory_mb"
ansible web1 -m setup -a "filter=ansible_default_ipv4"

# Afficher uniquement l'OS
ansible all -m setup -a "filter=ansible_os_family"
```

#### Module `user`

Gere les comptes utilisateurs sur les managed nodes.

```bash
# Creer un utilisateur
ansible all -m user -a "name=deploy state=present shell=/bin/bash" -b

# Creer un utilisateur avec un groupe
ansible all -m user -a "name=appuser state=present groups=sudo append=yes" -b

# Supprimer un utilisateur
ansible all -m user -a "name=olduser state=absent remove=yes" -b
```

#### Module `service`

Gere les services systemd/init.

```bash
# Demarrer un service
ansible webservers -m service -a "name=nginx state=started" -b

# Redemarrer un service
ansible webservers -m service -a "name=nginx state=restarted" -b

# Arreter un service
ansible webservers -m service -a "name=nginx state=stopped" -b

# Activer un service au demarrage
ansible webservers -m service -a "name=nginx enabled=yes" -b

# Verifier le statut
ansible webservers -m shell -a "systemctl status nginx" -b
```

#### Modules d'installation de paquets

```bash
# Installer un paquet (Debian/Ubuntu)
ansible webservers -m apt -a "name=nginx state=present update_cache=yes" -b

# Installer plusieurs paquets
ansible all -m apt -a "name=curl,wget,vim state=present" -b

# Mettre a jour tous les paquets
ansible all -m apt -a "upgrade=dist" -b

# Installer un paquet (RHEL/CentOS)
ansible webservers -m yum -a "name=httpd state=present" -b
```

### Parallelisme avec `-f` (forks)

Par defaut, Ansible execute les commandes sur 5 hosts en parallele. L'option `-f` permet de modifier ce comportement.

```bash
# Executer sur 10 hosts en parallele
ansible all -m ping -f 10

# Executer sur 1 host a la fois (sequentiel)
ansible all -m ping -f 1

# Executer sur 20 hosts en parallele
ansible all -m apt -a "name=nginx state=present" -b -f 20
```

**Recommandations :**

- Augmenter les forks pour les grandes infrastructures (50-100 hosts)
- Reduire a 1 pour le debug ou les operations sensibles
- Attention a ne pas surcharger le control node (RAM, CPU, connexions SSH)

### Elevation de privileges (become)

L'option `--become` (ou `-b`) permet d'executer les commandes avec des privileges eleves (sudo).

```bash
# Executer en tant que root
ansible all -m apt -a "name=nginx state=present" --become

# Forme courte
ansible all -m apt -a "name=nginx state=present" -b

# Specifier l'utilisateur cible
ansible all -m command -a "whoami" --become --become-user=www-data

# Demander le mot de passe sudo
ansible all -m apt -a "name=nginx state=present" -b -K

# Specifier la methode d'elevation
ansible all -m command -a "whoami" --become --become-method=su
```

**Configuration dans `ansible.cfg` pour eviter de repeter les options :**

```ini
[privilege_escalation]
become = True
become_method = sudo
become_user = root
become_ask_pass = False
```

---

## TP : Configurer un inventaire et executer des commandes ad hoc

### Objectifs

A l'issue de ce TP, vous serez capable de :

- Creer un inventaire statique aux formats INI et YAML
- Organiser les machines en groupes et groupes enfants
- Utiliser la structure `group_vars` et `host_vars`
- Executer des commandes ad hoc pour effectuer des operations courantes
- Utiliser le parallelisme et l'elevation de privileges
- Verifier la connectivite et collecter des informations systeme

### Contexte

Vous etes administrateur systeme dans une entreprise. Vous devez gerer une infrastructure composee de plusieurs machines :

| Machine | Role | Adresse IP |
|---------|------|------------|
| web1 | Serveur web (Nginx) | 192.168.56.10 |
| web2 | Serveur web (Nginx) | 192.168.56.11 |
| app1 | Serveur applicatif | 192.168.56.12 |
| db1 | Base de donnees (MySQL) | 192.168.56.20 |
| db2 | Base de donnees (MySQL, replica) | 192.168.56.21 |

L'environnement de test sera mis en place avec Docker Compose ou Vagrant (au choix).

### Prerequis : Mise en place de l'environnement

#### Option A : Docker Compose

Creez les fichiers suivants dans un repertoire `tp-inventaire/` :

**Dockerfile.ansible-node :**

```dockerfile
FROM ubuntu:22.04

RUN apt-get update && \
    apt-get install -y \
        openssh-server \
        python3 \
        python3-pip \
        sudo \
        curl \
        vim && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -m -s /bin/bash ansible && \
    echo "ansible ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

RUN mkdir /var/run/sshd && \
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config && \
    sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config

RUN mkdir -p /home/ansible/.ssh && \
    chmod 700 /home/ansible/.ssh
COPY ansible_key.pub /home/ansible/.ssh/authorized_keys
RUN chmod 600 /home/ansible/.ssh/authorized_keys && \
    chown -R ansible:ansible /home/ansible/.ssh

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]
```

**docker-compose.yml :**

```yaml
version: '3'
services:
  web1:
    build:
      context: .
      dockerfile: Dockerfile.ansible-node
    container_name: ansible-web1
    hostname: web1
    networks:
      ansible_net:
        ipv4_address: 192.168.56.10
    ports:
      - "2201:22"

  web2:
    build:
      context: .
      dockerfile: Dockerfile.ansible-node
    container_name: ansible-web2
    hostname: web2
    networks:
      ansible_net:
        ipv4_address: 192.168.56.11
    ports:
      - "2202:22"

  app1:
    build:
      context: .
      dockerfile: Dockerfile.ansible-node
    container_name: ansible-app1
    hostname: app1
    networks:
      ansible_net:
        ipv4_address: 192.168.56.12
    ports:
      - "2203:22"

  db1:
    build:
      context: .
      dockerfile: Dockerfile.ansible-node
    container_name: ansible-db1
    hostname: db1
    networks:
      ansible_net:
        ipv4_address: 192.168.56.20
    ports:
      - "2204:22"

  db2:
    build:
      context: .
      dockerfile: Dockerfile.ansible-node
    container_name: ansible-db2
    hostname: db2
    networks:
      ansible_net:
        ipv4_address: 192.168.56.21
    ports:
      - "2205:22"

networks:
  ansible_net:
    driver: bridge
    ipam:
      config:
        - subnet: 192.168.56.0/24
```

**Demarrage :**

```bash
# Generer une cle SSH si necessaire
ssh-keygen -t ed25519 -f ~/.ssh/ansible_key -N ""

# Copier la cle publique dans le repertoire du projet
cp ~/.ssh/ansible_key.pub .

# Demarrer les containers
docker-compose up -d

# Verifier que les containers sont en cours d'execution
docker-compose ps
```

#### Option B : Vagrant

```ruby
# Vagrantfile
Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/focal64"
  config.ssh.insert_key = false

  config.vm.provision "file", source: "~/.ssh/ansible_key.pub",
                              destination: "/tmp/ansible_key.pub"
  config.vm.provision "shell", inline: <<-SHELL
    cat /tmp/ansible_key.pub >> /home/vagrant/.ssh/authorized_keys
    apt-get update
    apt-get install -y python3 python3-pip
  SHELL

  machines = {
    "web1" => { ip: "192.168.56.10", memory: 512 },
    "web2" => { ip: "192.168.56.11", memory: 512 },
    "app1" => { ip: "192.168.56.12", memory: 512 },
    "db1"  => { ip: "192.168.56.20", memory: 1024 },
    "db2"  => { ip: "192.168.56.21", memory: 1024 }
  }

  machines.each do |name, config_vm|
    config.vm.define name do |node|
      node.vm.hostname = name
      node.vm.network "private_network", ip: config_vm[:ip]
      node.vm.provider "virtualbox" do |vb|
        vb.memory = config_vm[:memory]
        vb.cpus = 1
      end
    end
  end
end
```

```bash
vagrant up
```

### Etape 1 : Creer un inventaire statique au format INI

Creez un fichier `inventory.ini` :

```ini
# inventory.ini - Inventaire de l'infrastructure

# Serveurs Web
[webservers]
web1 ansible_host=192.168.56.10
web2 ansible_host=192.168.56.11

# Serveur Applicatif
[appservers]
app1 ansible_host=192.168.56.12

# Serveurs de Base de Donnees
[databases]
db1 ansible_host=192.168.56.20 db_role=master
db2 ansible_host=192.168.56.21 db_role=replica

# Groupes enfants
[production:children]
webservers
appservers
databases

[frontend:children]
webservers

[backend:children]
appservers
databases

# Variables de groupe
[webservers:vars]
http_port=80

[databases:vars]
mysql_port=3306

# Variables globales
[all:vars]
ansible_user=ansible
ansible_ssh_private_key_file=~/.ssh/ansible_key
ansible_python_interpreter=/usr/bin/python3
```

**Verification :**

```bash
# Lister tous les hosts
ansible-inventory -i inventory.ini --list

# Afficher le graphe des groupes
ansible-inventory -i inventory.ini --graph

# Lister les hosts du groupe production
ansible production -i inventory.ini --list-hosts

# Lister les hosts du groupe frontend
ansible frontend -i inventory.ini --list-hosts
```

### Etape 2 : Creer le meme inventaire au format YAML

Creez un fichier `inventory.yml` :

```yaml
# inventory.yml - Inventaire de l'infrastructure
all:
  vars:
    ansible_user: ansible
    ansible_ssh_private_key_file: ~/.ssh/ansible_key
    ansible_python_interpreter: /usr/bin/python3

  children:
    webservers:
      hosts:
        web1:
          ansible_host: 192.168.56.10
        web2:
          ansible_host: 192.168.56.11
      vars:
        http_port: 80

    appservers:
      hosts:
        app1:
          ansible_host: 192.168.56.12

    databases:
      hosts:
        db1:
          ansible_host: 192.168.56.20
          db_role: master
        db2:
          ansible_host: 192.168.56.21
          db_role: replica
      vars:
        mysql_port: 3306

    production:
      children:
        webservers:
        appservers:
        databases:

    frontend:
      children:
        webservers:

    backend:
      children:
        appservers:
        databases:
```

**Verification :**

```bash
# Verifier que les deux inventaires produisent le meme resultat
ansible-inventory -i inventory.ini --graph
ansible-inventory -i inventory.yml --graph
```

### Etape 3 : Mettre en place group_vars et host_vars

Creez la structure suivante :

```bash
mkdir -p group_vars host_vars
```

```yaml
# group_vars/all.yml
---
ansible_user: ansible
ansible_ssh_private_key_file: ~/.ssh/ansible_key
ansible_python_interpreter: /usr/bin/python3
ntp_server: ntp.ubuntu.com
environment: production
```

```yaml
# group_vars/webservers.yml
---
http_port: 80
https_port: 443
nginx_worker_processes: auto
document_root: /var/www/html
```

```yaml
# group_vars/databases.yml
---
mysql_port: 3306
mysql_max_connections: 200
backup_enabled: true
backup_schedule: "0 2 * * *"
```

```yaml
# host_vars/db1.yml
---
db_role: master
mysql_server_id: 1
```

```yaml
# host_vars/db2.yml
---
db_role: replica
mysql_server_id: 2
mysql_master_host: db1
```

**Verification :**

```bash
# Afficher les variables resolues pour un host
ansible-inventory -i inventory.yml --host web1
ansible-inventory -i inventory.yml --host db1
ansible-inventory -i inventory.yml --host db2
```

### Etape 4 : Tester la connectivite

```bash
# Ping de tous les hosts
ansible all -i inventory.yml -m ping

# Ping groupe par groupe
ansible webservers -i inventory.yml -m ping
ansible databases -i inventory.yml -m ping
ansible appservers -i inventory.yml -m ping

# Ping avec un pattern
ansible 'webservers:databases' -i inventory.yml -m ping

# Ping en excluant un host
ansible 'all:!db2' -i inventory.yml -m ping
```

**Resultat attendu pour chaque host :**

```
web1 | SUCCESS => {
    "changed": false,
    "ping": "pong"
}
```

### Etape 5 : Collecter des informations systeme

```bash
# Collecter tous les facts de web1
ansible web1 -i inventory.yml -m setup

# Filtrer : distribution OS
ansible all -i inventory.yml -m setup -a "filter=ansible_distribution*"

# Filtrer : memoire
ansible all -i inventory.yml -m setup -a "filter=ansible_memtotal_mb"

# Filtrer : adresses IP
ansible all -i inventory.yml -m setup -a "filter=ansible_default_ipv4"
```

### Etape 6 : Copier des fichiers

```bash
# Creer un fichier de test en local
echo "Deploye par Ansible le $(date)" > /tmp/deploy_info.txt

# Copier vers tous les webservers
ansible webservers -i inventory.yml -m copy -a "src=/tmp/deploy_info.txt dest=/tmp/deploy_info.txt"

# Creer un fichier directement sur les hosts
ansible all -i inventory.yml -m copy -a "content='Managed by Ansible\n' dest=/tmp/ansible_managed.txt mode=0644"

# Verifier que le fichier est bien copie
ansible webservers -i inventory.yml -a "cat /tmp/deploy_info.txt"
```

### Etape 7 : Executer des commandes

```bash
# Afficher le hostname de chaque machine
ansible all -i inventory.yml -a "hostname"

# Afficher l'uptime
ansible all -i inventory.yml -a "uptime"

# Verifier l'espace disque
ansible all -i inventory.yml -a "df -h"

# Lister les utilisateurs connectes
ansible all -i inventory.yml -a "who"

# Utiliser le module shell pour les commandes complexes
ansible all -i inventory.yml -m shell -a "ps aux | head -5"
ansible all -i inventory.yml -m shell -a "free -m | grep Mem"
```

### Etape 8 : Installer des paquets

```bash
# Mettre a jour le cache APT
ansible all -i inventory.yml -m apt -a "update_cache=yes" -b

# Installer curl sur toutes les machines
ansible all -i inventory.yml -m apt -a "name=curl state=present" -b

# Installer nginx sur les webservers
ansible webservers -i inventory.yml -m apt -a "name=nginx state=present" -b

# Installer mysql-client sur les databases
ansible databases -i inventory.yml -m apt -a "name=mysql-client state=present" -b

# Verifier les installations
ansible webservers -i inventory.yml -a "nginx -v"
ansible databases -i inventory.yml -a "mysql --version"
```

### Etape 9 : Gerer les services

```bash
# Demarrer nginx sur les webservers
ansible webservers -i inventory.yml -m service -a "name=nginx state=started" -b

# Verifier le statut
ansible webservers -i inventory.yml -m shell -a "systemctl status nginx" -b

# Activer nginx au demarrage
ansible webservers -i inventory.yml -m service -a "name=nginx enabled=yes" -b

# Redemarrer nginx
ansible webservers -i inventory.yml -m service -a "name=nginx state=restarted" -b

# Arreter nginx
ansible webservers -i inventory.yml -m service -a "name=nginx state=stopped" -b
```

### Etape 10 : Gerer les utilisateurs et les repertoires

```bash
# Creer un utilisateur "deploy" sur toutes les machines
ansible all -i inventory.yml -m user -a "name=deploy state=present shell=/bin/bash" -b

# Creer un repertoire pour l'application
ansible webservers -i inventory.yml -m file -a "path=/opt/webapp state=directory owner=deploy group=deploy mode=0755" -b

# Creer un repertoire de logs
ansible all -i inventory.yml -m file -a "path=/var/log/myapp state=directory owner=deploy mode=0755" -b

# Verifier la creation
ansible webservers -i inventory.yml -a "ls -la /opt/webapp"
ansible all -i inventory.yml -a "id deploy"
```

### Livrables attendus

A la fin de ce TP, vous devez fournir :

1. **Fichier `inventory.ini`** : inventaire au format INI avec groupes et variables
2. **Fichier `inventory.yml`** : inventaire equivalent au format YAML
3. **Repertoire `group_vars/`** contenant :
   - `all.yml`
   - `webservers.yml`
   - `databases.yml`
4. **Repertoire `host_vars/`** contenant :
   - `db1.yml`
   - `db2.yml`
5. **Capture d'ecran ou log** des commandes ad hoc executees avec succes :
   - Ping de tous les hosts
   - Installation de paquets
   - Gestion d'un service
   - Copie de fichier
6. **Fichier `ansible.cfg`** configure pour le projet

### Criteres de validation

| Critere | Description | Valide |
|---------|-------------|--------|
| Inventaire INI | Le fichier `inventory.ini` est syntaxiquement correct et contient les 5 machines reparties en groupes | |
| Inventaire YAML | Le fichier `inventory.yml` est equivalent a la version INI | |
| Groupes enfants | Les groupes `production`, `frontend` et `backend` sont correctement definis avec `:children` (INI) ou `children:` (YAML) | |
| group_vars / host_vars | La structure de repertoires est en place et les variables sont correctement definies | |
| Connectivite | La commande `ansible all -m ping` retourne SUCCESS pour les 5 machines | |
| Installation paquets | Nginx est installe sur les webservers via le module `apt` | |
| Gestion service | Nginx est demarre et active au demarrage sur les webservers | |
| Copie fichier | Un fichier a ete copie avec succes vers les managed nodes | |
| Commandes systeme | Les commandes `setup`, `shell` et `command` ont ete utilisees | |
| Utilisateur | L'utilisateur `deploy` existe sur toutes les machines | |

### Bonus : Creer un inventaire dynamique simple

Creez un script Python `dynamic_inventory.py` qui genere dynamiquement l'inventaire a partir d'un fichier de configuration JSON.

**Fichier `machines.json` :**

```json
{
  "machines": [
    {"name": "web1", "ip": "192.168.56.10", "group": "webservers", "user": "ansible"},
    {"name": "web2", "ip": "192.168.56.11", "group": "webservers", "user": "ansible"},
    {"name": "app1", "ip": "192.168.56.12", "group": "appservers", "user": "ansible"},
    {"name": "db1",  "ip": "192.168.56.20", "group": "databases",  "user": "ansible"},
    {"name": "db2",  "ip": "192.168.56.21", "group": "databases",  "user": "ansible"}
  ]
}
```

**Script `dynamic_inventory.py` :**

```python
#!/usr/bin/env python3
"""
Inventaire dynamique Ansible generant l'inventaire
a partir d'un fichier machines.json.
"""

import json
import sys
import os


def load_machines(config_file="machines.json"):
    """Charge les machines depuis le fichier de configuration."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, config_file)
    with open(config_path, "r") as f:
        return json.load(f)["machines"]


def build_inventory(machines):
    """Construit l'inventaire Ansible a partir de la liste de machines."""
    inventory = {
        "_meta": {
            "hostvars": {}
        }
    }

    for machine in machines:
        name = machine["name"]
        group = machine["group"]

        # Ajouter les hostvars
        inventory["_meta"]["hostvars"][name] = {
            "ansible_host": machine["ip"],
            "ansible_user": machine["user"],
            "ansible_python_interpreter": "/usr/bin/python3",
            "ansible_ssh_private_key_file": "~/.ssh/ansible_key"
        }

        # Ajouter au groupe
        if group not in inventory:
            inventory[group] = {"hosts": [], "vars": {}}
        inventory[group]["hosts"].append(name)

    # Ajouter le groupe production (tous les groupes)
    all_hosts = [m["name"] for m in machines]
    inventory["production"] = {
        "hosts": all_hosts,
        "vars": {"environment": "production"}
    }

    return inventory


def get_host_vars(hostname, machines):
    """Retourne les variables d'un host specifique."""
    for machine in machines:
        if machine["name"] == hostname:
            return {
                "ansible_host": machine["ip"],
                "ansible_user": machine["user"],
                "ansible_python_interpreter": "/usr/bin/python3",
                "ansible_ssh_private_key_file": "~/.ssh/ansible_key"
            }
    return {}


def main():
    machines = load_machines()

    if len(sys.argv) == 2 and sys.argv[1] == "--list":
        inventory = build_inventory(machines)
        print(json.dumps(inventory, indent=2))
    elif len(sys.argv) == 3 and sys.argv[1] == "--host":
        hostvars = get_host_vars(sys.argv[2], machines)
        print(json.dumps(hostvars, indent=2))
    else:
        print(f"Usage: {sys.argv[0]} --list | --host <hostname>")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

**Test du script :**

```bash
# Rendre executable
chmod +x dynamic_inventory.py

# Tester la sortie
./dynamic_inventory.py --list
./dynamic_inventory.py --host web1

# Utiliser avec Ansible
ansible all -i dynamic_inventory.py -m ping
ansible webservers -i dynamic_inventory.py -m ping
```

---

## Ressources complementaires

- [Documentation officielle : Inventaires](https://docs.ansible.com/ansible/latest/inventory_guide/index.html)
- [Documentation officielle : Patterns](https://docs.ansible.com/ansible/latest/inventory_guide/intro_patterns.html)
- [Documentation officielle : Commandes ad hoc](https://docs.ansible.com/ansible/latest/command_guide/intro_adhoc.html)
- [Documentation officielle : Inventory Plugins](https://docs.ansible.com/ansible/latest/plugins/inventory.html)

---

**"Un inventaire bien organise est le fondement de toute automatisation d'infrastructure."**
