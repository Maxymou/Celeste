# CELESTE X

Application de calcul mécanique pour lignes aériennes. Cette première ébauche fournit l'API FastAPI, l'interface React (build Vite) et le tableau de bord SQLAdmin.

## Contexte
- **Plateforme** : Debian VM sous Proxmox (reverse proxy HTTPS et firewall gérés en amont).
- **Ports** : 6000 pour l'application principale (API + SPA) et 8000 pour l'admin (accès local uniquement).
- **Contraintes** : pas de Docker, ni de firewall local ou Nginx sur cette VM. Tout service doit se binder sur `0.0.0.0` et utiliser `--proxy-headers` avec uvicorn.

## Structure
```
backend/         # FastAPI (API /api/* + service du bundle Vite)
backend_admin/   # FastAPI + SQLAdmin (tableau de bord DB)
frontend/        # SPA Vite React + TypeScript
scripts/         # Scripts utilitaires (import XML)
systemd/         # Unit files systemd
```

## Installation
1. **Cloner le dépôt**
   ```bash
   git clone https://github.com/Maxymou/CELESTE.git
   cd CELESTE
   ```

2. **Installer le frontend**
   ```bash
   cd frontend
   npm ci
   npm run build
   cd ..
   ```

3. **Installer l'API et l'admin**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   pip install -r backend/requirements.txt
   pip install sqladmin
   ```

4. **Configurer l'environnement**
   ```bash
   cp .env.example .env
   # Éditer .env puis sourcer si besoin
   ```

## Lancement local
### Application principale (port 6000)
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 6000 --proxy-headers
```
`/api/health` répond `{"status":"ok"}` et les requêtes non-API reviennent sur le bundle `frontend/dist` (SPA fallback).

### Tableau de bord admin (port 8000)
```bash
export CELESTEX_DB_PATH=${CELESTEX_DB_PATH:-$(pwd)/data/celestex.db}
export ADMIN_USER=${ADMIN_USER:-admin}
export ADMIN_PASS=${ADMIN_PASS:-change-me}
export ADMIN_SECRET=${ADMIN_SECRET:-change-this-too}
uvicorn backend_admin.main:app --host 0.0.0.0 --port 8000 --proxy-headers
```
Accès : `http://127.0.0.1:8000/admin/` avec authentification Basic. L'endpoint `GET /admin/health` renvoie l'état de la DB.

## Déploiement systemd
1. Copier les unités :
   ```bash
   sudo cp systemd/celestex.service /etc/systemd/system/
   sudo cp systemd/celestex-admin.service /etc/systemd/system/
   ```
2. Préparer un fichier `/opt/celestex/.env` basé sur `.env.example`.
3. (Re)charger et activer :
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable --now celestex.service
   sudo systemctl enable --now celestex-admin.service
   ```
4. Vérifier :
   ```bash
   sudo systemctl status celestex.service
   sudo systemctl status celestex-admin.service
   ```

## Importer les XML
Le script `scripts/import_cables.py` est un stub pour charger `Câble.xml` et `Couche câble.xml` dans SQLite (`data/celestex.db`). Exemple :
```bash
python scripts/import_cables.py --xml-cable "Câble.xml" --xml-layer "Couche câble.xml" --db data/celestex.db
```
Gardez les guillemets lorsque vous référencez des chemins contenant des espaces ou des accents.

## Troubleshooting
- 404 sur `/` : vérifier que `npm run build` a bien produit `frontend/dist/` avant de lancer uvicorn.
- Impossible d'accéder à l'admin : confirmer les variables `ADMIN_*` et `ADMIN_SECRET`, sinon l'authentification Basic échoue.
- Conflit de port 6000/8000 : ajuster les flags `--port` (et mettre à jour le reverse proxy si nécessaire).
- Assets SPA cassés derrière le proxy : `vite.config.ts` force `base: '/'`, garder cette valeur pour éviter les chemins relatifs incorrects.
