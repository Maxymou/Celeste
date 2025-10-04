# Changelog CELESTE X

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

## [1.0.0] - 2025-01-04

### Ajouté
- Application FastAPI avec React frontend
- Dashboard admin avec SQLAdmin
- Base de données SQLite avec modèles Cable et Layer
- Scripts d'installation automatisés pour Debian
- Script de désinstallation avec options flexibles
- Services systemd pour la production
- Documentation complète d'installation et désinstallation
- Scripts de vérification post-installation
- Configuration GitHub Actions pour les tests
- Support de l'installation depuis GitHub

### Fonctionnalités
- API REST avec endpoints `/api/health` et `/api/calc/span`
- Interface utilisateur avec onglets (Canton, Portée, Support, Câble, Température)
- Authentification Basic Auth pour l'admin
- Servage des fichiers statiques avec fallback SPA
- Support des fichiers XML d'import (stub)

### Installation
- Installation en une commande : `curl -sSL https://raw.githubusercontent.com/Maxymou/CELESTE/main/install.sh | bash`
- Installation manuelle avec `git clone` et `./install.sh`
- Vérification automatique avec `./check.sh`
- Désinstallation en une commande : `curl -sSL https://raw.githubusercontent.com/Maxymou/CELESTE/main/uninstall.sh | bash`

### Configuration
- Ports : 6000 (app), 8000 (admin)
- Utilisateur système : `celeste`
- Répertoire d'installation : `/opt/celestex`
- Identifiants admin par défaut : `admin` / `admin123`
