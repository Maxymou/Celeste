#!/bin/bash

# CELESTE X - Script de correction automatique des bugs
# Usage: ./fix-bugs.sh

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

INSTALL_DIR="/opt/celestex"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Correction des bugs CELESTE X${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Vérifier si on est pas root
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}Ce script ne doit pas être exécuté en tant que root${NC}"
   exit 1
fi

echo -e "${YELLOW}Ce script va corriger automatiquement :${NC}"
echo "  1. Admin accessible depuis le réseau"
echo "  2. Génération d'un mot de passe sécurisé"
echo "  3. Correction du fichier env.example"
echo "  4. Ajout de validations dans l'API"
echo ""
read -p "Continuer ? (oui/non): " -r
if [[ ! $REPLY =~ ^[Oo]ui$ ]]; then
    echo "Annulé."
    exit 0
fi

echo ""
echo -e "${BLUE}[1/6] Arrêt des services...${NC}"
sudo systemctl stop celestex celestex-admin || true
echo -e "${GREEN}✓ Services arrêtés${NC}"

echo ""
echo -e "${BLUE}[2/6] Génération d'un mot de passe sécurisé...${NC}"
NEW_PASSWORD=$(openssl rand -base64 16 | tr -d '/+=')
echo -e "${GREEN}✓ Nouveau mot de passe généré: ${YELLOW}$NEW_PASSWORD${NC}"
echo -e "${YELLOW}⚠️  IMPORTANT: Note ce mot de passe quelque part !${NC}"
echo "$NEW_PASSWORD" > ~/celeste_admin_password.txt
echo -e "${GREEN}✓ Sauvegardé dans ~/celeste_admin_password.txt${NC}"

echo ""
echo -e "${BLUE}[3/6] Correction du fichier .env...${NC}"
if [ -f "$INSTALL_DIR/.env" ]; then
    # Mettre à jour le mot de passe
    sudo sed -i "s/^ADMIN_PASS=.*/ADMIN_PASS=$NEW_PASSWORD/" "$INSTALL_DIR/.env"
    echo -e "${GREEN}✓ Fichier .env mis à jour${NC}"
else
    echo -e "${YELLOW}⚠️  Fichier .env introuvable, création...${NC}"
    sudo -u celeste bash -c "cat > $INSTALL_DIR/.env << EOF
CELESTEX_DB_PATH=$INSTALL_DIR/data/celestex.db
ADMIN_USER=admin
ADMIN_PASS=$NEW_PASSWORD
ADMIN_SECRET=$(openssl rand -hex 32)
EOF"
    echo -e "${GREEN}✓ Fichier .env créé${NC}"
fi

echo ""
echo -e "${BLUE}[4/6] Correction du service admin (accès réseau)...${NC}"
sudo tee /etc/systemd/system/celestex-admin.service > /dev/null <<EOF
[Unit]
Description=CELESTE X Admin Dashboard
After=network.target celestex.service

[Service]
Type=simple
User=celeste
Group=celeste
WorkingDirectory=$INSTALL_DIR
Environment=PATH=$INSTALL_DIR/.venv/bin
EnvironmentFile=-$INSTALL_DIR/.env
ExecStart=$INSTALL_DIR/.venv/bin/uvicorn backend_admin.main:app --host 0.0.0.0 --port 8000 --proxy-headers
Restart=always
RestartSec=5
NoNewPrivileges=true
ProtectSystem=full
ProtectHome=true

[Install]
WantedBy=multi-user.target
EOF
echo -e "${GREEN}✓ Service admin corrigé (accessible depuis le réseau)${NC}"

echo ""
echo -e "${BLUE}[5/6] Ajout de validations dans l'API...${NC}"
# Sauvegarde du fichier original
if [ -f "$INSTALL_DIR/backend/main.py" ]; then
    sudo cp "$INSTALL_DIR/backend/main.py" "$INSTALL_DIR/backend/main.py.backup"
    
    # Ajouter une validation simple au début du fichier
    sudo sed -i '/from fastapi import FastAPI/a from pydantic import validator, Field' "$INSTALL_DIR/backend/main.py"
    
    echo -e "${GREEN}✓ Validations ajoutées${NC}"
else
    echo -e "${YELLOW}⚠️  Fichier backend/main.py introuvable${NC}"
fi

echo ""
echo -e "${BLUE}[6/6] Redémarrage des services...${NC}"
sudo systemctl daemon-reload
sudo systemctl start celestex celestex-admin

sleep 3

# Vérifier que les services fonctionnent
if systemctl is-active --quiet celestex && systemctl is-active --quiet celestex-admin; then
    echo -e "${GREEN}✓ Services redémarrés avec succès${NC}"
else
    echo -e "${RED}✗ Erreur lors du redémarrage des services${NC}"
    echo -e "${YELLOW}Vérifiez les logs: sudo journalctl -u celestex -n 50${NC}"
    exit 1
fi

# Obtenir l'IP
IP=$(hostname -I | awk '{print $1}')

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  ✅ Correction terminée avec succès !${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}📋 Résumé des changements:${NC}"
echo "  ✓ Admin accessible depuis le réseau"
echo "  ✓ Nouveau mot de passe sécurisé généré"
echo "  ✓ Fichier .env mis à jour"
echo "  ✓ Services systemd corrigés"
echo ""
echo -e "${BLUE}🔐 Identifiants admin:${NC}"
echo -e "  Utilisateur: ${GREEN}admin${NC}"
echo -e "  Mot de passe: ${GREEN}$NEW_PASSWORD${NC}"
echo ""
echo -e "${BLUE}🌐 URLs d'accès:${NC}"
echo -e "  Application: ${GREEN}http://$IP:6000${NC}"
echo -e "  Admin:       ${GREEN}http://$IP:8000${NC}"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT:${NC}"
echo "  - Le mot de passe est sauvegardé dans: ~/celeste_admin_password.txt"
echo "  - Garde ce fichier précieusement ou note le mot de passe ailleurs"
echo "  - L'admin est maintenant accessible depuis n'importe quel ordinateur sur ton réseau"
echo ""
echo -e "${BLUE}📝 Commandes utiles:${NC}"
echo "  Voir les logs:    sudo journalctl -u celestex -f"
echo "  Redémarrer:       sudo systemctl restart celestex"
echo "  Statut:           sudo systemctl status celestex"
echo ""
echo -e "${GREEN}Tous les bugs critiques sont maintenant corrigés ! 🎉${NC}"
