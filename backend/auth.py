"""
Module d'authentification pour CELESTE X
Gestion de l'authentification par liste blanche d'emails et JWT
"""
import os
import logging
from datetime import datetime, timedelta
from typing import Optional
from pathlib import Path
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

# Import du modèle User
try:
    from backend.models.db_models import User
    USER_MODEL_AVAILABLE = True
except ImportError:
    logger.warning("Modèle User non disponible, utilisation de l'authentification fallback uniquement")
    USER_MODEL_AVAILABLE = False

# Configuration de la base de données
DB_PATH = os.getenv("CELESTEX_DB_PATH", "./data/celestex.db")
Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "votre-secret-jwt-a-changer-en-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 heures

# Identifiants admin
ADMIN_USERNAME = os.getenv("ADMIN_USER", "admin@admin.fr")
ADMIN_PASSWORD = os.getenv("ADMIN_PASS", "admin")

# Liste blanche d'emails autorisés (à configurer via .env ou base de données)
ALLOWED_EMAILS = os.getenv(
    "ALLOWED_EMAILS",
    "user@example.com,test@example.com"
).split(",")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class LoginRequest(BaseModel):
    """Requête de connexion"""
    email: str  # Accepte aussi un username (pas uniquement EmailStr)
    password: str


class TokenResponse(BaseModel):
    """Réponse avec token JWT"""
    token: str
    token_type: str = "bearer"
    email: str
    expires_at: str


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie un mot de passe contre son hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> bool:
    """Génère le hash d'un mot de passe"""
    return pwd_context.hash(password)


def is_email_allowed(email: str) -> bool:
    """
    Vérifie si l'email est dans la liste blanche

    En production, cette fonction devrait interroger la base de données
    pour vérifier si l'utilisateur existe et est actif.
    """
    # Normaliser l'email (minuscules, trim)
    email = email.lower().strip()

    # Vérifier la liste blanche
    allowed = [e.lower().strip() for e in ALLOWED_EMAILS]

    return email in allowed


def authenticate_user(email: str, password: str) -> bool:
    """
    Authentifie un utilisateur

    Supporte trois modes d'authentification (dans l'ordre de priorité) :
    1. Base de données (utilisateurs créés via l'interface admin)
    2. Compte admin hardcodé (fallback)
    3. Liste blanche d'emails (legacy, accepte n'importe quel mot de passe)

    Args:
        email: Email ou username de l'utilisateur
        password: Mot de passe

    Returns:
        True si authentifié, False sinon
    """
    # Normaliser l'identifiant
    identifier = email.strip().lower()

    # 1. Vérifier dans la base de données en premier
    if USER_MODEL_AVAILABLE:
        try:
            db = SessionLocal()
            try:
                user = db.query(User).filter(User.email == identifier).first()
                if user:
                    # Vérifier que l'utilisateur est actif
                    if not user.is_active:
                        logger.warning(f"Tentative de connexion avec compte désactivé: {identifier}")
                        return False

                    # Vérifier le mot de passe
                    if verify_password(password, user.hashed_password):
                        logger.info(f"Connexion BDD réussie pour: {identifier}")
                        return True
                    else:
                        logger.warning(f"Mot de passe incorrect pour utilisateur BDD: {identifier}")
                        return False
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Erreur lors de la vérification BDD: {e}")
            # Continuer avec les autres méthodes en cas d'erreur BDD

    # 2. Fallback sur le compte admin hardcodé
    if identifier == ADMIN_USERNAME.lower():
        if password == ADMIN_PASSWORD:
            logger.info(f"Connexion admin hardcodé réussie pour: {identifier}")
            return True
        else:
            logger.warning(f"Tentative de connexion admin avec mot de passe incorrect")
            return False

    # 3. Fallback sur la liste blanche (legacy, accepte n'importe quel mot de passe)
    if is_email_allowed(identifier):
        logger.info(f"Connexion liste blanche (legacy) réussie pour: {identifier}")
        logger.warning(f"SÉCURITÉ: Connexion legacy sans vérification mot de passe pour {identifier}")
        return True

    # Aucune méthode n'a fonctionné
    logger.warning(f"Tentative de connexion avec email non autorisé: {identifier}")
    return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crée un token JWT

    Args:
        data: Données à encoder dans le token
        expires_delta: Durée de validité du token

    Returns:
        Token JWT signé
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt, expire


def verify_token(token: str) -> Optional[str]:
    """
    Vérifie et décode un token JWT

    Args:
        token: Token JWT à vérifier

    Returns:
        Email de l'utilisateur si valide, None sinon
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")

        if email is None:
            return None

        return email

    except JWTError as e:
        logger.warning(f"Token JWT invalide: {e}")
        return None
