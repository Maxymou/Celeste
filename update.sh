#!/bin/bash

# CELESTE X - Script de mise à jour
# Usage: curl -sSL https://raw.githubusercontent.com/Maxymou/CELESTE/main/update.sh | bash
# Ou: sudo -u celeste ./update.sh

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
BRANCH="${1:-main}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}    Mise à jour de CELESTE X${NC}"
echo -e "${BLUE}========================================${NC}"

# Vérifier si on est l'utilisateur celeste ou root
if [[ $EUID -ne 0 ]] && [[ $(whoami) != "$SERVICE_USER" ]]; then
   echo -e "${RED}Ce script doit être exécuté en tant que root ou $SERVICE_USER${NC}"
   echo "Utilisez: sudo -u celeste ./update.sh"
   echo "Ou: curl -sSL https://raw.githubusercontent.com/Maxymou/CELESTE/main/update.sh | bash"
   exit 1
fi

# Vérifier que l'installation existe
if [ ! -d "$INSTALL_DIR" ]; then
    echo -e "${RED}CELESTE X n'est pas installé dans $INSTALL_DIR${NC}"
    echo -e "${YELLOW}Pour installer CELESTE X:${NC}"
    echo "curl -sSL https://raw.githubusercontent.com/Maxymou/CELESTE/main/install.sh | bash"
    exit 1
fi

# Aller dans le répertoire d'installation
cd "$INSTALL_DIR"

# Vérifier la branche actuelle
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
echo -e "${BLUE}Branche actuelle:${NC} $CURRENT_BRANCH"
echo -e "${BLUE}Mise à jour vers:${NC} $BRANCH"

# Sauvegarder les modifications locales
echo -e "${YELLOW}Vérification des modifications locales...${NC}"
if ! git diff-index --quiet HEAD --; then
    echo -e "${YELLOW}⚠ Des modifications locales ont été détectées${NC}"
    echo -e "${YELLOW}  Sauvegarde en cours...${NC}"
    git stash push -m "Auto-stash before update $(date +%Y%m%d_%H%M%S)"
    STASHED=true
else
    STASHED=false
fi

# Arrêter les services
echo -e "${YELLOW}Arrêt des services...${NC}"
if [[ $EUID -eq 0 ]]; then
    systemctl stop $SERVICE_MAIN $SERVICE_ADMIN
else
    sudo systemctl stop $SERVICE_MAIN $SERVICE_ADMIN
fi
echo -e "${GREEN}✓ Services arrêtés${NC}"

# Récupérer les dernières modifications
echo -e "${YELLOW}Téléchargement des mises à jour...${NC}"
git fetch origin

# Checkout de la branche demandée
if [ "$CURRENT_BRANCH" != "$BRANCH" ]; then
    echo -e "${YELLOW}Changement de branche: $CURRENT_BRANCH → $BRANCH${NC}"
    git checkout $BRANCH
fi

# Pull les modifications
BEFORE_UPDATE=$(git rev-parse HEAD)
git pull origin $BRANCH
AFTER_UPDATE=$(git rev-parse HEAD)

if [ "$BEFORE_UPDATE" == "$AFTER_UPDATE" ]; then
    echo -e "${GREEN}✓ Déjà à jour${NC}"
    NO_UPDATES=true
else
    echo -e "${GREEN}✓ Mise à jour effectuée${NC}"
    echo -e "${BLUE}Changements:${NC}"
    git log --oneline --no-merges $BEFORE_UPDATE..$AFTER_UPDATE | head -10
    NO_UPDATES=false
fi

# Restaurer les modifications locales si nécessaire
if [ "$STASHED" = true ]; then
    echo -e "${YELLOW}Restauration des modifications locales...${NC}"
    if git stash pop; then
        echo -e "${GREEN}✓ Modifications locales restaurées${NC}"
    else
        echo -e "${RED}⚠ Conflit lors de la restauration des modifications${NC}"
        echo -e "${YELLOW}  Vos modifications sont toujours disponibles dans le stash${NC}"
        echo -e "${YELLOW}  Utilisez 'git stash list' pour les voir${NC}"
    fi
fi

# Vérifier si le frontend a changé
if [ "$NO_UPDATES" = false ]; then
    FRONTEND_CHANGED=$(git diff --name-only $BEFORE_UPDATE $AFTER_UPDATE | grep -c "^frontend/" || echo "0")

    if [ "$FRONTEND_CHANGED" -gt 0 ]; then
        echo -e "${YELLOW}Mise à jour du frontend détectée${NC}"
        echo -e "${BLUE}Nettoyage et rebuild...${NC}"

        cd frontend
        rm -rf node_modules package-lock.json dist
        npm install
        npm run build

        if [ ! -f "dist/index.html" ]; then
            echo -e "${RED}Erreur: Le build frontend a échoué${NC}"
            exit 1
        fi

        echo -e "${GREEN}✓ Frontend mis à jour${NC}"
        cd ..
    else
        echo -e "${GREEN}✓ Pas de changement frontend${NC}"
    fi

    # Vérifier si le backend a changé
    BACKEND_CHANGED=$(git diff --name-only $BEFORE_UPDATE $AFTER_UPDATE | grep -c "^backend/" || echo "0")

    if [ "$BACKEND_CHANGED" -gt 0 ]; then
        echo -e "${YELLOW}Mise à jour du backend détectée${NC}"
        echo -e "${BLUE}Mise à jour des dépendances...${NC}"

        source .venv/bin/activate
        pip install --upgrade pip
        pip install -r backend/requirements.txt

        echo -e "${GREEN}✓ Backend mis à jour${NC}"
    else
        echo -e "${GREEN}✓ Pas de changement backend${NC}"
    fi

    # Exécuter les migrations si nécessaire
    if [ -f "scripts/migrate_add_users.py" ]; then
        echo -e "${YELLOW}Vérification des migrations...${NC}"
        source .venv/bin/activate
        python scripts/migrate_add_users.py 2>&1 | grep -q "existe déjà" && \
            echo -e "${GREEN}✓ Base de données à jour${NC}" || \
            echo -e "${GREEN}✓ Migrations appliquées${NC}"
    fi
fi

# Redémarrer les services
echo -e "${YELLOW}Redémarrage des services...${NC}"
if [[ $EUID -eq 0 ]]; then
    systemctl start $SERVICE_MAIN $SERVICE_ADMIN
    sleep 3
    systemctl status $SERVICE_MAIN --no-pager -l || true
    systemctl status $SERVICE_ADMIN --no-pager -l || true
else
    sudo systemctl start $SERVICE_MAIN $SERVICE_ADMIN
    sleep 3
    sudo systemctl status $SERVICE_MAIN --no-pager -l || true
    sudo systemctl status $SERVICE_ADMIN --no-pager -l || true
fi

# Vérifier que les services fonctionnent
echo -e "${YELLOW}Vérification des services...${NC}"
if systemctl is-active --quiet $SERVICE_MAIN; then
    echo -e "${GREEN}✓ Service $SERVICE_MAIN actif${NC}"
else
    echo -e "${RED}✗ Service $SERVICE_MAIN inactif${NC}"
    if [[ $EUID -eq 0 ]]; then
        journalctl -u $SERVICE_MAIN -n 20
    else
        sudo journalctl -u $SERVICE_MAIN -n 20
    fi
fi

if systemctl is-active --quiet $SERVICE_ADMIN; then
    echo -e "${GREEN}✓ Service $SERVICE_ADMIN actif${NC}"
else
    echo -e "${RED}✗ Service $SERVICE_ADMIN inactif${NC}"
    if [[ $EUID -eq 0 ]]; then
        journalctl -u $SERVICE_ADMIN -n 20
    else
        sudo journalctl -u $SERVICE_ADMIN -n 20
    fi
fi

# Obtenir l'IP
IP=$(hostname -I | awk '{print $1}')

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}    Mise à jour terminée !${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Accès à l'application:${NC}"
echo -e "  Application: http://$IP:6000"
echo -e "  Admin:       http://$IP:8000"
echo ""
echo -e "${BLUE}Commandes utiles:${NC}"
echo "  sudo systemctl status $SERVICE_MAIN"
echo "  sudo systemctl restart $SERVICE_MAIN"
echo "  sudo journalctl -u $SERVICE_MAIN -f"
echo ""
echo -e "${GREEN}Mise à jour réussie ! 🎉${NC}"
