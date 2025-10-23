#!/bin/bash

# CELESTE X - Script de correction du build frontend
# Usage: ./fix-build.sh

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

INSTALL_DIR="/opt/celestex"
SERVICE_USER="celeste"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Correction du build CELESTE X${NC}"
echo -e "${BLUE}========================================${NC}"

# Vérifier si on est root
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}Ce script ne doit pas être exécuté en tant que root${NC}"
   exit 1
fi

# Vérifier que le répertoire existe
if [ ! -d "$INSTALL_DIR" ]; then
    echo -e "${RED}Erreur: Le répertoire $INSTALL_DIR n'existe pas${NC}"
    echo -e "${YELLOW}Lancez d'abord le script d'installation${NC}"
    exit 1
fi

cd "$INSTALL_DIR"

echo -e "${YELLOW}1. Arrêt du service...${NC}"
sudo systemctl stop celestex || true

echo -e "${YELLOW}2. Sauvegarde de l'ancien build...${NC}"
if [ -d "frontend/dist" ]; then
    sudo -u "$SERVICE_USER" mv frontend/dist frontend/dist.backup.$(date +%Y%m%d_%H%M%S) || true
fi

echo -e "${YELLOW}3. Nettoyage des dépendances Node.js...${NC}"
sudo -u "$SERVICE_USER" bash -c "cd frontend && rm -rf node_modules package-lock.json"
echo -e "${GREEN}✓ Nettoyage terminé${NC}"

echo -e "${YELLOW}4. Installation des dépendances...${NC}"
sudo -u "$SERVICE_USER" bash -c "cd frontend && npm install"
echo -e "${GREEN}✓ Dépendances installées${NC}"

echo -e "${YELLOW}5. Build du frontend...${NC}"
sudo -u "$SERVICE_USER" bash -c "cd frontend && npm run build"

# Vérifier que le build a réussi
if [ ! -f "$INSTALL_DIR/frontend/dist/index.html" ]; then
    echo -e "${RED}✗ Erreur: Le build a échoué${NC}"
    echo -e "${RED}Le fichier index.html n'existe pas dans frontend/dist/${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Build réussi${NC}"

echo -e "${YELLOW}6. Vérification des fichiers générés...${NC}"
echo -e "${BLUE}Contenu de frontend/dist/:${NC}"
ls -lh "$INSTALL_DIR/frontend/dist/" || true
ls -lh "$INSTALL_DIR/frontend/dist/assets/" || true

echo -e "${YELLOW}7. Correction des permissions...${NC}"
sudo chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR/frontend/dist"
echo -e "${GREEN}✓ Permissions corrigées${NC}"

echo -e "${YELLOW}8. Redémarrage du service...${NC}"
sudo systemctl start celestex

# Attendre le démarrage
sleep 3

# Vérifier que le service fonctionne
if systemctl is-active --quiet celestex; then
    echo -e "${GREEN}✓ Service celestex démarré${NC}"
else
    echo -e "${RED}✗ Erreur: Le service n'a pas démarré${NC}"
    echo -e "${YELLOW}Affichage des logs:${NC}"
    sudo journalctl -u celestex -n 30
    exit 1
fi

echo -e "${YELLOW}9. Test de l'API...${NC}"
sleep 2

if curl -s http://localhost:6000/api/health | grep -q "ok"; then
    echo -e "${GREEN}✓ API opérationnelle${NC}"
else
    echo -e "${RED}✗ L'API ne répond pas${NC}"
    exit 1
fi

# Obtenir l'IP
IP=$(hostname -I | awk '{print $1}')

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Correction terminée avec succès !${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Votre application est accessible:${NC}"
echo -e "  Local:    http://localhost:6000"
echo -e "  Réseau:   http://$IP:6000"
echo -e "  Domaine:  https://celeste.redyx.fr"
echo ""
echo -e "${YELLOW}Vérification dans le navigateur:${NC}"
echo -e "  Ouvrez https://celeste.redyx.fr"
echo -e "  Vous devriez voir l'interface CELESTE"
echo ""
echo -e "${BLUE}Commandes utiles:${NC}"
echo -e "  Logs:    sudo journalctl -u celestex -f"
echo -e "  Status:  sudo systemctl status celestex"
echo -e "  Restart: sudo systemctl restart celestex"
echo ""
echo -e "${GREEN}Correction terminée ! 🎉${NC}"
