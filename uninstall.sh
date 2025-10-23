#!/bin/bash

# CELESTE X - Script de désinstallation
# Usage: curl -sSL https://raw.githubusercontent.com/Maxymou/CELESTE/main/uninstall.sh | bash
# Ou: ./uninstall.sh

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
SERVICE_MAIN="celestex"
SERVICE_ADMIN="celestex-admin"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}    Désinstallation de CELESTE X${NC}"
echo -e "${BLUE}========================================${NC}"

# Vérifier si on est root
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}Ce script ne doit pas être exécuté en tant que root${NC}"
   echo "Utilisez: curl -sSL https://raw.githubusercontent.com/Maxymou/CELESTE/main/uninstall.sh | bash"
   exit 1
fi

# Demander confirmation
echo -e "${YELLOW}⚠️  ATTENTION: Cette action va supprimer complètement CELESTE X${NC}"
echo -e "${YELLOW}   - Arrêt des services systemd${NC}"
echo -e "${YELLOW}   - Suppression des fichiers d'installation${NC}"
echo -e "${YELLOW}   - Suppression de l'utilisateur système${NC}"
echo -e "${YELLOW}   - Suppression de la base de données${NC}"
echo ""
read -p "Êtes-vous sûr de vouloir continuer ? (oui/non): " -r
if [[ ! $REPLY =~ ^[Oo][Uu][Ii]$ ]]; then
    echo -e "${GREEN}Désinstallation annulée.${NC}"
    exit 0
fi

echo ""
echo -e "${YELLOW}Début de la désinstallation...${NC}"

# Arrêter les services
echo -e "${YELLOW}Arrêt des services...${NC}"
if systemctl is-active --quiet $SERVICE_MAIN; then
    sudo systemctl stop $SERVICE_MAIN
    echo -e "${GREEN}✓ Service $SERVICE_MAIN arrêté${NC}"
else
    echo -e "${YELLOW}⚠ Service $SERVICE_MAIN déjà arrêté${NC}"
fi

if systemctl is-active --quiet $SERVICE_ADMIN; then
    sudo systemctl stop $SERVICE_ADMIN
    echo -e "${GREEN}✓ Service $SERVICE_ADMIN arrêté${NC}"
else
    echo -e "${YELLOW}⚠ Service $SERVICE_ADMIN déjà arrêté${NC}"
fi

# Désactiver les services
echo -e "${YELLOW}Désactivation des services...${NC}"
if systemctl is-enabled --quiet $SERVICE_MAIN; then
    sudo systemctl disable $SERVICE_MAIN
    echo -e "${GREEN}✓ Service $SERVICE_MAIN désactivé${NC}"
else
    echo -e "${YELLOW}⚠ Service $SERVICE_MAIN déjà désactivé${NC}"
fi

if systemctl is-enabled --quiet $SERVICE_ADMIN; then
    sudo systemctl disable $SERVICE_ADMIN
    echo -e "${GREEN}✓ Service $SERVICE_ADMIN désactivé${NC}"
else
    echo -e "${YELLOW}⚠ Service $SERVICE_ADMIN déjà désactivé${NC}"
fi

# Supprimer les fichiers de service systemd
echo -e "${YELLOW}Suppression des fichiers systemd...${NC}"
if [ -f "/etc/systemd/system/$SERVICE_MAIN.service" ]; then
    sudo rm -f "/etc/systemd/system/$SERVICE_MAIN.service"
    echo -e "${GREEN}✓ Fichier $SERVICE_MAIN.service supprimé${NC}"
else
    echo -e "${YELLOW}⚠ Fichier $SERVICE_MAIN.service non trouvé${NC}"
fi

if [ -f "/etc/systemd/system/$SERVICE_ADMIN.service" ]; then
    sudo rm -f "/etc/systemd/system/$SERVICE_ADMIN.service"
    echo -e "${GREEN}✓ Fichier $SERVICE_ADMIN.service supprimé${NC}"
else
    echo -e "${YELLOW}⚠ Fichier $SERVICE_ADMIN.service non trouvé${NC}"
fi

# Recharger systemd
sudo systemctl daemon-reload
echo -e "${GREEN}✓ Configuration systemd rechargée${NC}"

# Demander si on veut garder les données
echo ""
echo -e "${YELLOW}Que souhaitez-vous faire avec les données ?${NC}"
echo "1) Supprimer complètement (base de données + fichiers)"
echo "2) Garder les données (base de données + fichiers)"
echo "3) Supprimer seulement la base de données"
read -p "Votre choix (1/2/3): " -r

case $REPLY in
    1)
        echo -e "${YELLOW}Suppression complète des données...${NC}"
        if [ -d "$INSTALL_DIR" ]; then
            sudo rm -rf "$INSTALL_DIR"
            echo -e "${GREEN}✓ Répertoire $INSTALL_DIR supprimé${NC}"
        else
            echo -e "${YELLOW}⚠ Répertoire $INSTALL_DIR non trouvé${NC}"
        fi
        ;;
    2)
        echo -e "${GREEN}✓ Données conservées dans $INSTALL_DIR${NC}"
        ;;
    3)
        echo -e "${YELLOW}Suppression de la base de données uniquement...${NC}"
        if [ -f "$INSTALL_DIR/data/celestex.db" ]; then
            sudo rm -f "$INSTALL_DIR/data/celestex.db"
            echo -e "${GREEN}✓ Base de données supprimée${NC}"
        else
            echo -e "${YELLOW}⚠ Base de données non trouvée${NC}"
        fi
        ;;
    *)
        echo -e "${YELLOW}Choix invalide, conservation des données par défaut${NC}"
        ;;
esac

# Supprimer l'utilisateur système
echo -e "${YELLOW}Suppression de l'utilisateur système...${NC}"
if id "$SERVICE_USER" &>/dev/null; then
    # Vérifier si l'utilisateur a des processus en cours
    if pgrep -u "$SERVICE_USER" > /dev/null; then
        echo -e "${YELLOW}⚠ L'utilisateur $SERVICE_USER a des processus en cours${NC}"
        echo -e "${YELLOW}  Arrêt des processus...${NC}"
        sudo pkill -u "$SERVICE_USER" || true
        sleep 2
    fi
    
    sudo userdel -r "$SERVICE_USER" 2>/dev/null || {
        echo -e "${YELLOW}⚠ Impossible de supprimer l'utilisateur $SERVICE_USER${NC}"
        echo -e "${YELLOW}  (peut-être qu'il a encore des fichiers ouverts)${NC}"
    }
    echo -e "${GREEN}✓ Utilisateur $SERVICE_USER supprimé${NC}"
else
    echo -e "${YELLOW}⚠ Utilisateur $SERVICE_USER non trouvé${NC}"
fi

# Nettoyer les logs systemd
echo -e "${YELLOW}Nettoyage des logs systemd...${NC}"
sudo journalctl --vacuum-time=1d > /dev/null 2>&1 || true
echo -e "${GREEN}✓ Logs systemd nettoyés${NC}"

# Vérifier les ports
echo -e "${YELLOW}Vérification des ports...${NC}"
if netstat -tlnp 2>/dev/null | grep -q ":6000 "; then
    echo -e "${YELLOW}⚠ Port 6000 encore utilisé${NC}"
    netstat -tlnp 2>/dev/null | grep ":6000 "
fi

if netstat -tlnp 2>/dev/null | grep -q ":8000 "; then
    echo -e "${YELLOW}⚠ Port 8000 encore utilisé${NC}"
    netstat -tlnp 2>/dev/null | grep ":8000 "
fi

# Message final
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}    Désinstallation terminée !${NC}"
echo -e "${GREEN}========================================${NC}"

if [ -d "$INSTALL_DIR" ]; then
    echo -e "${BLUE}Données conservées dans:${NC} $INSTALL_DIR"
    echo -e "${BLUE}Pour supprimer complètement:${NC} sudo rm -rf $INSTALL_DIR"
else
    echo -e "${GREEN}✓ Toutes les données ont été supprimées${NC}"
fi

echo ""
echo -e "${YELLOW}Pour réinstaller CELESTE X:${NC}"
echo "curl -sSL https://raw.githubusercontent.com/Maxymou/CELESTE/main/install.sh | bash"
echo ""
echo -e "${GREEN}Merci d'avoir utilisé CELESTE X ! 👋${NC}"
