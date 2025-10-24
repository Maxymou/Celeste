Hash bcrypt généré avec succès!

Mot de passe: MonMotDePasseSecurise2025!

Hash bcrypt:
$2b$12$xyz...

Ajoutez cette ligne dans votre fichier .env:
ADMIN_PASS=$2b$12$xyz...
```

#### Méthode 2 : Édition manuelle

```bash
# Éditer le fichier .env
sudo -u celeste nano /opt/celestex/.env

# Remplacer la ligne ADMIN_PASS par le hash généré
ADMIN_PASS=$2b$12$xyz...

# Redémarrer le service admin
sudo systemctl restart celestex-admin
```

### Vérification de la sécurité

Les logs afficheront un **warning** si un mot de passe en clair est détecté :

```bash
sudo journalctl -u celestex-admin -n 20

# Si vous voyez ce message, changez le mot de passe !
WARNING - SÉCURITÉ: Le mot de passe admin est stocké en clair.
```

### Recommandations de sécurité

- ✅ **Obligatoire** : Changer le mot de passe admin par défaut
- ✅ **Recommandé** : Utiliser un mot de passe d'au moins 12 caractères
- ✅ **Recommandé** : Restreindre l'accès au port 8000 (admin) via firewall
- ✅ **Recommandé** : Configurer HTTPS sur le reverse proxy

---

## 🔧 Configuration

### Fichier de configuration principal

Éditez `/opt/celestex/.env` :

```bash
# Configuration de base
CELESTEX_DB_PATH=/opt/celestex/data/celestex.db

# Admin (CHANGER EN PRODUCTION)
ADMIN_USER=admin
ADMIN_PASS=$2b$12$xyz...  # Hash bcrypt généré
ADMIN_SECRET=votre-secret-session-unique

# Ports (si modification nécessaire)
APP_PORT=6000
ADMIN_PORT=8000
```

### Personnalisation avancée

Éditez `/opt/celestex/deploy.conf` pour personnaliser :

```bash
# Répertoire d'installation
INSTALL_DIR="/opt/celestex"

# Utilisateur système
SERVICE_USER="celeste"

# Repository GitHub
GITHUB_REPO="https://github.com/Maxymou/CELESTE.git"

# Ports
APP_PORT=6000
ADMIN_PORT=8000
```

---

## 🔌 API

### Endpoints disponibles

#### Santé et informations

- **`GET /api/health`** - Vérification de l'état de l'API
  ```json
  {"status": "ok", "version": "1.0.0"}
  ```

- **`GET /api/cables`** - Liste des câbles disponibles
  ```json
  {
    "success": true,
    "count": 3,
    "cables": [...]
  }
  ```

#### Calculs mécaniques

- **`POST /api/calc/span`** - Calcul complet d'une portée
  - Géométrie (corde, flèches)
  - Tensions (T₀, TA, TB)
  - Warnings et erreurs

- **`POST /api/calc/equivalent-span`** - Portée équivalente (Blondel)

- **`POST /api/calc/crr`** - Charge de rupture résiduelle

- **`POST /api/calc/vhl`** - Effort résultant sur support

- **`GET /api/calc/cigre-emissivity`** - Émissivité câble (CIGRE)

- **`POST /api/calc/validate-domain`** - Validation domaine CELESTE

### Exemples d'utilisation

#### Calcul de portée

```bash
curl -X POST "http://localhost:6000/api/calc/span" \
  -H "Content-Type: application/json" \
  -d '{
    "span_length_m": 500.0,
    "delta_h_m": 10.0,
    "cable": {
      "name": "Aster 570",
      "mass_lin_kg_per_m": 1.631,
      "E_MPa": 78000,
      "section_mm2": 564.6,
      "alpha_1e6_per_C": 19.1,
      "rupture_dan": 17200,
      "diameter_mm": 31.5
    },
    "rho_m": 2000,
    "wind_pressure_daPa": 20,
    "angle_topo_grade": 5
  }'
```

Réponse :
```json
{
  "success": true,
  "result": {
    "geometry": {
      "b_m": 500.1,
      "F1_m": 15.63,
      "F2_m": 15.23,
      "H_m": 25.23
    },
    "tensions": {
      "T0_dan": 3200,
      "TA_dan": 3224,
      "TB_dan": 3240
    },
    "warnings": [],
    "errors": []
  }
}
```

#### Récupérer la liste des câbles

```bash
curl http://localhost:6000/api/cables
```

### Documentation interactive

Accédez à la documentation Swagger automatique :
- **URL** : `http://<IP_VM>:6000/docs`
- Testez les endpoints directement depuis l'interface

---

## 🧪 Tests

### Exécuter les tests

```bash
cd /opt/celestex
source .venv/bin/activate

# Tous les tests
pytest backend/tests/ -v

# Tests avec couverture
pytest backend/tests/ --cov=backend --cov-report=html

# Test spécifique
pytest backend/tests/test_mechanical.py::test_calculate_span_complete -v
```

### Résultats attendus

```
collected 21 items

backend/tests/test_mechanical.py::test_span_geometry_cord_length PASSED  [  4%]
backend/tests/test_mechanical.py::test_calculate_sag_horizontal_span PASSED [  9%]
...
backend/tests/test_mechanical.py::test_calculate_span_rho_warning_high PASSED [100%]

```

### Tests couverts

- ✅ Géométrie (corde, longueur)
- ✅ Flèches (portée horizontale, avec dénivelé)
- ✅ Tensions (T₀, TA, TB)
- ✅ Portée équivalente (Blondel)
- ✅ CRR (charge de rupture résiduelle)
- ✅ Effort VHL
- ✅ Émissivité CIGRE
- ✅ Validation domaine CELESTE
- ✅ Warnings et erreurs métier

---

## 🔄 Mise à jour

### Mise à jour automatique

```bash
cd /opt/celestex

# Récupérer les dernières modifications
sudo -u celeste git pull

# Installer les nouvelles dépendances Python
sudo -u celeste bash -c 'source .venv/bin/activate && pip install -r backend/requirements.txt'

# Rebuild le frontend
sudo -u celeste bash -c 'cd frontend && npm ci && npm run build'

# Redémarrer les services
sudo systemctl restart celestex celestex-admin

# Vérifier que tout fonctionne
./check.sh
```

### Vérification après mise à jour

```bash
# Tester l'API
curl http://localhost:6000/api/health

# Vérifier les logs
sudo journalctl -u celestex -n 50
sudo journalctl -u celestex-admin -n 50

# Exécuter les tests
source .venv/bin/activate
pytest backend/tests/ -v
```

### Résolution de problèmes

#### Conflit de fichiers lors du `git pull`

```bash
# Sauvegarder et supprimer les fichiers en conflit
sudo -u celeste mv frontend/package-lock.json /tmp/package-lock.json.bak
sudo -u celeste git pull
```

#### Problèmes de dépendances

```bash
# Réinstaller toutes les dépendances
sudo -u celeste bash -c 'source .venv/bin/activate && pip install --upgrade -r backend/requirements.txt'
sudo -u celeste bash -c 'cd frontend && rm -rf node_modules && npm install'
```

---

## 🗑️ Désinstallation

### Désinstallation automatique

```bash
# Désinstallation complète
curl -sSL https://raw.githubusercontent.com/Maxymou/CELESTE/main/uninstall.sh | bash

# Ou depuis le répertoire d'installation
cd /opt/celestex
./uninstall.sh
```

Le script propose 3 options :
1. **Suppression complète** : services, fichiers, base de données et utilisateur
2. **Conservation des données** : garde `/opt/celestex` pour réinstallation future
3. **Suppression DB uniquement** : efface seulement `data/celestex.db`

### Vérification de la désinstallation

```bash
./verify-uninstall.sh
```

### Désinstallation manuelle (si nécessaire)

```bash
# Arrêter et désactiver les services
sudo systemctl stop celestex celestex-admin
sudo systemctl disable celestex celestex-admin

# Supprimer les fichiers systemd
sudo rm -f /etc/systemd/system/celestex.service
sudo rm -f /etc/systemd/system/celestex-admin.service
sudo systemctl daemon-reload

# Supprimer l'utilisateur
sudo userdel -r celeste

# Supprimer les fichiers
sudo rm -rf /opt/celestex
```

---

## 🔧 Gestion des services

### Commandes systemd

```bash
# Vérifier le statut
sudo systemctl status celestex
sudo systemctl status celestex-admin

# Démarrer
sudo systemctl start celestex celestex-admin

# Arrêter
sudo systemctl stop celestex celestex-admin

# Redémarrer
sudo systemctl restart celestex celestex-admin

# Activer au démarrage
sudo systemctl enable celestex celestex-admin
```

### Consultation des logs

```bash
# Logs en temps réel
sudo journalctl -u celestex -f
sudo journalctl -u celestex-admin -f

# Dernières 100 lignes
sudo journalctl -u celestex -n 100

# Logs avec horodatage
sudo journalctl -u celestex --since "2025-01-01" --until "2025-01-31"

# Logs d'erreur uniquement
sudo journalctl -u celestex -p err
```

---

## 🛠️ Développement

### Démarrage en mode développement

#### Terminal 1 : Frontend (React + Vite)

```bash
cd /opt/celestex/frontend
npm run dev
# Accès : http://localhost:5173
```

#### Terminal 2 : Backend (FastAPI)

```bash
cd /opt/celestex
source .venv/bin/activate
uvicorn backend.main:app --reload --host 0.0.0.0 --port 6000
# Accès : http://localhost:6000
```

#### Terminal 3 : Admin (SQLAdmin)

```bash
cd /opt/celestex
source .venv/bin/activate
export CELESTEX_DB_PATH=./data/celestex.db
export ADMIN_USER=admin
export ADMIN_PASS=admin123
export ADMIN_SECRET=dev-secret
uvicorn backend_admin.main:app --reload --host 0.0.0.0 --port 8000
# Accès : http://localhost:8000
```

### Lancer les tests en mode watch

```bash
source .venv/bin/activate
pytest backend/tests/ -v --looponfail
```

### Build de production

```bash
# Frontend
cd frontend
npm run build
# Fichiers générés dans : frontend/dist/

# Backend (aucun build nécessaire)
```

---

## 📚 Documentation supplémentaire

- **`IMPROVEMENTS.md`** - Détails des améliorations v1.1.0
- **`CONTRIBUTING.md`** - Guide de contribution
- **`CHANGELOG.md`** - Historique des versions
- **`Projet_celeste.md`** - Cahier des charges complet

---

## 📊 Structure du projet

```
celestex/
├── backend/                      # API FastAPI
│   ├── main.py                  # Application principale
│   ├── security.py              # Hashage mots de passe
│   ├── exceptions.py            # Exceptions personnalisées
│   ├── requirements.txt         # Dépendances Python
│   ├── domain/                  # Logique métier
│   │   └── mechanical.py        # Calculs mécaniques
│   ├── models/                  # Modèles de données
│   │   └── db_models.py         # ORM SQLAlchemy
│   └── tests/                   # Tests unitaires
│       └── test_mechanical.py   # Tests calculs
├── backend_admin/               # Dashboard admin
│   └── main.py                  # Interface SQLAdmin
├── frontend/                    # Interface React
│   ├── src/
│   │   ├── App.tsx              # Composant principal
│   │   ├── components/          # Composants React
│   │   └── styles/              # Styles CSS
│   ├── package.json
│   └── vite.config.ts
├── systemd/                     # Services systemd
│   ├── celestex.service
│   └── celestex-admin.service
├── data/                        # Base de données
│   ├── celestex.db              # SQLite
│   ├── Câble.xml                # Catalogue câbles
│   └── Couche câble.xml         # Couches câbles
├── .env                         # Configuration (généré)
├── .gitignore                   # Fichiers ignorés
├── pytest.ini                   # Configuration pytest
├── install.sh                   # Script installation
├── uninstall.sh                 # Script désinstallation
├── check.sh                     # Script vérification
└── README.md                    # Ce fichier
```

---

## 🤝 Contribution

Les contributions sont les bienvenues ! Consultez `CONTRIBUTING.md` pour les guidelines.

---

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

---

## 👤 Auteur

Application professionnelle de calcul de lignes électriques

---

## 📞 Support

En cas de problème :

1. Consultez les logs : `sudo journalctl -u celestex -n 100`
2. Vérifiez la configuration : `./check.sh`
3. Consultez la documentation : `IMPROVEMENTS.md`
4. Ouvrez une issue sur GitHub

---

**Version** : 1.1.0
**Dernière mise à jour** : 21 Octobre 2025
# CELESTE X

[![Version](https://img.shields.io/badge/version-1.2.0-blue.svg)](https://github.com/Maxymou/CELESTE/releases)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/Maxymou/CELESTE/blob/main/LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![Node.js](https://img.shields.io/badge/node.js-16%2B-green.svg)](https://nodejs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3.1-61DAFB.svg)](https://reactjs.org)
[![Tests](https://img.shields.io/badge/tests-21%2F21%20passing-success.svg)](tests)

Application de calcul mécanique pour lignes électriques aériennes avec validation métier, tests unitaires et sécurité renforcée.

## 📋 Table des matières

- [Contexte](#contexte)
- [Nouveautés v1.2.0](#-nouveautés-v120)
- [Architecture](#architecture)
- [Authentification](#-authentification)
- [Installation](#-installation-rapide)
- [Configuration](#-configuration)
- [Sécurité](#-sécurité)
- [API](#-api)
- [Tests](#-tests)
- [Mise à jour](#-mise-à-jour)
- [Développement](#️-développement)

---

## Contexte

### Environnement de déploiement

- **Plateforme** : VM Debian sur Proxmox
- **Proxy inverse** : Nginx Proxy Manager (externe)
- **Firewall** : Géré en externe
- **Ports** :
  - `6000` : Application principale (API + Frontend)
  - `8000` : Interface admin (accès local uniquement recommandé)

### Stack technique

- **Backend** : FastAPI 0.115.0 (Python 3.8+)
- **Frontend** : React 18.3.1 + Vite + TypeScript
- **Base de données** : SQLite
- **Admin** : SQLAdmin avec authentification sécurisée
- **Déploiement** : Services systemd

---

## 🎉 Nouveautés v1.2.0

### 🔐 Authentification JWT
- ✅ **Système d'authentification complet** avec JWT (JSON Web Tokens)
- ✅ **Liste blanche d'emails** configurable via variables d'environnement
- ✅ **Page de connexion** avec design dark mode cohérent
- ✅ **Contexte d'authentification** React avec gestion de session
- ✅ **Menu de déconnexion** dans le profil utilisateur
- ✅ Tokens valides pendant 8 heures
- ✅ Protection automatique des routes
- ✅ Documentation complète dans [AUTHENTIFICATION.md](./AUTHENTIFICATION.md)

### 🔐 Sécurité renforcée (v1.1.0)
- ✅ **Hashage des mots de passe** avec bcrypt (passlib)
- ✅ **CLI de génération de hash** : `python -m backend.security`
- ✅ Support rétrocompatible avec warning pour mots de passe en clair
- ✅ Logging des événements de sécurité

### ✔️ Validation métier améliorée
- ✅ **Vérification tensions vs rupture** : erreur si dépassement
- ✅ Warning si tension > 90% de la charge de rupture
- ✅ Validation du paramètre ρ (100-10000m recommandé)
- ✅ Messages d'erreur détaillés avec valeurs calculées

### 🧪 Tests unitaires
- ✅ **21 tests** couvrant 100% des calculs mécaniques
- ✅ Tests de géométrie, flèches, tensions, CRR, VHL, émissivité
- ✅ Validation domaine CELESTE
- ✅ Configuration pytest complète

### 🛡️ Gestion d'erreurs professionnelle
- ✅ Exceptions personnalisées (`ValidationError`, `CalculationError`)
- ✅ Handlers avec codes HTTP sémantiquement corrects
- ✅ Messages d'erreur structurés et clairs
- ✅ Logging complet des erreurs

### 🔌 API enrichie
- ✅ Nouvel endpoint `GET /api/cables` pour récupérer les câbles
- ✅ Logging structuré sur tous les endpoints
- ✅ Validation des entrées renforcée

### 🎨 Frontend amélioré
- ✅ Validation côté client avant soumission
- ✅ Chargement dynamique des câbles depuis l'API
- ✅ Affichage des erreurs de validation en temps réel
- ✅ Meilleure gestion des erreurs HTTP

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Nginx Proxy Manager                  │
│                  (Reverse Proxy externe)                │
└──────────────────────────┬──────────────────────────────┘
                           │
          ┌────────────────┴────────────────┐
          │                                 │
    ┌─────▼─────┐                    ┌─────▼─────┐
    │  Port 6000 │                    │  Port 8000 │
    │            │                    │            │
    │  FastAPI   │                    │  SQLAdmin  │
    │            │                    │  (Admin)   │
    │  API REST  │                    │            │
    │     +      │◄───────────┐       └────────────┘
    │  Static    │            │
    │  React     │            │
    └────────────┘            │
                              │
                    ┌─────────┴──────────┐
                    │                    │
              ┌─────▼─────┐      ┌──────▼──────┐
              │  SQLite   │      │   Calculs   │
              │  Database │      │  Mécaniques │
              └───────────┘      │   (domain)  │
                                 └─────────────┘
```

---

## 🚀 Installation rapide

### Installation automatisée (recommandée)

```bash
# Installation en une commande
curl -sSL https://raw.githubusercontent.com/Maxymou/CELESTE/main/install.sh | bash
```

> ℹ️ **Important** : Exécutez cette commande en tant qu'utilisateur standard disposant des
> droits `sudo`. Le script refuse d'être lancé directement en root.

### Installation manuelle

#### 1. Prérequis

```bash
sudo apt update
sudo apt install python3 python3-venv nodejs npm git curl
```

#### 2. Cloner et installer

```bash
git clone https://github.com/Maxymou/CELESTE.git /opt/celestex
cd /opt/celestex
chmod +x install.sh
./install.sh
```

#### 3. Vérification

```bash
# Vérifier que tout fonctionne
./check.sh

# Vérifier les services
sudo systemctl status celestex
sudo systemctl status celestex-admin
```

### Première connexion

Une fois l'installation terminée, accédez à :

- **Application principale** : `http://<IP_VM>:6000`
- **Interface admin** : `http://<IP_VM>:8000`
- **Documentation API** : `http://<IP_VM>:6000/docs`

**Identifiants admin par défaut** :
- Utilisateur : `admin`
- Mot de passe : `admin123` (⚠️ À CHANGER immédiatement en production)

---

## 🔐 Sécurité

### Changer le mot de passe admin (OBLIGATOIRE en production)

#### Méthode 1 : Génération automatique

```bash
cd /opt/celestex
source .venv/bin/activate

# Générer un hash sécurisé
python -m backend.security "MonMotDePasseSecurise2025!"
```

Sortie :
```
Hash bcrypt généré avec succès!

Mot de passe: MonMotDePasseSecurise2025!

Hash bcrypt:
$2b$12$xyz...

Ajoutez cette ligne dans votre fichier .env:
ADMIN_PASS=$2b$12$xyz...
```

#### Méthode 2 : Édition manuelle

```bash
# Éditer le fichier .env
sudo -u celeste nano /opt/celestex/.env

# Remplacer la ligne ADMIN_PASS par le hash généré
ADMIN_PASS=$2b$12$xyz...

# Redémarrer le service admin
sudo systemctl restart celestex-admin
```

### Vérification de la sécurité

Les logs afficheront un **warning** si un mot de passe en clair est détecté :

```bash
sudo journalctl -u celestex-admin -n 20

# Si vous voyez ce message, changez le mot de passe !
WARNING - SÉCURITÉ: Le mot de passe admin est stocké en clair.
```

### Recommandations de sécurité

- ✅ **Obligatoire** : Changer le mot de passe admin par défaut
- ✅ **Recommandé** : Utiliser un mot de passe d'au moins 12 caractères
- ✅ **Recommandé** : Restreindre l'accès au port 8000 (admin) via firewall
- ✅ **Recommandé** : Configurer HTTPS sur le reverse proxy

---

## 🔧 Configuration

### Fichier de configuration principal

Éditez `/opt/celestex/.env` :

```bash
# Configuration de base
CELESTEX_DB_PATH=/opt/celestex/data/celestex.db

# Admin (CHANGER EN PRODUCTION)
ADMIN_USER=admin
ADMIN_PASS=$2b$12$xyz...  # Hash bcrypt généré
ADMIN_SECRET=votre-secret-session-unique

# Ports (si modification nécessaire)
APP_PORT=6000
ADMIN_PORT=8000
```

### Personnalisation avancée

Éditez `/opt/celestex/deploy.conf` pour personnaliser :

```bash
# Répertoire d'installation
INSTALL_DIR="/opt/celestex"

# Utilisateur système
SERVICE_USER="celeste"

# Repository GitHub
GITHUB_REPO="https://github.com/Maxymou/CELESTE.git"

# Ports
APP_PORT=6000
ADMIN_PORT=8000
```

---

## 🔌 API

### Endpoints disponibles

#### Santé et informations

- **`GET /api/health`** - Vérification de l'état de l'API
  ```json
  {"status": "ok", "version": "1.0.0"}
  ```

- **`GET /api/cables`** - Liste des câbles disponibles
  ```json
  {
    "success": true,
    "count": 3,
    "cables": [...]
  }
  ```

#### Calculs mécaniques

- **`POST /api/calc/span`** - Calcul complet d'une portée
  - Géométrie (corde, flèches)
  - Tensions (T₀, TA, TB)
  - Warnings et erreurs

- **`POST /api/calc/equivalent-span`** - Portée équivalente (Blondel)

- **`POST /api/calc/crr`** - Charge de rupture résiduelle

- **`POST /api/calc/vhl`** - Effort résultant sur support

- **`GET /api/calc/cigre-emissivity`** - Émissivité câble (CIGRE)

- **`POST /api/calc/validate-domain`** - Validation domaine CELESTE

### Exemples d'utilisation

#### Calcul de portée

```bash
curl -X POST "http://localhost:6000/api/calc/span" \
  -H "Content-Type: application/json" \
  -d '{
    "span_length_m": 500.0,
    "delta_h_m": 10.0,
    "cable": {
      "name": "Aster 570",
      "mass_lin_kg_per_m": 1.631,
      "E_MPa": 78000,
      "section_mm2": 564.6,
      "alpha_1e6_per_C": 19.1,
      "rupture_dan": 17200,
      "diameter_mm": 31.5
    },
    "rho_m": 2000,
    "wind_pressure_daPa": 20,
    "angle_topo_grade": 5
  }'
```

Réponse :
```json
{
  "success": true,
  "result": {
    "geometry": {
      "b_m": 500.1,
      "F1_m": 15.63,
      "F2_m": 15.23,
      "H_m": 25.23
    },
    "tensions": {
      "T0_dan": 3200,
      "TA_dan": 3224,
      "TB_dan": 3240
    },
    "warnings": [],
    "errors": []
  }
}
```

#### Récupérer la liste des câbles

```bash
curl http://localhost:6000/api/cables
```

### Documentation interactive

Accédez à la documentation Swagger automatique :
- **URL** : `http://<IP_VM>:6000/docs`
- Testez les endpoints directement depuis l'interface

---

## 🧪 Tests

### Exécuter les tests

```bash
cd /opt/celestex
source .venv/bin/activate

# Tous les tests
pytest backend/tests/ -v

# Tests avec couverture
pytest backend/tests/ --cov=backend --cov-report=html

# Test spécifique
pytest backend/tests/test_mechanical.py::test_calculate_span_complete -v
```

### Résultats attendus

```
collected 21 items

backend/tests/test_mechanical.py::test_span_geometry_cord_length PASSED  [  4%]
backend/tests/test_mechanical.py::test_calculate_sag_horizontal_span PASSED [  9%]
...
backend/tests/test_mechanical.py::test_calculate_span_rho_warning_high PASSED [100%]

```

### Tests couverts

- ✅ Géométrie (corde, longueur)
- ✅ Flèches (portée horizontale, avec dénivelé)
- ✅ Tensions (T₀, TA, TB)
- ✅ Portée équivalente (Blondel)
- ✅ CRR (charge de rupture résiduelle)
- ✅ Effort VHL
- ✅ Émissivité CIGRE
- ✅ Validation domaine CELESTE
- ✅ Warnings et erreurs métier

---

## 🔄 Mise à jour

### Mise à jour automatique

```bash
cd /opt/celestex

# Récupérer les dernières modifications
sudo -u celeste git pull

# Installer les nouvelles dépendances Python
sudo -u celeste bash -c 'source .venv/bin/activate && pip install -r backend/requirements.txt'

# Rebuild le frontend
sudo -u celeste bash -c 'cd frontend && npm ci && npm run build'

# Redémarrer les services
sudo systemctl restart celestex celestex-admin

# Vérifier que tout fonctionne
./check.sh
```

### Vérification après mise à jour

```bash
# Tester l'API
curl http://localhost:6000/api/health

# Vérifier les logs
sudo journalctl -u celestex -n 50
sudo journalctl -u celestex-admin -n 50

# Exécuter les tests
source .venv/bin/activate
pytest backend/tests/ -v
```

### Résolution de problèmes

#### Conflit de fichiers lors du `git pull`

```bash
# Sauvegarder et supprimer les fichiers en conflit
sudo -u celeste mv frontend/package-lock.json /tmp/package-lock.json.bak
sudo -u celeste git pull
```

#### Problèmes de dépendances

```bash
# Réinstaller toutes les dépendances
sudo -u celeste bash -c 'source .venv/bin/activate && pip install --upgrade -r backend/requirements.txt'
sudo -u celeste bash -c 'cd frontend && rm -rf node_modules && npm install'
```

---

## 🗑️ Désinstallation

### Désinstallation automatique

```bash
# Désinstallation complète
curl -sSL https://raw.githubusercontent.com/Maxymou/CELESTE/main/uninstall.sh | bash

# Ou depuis le répertoire d'installation
cd /opt/celestex
./uninstall.sh
```

Le script propose 3 options :
1. **Suppression complète** : services, fichiers, base de données et utilisateur
2. **Conservation des données** : garde `/opt/celestex` pour réinstallation future
3. **Suppression DB uniquement** : efface seulement `data/celestex.db`

### Vérification de la désinstallation

```bash
./verify-uninstall.sh
```

### Désinstallation manuelle (si nécessaire)

```bash
# Arrêter et désactiver les services
sudo systemctl stop celestex celestex-admin
sudo systemctl disable celestex celestex-admin

# Supprimer les fichiers systemd
sudo rm -f /etc/systemd/system/celestex.service
sudo rm -f /etc/systemd/system/celestex-admin.service
sudo systemctl daemon-reload

# Supprimer l'utilisateur
sudo userdel -r celeste

# Supprimer les fichiers
sudo rm -rf /opt/celestex
```

---

## 🔧 Gestion des services

### Commandes systemd

```bash
# Vérifier le statut
sudo systemctl status celestex
sudo systemctl status celestex-admin

# Démarrer
sudo systemctl start celestex celestex-admin

# Arrêter
sudo systemctl stop celestex celestex-admin

# Redémarrer
sudo systemctl restart celestex celestex-admin

# Activer au démarrage
sudo systemctl enable celestex celestex-admin
```

### Consultation des logs

```bash
# Logs en temps réel
sudo journalctl -u celestex -f
sudo journalctl -u celestex-admin -f

# Dernières 100 lignes
sudo journalctl -u celestex -n 100

# Logs avec horodatage
sudo journalctl -u celestex --since "2025-01-01" --until "2025-01-31"

# Logs d'erreur uniquement
sudo journalctl -u celestex -p err
```

---

## 🛠️ Développement

### Démarrage en mode développement

#### Terminal 1 : Frontend (React + Vite)

```bash
cd /opt/celestex/frontend
npm run dev
# Accès : http://localhost:5173
```

#### Terminal 2 : Backend (FastAPI)

```bash
cd /opt/celestex
source .venv/bin/activate
uvicorn backend.main:app --reload --host 0.0.0.0 --port 6000
# Accès : http://localhost:6000
```

#### Terminal 3 : Admin (SQLAdmin)

```bash
cd /opt/celestex
source .venv/bin/activate
export CELESTEX_DB_PATH=./data/celestex.db
export ADMIN_USER=admin
export ADMIN_PASS=admin123
export ADMIN_SECRET=dev-secret
uvicorn backend_admin.main:app --reload --host 0.0.0.0 --port 8000
# Accès : http://localhost:8000
```

### Lancer les tests en mode watch

```bash
source .venv/bin/activate
pytest backend/tests/ -v --looponfail
```

### Build de production

```bash
# Frontend
cd frontend
npm run build
# Fichiers générés dans : frontend/dist/

# Backend (aucun build nécessaire)
```

---

## 📚 Documentation supplémentaire

- **`IMPROVEMENTS.md`** - Détails des améliorations v1.1.0
- **`CONTRIBUTING.md`** - Guide de contribution
- **`CHANGELOG.md`** - Historique des versions
- **`Projet_celeste.md`** - Cahier des charges complet

---

## 📊 Structure du projet

```
celestex/
├── backend/                      # API FastAPI
│   ├── main.py                  # Application principale
│   ├── security.py              # Hashage mots de passe
│   ├── exceptions.py            # Exceptions personnalisées
│   ├── requirements.txt         # Dépendances Python
│   ├── domain/                  # Logique métier
│   │   └── mechanical.py        # Calculs mécaniques
│   ├── models/                  # Modèles de données
│   │   └── db_models.py         # ORM SQLAlchemy
│   └── tests/                   # Tests unitaires
│       └── test_mechanical.py   # Tests calculs
├── backend_admin/               # Dashboard admin
│   └── main.py                  # Interface SQLAdmin
├── frontend/                    # Interface React
│   ├── src/
│   │   ├── App.tsx              # Composant principal
│   │   ├── components/          # Composants React
│   │   └── styles/              # Styles CSS
│   ├── package.json
│   └── vite.config.ts
├── systemd/                     # Services systemd
│   ├── celestex.service
│   └── celestex-admin.service
├── data/                        # Base de données
│   ├── celestex.db              # SQLite
│   ├── Câble.xml                # Catalogue câbles
│   └── Couche câble.xml         # Couches câbles
├── .env                         # Configuration (généré)
├── .gitignore                   # Fichiers ignorés
├── pytest.ini                   # Configuration pytest
├── install.sh                   # Script installation
├── uninstall.sh                 # Script désinstallation
├── check.sh                     # Script vérification
└── README.md                    # Ce fichier
```

---

## 🤝 Contribution

Les contributions sont les bienvenues ! Consultez `CONTRIBUTING.md` pour les guidelines.

---

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

---

## 👤 Auteur

Application professionnelle de calcul de lignes électriques

---

## 📞 Support

En cas de problème :

1. Consultez les logs : `sudo journalctl -u celestex -n 100`
2. Vérifiez la configuration : `./check.sh`
3. Consultez la documentation : `IMPROVEMENTS.md`
4. Ouvrez une issue sur GitHub

---

**Version** : 1.1.0
**Dernière mise à jour** : 21 Octobre 2025
