# 🌟 CELESTE X

**CELESTE X** est une application web professionnelle pour la gestion et le calcul de câbles électriques, développée avec React/TypeScript (frontend) et FastAPI (backend).

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Node 20+](https://img.shields.io/badge/node-20+-green.svg)](https://nodejs.org/)

---

## 📋 Table des matières

- [✨ Fonctionnalités](#-fonctionnalités)
- [🚀 Installation rapide](#-installation-rapide)
- [🔒 Authentification et gestion des utilisateurs](#-authentification-et-gestion-des-utilisateurs)
- [🔧 Configuration](#-configuration)
- [🔄 Mise à jour](#-mise-à-jour)
- [🗑️ Désinstallation](#️-désinstallation)
- [🔌 API](#-api)
- [🛠️ Développement](#️-développement)
- [📊 Architecture](#-architecture)
- [🐛 Dépannage](#-dépannage)
- [📝 Changelog](#-changelog)

---

## ✨ Fonctionnalités

### Application principale
- ⚡ **Dashboard intuitif** avec indicateurs en temps réel
- 📊 **Calculs de câbles** : tension mécanique, longueurs de portée, flèches
- 📁 **Import/Export** de données (JSON, Excel, CSV)
- 🔐 **Authentification sécurisée** avec JWT
- 👥 **Gestion des utilisateurs** multi-niveaux
- 📱 **Interface responsive** adaptée mobile/tablette
- 🌙 **Mode sombre** disponible

### Interface d'administration
- 👤 **Gestion complète des utilisateurs**
  - Création et suppression d'utilisateurs
  - Modification des informations (nom, email, mot de passe)
  - Activation/désactivation des comptes
  - Mots de passe hashés avec bcrypt
- 📊 **Gestion de la base de données câbles**
- 🔍 **Recherche et filtrage avancés**
- 📈 **Statistiques d'utilisation**

---

## 🚀 Installation rapide

### Prérequis

- **OS** : Debian 11+, Ubuntu 20.04+ ou distribution compatible
- **Python** : 3.13+
- **Node.js** : 20+
- **npm** : 9+
- **Git** : Pour le clonage du repository

### Installation automatique

```bash
curl -sSL https://raw.githubusercontent.com/Maxymou/CELESTE/main/install.sh | bash
```

Le script d'installation va automatiquement :
1. ✅ Installer les dépendances système
2. ✅ Créer l'utilisateur système `celeste`
3. ✅ Cloner le repository dans `/opt/celestex`
4. ✅ Builder le frontend React
5. ✅ Installer les dépendances Python
6. ✅ Créer la base de données et l'utilisateur admin
7. ✅ Configurer les services systemd
8. ✅ Démarrer l'application

### Accès après installation

- **Application** : http://VOTRE_IP:6000
- **Administration** : http://VOTRE_IP:8000

**Identifiants par défaut** :
- Email : `admin@admin.fr`
- Mot de passe : `admin`

⚠️ **IMPORTANT** : Changez le mot de passe admin immédiatement après la première connexion !

---

## 🔒 Authentification et gestion des utilisateurs

### Système d'authentification multi-niveaux

CELESTE X utilise un système d'authentification en 3 niveaux :

1. **Base de données** : Utilisateurs créés via l'interface admin (priorité 1)
2. **Admin hardcodé** : Compte admin par défaut (fallback)
3. **Liste blanche** : Pour rétrocompatibilité (legacy)

### Gestion des utilisateurs via l'interface admin

#### Accéder à la gestion des utilisateurs

1. Connectez-vous à l'interface admin : http://VOTRE_IP:8000
2. Utilisez les identifiants admin
3. Cliquez sur l'onglet **"Users"** dans le menu

#### Créer un nouvel utilisateur

1. Cliquez sur **"Create"**
2. Remplissez le formulaire :
   - **Nom** : Nom complet de l'utilisateur
   - **Email** : Adresse email (utilisée pour la connexion)
   - **Mot de passe** : Mot de passe (sera hashé automatiquement)
   - **Actif** : Cochez pour activer le compte
3. Cliquez sur **"Save"**

#### Modifier un utilisateur

1. Cliquez sur un utilisateur dans la liste
2. Modifiez les champs souhaités
3. Laissez le champ **"Mot de passe"** vide pour conserver l'ancien
4. Cliquez sur **"Save"**

#### Désactiver un utilisateur

1. Cliquez sur un utilisateur
2. Décochez **"Actif"**
3. Cliquez sur **"Save"**

L'utilisateur ne pourra plus se connecter mais ses données sont conservées.

#### Supprimer un utilisateur

1. Cliquez sur un utilisateur
2. Cliquez sur **"Delete"**
3. Confirmez la suppression

⚠️ **Attention** : La suppression est irréversible !

### Sécurité des mots de passe

- ✅ **Hashage bcrypt** : Tous les mots de passe sont hashés avec bcrypt
- ✅ **Salage automatique** : Chaque mot de passe a un salt unique
- ✅ **Validation JWT** : Les tokens sont vérifiés à chaque requête
- ✅ **Expiration automatique** : Les sessions expirent après 30 jours

### Changer le mot de passe admin

#### Via l'interface admin

1. Connectez-vous à http://VOTRE_IP:8000
2. Cliquez sur **"Users"**
3. Cliquez sur l'utilisateur **"Administrateur"**
4. Entrez un nouveau mot de passe dans le champ **"Mot de passe"**
5. Cliquez sur **"Save"**

#### Via la ligne de commande

```bash
# Méthode 1 : Utiliser le script de migration
cd /opt/celestex
sudo -u celeste .venv/bin/python scripts/migrate_add_users.py

# Le script recréera l'admin avec le mot de passe défini dans .env

# Méthode 2 : Générer un hash manuellement
cd /opt/celestex
sudo -u celeste .venv/bin/python -m backend.security "VotreNouveauMotDePasse"

# Copiez le hash généré et mettez à jour la base de données via l'interface admin
```

### Recommandations de sécurité

- ✅ **Obligatoire** : Changer le mot de passe admin par défaut
- ✅ **Recommandé** : Utiliser des mots de passe d'au moins 12 caractères
- ✅ **Recommandé** : Activer un firewall et restreindre l'accès au port 8000
- ✅ **Recommandé** : Configurer HTTPS avec un reverse proxy (nginx/caddy)
- ✅ **Recommandé** : Désactiver les comptes utilisateurs inutilisés
- ✅ **Recommandé** : Effectuer des sauvegardes régulières de la base de données

---

## 🔧 Configuration

### Fichier de configuration principal

Le fichier `/opt/celestex/.env` contient toutes les variables de configuration :

```bash
# Base de données
CELESTEX_DB_PATH=/opt/celestex/data/celestex.db

# JWT (généré automatiquement à l'installation)
JWT_SECRET_KEY=votre-secret-jwt-64-caracteres-genere-automatiquement

# Admin par défaut (CHANGER EN PRODUCTION)
ADMIN_USER=admin@admin.fr
ADMIN_PASS=admin

# Secret de session admin
ADMIN_SECRET=votre-secret-session-unique-genere-automatiquement

# Ports (si modification nécessaire)
APP_PORT=6000
ADMIN_PORT=8000
```

### Modifier la configuration

```bash
# Éditer le fichier de configuration
sudo -u celeste nano /opt/celestex/.env

# Redémarrer les services après modification
sudo systemctl restart celestex celestex-admin
```

### Configuration avancée

Pour personnaliser l'installation (répertoire, utilisateur, ports), éditez `/opt/celestex/deploy.conf` avant l'installation.

---

## 🔄 Mise à jour

### Mise à jour automatique

```bash
curl -sSL https://raw.githubusercontent.com/Maxymou/CELESTE/main/update.sh | bash
```

ou

```bash
cd /opt/celestex
sudo -u celeste ./update.sh
```

Le script de mise à jour va :
1. Sauvegarder les modifications locales
2. Arrêter les services
3. Télécharger les dernières modifications
4. Rebuilder le frontend si nécessaire
5. Mettre à jour les dépendances backend
6. Exécuter les migrations de base de données
7. Redémarrer les services

### Mise à jour manuelle

```bash
# Aller dans le répertoire d'installation
cd /opt/celestex

# Arrêter les services
sudo systemctl stop celestex celestex-admin

# Sauvegarder les modifications locales
sudo -u celeste git stash

# Télécharger les mises à jour
sudo -u celeste git pull origin main

# Restaurer les modifications locales
sudo -u celeste git stash pop

# Rebuild du frontend (si nécessaire)
cd frontend
sudo -u celeste rm -rf node_modules package-lock.json dist
sudo -u celeste npm install
sudo -u celeste npm run build
cd ..

# Mise à jour des dépendances backend (si nécessaire)
sudo -u celeste bash -c "source .venv/bin/activate && pip install -r backend/requirements.txt"

# Exécuter les migrations (si nécessaire)
sudo -u celeste bash -c "source .venv/bin/activate && python scripts/migrate_add_users.py"

# Redémarrer les services
sudo systemctl start celestex celestex-admin

# Vérifier le statut
sudo systemctl status celestex celestex-admin
```

### Changer de branche

```bash
cd /opt/celestex
sudo systemctl stop celestex celestex-admin
sudo -u celeste git checkout NOM_DE_LA_BRANCHE
sudo -u celeste git pull
# Suivre les étapes de mise à jour manuelle ci-dessus
```

---

## 🗑️ Désinstallation

### Désinstallation automatique

```bash
curl -sSL https://raw.githubusercontent.com/Maxymou/CELESTE/main/uninstall.sh | bash
```

Le script vous demandera :
1. Confirmation de la désinstallation
2. Si vous souhaitez conserver ou supprimer les données

### Options de désinstallation

- **Option 1** : Suppression complète (application + données)
- **Option 2** : Garder les données (réinstallation possible)
- **Option 3** : Supprimer seulement la base de données

### Désinstallation manuelle

```bash
# Arrêter et désactiver les services
sudo systemctl stop celestex celestex-admin
sudo systemctl disable celestex celestex-admin

# Supprimer les fichiers systemd
sudo rm /etc/systemd/system/celestex.service
sudo rm /etc/systemd/system/celestex-admin.service
sudo systemctl daemon-reload

# Supprimer l'installation
sudo rm -rf /opt/celestex

# Supprimer l'utilisateur système
sudo userdel -r celeste
```

---

## 🔌 API

### Endpoints disponibles

#### Santé et informations

- **`GET /api/health`** - Vérification de l'état de l'API
  ```json
  {"status": "ok", "version": "1.0.0"}
  ```

#### Authentification

- **`POST /api/login`** - Connexion utilisateur
  ```json
  {
    "email": "admin@admin.fr",
    "password": "admin"
  }
  ```
  Retourne un JWT token

- **`GET /api/auth/verify`** - Vérifier un token JWT
  Nécessite le header `Authorization: Bearer TOKEN`

#### Câbles

- **`GET /api/cables`** - Liste des câbles disponibles
  ```json
  {
    "success": true,
    "cables": [...]
  }
  ```

- **`GET /api/cables/{cable_id}`** - Détails d'un câble spécifique

#### Calculs

- **`POST /api/calculate/tension`** - Calculer la tension mécanique
- **`POST /api/calculate/span`** - Calculer les longueurs de portée
- **`POST /api/calculate/sag`** - Calculer les flèches

### Interface d'administration API

L'interface admin fournit des endpoints pour :
- Gestion CRUD des utilisateurs
- Gestion CRUD des câbles
- Import/Export de données

Documentation complète : http://VOTRE_IP:6000/docs

---

## 🛠️ Développement

### Environnement local

#### Prérequis
- Python 3.13+
- Node.js 20+
- Git

#### Installation

```bash
# Cloner le repository
git clone https://github.com/Maxymou/CELESTE.git
cd CELESTE

# Backend
cd backend
python3 -m venv .venv
source .venv/bin/activate  # ou .venv\Scripts\activate sur Windows
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

#### Lancer en développement

```bash
# Terminal 1 : Backend
cd backend
source .venv/bin/activate
uvicorn main:app --reload --port 6000

# Terminal 2 : Frontend
cd frontend
npm run dev

# Terminal 3 : Admin
cd backend_admin
source ../backend/.venv/bin/activate
uvicorn main:app --reload --port 8000
```

### Structure du projet

```
CELESTE/
├── backend/              # API FastAPI
│   ├── main.py          # Point d'entrée principal
│   ├── auth.py          # Gestion de l'authentification
│   ├── security.py      # Hashage des mots de passe
│   ├── models/          # Modèles de données
│   │   └── db_models.py # Modèles SQLAlchemy
│   └── requirements.txt
├── backend_admin/        # Interface d'administration
│   └── main.py          # Vues admin SQLAdmin
├── frontend/            # Application React
│   ├── src/
│   │   ├── components/  # Composants React
│   │   ├── contexts/    # Contexts (Auth, etc.)
│   │   └── pages/       # Pages de l'application
│   └── package.json
├── scripts/             # Scripts utilitaires
│   └── migrate_add_users.py  # Migration utilisateurs
├── install.sh           # Script d'installation
├── update.sh            # Script de mise à jour
├── uninstall.sh         # Script de désinstallation
└── README.md            # Ce fichier
```

### Tests

```bash
# Backend
cd backend
source .venv/bin/activate
pytest

# Frontend
cd frontend
npm test
```

### Build de production

```bash
# Frontend
cd frontend
npm run build

# Le frontend buildé sera dans frontend/dist/
```

---

## 📊 Architecture

### Stack technique

**Frontend**
- React 18 + TypeScript
- Vite (build tool)
- Tailwind CSS
- React Router

**Backend**
- FastAPI (Python 3.13)
- SQLAlchemy (ORM)
- SQLAdmin (interface admin)
- Pydantic (validation)
- JWT (authentification)
- Bcrypt (hashage mots de passe)

**Base de données**
- SQLite (développement/production légère)
- PostgreSQL (production scalable)

**Déploiement**
- systemd (gestion des services)
- Uvicorn (serveur ASGI)
- Nginx/Caddy (reverse proxy optionnel)

### Flux d'authentification

1. L'utilisateur se connecte avec email/password
2. Le backend vérifie d'abord dans la base de données
3. Si trouvé, vérifie le hash bcrypt du mot de passe
4. Si valide, génère un JWT token avec expiration 30 jours
5. Le frontend stocke le token dans localStorage
6. Chaque requête API inclut le token dans le header `Authorization`
7. Le backend valide le token avant de traiter la requête

---

## 🐛 Dépannage

### Les services ne démarrent pas

```bash
# Vérifier les logs
sudo journalctl -u celestex -n 50
sudo journalctl -u celestex-admin -n 50

# Vérifier les permissions
sudo chown -R celeste:celeste /opt/celestex

# Redémarrer les services
sudo systemctl restart celestex celestex-admin
```

### Erreur "Cannot use column_list and column_exclude_list together"

Cette erreur a été corrigée dans les dernières versions. Mettez à jour :

```bash
curl -sSL https://raw.githubusercontent.com/Maxymou/CELESTE/main/update.sh | bash
```

### Erreur "KeyError: 'password'" lors de la création d'utilisateur

Cette erreur a été corrigée. Le modèle User inclut maintenant une propriété `password` temporaire. Mettez à jour l'application.

### Le champ mot de passe n'apparaît pas dans le formulaire

Vérifiez que vous utilisez la dernière version :
```bash
cd /opt/celestex
sudo -u celeste git log -1
```

Le dernier commit doit inclure le fix pour le champ password.

### Problème de connexion avec les identifiants admin

```bash
# Vérifier le fichier .env
cat /opt/celestex/.env | grep ADMIN

# Réinitialiser le mot de passe admin
cd /opt/celestex
sudo -u celeste bash -c "source .venv/bin/activate && python scripts/migrate_add_users.py"
```

### Port déjà utilisé

```bash
# Vérifier les ports en cours d'utilisation
sudo netstat -tlnp | grep -E ':(6000|8000)'

# Arrêter les processus utilisant les ports
sudo systemctl stop celestex celestex-admin

# Ou modifier les ports dans /opt/celestex/.env
```

### Base de données corrompue

```bash
# Sauvegarder l'ancienne base
sudo -u celeste cp /opt/celestex/data/celestex.db /opt/celestex/data/celestex.db.backup

# Recréer la base
sudo -u celeste rm /opt/celestex/data/celestex.db
sudo -u celeste bash -c "source .venv/bin/activate && python scripts/migrate_add_users.py"

# Redémarrer les services
sudo systemctl restart celestex celestex-admin
```

---

## 📝 Changelog

### Version actuelle (main)

**Nouvelles fonctionnalités**
- ✨ Système complet de gestion des utilisateurs
- ✨ Interface admin pour créer/modifier/supprimer des utilisateurs
- ✨ Authentification multi-niveaux (BDD, admin hardcodé, liste blanche)
- ✨ Hashage sécurisé des mots de passe avec bcrypt
- ✨ Vérification des tokens JWT au chargement de l'application
- ✨ Script de mise à jour automatique (update.sh)
- ✨ Script de migration pour créer la table users

**Améliorations**
- 🔧 Identifiants admin changés en admin@admin.fr / admin
- 🔧 Génération automatique de JWT_SECRET_KEY à l'installation
- 🔧 Suppression de toutes les références à "RTE"
- 🔧 Documentation complète dans le README

**Corrections de bugs**
- 🐛 Fix: Erreur "column_list and column_exclude_list together"
- 🐛 Fix: Erreur "KeyError: 'password'"
- 🐛 Fix: Incompatibilité SQLAlchemy 2.x avec annotations non mappées
- 🐛 Fix: Incompatibilité passlib/bcrypt - utilisation directe de bcrypt
- 🐛 Fix: Champ password non visible dans le formulaire utilisateur

**Sécurité**
- 🔒 Hashage bcrypt pour tous les mots de passe
- 🔒 Validation des tokens JWT côté serveur
- 🔒 Propriété password temporaire non persistée en base

Voir [CHANGELOG.md](CHANGELOG.md) pour l'historique complet.

---

## 🤝 Contribution

Les contributions sont les bienvenues ! Voir [CONTRIBUTING.md](CONTRIBUTING.md) pour les guidelines.

1. Fork le projet
2. Créez une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

---

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## 📞 Support

- 📧 **Issues GitHub** : [https://github.com/Maxymou/CELESTE/issues](https://github.com/Maxymou/CELESTE/issues)
- 📚 **Documentation** : Voir les fichiers `.md` dans le repository
- 💬 **Discussions** : [https://github.com/Maxymou/CELESTE/discussions](https://github.com/Maxymou/CELESTE/discussions)

---

## 🙏 Remerciements

Merci à tous les contributeurs qui ont participé à ce projet !

---

**Développé avec ❤️ par l'équipe CELESTE X**
