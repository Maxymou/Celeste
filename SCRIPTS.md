# Scripts CELESTE X

Ce document décrit tous les scripts disponibles pour gérer CELESTE X.

## 📦 Scripts d'installation

### `install.sh`
Script d'installation automatisé complet.

**Usage :**
```bash
# Installation depuis GitHub
curl -sSL https://raw.githubusercontent.com/Maxymou/CELESTE/main/install.sh | bash

# Installation locale
./install.sh
```

**Fonctionnalités :**
- Installation des prérequis (Python, Node.js, Git)
- Création de l'utilisateur système `celeste`
- Clonage du repository
- Configuration du frontend (npm install + build)
- Configuration du backend (venv + pip install)
- Installation des services systemd
- Démarrage automatique des services
- Configuration des variables d'environnement

## 🔍 Scripts de vérification

### `check.sh`
Script de vérification post-installation.

**Usage :**
```bash
./check.sh
```

**Vérifications :**
- Statut des services systemd
- Ouverture des ports 6000 et 8000
- Réponse des endpoints API
- Présence des fichiers de build
- Existence de la base de données

### `verify-uninstall.sh`
Script de vérification post-désinstallation.

**Usage :**
```bash
./verify-uninstall.sh
```

**Vérifications :**
- Arrêt des services
- Désactivation des services
- Suppression des fichiers systemd
- Libération des ports
- Suppression de l'utilisateur
- Suppression des fichiers d'installation

## 🗑️ Scripts de désinstallation

### `uninstall.sh`
Script de désinstallation avec options flexibles.

**Usage :**
```bash
# Désinstallation depuis GitHub
curl -sSL https://raw.githubusercontent.com/Maxymou/CELESTE/main/uninstall.sh | bash

# Désinstallation locale
./uninstall.sh
```

**Options proposées :**
1. **Suppression complète** : Supprime tout (services, fichiers, base de données, utilisateur)
2. **Conservation des données** : Garde les fichiers et la base de données
3. **Suppression DB uniquement** : Supprime seulement la base de données

**Actions :**
- Arrêt des services
- Désactivation des services
- Suppression des fichiers systemd
- Rechargement de systemd
- Suppression de l'utilisateur (avec gestion des processus)
- Nettoyage des logs
- Vérification des ports

### `cleanup.sh`
Script de nettoyage complet (dernier recours).

**Usage :**
```bash
./cleanup.sh
```

**⚠️ ATTENTION** : Ce script force la suppression de TOUS les composants sans demander de confirmation pour les données.

**Actions forcées :**
- Arrêt forcé de tous les processus liés
- Suppression forcée de l'utilisateur
- Suppression complète du répertoire d'installation
- Nettoyage des logs et caches
- Vérification des ports

## 🔧 Configuration des scripts

### Variables communes
Tous les scripts utilisent les mêmes variables de configuration :

```bash
INSTALL_DIR="/opt/celestex"
SERVICE_USER="celeste"
SERVICE_MAIN="celestex"
SERVICE_ADMIN="celestex-admin"
GITHUB_REPO="https://github.com/Maxymou/CELESTE.git"
```

### Permissions
Les scripts doivent être exécutables :
```bash
chmod +x *.sh
```

### Sécurité
- Les scripts ne doivent pas être exécutés en tant que root
- Confirmation requise pour les actions destructives
- Vérifications de sécurité intégrées

## 📋 Workflow recommandé

### Installation
1. `install.sh` - Installation complète
2. `check.sh` - Vérification de l'installation

### Mise à jour
1. `git pull` - Mise à jour du code
2. Rebuild frontend et backend
3. `systemctl restart` - Redémarrage des services
4. `check.sh` - Vérification

### Désinstallation
1. `uninstall.sh` - Désinstallation normale
2. `verify-uninstall.sh` - Vérification
3. `cleanup.sh` - Si nécessaire (dernier recours)

## 🐛 Dépannage

### Problèmes courants

**Service ne démarre pas :**
```bash
sudo journalctl -u celestex -f
sudo systemctl status celestex
```

**Port déjà utilisé :**
```bash
netstat -tlnp | grep :6000
sudo lsof -i :6000
```

**Permissions insuffisantes :**
```bash
sudo chown -R celeste:celeste /opt/celestex
```

**Utilisateur verrouillé :**
```bash
sudo pkill -u celeste
sudo userdel -f -r celeste
```

### Logs utiles
- Services : `sudo journalctl -u celestex -f`
- Installation : Vérifier la sortie du script
- Système : `/var/log/syslog`

## 🔗 Liens utiles

- [README.md](README.md) - Documentation principale
- [CONTRIBUTING.md](CONTRIBUTING.md) - Guide de contribution
- [CHANGELOG.md](CHANGELOG.md) - Historique des versions
