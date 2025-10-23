#!/bin/bash

# CELESTE X - Script de vérification post-installation
# Usage: ./check.sh

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}    Vérification CELESTE X${NC}"
echo -e "${BLUE}========================================${NC}"

# Charger la configuration depuis .env si présent
ENV_FILE="/opt/celestex/.env"
if [ -f "$ENV_FILE" ]; then
    # shellcheck disable=SC1090
    source "$ENV_FILE"
fi

ADMIN_USER=${ADMIN_USER:-admin}
ADMIN_PASS=${ADMIN_PASS:-admin123}

# Vérifier les services
echo -e "${YELLOW}Vérification des services systemd...${NC}"

if systemctl is-active --quiet celestex; then
    echo -e "${GREEN}✓ Service celestex: ACTIF${NC}"
else
    echo -e "${RED}✗ Service celestex: INACTIF${NC}"
fi

if systemctl is-active --quiet celestex-admin; then
    echo -e "${GREEN}✓ Service celestex-admin: ACTIF${NC}"
else
    echo -e "${RED}✗ Service celestex-admin: INACTIF${NC}"
fi

# Vérifier les ports
echo -e "${YELLOW}Vérification des ports...${NC}"

if netstat -tlnp 2>/dev/null | grep -q ":6000 "; then
    echo -e "${GREEN}✓ Port 6000 (app): OUVERT${NC}"
else
    echo -e "${RED}✗ Port 6000 (app): FERMÉ${NC}"
fi

if netstat -tlnp 2>/dev/null | grep -q ":8000 "; then
    echo -e "${GREEN}✓ Port 8000 (admin): OUVERT${NC}"
else
    echo -e "${RED}✗ Port 8000 (admin): FERMÉ${NC}"
fi

# Test des endpoints
echo -e "${YELLOW}Test des endpoints...${NC}"

if curl -s http://localhost:6000/api/health | grep -q "ok"; then
    echo -e "${GREEN}✓ API principale: RÉPOND${NC}"
else
    echo -e "${RED}✗ API principale: NE RÉPOND PAS${NC}"
fi

if curl -s -u "$ADMIN_USER:$ADMIN_PASS" http://localhost:8000/admin/health | grep -q "ok"; then
    echo -e "${GREEN}✓ API admin: RÉPOND${NC}"
else
    echo -e "${RED}✗ API admin: NE RÉPOND PAS${NC}"
fi

# Vérifier les fichiers
echo -e "${YELLOW}Vérification des fichiers...${NC}"

if [ -f "/opt/celestex/frontend/dist/index.html" ]; then
    echo -e "${GREEN}✓ Build frontend: PRÉSENT${NC}"
else
    echo -e "${RED}✗ Build frontend: MANQUANT${NC}"
fi

if [ -f "/opt/celestex/data/celestex.db" ]; then
    echo -e "${GREEN}✓ Base de données: PRÉSENTE${NC}"
else
    echo -e "${YELLOW}⚠ Base de données: CRÉÉE À LA PREMIÈRE UTILISATION${NC}"
fi

# Obtenir l'IP
IP=$(hostname -I | awk '{print $1}')

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}    Résumé de la vérification${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "${BLUE}Application:${NC} http://$IP:6000"
echo -e "${BLUE}Admin:${NC}       http://$IP:8000"
echo -e "${BLUE}Identifiants:${NC} $ADMIN_USER / $ADMIN_PASS"
echo ""
echo -e "${YELLOW}Logs en temps réel:${NC}"
echo "  sudo journalctl -u celestex -f"
echo "  sudo journalctl -u celestex-admin -f"
