# Système d'Authentification CELESTE X

## Vue d'ensemble

CELESTE X dispose maintenant d'un système d'authentification complet basé sur JWT (JSON Web Tokens) avec une liste blanche d'emails autorisés.

## Architecture

### Backend

#### Module d'authentification (`backend/auth.py`)

Le module d'authentification fournit:

- **Génération de tokens JWT** : Tokens signés avec une clé secrète configurable
- **Liste blanche d'emails** : Seuls les emails autorisés peuvent se connecter
- **Validation des emails** : Vérification du format email
- **Durée de session** : Tokens valides pendant 8 heures

#### Endpoint API

```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "mot_de_passe"
}
```

**Réponse en cas de succès (200 OK):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "email": "user@example.com",
  "expires_at": "2025-10-22T01:27:43.701077"
}
```

**Réponse en cas d'échec (401 Unauthorized):**
```json
{
  "detail": "Email ou mot de passe incorrect, ou accès non autorisé"
}
```

### Frontend

#### Composants

1. **Login.tsx** - Page de connexion
   - Design dark mode cohérent avec CELESTE X
   - Formulaire email/password
   - Gestion des erreurs
   - États de chargement
   - Stockage automatique du token

2. **AuthContext.tsx** - Contexte d'authentification
   - Gestion de l'état global d'authentification
   - Fonctions `login()` et `logout()`
   - Persistance du token dans localStorage
   - Vérification du token au chargement de l'app

3. **App.tsx** - Application principale
   - Affichage conditionnel : Login ou Dashboard
   - Menu de déconnexion dans le profil
   - Protection automatique des routes

## Configuration

### Variables d'environnement

Créer un fichier `.env` à la racine du projet (voir `.env.example`):

```bash
# JWT Configuration
JWT_SECRET_KEY=votre-secret-jwt-super-securise-aleatoire-123456789

# Liste des emails autorisés (séparés par des virgules)
ALLOWED_EMAILS=admin@admin.fr,user@example.com,engineer@example.com
```

### Générer une clé secrète JWT

```bash
# Avec Python
python3 -c "import secrets; print(secrets.token_urlsafe(64))"

# Avec OpenSSL
openssl rand -base64 64
```

## Installation

### Dépendances backend

```bash
source .venv/bin/activate
pip install python-jose[cryptography]==3.3.0 email-validator==2.1.0
```

Ou avec le fichier requirements.txt :

```bash
pip install -r backend/requirements.txt
```

### Dépendances frontend

Aucune dépendance supplémentaire requise (utilise React natif).

## Utilisation

### Pour les développeurs

1. **Configurer les emails autorisés**

   Éditer `.env` et ajouter les emails autorisés:
   ```bash
   ALLOWED_EMAILS=user1@example.com,user2@example.com
   ```

2. **Démarrer le serveur**

   ```bash
   source .venv/bin/activate
   uvicorn backend.main:app --host 0.0.0.0 --port 6000 --reload
   ```

3. **Builder le frontend**

   ```bash
   cd frontend
   npm run build
   ```

4. **Accéder à l'application**

   Ouvrir http://localhost:6000 dans un navigateur

### Pour les utilisateurs finaux

1. Ouvrir l'application CELESTE X
2. Entrer votre email (doit être dans la liste blanche)
3. Entrer votre mot de passe
4. Cliquer sur "Se connecter"
5. Une fois connecté, accéder au profil (icône en haut à droite) pour se déconnecter

## Sécurité

### Mesures implémentées

✅ **Authentification par liste blanche**
- Seuls les emails configurés peuvent se connecter
- Impossible d'énumérer les emails valides (message d'erreur générique)

✅ **Tokens JWT signés**
- Chaque token est signé avec une clé secrète
- Impossible de falsifier un token sans la clé
- Expiration automatique après 8 heures

✅ **Validation côté serveur**
- Format email vérifié avec `email-validator`
- Vérification de la liste blanche à chaque connexion
- Logging des tentatives de connexion

✅ **HTTPS recommandé en production**
- Les tokens doivent transiter sur HTTPS uniquement
- Nginx Proxy Manager gère le SSL sur https://celeste.redyx.fr/

### Points d'attention

⚠️ **Clé secrète JWT**
- DOIT être changée en production (ne jamais utiliser la valeur par défaut)
- DOIT être gardée secrète (ne jamais committer dans Git)
- Utiliser une chaîne aléatoire longue (minimum 32 caractères)

⚠️ **Liste blanche d'emails**
- Vérifier que seuls les emails autorisés sont dans la liste
- Ne pas exposer la liste publiquement
- Mettre à jour régulièrement

⚠️ **Stockage des tokens**
- Actuellement dans localStorage (accessible en JavaScript)
- Considérer httpOnly cookies pour plus de sécurité (nécessite modifications backend)

## Personnalisation

### Modifier la durée de session

Dans `backend/main.py`, ligne 431:

```python
access_token, expires_at = create_access_token(
    data={"sub": credentials.email},
    expires_delta=timedelta(minutes=480)  # ← Changer ici (480 min = 8h)
)
```

### Ajouter une validation de mot de passe

Actuellement, le système n'utilise pas de base de données de mots de passe. Pour ajouter cette fonctionnalité:

1. Créer une table `users` avec emails et mots de passe hashés (bcrypt)
2. Modifier `backend/auth.py` pour vérifier le mot de passe
3. Utiliser le module `backend/security.py` existant pour hasher les mots de passe

### Personnaliser le design de la page de connexion

Éditer `frontend/src/styles/Login.css`:

```css
.login-container {
  /* Modifier le fond */
  background: radial-gradient(...);
}

.login-button {
  /* Modifier le bouton */
  background: linear-gradient(...);
}
```

## Tests

### Tester l'endpoint avec curl

**Connexion réussie:**
```bash
curl -X POST http://localhost:6000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@admin.fr", "password": "admin"}'
```

**Email non autorisé:**
```bash
curl -X POST http://localhost:6000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "hacker@example.com", "password": "test123"}'
# Retourne 401 Unauthorized
```

### Vérifier les logs

Les tentatives de connexion sont loggées:

```
2025-10-21 19:27:43 - backend.main - INFO - Tentative de connexion pour: admin@admin.fr
2025-10-21 19:27:43 - backend.main - INFO - Connexion réussie pour: admin@admin.fr

2025-10-21 19:28:15 - backend.main - WARNING - Échec d'authentification pour: hacker@example.com
```

## Déploiement en production

### Checklist de sécurité

- [ ] Générer une nouvelle clé JWT sécurisée
- [ ] Configurer la liste blanche d'emails
- [ ] Activer HTTPS (déjà fait avec Nginx Proxy Manager)
- [ ] Vérifier que `.env` n'est pas commité dans Git
- [ ] Configurer des mots de passe forts si intégration BDD
- [ ] Activer le rate limiting sur l'endpoint de login
- [ ] Configurer la rotation des logs
- [ ] Tester la déconnexion et l'expiration des tokens

### Mise à jour sur le serveur

```bash
# Se connecter au serveur
ssh user@celeste.redyx.fr

# Récupérer les dernières modifications
cd /path/to/Celeste
git pull

# Mettre à jour les dépendances
source .venv/bin/activate
pip install -r backend/requirements.txt

# Configurer .env (si pas déjà fait)
cp .env.example .env
nano .env  # Éditer avec les vraies valeurs

# Builder le frontend
cd frontend
npm install
npm run build

# Redémarrer le service
sudo systemctl restart celeste
```

## Dépannage

### Le token expire trop vite

Augmenter la durée dans `backend/main.py`:
```python
expires_delta=timedelta(minutes=480)  # 8h → changer
```

### Email non autorisé mais devrait l'être

1. Vérifier `.env`:
   ```bash
   cat .env | grep ALLOWED_EMAILS
   ```
2. Vérifier qu'il n'y a pas d'espaces autour des emails
3. Vérifier la casse (respecte majuscules/minuscules)
4. Redémarrer le serveur après modification

### Page de login ne s'affiche pas

1. Vérifier que le frontend est bien buildé:
   ```bash
   ls -la frontend/dist/
   ```
2. Vérifier les logs du serveur
3. Vider le cache du navigateur
4. Vérifier la console développeur du navigateur (F12)

### Token non reconnu après connexion

1. Vérifier que la clé JWT est la même sur toutes les instances
2. Vérifier que le token n'a pas expiré
3. Supprimer le localStorage et se reconnecter:
   ```javascript
   localStorage.clear()
   ```

## Roadmap

### Améliorations futures possibles

- [ ] Authentification avec base de données (emails + mots de passe hashés)
- [ ] Refresh tokens pour prolonger les sessions
- [ ] Authentification à deux facteurs (2FA)
- [ ] OAuth2 / LDAP pour authentification externe
- [ ] Gestion des rôles et permissions (admin, user, readonly)
- [ ] Historique des connexions
- [ ] Rate limiting pour prévenir les attaques par force brute
- [ ] Blacklist de tokens révoqués
- [ ] Remember me avec tokens de longue durée

## Support

Pour toute question ou problème concernant l'authentification:

1. Consulter les logs du serveur
2. Vérifier la configuration `.env`
3. Tester l'endpoint avec curl
4. Créer une issue sur GitHub

---

**Version:** 1.2.0
**Dernière mise à jour:** 21 Octobre 2025
**Auteur:** Claude Code pour CELESTE X
