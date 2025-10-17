#!/bin/bash

# CELESTE X - Script de vérification de santé complète
# Usage: ./health-check.sh

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

INSTALL_DIR="/opt/celestex"
SERVICE_USER="celeste"
ERRORS=0
WARNINGS=0

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Vérification CELESTE X${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Fonction pour afficher les résultats
check_ok() {
    echo -e "${GREEN}✓${NC} $1"
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARNINGS++))
}

check_error() {
    echo -e "${RED}✗${NC} $1"
    ((ERRORS++))
}

# 1. Vérifier l'utilisateur système
echo -e "${BLUE}[1/12] Utilisateur système${NC}"
if id "$SERVICE_USER" &>/dev/null; then
    check_ok "Utilisateur $SERVICE_USER existe"
else
    check_error "Utilisateur $SERVICE_USER n'existe pas"
fi
echo ""

# 2. Vérifier le répertoire d'installation
echo -e "${BLUE}[2/12] Répertoire d'installation${NC}"
if [ -d "$INSTALL_DIR" ]; then
    check_ok "Répertoire $INSTALL_DIR existe"
    
    # Vérifier les permissions
    OWNER=$(stat -c '%U' "$INSTALL_DIR")
    if [ "$OWNER" == "$SERVICE_USER" ]; then
        check_ok "Permissions correctes sur $INSTALL_DIR"
    else
        check_warn "Propriétaire incorrect: $OWNER (devrait être $SERVICE_USER)"
    fi
else
    check_error "Répertoire $INSTALL_DIR n'existe pas"
fi
echo ""

# 3. Vérifier les fichiers backend
echo -e "${BLUE}[3/12] Backend Python${NC}"
if [ -f "$INSTALL_DIR/backend/main.py" ]; then
    check_ok "Fichier backend/main.py existe"
else
    check_error "Fichier backend/main.py manquant"
fi

if [ -d "$INSTALL_DIR/.venv" ]; then
    check_ok "Environnement virtuel Python existe"
else
    check_error "Environnement virtuel Python manquant"
fi

if [ -f "$INSTALL_DIR/backend/requirements.txt" ]; then
    check_ok "Fichier requirements.txt existe"
else
    check_error "Fichier requirements.txt manquant"
fi
echo ""

# 4. Vérifier les fichiers frontend
echo -e "${BLUE}[4/12] Frontend React${NC}"
if [ -d "$INSTALL_DIR/frontend" ]; then
    check_ok "Répertoire frontend existe"
else
    check_error "Répertoire frontend manquant"
fi

if [ -f "$INSTALL_DIR/frontend/package.json" ]; then
    check_ok "Fichier package.json existe"
else
    check_error "Fichier package.json manquant"
fi

if [ -d "$INSTALL_DIR/frontend/src" ]; then
    check_ok "Répertoire src existe"
else
    check_error "Répertoire src manquant"
fi
echo ""

# 5. Vérifier le build frontend
echo -e "${BLUE}[5/12] Build frontend${NC}"
if [ -d "$INSTALL_DIR/frontend/dist" ]; then
    check_ok "Répertoire dist existe"
    
    if [ -f "$INSTALL_DIR/frontend/dist/index.html" ]; then
        check_ok "Fichier index.html existe"
        
        # Vérifier la taille du fichier
        SIZE=$(stat -c%s "$INSTALL_DIR/frontend/dist/index.html")
        if [ "$SIZE" -gt 100 ]; then
            check_ok "Fichier index.html non vide ($SIZE octets)"
        else
            check_warn "Fichier index.html trop petit ($SIZE octets)"
        fi
    else
        check_error "Fichier index.html manquant"
    fi
    
    if [ -d "$INSTALL_DIR/frontend/dist/assets" ]; then
        COUNT=$(ls -1 "$INSTALL_DIR/frontend/dist/assets" 2>/dev/null | wc -l)
        if [ "$COUNT" -gt 0 ]; then
            check_ok "Dossier assets contient $COUNT fichier(s)"
        else
            check_warn "Dossier assets vide"
        fi
    else
        check_warn "Dossier assets manquant"
    fi
else
    check_error "Répertoire dist manquant - Le build n'a pas été effectué"
    echo -e "${YELLOW}  → Exécutez: ./fix-build.sh${NC}"
fi
echo ""

# 6. Vérifier les services systemd
echo -e "${BLUE}[6/12] Services systemd${NC}"
if systemctl is-enabled --quiet celestex 2>/dev/null; then
    check_ok "Service celestex activé au démarrage"
else
    check_warn "Service celestex non activé au démarrage"
fi

if systemctl is-active --quiet celestex 2>/dev/null; then
    check_ok "Service celestex actif"
else
    check_error "Service celestex inactif"
fi

if systemctl is-enabled --quiet celestex-admin 2>/dev/null; then
    check_ok "Service celestex-admin activé au démarrage"
else
    check_warn "Service celestex-admin non activé au démarrage"
fi

if systemctl is-active --quiet celestex-admin 2>/dev/null; then
    check_ok "Service celestex-admin actif"
else
    check_error "Service celestex-admin inactif"
fi
echo ""

# 7. Vérifier les ports
echo -e "${BLUE}[7/12] Ports réseau${NC}"
if command -v netstat &> /dev/null; then
    if netstat -tlnp 2>/dev/null | grep -q ":6000 "; then
        check_ok "Port 6000 ouvert (application)"
    else
        check_error "Port 6000 fermé"
    fi
    
    if netstat -tlnp 2>/dev/null | grep -q ":8000 "; then
        check_ok "Port 8000 ouvert (admin)"
    else
        check_error "Port 8000 fermé"
    fi
else
    check_warn "netstat non disponible, impossible de vérifier les ports"
fi
echo ""

# 8. Vérifier les endpoints API
echo -e "${BLUE}[8/12] Endpoints API${NC}"
if command -v curl &> /dev/null; then
    if curl -s --connect-timeout 5 http://localhost:6000/api/health 2>/dev/null | grep -q "ok"; then
        check_ok "API principale répond (/api/health)"
    else
        check_error "API principale ne répond pas"
    fi
    
    if curl -s --connect-timeout 5 -u admin:admin123 http://localhost:8000/admin/health 2>/dev/null | grep -q "ok"; then
        check_ok "API admin répond (/admin/health)"
    else
        check_warn "API admin ne répond pas (ou identifiants incorrects)"
    fi
else
    check_warn "curl non disponible, impossible de tester les endpoints"
fi
echo ""

# 9. Vérifier la base de données
echo -e "${BLUE}[9/12] Base de données${NC}"
if [ -f "$INSTALL_DIR/data/celestex.db" ]; then
    check_ok "Fichier celestex.db existe"
    
    SIZE=$(stat -c%s "$INSTALL_DIR/data/celestex.db")
    if [ "$SIZE" -gt 0 ]; then
        check_ok "Base de données non vide ($SIZE octets)"
    else
        check_warn "Base de données vide"
    fi
else
    check_warn "Base de données non créée (sera créée au premier démarrage)"
fi
echo ""

# 10. Vérifier les fichiers de configuration
echo -e "${BLUE}[10/12] Configuration${NC}"
if [ -f "$INSTALL_DIR/.env" ]; then
    check_ok "Fichier .env existe"
else
    check_warn "Fichier .env manquant"
fi

if [ -f "/etc/systemd/system/celestex.service" ]; then
    check_ok "Fichier service celestex existe"
else
    check_error "Fichier service celestex manquant"
fi

if [ -f "/etc/systemd/system/celestex-admin.service" ]; then
    check_ok "Fichier service celestex-admin existe"
else
    check_error "Fichier service celestex-admin manquant"
fi
echo ""

# 11. Vérifier les dépendances système
echo -e "${BLUE}[11/12] Dépendances système${NC}"
if command -v python3 &> /dev/null; then
    VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    check_ok "Python installé (version $VERSION)"
else
    check_error "Python3 non installé"
fi

if command -v node &> /dev/null; then
    VERSION=$(node --version)
    check_ok "Node.js installé (version $VERSION)"
else
    check_error "Node.js non installé"
fi

if command -v npm &> /dev/null; then
    VERSION=$(npm --version)
    check_ok "npm installé (version $VERSION)"
else
    check_error "npm non installé"
fi

if command -v git &> /dev/null; then
    VERSION=$(git --version | awk '{print $3}')
    check_ok "Git installé (version $VERSION)"
else
    check_warn "Git non installé"
fi
echo ""

# 12. Vérifier l'accès réseau
echo -e "${BLUE}[12/12] Accès réseau${NC}"
IP=$(hostname -I 2>/dev/null | awk '{print $1}')
if [ -n "$IP" ]; then
    check_ok "Adresse IP: $IP"
else
    check_warn "Impossible de déterminer l'adresse IP"
fi

if command -v hostname &> /dev/null; then
    HOSTNAME=$(hostname)
    check_ok "Nom d'hôte: $HOSTNAME"
fi
echo ""

# Résumé
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Résumé${NC}"
echo -e "${BLUE}========================================${NC}"

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ Tous les tests sont passés !${NC}"
    echo -e "${GREEN}   CELESTE X est correctement installé et fonctionnel${NC}"
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  $WARNINGS avertissement(s) détecté(s)${NC}"
    echo -e "${YELLOW}   L'application fonctionne mais pourrait être améliorée${NC}"
else
    echo -e "${RED}❌ $ERRORS erreur(s) et $WARNINGS avertissement(s) détectés${NC}"
    echo -e "${RED}   L'application nécessite des corrections${NC}"
fi

echo ""
echo -e "${BLUE}Informations d'accès:${NC}"
if [ -n "$IP" ]; then
    echo -e "  Application: http://$IP:6000"
    echo -e "  Admin:       http://$IP:8000"
fi
echo -e "  Local:       http://localhost:6000"

echo ""
echo -e "${BLUE}Commandes utiles:${NC}"
echo -e "  Logs:        sudo journalctl -u celestex -f"
echo -e "  Status:      sudo systemctl status celestex"
echo -e "  Restart:     sudo systemctl restart celestex"
if [ $ERRORS -gt 0 ]; then
    echo -e "  Correction:  ./fix-build.sh"
fi

exit $ERRORS
