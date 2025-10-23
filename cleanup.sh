#!/bin/bash

# CELESTE X - Script de nettoyage complet (à utiliser en dernier recours)
# Usage: ./cleanup.sh
# ATTENTION: Ce script force la suppression de tout ce qui concerne CELESTE X

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${RED}========================================${NC}"
echo -e "${RED}    NETTOYAGE COMPLET CELESTE X${NC}"
echo -e "${RED}========================================${NC}"
echo -e "${RED}⚠️  ATTENTION: Ce script va FORCER la suppression${NC}"
echo -e "${RED}   de TOUS les composants CELESTE X !${NC}"
echo ""

# Demander confirmation multiple
read -p "Êtes-vous ABSOLUMENT SÛR ? Tapez 'SUPPRIMER' pour continuer: " -r
if [[ ! $REPLY == "SUPPRIMER" ]]; then
    echo -e "${GREEN}Nettoyage annulé.${NC}"
    exit 0
fi

echo ""
echo -e "${YELLOW}Début du nettoyage complet...${NC}"

# Tuer tous les processus liés à CELESTE X
echo -e "${YELLOW}Arrêt forcé des processus...${NC}"
sudo pkill -f "celestex" 2>/dev/null || true
sudo pkill -f "uvicorn.*celestex" 2>/dev/null || true
sudo pkill -u "celeste" 2>/dev/null || true
sleep 2

# Arrêter et désactiver les services
echo -e "${YELLOW}Arrêt et désactivation des services...${NC}"
sudo systemctl stop celestex celestex-admin 2>/dev/null || true
sudo systemctl disable celestex celestex-admin 2>/dev/null || true

# Supprimer les fichiers de service
echo -e "${YELLOW}Suppression des fichiers systemd...${NC}"
sudo rm -f /etc/systemd/system/celestex.service
sudo rm -f /etc/systemd/system/celestex-admin.service
sudo systemctl daemon-reload

# Supprimer l'utilisateur (forcé)
echo -e "${YELLOW}Suppression forcée de l'utilisateur...${NC}"
sudo userdel -f -r celeste 2>/dev/null || true

# Supprimer le répertoire d'installation
echo -e "${YELLOW}Suppression du répertoire d'installation...${NC}"
sudo rm -rf /opt/celestex

# Nettoyer les logs
echo -e "${YELLOW}Nettoyage des logs...${NC}"
sudo journalctl --vacuum-time=1d > /dev/null 2>&1 || true

# Nettoyer les caches
echo -e "${YELLOW}Nettoyage des caches...${NC}"
sudo apt autoremove -y 2>/dev/null || true
sudo apt autoclean 2>/dev/null || true

# Vérifier les ports
echo -e "${YELLOW}Vérification des ports...${NC}"
if netstat -tlnp 2>/dev/null | grep -q ":6000 "; then
    echo -e "${YELLOW}⚠ Port 6000 encore utilisé, processus:${NC}"
    netstat -tlnp 2>/dev/null | grep ":6000 "
    echo -e "${YELLOW}  Vous devrez peut-être redémarrer le système${NC}"
fi

if netstat -tlnp 2>/dev/null | grep -q ":8000 "; then
    echo -e "${YELLOW}⚠ Port 8000 encore utilisé, processus:${NC}"
    netstat -tlnp 2>/dev/null | grep ":8000 "
    echo -e "${YELLOW}  Vous devrez peut-être redémarrer le système${NC}"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}    NETTOYAGE COMPLET TERMINÉ${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ Tous les composants CELESTE X ont été supprimés${NC}"
echo ""
echo -e "${YELLOW}Recommandations:${NC}"
echo "1. Redémarrez le système pour libérer complètement les ports"
echo "2. Vérifiez avec: ./verify-uninstall.sh"
echo "3. Pour réinstaller: curl -sSL https://raw.githubusercontent.com/Maxymou/CELESTE/main/install.sh | bash"
echo ""
echo -e "${GREEN}Nettoyage terminé ! 🧹${NC}"
