"""
Module d'authentification pour CELESTE X
Gestion de l'authentification par liste blanche d'emails et JWT
"""
import os
import logging
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr

logger = logging.getLogger(__name__)

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "votre-secret-jwt-a-changer-en-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 heures

# Liste blanche d'emails autorisés (à configurer via .env ou base de données)
ALLOWED_EMAILS = os.getenv(
    "ALLOWED_EMAILS",
    "admin@rte-france.com,user@rte-france.com,test@rte-france.com"
).split(",")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class LoginRequest(BaseModel):
    """Requête de connexion"""
    email: EmailStr
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

    Pour le moment : authentification simple par liste blanche
    En production : vérifier contre la base de données avec hash bcrypt

    Args:
        email: Email de l'utilisateur
        password: Mot de passe (pour l'instant non vérifié, TODO)

    Returns:
        True si authentifié, False sinon
    """
    # Vérifier si l'email est autorisé
    if not is_email_allowed(email):
        logger.warning(f"Tentative de connexion avec email non autorisé: {email}")
        return False

    # TODO: Vérifier le mot de passe contre la base de données
    # Pour l'instant, on accepte n'importe quel mot de passe pour les emails autorisés
    # En production, faire :
    # user = get_user_from_db(email)
    # return verify_password(password, user.hashed_password)

    logger.info(f"Connexion réussie pour: {email}")
    return True


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
