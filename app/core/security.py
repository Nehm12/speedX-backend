"""
Module de sécurité pour le hachage des mots de passe
"""

from passlib.context import CryptContext

# Configuration du contexte de hachage
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """
    Hash un mot de passe en utilisant bcrypt
    
    Args:
        password: Le mot de passe en clair
        
    Returns:
        Le mot de passe haché
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Vérifie qu'un mot de passe correspond à son hash
    
    Args:
        plain_password: Le mot de passe en clair
        hashed_password: Le mot de passe haché
        
    Returns:
        True si le mot de passe correspond, False sinon
    """
    return pwd_context.verify(plain_password, hashed_password)