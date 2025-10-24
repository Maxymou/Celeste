#!/usr/bin/env python3
"""
Script de migration pour ajouter la table users à la base de données

Usage:
    python scripts/migrate_add_users.py
"""
import sys
import os
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.models.db_models import Base, User
from backend.security import get_password_hash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Configuration
DB_PATH = os.getenv("CELESTEX_DB_PATH", "./data/celestex.db")
ADMIN_EMAIL = os.getenv("ADMIN_USER", "admin@admin.fr")
ADMIN_PASSWORD = os.getenv("ADMIN_PASS", "admin")


def main():
    """Exécute la migration"""
    print("=" * 60)
    print("Migration: Ajout de la table users")
    print("=" * 60)
    print()

    # Créer le dossier data s'il n'existe pas
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)

    # Créer la connexion
    print(f"📁 Base de données: {DB_PATH}")
    engine = create_engine(
        f"sqlite:///{DB_PATH}",
        connect_args={"check_same_thread": False}
    )

    # Créer toutes les tables (y compris la nouvelle table user)
    print("🔧 Création de la table 'user'...")
    Base.metadata.create_all(engine, checkfirst=True)
    print("✓ Table créée avec succès")
    print()

    # Créer une session
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        # Vérifier si l'utilisateur admin existe déjà
        existing_admin = db.query(User).filter(User.email == ADMIN_EMAIL.lower()).first()

        if existing_admin:
            print(f"ℹ️  L'utilisateur admin '{ADMIN_EMAIL}' existe déjà")
            print(f"   ID: {existing_admin.id}")
            print(f"   Nom: {existing_admin.name}")
            print(f"   Actif: {existing_admin.is_active}")
        else:
            # Créer l'utilisateur admin
            print(f"👤 Création de l'utilisateur admin: {ADMIN_EMAIL}")
            admin_user = User(
                name="Administrateur",
                email=ADMIN_EMAIL.lower(),
                hashed_password=get_password_hash(ADMIN_PASSWORD),
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(admin_user)
            db.commit()
            print("✓ Utilisateur admin créé avec succès")
            print()
            print(f"   Email: {ADMIN_EMAIL}")
            print(f"   Mot de passe: {ADMIN_PASSWORD}")
            print(f"   ID: {admin_user.id}")

        print()
        print("=" * 60)
        print("✅ Migration terminée avec succès!")
        print("=" * 60)
        print()
        print("Vous pouvez maintenant:")
        print(f"  1. Vous connecter avec {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
        print("  2. Gérer les utilisateurs via l'interface admin (port 8000)")
        print()

    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
