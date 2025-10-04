#!/bin/bash

# CELESTE X - Script de vérification post-désinstallation
# Usage: ./verify-uninstall.sh

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}    Vérification post-désinstallation${NC}"
echo -e "${BLUE}========================================${NC}"

# Vérifier les services
echo -e "${YELLOW}Vérification des services systemd...${NC}"

if systemctl is-active --quiet celestex; then
    echo -e "${RED}✗ Service celestex: ENCORE ACTIF${NC}"
else
    echo -e "${GREEN}✓ Service celestex: ARRÊTÉ${NC}"
fi

if systemctl is-active --quiet celestex-admin; then
    echo -e "${RED}✗ Service celestex-admin: ENCORE ACTIF${NC}"
else
    echo -e "${GREEN}✓ Service celestex-admin: ARRÊTÉ${NC}"
fi

# Vérifier si les services sont désactivés
if systemctl is-enabled --quiet celestex; then
    echo -e "${RED}✗ Service celestex: ENCORE ACTIVÉ${NC}"
else
    echo -e "${GREEN}✓ Service celestex: DÉSACTIVÉ${NC}"
fi

if systemctl is-enabled --quiet celestex-admin; then
    echo -e "${RED}✗ Service celestex-admin: ENCORE ACTIVÉ${NC}"
else
    echo -e "${GREEN}✓ Service celestex-admin: DÉSACTIVÉ${NC}"
fi

# Vérifier les fichiers de service
echo -e "${YELLOW}Vérification des fichiers systemd...${NC}"

if [ -f "/etc/systemd/system/celestex.service" ]; then
    echo -e "${RED}✗ Fichier celestex.service: ENCORE PRÉSENT${NC}"
else
    echo -e "${GREEN}✓ Fichier celestex.service: SUPPRIMÉ${NC}"
fi

if [ -f "/etc/systemd/system/celestex-admin.service" ]; then
    echo -e "${RED}✗ Fichier celestex-admin.service: ENCORE PRÉSENT${NC}"
else
    echo -e "${GREEN}✓ Fichier celestex-admin.service: SUPPRIMÉ${NC}"
fi

# Vérifier les ports
echo -e "${YELLOW}Vérification des ports...${NC}"

if netstat -tlnp 2>/dev/null | grep -q ":6000 "; then
    echo -e "${RED}✗ Port 6000: ENCORE UTILISÉ${NC}"
    netstat -tlnp 2>/dev/null | grep ":6000 "
else
    echo -e "${GREEN}✓ Port 6000: LIBRE${NC}"
fi

if netstat -tlnp 2>/dev/null | grep -q ":8000 "; then
    echo -e "${RED}✗ Port 8000: ENCORE UTILISÉ${NC}"
    netstat -tlnp 2>/dev/null | grep ":8000 "
else
    echo -e "${GREEN}✓ Port 8000: LIBRE${NC}"
fi

# Vérifier l'utilisateur
echo -e "${YELLOW}Vérification de l'utilisateur système...${NC}"

if id "celeste" &>/dev/null; then
    echo -e "${RED}✗ Utilisateur celeste: ENCORE PRÉSENT${NC}"
else
    echo -e "${GREEN}✓ Utilisateur celeste: SUPPRIMÉ${NC}"
fi

# Vérifier les fichiers d'installation
echo -e "${YELLOW}Vérification des fichiers d'installation...${NC}"

if [ -d "/opt/celestex" ]; then
    echo -e "${YELLOW}⚠ Répertoire /opt/celestex: ENCORE PRÉSENT${NC}"
    echo -e "${YELLOW}  Contenu:${NC}"
    ls -la /opt/celestex/ 2>/dev/null || echo "  (accès refusé)"
else
    echo -e "${GREEN}✓ Répertoire /opt/celestex: SUPPRIMÉ${NC}"
fi

# Vérifier la base de données
if [ -f "/opt/celestex/data/celestex.db" ]; then
    echo -e "${YELLOW}⚠ Base de données: ENCORE PRÉSENTE${NC}"
else
    echo -e "${GREEN}✓ Base de données: SUPPRIMÉE${NC}"
fi

# Test des endpoints
echo -e "${YELLOW}Test des endpoints...${NC}"

if curl -s --connect-timeout 2 http://localhost:6000/api/health >/dev/null 2>&1; then
    echo -e "${RED}✗ API principale: ENCORE ACCESSIBLE${NC}"
else
    echo -e "${GREEN}✓ API principale: INACCESSIBLE${NC}"
fi

if curl -s --connect-timeout 2 -u admin:admin123 http://localhost:8000/admin/health >/dev/null 2>&1; then
    echo -e "${RED}✗ API admin: ENCORE ACCESSIBLE${NC}"
else
    echo -e "${GREEN}✓ API admin: INACCESSIBLE${NC}"
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}    Résumé de la vérification${NC}"
echo -e "${GREEN}========================================${NC}"

# Compter les erreurs
errors=0
if systemctl is-active --quiet celestex; then ((errors++)); fi
if systemctl is-active --quiet celestex-admin; then ((errors++)); fi
if systemctl is-enabled --quiet celestex; then ((errors++)); fi
if systemctl is-enabled --quiet celestex-admin; then ((errors++)); fi
if [ -f "/etc/systemd/system/celestex.service" ]; then ((errors++)); fi
if [ -f "/etc/systemd/system/celestex-admin.service" ]; then ((errors++)); fi
if netstat -tlnp 2>/dev/null | grep -q ":6000 "; then ((errors++)); fi
if netstat -tlnp 2>/dev/null | grep -q ":8000 "; then ((errors++)); fi
if id "celeste" &>/dev/null; then ((errors++)); fi

if [ $errors -eq 0 ]; then
    echo -e "${GREEN}✅ Désinstallation complète réussie !${NC}"
    echo -e "${GREEN}   Tous les composants ont été supprimés.${NC}"
else
    echo -e "${YELLOW}⚠️  Désinstallation partielle${NC}"
    echo -e "${YELLOW}   $errors composant(s) encore présent(s).${NC}"
    echo -e "${YELLOW}   Relancez le script de désinstallation si nécessaire.${NC}"
fi

echo ""
echo -e "${BLUE}Pour réinstaller CELESTE X:${NC}"
echo "curl -sSL https://raw.githubusercontent.com/Maxymou/CELESTE/main/install.sh | bash"
