#!/bin/bash

# CELESTE X - Script d'installation automatisé pour Debian
# Usage: curl -sSL https://raw.githubusercontent.com/Maxymou/CELESTE/main/install.sh | bash

set -e

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="/opt/celestex"
SERVICE_USER="celeste"
GITHUB_REPO="https://github.com/Maxymou/CELESTE.git"
ADMIN_USER="admin"
ADMIN_PASS="admin123"  # À changer en production !
if [ -z "${ADMIN_SECRET:-}" ]; then
    if command -v openssl >/dev/null 2>&1; then
        ADMIN_SECRET="$(openssl rand -hex 32)"
    else
        ADMIN_SECRET="$(python3 - <<'PY'
import secrets
print(secrets.token_hex(32))
PY
)"
    fi
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}    Installation de CELESTE X${NC}"
echo -e "${BLUE}========================================${NC}"

# Vérifier si on est root
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}Ce script ne doit pas être exécuté en tant que root${NC}"
   echo "Utilisez: curl -sSL https://raw.githubusercontent.com/Maxymou/CELESTE/main/install.sh | bash"
   exit 1
fi

# Vérifier la distribution
if ! command -v apt &> /dev/null; then
    echo -e "${RED}Ce script est conçu pour Debian/Ubuntu avec apt${NC}"
    exit 1
fi

echo -e "${YELLOW}Mise à jour du système...${NC}"
sudo apt update

echo -e "${YELLOW}Installation des prérequis...${NC}"
sudo apt install -y python3 python3-venv python3-pip nodejs npm git curl

# Vérifier les versions
echo -e "${YELLOW}Vérification des versions...${NC}"
python3 --version
node --version
npm --version

# Créer l'utilisateur système
echo -e "${YELLOW}Création de l'utilisateur système...${NC}"
if ! id "$SERVICE_USER" &>/dev/null; then
    sudo useradd -r -s /bin/false -d "$INSTALL_DIR" "$SERVICE_USER"
    echo -e "${GREEN}Utilisateur $SERVICE_USER créé${NC}"
else
    echo -e "${YELLOW}Utilisateur $SERVICE_USER existe déjà${NC}"
fi

# Créer le répertoire d'installation
echo -e "${YELLOW}Préparation du répertoire d'installation...${NC}"
sudo mkdir -p "$INSTALL_DIR"
sudo chown "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"

# Cloner le repository
echo -e "${YELLOW}Téléchargement du code source...${NC}"
if [ -d "$INSTALL_DIR/.git" ]; then
    echo -e "${YELLOW}Mise à jour du code existant...${NC}"
    sudo -u "$SERVICE_USER" git -C "$INSTALL_DIR" pull
else
    sudo -u "$SERVICE_USER" git clone "$GITHUB_REPO" "$INSTALL_DIR"
fi

# Aller dans le répertoire d'installation
cd "$INSTALL_DIR"

# Configuration du frontend
echo -e "${YELLOW}Configuration du frontend...${NC}"
sudo -u "$SERVICE_USER" bash -c "cd frontend && npm ci && npm run build"

# Configuration du backend
echo -e "${YELLOW}Configuration du backend...${NC}"
sudo -u "$SERVICE_USER" python3 -m venv .venv
sudo -u "$SERVICE_USER" bash -c "source .venv/bin/activate && pip install --upgrade pip"
sudo -u "$SERVICE_USER" bash -c "source .venv/bin/activate && pip install -r backend/requirements.txt"
sudo -u "$SERVICE_USER" bash -c "source .venv/bin/activate && pip install sqladmin"

# Créer le répertoire data
sudo -u "$SERVICE_USER" mkdir -p data

# Configuration des variables d'environnement
echo -e "${YELLOW}Configuration des variables d'environnement...${NC}"
sudo -u "$SERVICE_USER" cp env.example .env
sudo -u "$SERVICE_USER" sed -i "s|/opt/celestex/data/celestex.db|$INSTALL_DIR/data/celestex.db|g" .env
sudo -u "$SERVICE_USER" sed -i "s|ADMIN_USER=admin|ADMIN_USER=$ADMIN_USER|g" .env
sudo -u "$SERVICE_USER" sed -i "s|ADMIN_PASS=admin|ADMIN_PASS=$ADMIN_PASS|g" .env
sudo -u "$SERVICE_USER" sed -i "s|ADMIN_SECRET=change-me|ADMIN_SECRET=$ADMIN_SECRET|g" .env

# Installation des services systemd
echo -e "${YELLOW}Installation des services systemd...${NC}"
sudo cp systemd/celestex.service /etc/systemd/system/
sudo cp systemd/celestex-admin.service /etc/systemd/system/

# Mettre à jour les chemins dans les services
sudo sed -i "s|/opt/celestex|$INSTALL_DIR|g" /etc/systemd/system/celestex.service
sudo sed -i "s|/opt/celestex|$INSTALL_DIR|g" /etc/systemd/system/celestex-admin.service

# Recharger systemd et activer les services
sudo systemctl daemon-reload
sudo systemctl enable celestex
sudo systemctl enable celestex-admin

# Démarrer les services
echo -e "${YELLOW}Démarrage des services...${NC}"
sudo systemctl start celestex
sudo systemctl start celestex-admin

# Attendre que les services démarrent
sleep 3

# Vérifier le statut des services
echo -e "${YELLOW}Vérification du statut des services...${NC}"
if sudo systemctl is-active --quiet celestex; then
    echo -e "${GREEN}✓ Service celestex démarré avec succès${NC}"
else
    echo -e "${RED}✗ Erreur lors du démarrage du service celestex${NC}"
    sudo systemctl status celestex
fi

if sudo systemctl is-active --quiet celestex-admin; then
    echo -e "${GREEN}✓ Service celestex-admin démarré avec succès${NC}"
else
    echo -e "${RED}✗ Erreur lors du démarrage du service celestex-admin${NC}"
    sudo systemctl status celestex-admin
fi

# Obtenir l'IP de la machine
IP=$(hostname -I | awk '{print $1}')

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}    Installation terminée !${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "${BLUE}Application principale:${NC} http://$IP:6000"
echo -e "${BLUE}Admin dashboard:${NC}      http://$IP:8000"
echo -e "${BLUE}Identifiants admin:${NC}   $ADMIN_USER / $ADMIN_PASS"
echo ""
echo -e "${YELLOW}Commandes utiles:${NC}"
echo "  sudo systemctl status celestex"
echo "  sudo systemctl status celestex-admin"
echo "  sudo systemctl restart celestex"
echo "  sudo systemctl restart celestex-admin"
echo "  sudo journalctl -u celestex -f"
echo "  sudo journalctl -u celestex-admin -f"
echo ""
echo -e "${YELLOW}Pour mettre à jour:${NC}"
echo "  cd $INSTALL_DIR"
echo "  sudo -u $SERVICE_USER git pull"
echo "  sudo -u $SERVICE_USER bash -c 'cd frontend && npm ci && npm run build'"
echo "  sudo -u $SERVICE_USER bash -c 'source .venv/bin/activate && pip install -r backend/requirements.txt'"
echo "  sudo systemctl restart celestex celestex-admin"
