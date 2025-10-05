# CELESTE X

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/Maxymou/CELESTE/releases)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/Maxymou/CELESTE/blob/main/LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![Node.js](https://img.shields.io/badge/node.js-16%2B-green.svg)](https://nodejs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3.1-61DAFB.svg)](https://reactjs.org)

Application de calcul mécanique pour lignes électriques aériennes.

## Contexte

- **Plateforme** : Debian VM sur Proxmox
- **Proxy inverse** : Nginx Proxy Manager (externe)
- **Firewall** : Géré externe
- **Ports** : 6000 (app principale), 8000 (admin DB, local uniquement)

## Architecture

- **Backend** : FastAPI (port 6000) - sert l'API et les fichiers statiques React
- **Frontend** : React + Vite + TypeScript
- **Base de données** : SQLite
- **Admin** : SQLAdmin (port 8000) avec authentification Basic Auth

## 🚀 Installation rapide depuis GitHub

### Installation automatisée (recommandée)

```bash
# Installation en une commande
curl -sSL https://raw.githubusercontent.com/Maxymou/CELESTE/main/install.sh | bash
```

**Installation prête avec le repository Maxymou/CELESTE !**

### Installation manuelle

1. **Prérequis** :
```bash
sudo apt update
sudo apt install python3 python3-venv nodejs npm git curl
```

2. **Cloner et installer** :
```bash
git clone https://github.com/Maxymou/CELESTE.git /opt/celestex
cd /opt/celestex
chmod +x install.sh
sudo ./install.sh
```

### Vérification de l'installation

```bash
# Vérifier que tout fonctionne
./check.sh
```

### Désinstallation

```bash
# Désinstallation complète
curl -sSL https://raw.githubusercontent.com/Maxymou/CELESTE/main/uninstall.sh | bash

# Ou désinstallation manuelle
./uninstall.sh
```

**Options de désinstallation :**
- **Suppression complète** : Supprime tout (services, fichiers, base de données, utilisateur)
- **Conservation des données** : Garde les fichiers et la base de données
- **Suppression DB uniquement** : Supprime seulement la base de données

### Vérification de la désinstallation

```bash
# Vérifier que la désinstallation est complète
./verify-uninstall.sh
```

## 📋 Accès après installation

Une fois l'installation terminée, vous pouvez accéder à :

- **Application principale** : `http://<IP_VM>:6000`
- **Admin dashboard** : `http://<IP_VM>:8000`
- **Identifiants admin** : `admin` / `admin123`

## 🔧 Gestion des services

### Commandes utiles

```bash
# Vérifier le statut
sudo systemctl status celestex
sudo systemctl status celestex-admin

# Redémarrer les services
sudo systemctl restart celestex
sudo systemctl restart celestex-admin

# Voir les logs en temps réel
sudo journalctl -u celestex -f
sudo journalctl -u celestex-admin -f

# Arrêter les services
sudo systemctl stop celestex
sudo systemctl stop celestex-admin
```

### Vérification complète

```bash
# Script de vérification automatique
./check.sh
```

## 🔄 Mise à jour

```bash
# Mise à jour depuis GitHub
cd /opt/celestex
sudo -u celeste git pull
sudo -u celeste bash -c 'cd frontend && npm ci && npm run build'
sudo -u celeste bash -c 'source .venv/bin/activate && pip install -r backend/requirements.txt'
sudo systemctl restart celestex celestex-admin
```

> 💡 **Astuce** : si `git pull` signale qu'un fichier non suivi serait écrasé
> (ex. `frontend/package-lock.json`), supprimez ou déplacez ce fichier avant
> de relancer la commande :
>
> ```bash
> sudo -u celeste rm frontend/package-lock.json
> # ou
> sudo -u celeste mv frontend/package-lock.json /tmp/package-lock.json.bak
> ```

## 🗑️ Désinstallation

### Désinstallation automatisée

```bash
# Désinstallation en une commande
curl -sSL https://raw.githubusercontent.com/Maxymou/CELESTE/main/uninstall.sh | bash
```

### Options de désinstallation

Le script de désinstallation vous propose 3 options :

1. **Suppression complète** : Supprime tout (services, fichiers, base de données, utilisateur)
2. **Conservation des données** : Garde les fichiers et la base de données pour une réinstallation future
3. **Suppression DB uniquement** : Supprime seulement la base de données

### Désinstallation manuelle

```bash
# Arrêter les services
sudo systemctl stop celestex celestex-admin

# Désactiver les services
sudo systemctl disable celestex celestex-admin

# Supprimer les fichiers systemd
sudo rm -f /etc/systemd/system/celestex.service
sudo rm -f /etc/systemd/system/celestex-admin.service
sudo systemctl daemon-reload

# Supprimer l'utilisateur
sudo userdel -r celeste

# Supprimer les fichiers (optionnel)
sudo rm -rf /opt/celestex
```

### Nettoyage complet (dernier recours)

Si la désinstallation normale ne fonctionne pas :

```bash
# Nettoyage forcé complet
./cleanup.sh
```

**⚠️ ATTENTION** : Ce script force la suppression de TOUS les composants CELESTE X sans demander de confirmation pour les données.

## API

### Endpoints disponibles

- `GET /api/health` → `{"status":"ok"}`
- `POST /api/calc/span` → Calcul de portée (stub)

### Exemple de requête span

```bash
curl -X POST "http://localhost:6000/api/calc/span" \
  -H "Content-Type: application/json" \
  -d '{
    "span_length_m": 100.0,
    "delta_h_m": 5.0,
    "angle_topo_grade": 2.0,
    "tension_ini_dan": 1000.0
  }'
```

## Import de données

Le script `scripts/import_cables.py` est un stub pour importer les fichiers XML :
- `Câble.xml`
- `Couche câble.xml`

```bash
python scripts/import_cables.py --xml-cable Câble.xml --xml-layer "Couche câble.xml"
```

## Structure du projet

```
celestex/
├── backend/                 # API FastAPI
│   ├── main.py             # Application principale
│   ├── requirements.txt    # Dépendances Python
│   ├── domain/             # Logique métier
│   └── models/             # Modèles de données
├── backend_admin/          # Dashboard admin
│   └── main.py             # SQLAdmin
├── frontend/               # Interface React
│   ├── src/                # Code source
│   ├── package.json        # Dépendances Node
│   └── vite.config.ts      # Configuration Vite
├── scripts/                # Scripts utilitaires
│   └── import_cables.py    # Import XML
├── systemd/                # Services systemd
├── data/                   # Base de données SQLite
├── .env.example            # Variables d'environnement
└── README.md               # Cette documentation
```

## Développement

### Frontend
```bash
cd frontend
npm run dev  # Mode développement
npm run build  # Build de production
```

### Backend
```bash
source .venv/bin/activate
uvicorn backend.main:app --reload  # Mode développement
```

## Logs

```bash
# Logs application
sudo journalctl -u celestex -f

# Logs admin
sudo journalctl -u celestex-admin -f
```

## 🛠️ Développement

### Démarrage en mode développement

```bash
# Frontend (terminal 1)
cd frontend
npm run dev

# Backend (terminal 2)
cd backend
source ../.venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 6000

# Admin (terminal 3)
cd backend_admin
source ../.venv/bin/activate
export CELESTEX_DB_PATH=../data/celestex.db
export ADMIN_USER=admin
export ADMIN_PASS=admin123
export ADMIN_SECRET=admin
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Configuration personnalisée

Modifiez le fichier `deploy.conf` pour personnaliser :
- Répertoire d'installation
- Utilisateur système
- Ports
- Identifiants admin
- Repository GitHub
