"""
Module de sécurité pour l'application CELESTE X
Gestion du hashage et vérification des mots de passe

Usage CLI:
    python -m backend.security [mot_de_passe]
"""
import sys
import bcrypt


def hash_password(password: str) -> str:
    """
    Hash un mot de passe avec bcrypt

    Args:
        password: Le mot de passe en clair

    Returns:
        Le hash bcrypt du mot de passe
    """
    # Convertir le mot de passe en bytes et le hasher
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    # Retourner le hash en string
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Vérifie qu'un mot de passe correspond à son hash

    Args:
        plain_password: Le mot de passe en clair à vérifier
        hashed_password: Le hash bcrypt de référence

    Returns:
        True si le mot de passe est valide, False sinon
    """
    # Convertir les strings en bytes
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    # Vérifier le mot de passe
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def generate_password_hash(password: str) -> str:
    """
    Génère un hash pour un mot de passe (alias de hash_password)
    Utilisé pour la génération initiale de hash

    Usage:
        from backend.security import generate_password_hash
        print(generate_password_hash("votre_mot_de_passe"))
    """
    return hash_password(password)


def get_password_hash(password: str) -> str:
    """
    Alias de hash_password pour compatibilité
    Utilisé par l'interface d'administration

    Args:
        password: Le mot de passe en clair

    Returns:
        Le hash bcrypt du mot de passe
    """
    return hash_password(password)


def main():
    """Point d'entrée CLI pour générer des hash de mots de passe"""
    if len(sys.argv) < 2:
        print("Usage: python -m backend.security <mot_de_passe>")
        print("\nExemple:")
        print("  python -m backend.security mon_super_password")
        print("\nPuis copiez le hash généré dans votre fichier .env:")
        print("  ADMIN_PASS=$2b$12$...")
        sys.exit(1)

    password = sys.argv[1]

    if len(password) < 8:
        print("⚠️  ATTENTION: Le mot de passe est trop court (minimum 8 caractères recommandé)")

    hashed = hash_password(password)

    print("\n" + "="*60)
    print("Hash bcrypt généré avec succès!")
    print("="*60)
    print(f"\nMot de passe: {password}")
    print(f"\nHash bcrypt:")
    print(hashed)
    print("\n" + "="*60)
    print("Ajoutez cette ligne dans votre fichier .env:")
    print("="*60)
    print(f"ADMIN_PASS={hashed}")
    print("\n")


if __name__ == "__main__":
    main()
