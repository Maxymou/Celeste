# Guide de Sécurité CELESTE X

Ce document décrit les bonnes pratiques de sécurité pour l'installation et l'exploitation de CELESTE X en production.

## 📋 Table des matières

- [Sécurisation initiale](#-sécurisation-initiale)
- [Gestion des mots de passe](#-gestion-des-mots-de-passe)
- [Contrôle d'accès réseau](#-contrôle-daccès-réseau)
- [Sécurisation du reverse proxy](#-sécurisation-du-reverse-proxy)
- [Surveillance et journalisation](#-surveillance-et-journalisation)
- [Mises à jour de sécurité](#-mises-à-jour-de-sécurité)
- [Sauvegarde et restauration](#-sauvegarde-et-restauration)
- [Audit de sécurité](#-audit-de-sécurité)

---

## 🔐 Sécurisation initiale

### 1. Changer immédiatement le mot de passe admin

**CRITIQUE** : Le mot de passe par défaut `admin123` DOIT être changé avant toute mise en production.

#### Étape 1 : Générer un hash bcrypt sécurisé

```bash
cd /opt/celestex
source .venv/bin/activate

# Générer un hash avec un mot de passe fort
python -m backend.security "VotreMotDePasseTresSecurise2025!"
```

**Règles pour un mot de passe fort** :
- ✅ Minimum 12 caractères
- ✅ Mélange de majuscules et minuscules
- ✅ Chiffres et caractères spéciaux
- ✅ Unique (jamais utilisé ailleurs)
- ❌ Pas de mots du dictionnaire
- ❌ Pas d'informations personnelles

#### Étape 2 : Mettre à jour le fichier .env

```bash
# Éditer le fichier de configuration
sudo -u celeste nano /opt/celestex/.env

# Remplacer cette ligne :
ADMIN_PASS=admin123

# Par le hash généré :
ADMIN_PASS=$2b$12$xyz...abcdef123456789
```

#### Étape 3 : Redémarrer le service admin

```bash
sudo systemctl restart celestex-admin

# Vérifier qu'il n'y a plus de warning de sécurité
sudo journalctl -u celestex-admin -n 20 | grep -i "sécurité"
```

✅ **Si aucun warning** → Mot de passe sécurisé
❌ **Si warning présent** → Le hash n'a pas été appliqué correctement

---

### 2. Modifier le secret de session

Le secret de session est utilisé pour chiffrer les cookies d'authentification.

```bash
# Générer un secret aléatoire
openssl rand -hex 32

# Éditer .env
sudo -u celeste nano /opt/celestex/.env

# Remplacer :
ADMIN_SECRET=change-me

# Par une valeur aléatoire unique :
ADMIN_SECRET=a1b2c3d4e5f6...xyz789

# Redémarrer
sudo systemctl restart celestex-admin
```

---

### 3. Vérifier les permissions des fichiers

```bash
# Le fichier .env doit être accessible uniquement par l'utilisateur celeste
sudo chown celeste:celeste /opt/celestex/.env
sudo chmod 600 /opt/celestex/.env

# Vérifier
ls -la /opt/celestex/.env
# Attendu : -rw------- 1 celeste celeste ...
```

---

## 🔑 Gestion des mots de passe

### Politique de mots de passe

| Critère | Minimum | Recommandé |
|---------|---------|------------|
| Longueur | 8 caractères | 16+ caractères |
| Majuscules | Oui | Oui |
| Minuscules | Oui | Oui |
| Chiffres | Oui | Oui |
| Caractères spéciaux | Non | Oui |
| Changement | Jamais | Tous les 90 jours |

### Rotation des mots de passe

```bash
# 1. Générer un nouveau hash
python -m backend.security "NouveauMotDePasseSecurise2025!"

# 2. Mettre à jour .env
sudo -u celeste nano /opt/celestex/.env

# 3. Tester la connexion avant de redémarrer
# Gardez une session admin ouverte comme backup !

# 4. Redémarrer le service
sudo systemctl restart celestex-admin

# 5. Vérifier la connexion avec le nouveau mot de passe
```

### Stockage sécurisé

❌ **À NE PAS FAIRE** :
- Stocker les mots de passe en clair dans des fichiers
- Partager les mots de passe par email
- Utiliser le même mot de passe sur plusieurs systèmes

✅ **BONNES PRATIQUES** :
- Utiliser un gestionnaire de mots de passe (Bitwarden, KeePass)
- Stocker le hash bcrypt dans `.env` uniquement
- Limiter l'accès au fichier `.env`

---

## 🌐 Contrôle d'accès réseau

### Firewall - Restreindre l'accès au port admin (8000)

```bash
# Si vous utilisez UFW (Uncomplicated Firewall)

# Autoriser uniquement depuis localhost
sudo ufw allow from 127.0.0.1 to any port 8000

# OU autoriser uniquement depuis un réseau privé
sudo ufw allow from 192.168.1.0/24 to any port 8000

# Autoriser l'app principale depuis n'importe où
sudo ufw allow 6000/tcp

# Activer le firewall
sudo ufw enable

# Vérifier les règles
sudo ufw status numbered
```

### Accès via tunnel SSH

Pour accéder à l'interface admin depuis l'extérieur de manière sécurisée :

```bash
# Depuis votre machine locale
ssh -L 8000:localhost:8000 user@<IP_VM>

# Accédez ensuite à http://localhost:8000 dans votre navigateur local
```

### Désactiver l'accès direct au port 8000

Si vous voulez complètement bloquer l'accès externe :

```bash
# Éditer le service admin
sudo nano /etc/systemd/system/celestex-admin.service

# Remplacer dans la ligne ExecStart :
--host 0.0.0.0

# Par :
--host 127.0.0.1

# Recharger et redémarrer
sudo systemctl daemon-reload
sudo systemctl restart celestex-admin
```

---

## 🔒 Sécurisation du reverse proxy

### Configuration Nginx Proxy Manager

#### 1. Activer HTTPS (SSL/TLS)

- ✅ **Obligatoire en production**
- Utilisez Let's Encrypt pour des certificats gratuits
- Renouvellement automatique

Dans Nginx Proxy Manager :
1. Proxy Hosts → Éditer l'hôte CELESTE
2. SSL → Activer "Force SSL"
3. Sélectionner "Request a new SSL Certificate"
4. Activer "Force SSL" et "HTTP/2 Support"

#### 2. Headers de sécurité

Ajoutez dans la configuration Nginx (Custom Locations) :

```nginx
# Dans l'onglet "Custom Locations" ou "Advanced"
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

#### 3. Limiter les taux de requêtes (Rate Limiting)

```nginx
# Dans la configuration personnalisée
limit_req_zone $binary_remote_addr zone=celestex:10m rate=10r/s;
limit_req zone=celestex burst=20 nodelay;
```

#### 4. Bloquer l'accès direct par IP

```bash
# Sur le serveur où tourne CELESTE
sudo ufw deny 6000/tcp
sudo ufw allow from <IP_NGINX_PROXY> to any port 6000
```

---

## 📊 Surveillance et journalisation

### Activer les logs détaillés

```bash
# Logs en temps réel
sudo journalctl -u celestex -u celestex-admin -f

# Filtrer par niveau de gravité
sudo journalctl -u celestex-admin -p warning

# Logs de sécurité uniquement
sudo journalctl -u celestex-admin | grep -i "sécurité\|security\|auth"
```

### Rotation des logs

Les logs systemd sont automatiquement gérés par `journald`, mais vous pouvez configurer :

```bash
# Éditer la configuration journald
sudo nano /etc/systemd/journald.conf

# Recommandations :
SystemMaxUse=500M
MaxRetentionSec=1month
```

### Surveillance des tentatives d'authentification

```bash
# Script de surveillance (à créer)
sudo nano /opt/celestex/monitor_auth.sh
```

```bash
#!/bin/bash
# Surveille les tentatives d'authentification échouées

journalctl -u celestex-admin --since "1 hour ago" | \
  grep -i "unauthorized\|401\|403" | \
  wc -l
```

```bash
chmod +x /opt/celestex/monitor_auth.sh

# Ajouter à cron pour surveillance régulière
crontab -e
# */30 * * * * /opt/celestex/monitor_auth.sh > /var/log/celestex_auth.log
```

### Alertes par email (optionnel)

Installez `mailutils` pour recevoir des alertes :

```bash
sudo apt install mailutils

# Créer un script d'alerte
sudo nano /opt/celestex/alert_security.sh
```

```bash
#!/bin/bash
AUTH_FAILURES=$(journalctl -u celestex-admin --since "1 hour ago" | grep -c "401")

if [ $AUTH_FAILURES -gt 10 ]; then
  echo "ALERTE: $AUTH_FAILURES tentatives d'authentification échouées détectées" | \
    mail -s "Alerte Sécurité CELESTE X" admin@example.com
fi
```

---

## 🔄 Mises à jour de sécurité

### Politique de mise à jour

- ✅ **Critique** : Appliquer dans les 24h
- ⚠️ **Importante** : Appliquer dans la semaine
- ℹ️ **Mineure** : Appliquer lors de la maintenance mensuelle

### Mise à jour du système

```bash
# Mettre à jour le système Debian
sudo apt update && sudo apt upgrade -y

# Vérifier les paquets de sécurité
sudo apt list --upgradable | grep -i security
```

### Mise à jour de CELESTE X

```bash
cd /opt/celestex

# Vérifier les changements avant de mettre à jour
sudo -u celeste git fetch
sudo -u celeste git log HEAD..origin/main --oneline

# Mettre à jour
sudo -u celeste git pull

# Vérifier le CHANGELOG
cat CHANGELOG.md

# Appliquer les mises à jour
sudo -u celeste bash -c 'source .venv/bin/activate && pip install -r backend/requirements.txt'
sudo -u celeste bash -c 'cd frontend && npm ci && npm run build'

# Redémarrer
sudo systemctl restart celestex celestex-admin

# Vérifier les logs
sudo journalctl -u celestex -n 50
```

### Vérifier les vulnérabilités des dépendances

```bash
# Python
source .venv/bin/activate
pip list --outdated
pip-audit  # Si installé

# npm
cd frontend
npm audit
npm audit fix  # Corriger automatiquement si possible
```

---

## 💾 Sauvegarde et restauration

### Sauvegarde de la base de données

```bash
# Script de sauvegarde quotidienne
sudo nano /opt/celestex/backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/opt/celestex/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Sauvegarder la base de données
cp /opt/celestex/data/celestex.db "$BACKUP_DIR/celestex_$DATE.db"

# Sauvegarder la configuration
cp /opt/celestex/.env "$BACKUP_DIR/env_$DATE.backup"

# Garder seulement les 30 derniers jours
find $BACKUP_DIR -name "celestex_*.db" -mtime +30 -delete
find $BACKUP_DIR -name "env_*.backup" -mtime +30 -delete

echo "Sauvegarde terminée: $DATE"
```

```bash
chmod +x /opt/celestex/backup.sh

# Programmer une sauvegarde quotidienne à 3h du matin
sudo crontab -e -u celeste
# 0 3 * * * /opt/celestex/backup.sh >> /var/log/celestex_backup.log 2>&1
```

### Restauration

```bash
# Arrêter les services
sudo systemctl stop celestex celestex-admin

# Restaurer la base de données
sudo -u celeste cp /opt/celestex/backups/celestex_20251021_030000.db /opt/celestex/data/celestex.db

# Restaurer la configuration (si nécessaire)
sudo -u celeste cp /opt/celestex/backups/env_20251021_030000.backup /opt/celestex/.env

# Redémarrer
sudo systemctl start celestex celestex-admin

# Vérifier
./check.sh
```

### Sauvegarde externe (recommandé)

```bash
# Synchroniser vers un serveur distant
rsync -avz --delete \
  /opt/celestex/backups/ \
  user@backup-server:/backups/celestex/

# Ou vers un service cloud
rclone sync /opt/celestex/backups/ remote:celestex-backups
```

---

## 🔍 Audit de sécurité

### Liste de contrôle de sécurité

| Élément | État | Action si ❌ |
|---------|------|-------------|
| Mot de passe admin changé | ☐ | Changer immédiatement |
| Hash bcrypt utilisé | ☐ | Générer un hash |
| Secret de session unique | ☐ | Générer avec openssl |
| Port 8000 restreint | ☐ | Configurer le firewall |
| HTTPS activé | ☐ | Configurer Nginx |
| Logs surveillés | ☐ | Mettre en place monitoring |
| Sauvegardes automatiques | ☐ | Créer script de sauvegarde |
| Système à jour | ☐ | apt update && upgrade |
| Permissions .env correctes | ☐ | chmod 600 .env |
| Tests de sécurité passés | ☐ | Exécuter audit |

### Script d'audit automatique

```bash
sudo nano /opt/celestex/security_audit.sh
```

```bash
#!/bin/bash

echo "=== Audit de sécurité CELESTE X ==="
echo ""

# 1. Vérifier le mot de passe admin
if grep -q "ADMIN_PASS=admin123" /opt/celestex/.env 2>/dev/null; then
  echo "❌ CRITIQUE: Mot de passe admin par défaut détecté !"
else
  echo "✅ Mot de passe admin modifié"
fi

# 2. Vérifier le hash bcrypt
if grep -qE "ADMIN_PASS=\$2[aby]\$" /opt/celestex/.env 2>/dev/null; then
  echo "✅ Hash bcrypt utilisé"
else
  echo "⚠️ WARNING: Pas de hash bcrypt détecté"
fi

# 3. Vérifier les permissions .env
PERMS=$(stat -c "%a" /opt/celestex/.env 2>/dev/null)
if [ "$PERMS" = "600" ]; then
  echo "✅ Permissions .env correctes (600)"
else
  echo "⚠️ WARNING: Permissions .env à corriger (actuellement: $PERMS)"
fi

# 4. Vérifier HTTPS
if curl -s -I http://localhost:6000 | grep -q "location: https"; then
  echo "✅ Redirection HTTPS active"
else
  echo "⚠️ INFO: Pas de redirection HTTPS (normal si reverse proxy)"
fi

# 5. Vérifier les services
if systemctl is-active --quiet celestex; then
  echo "✅ Service celestex actif"
else
  echo "❌ ERREUR: Service celestex inactif"
fi

if systemctl is-active --quiet celestex-admin; then
  echo "✅ Service celestex-admin actif"
else
  echo "❌ ERREUR: Service celestex-admin inactif"
fi

echo ""
echo "=== Fin de l'audit ==="
```

```bash
chmod +x /opt/celestex/security_audit.sh
./security_audit.sh
```

---

## 📞 En cas d'incident de sécurité

### Procédure d'urgence

#### 1. Isoler le système

```bash
# Arrêter immédiatement les services
sudo systemctl stop celestex celestex-admin

# Bloquer tout accès externe
sudo ufw deny 6000/tcp
sudo ufw deny 8000/tcp
```

#### 2. Analyser les logs

```bash
# Identifier l'incident
sudo journalctl -u celestex -u celestex-admin --since "24 hours ago" > /tmp/incident_logs.txt

# Chercher des patterns suspects
grep -i "401\|403\|error\|failed" /tmp/incident_logs.txt
```

#### 3. Changer tous les secrets

```bash
# Nouveau mot de passe admin
python -m backend.security "NouveauMotDePasseUrgence$(date +%s)"

# Nouveau secret de session
openssl rand -hex 32

# Mettre à jour .env
sudo -u celeste nano /opt/celestex/.env
```

#### 4. Restaurer depuis une sauvegarde saine

```bash
# Si compromission suspectée
sudo -u celeste cp /opt/celestex/backups/celestex_DATE_SAINE.db /opt/celestex/data/celestex.db
```

#### 5. Redémarrer et surveiller

```bash
# Réactiver les services
sudo ufw allow 6000/tcp
sudo systemctl start celestex celestex-admin

# Surveiller en continu
sudo journalctl -u celestex -u celestex-admin -f
```

---

## 📚 Ressources supplémentaires

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Sécurité FastAPI](https://fastapi.tiangolo.com/tutorial/security/)
- [Bonnes pratiques Python](https://python.readthedocs.io/en/stable/library/security.html)
- [Guide Debian Sécurité](https://www.debian.org/doc/manuals/securing-debian-manual/)

---

**Dernière révision** : 21 Octobre 2025
**Auteur** : Équipe CELESTE X
