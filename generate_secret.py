#!/usr/bin/env python3
"""
Script pour générer une nouvelle clé secrète sécurisée pour SpeedX en production.
"""
import secrets

def generate_secret_key():
    """Génère une clé secrète sécurisée de 32 bytes (256 bits)."""
    return secrets.token_urlsafe(32)

if __name__ == "__main__":
    secret_key = generate_secret_key()
    print("🔐 Nouvelle clé secrète générée :")
    print(f"SECRET_KEY={secret_key}")
    print("\n⚠️  IMPORTANT :")
    print("- Utilisez cette clé dans vos variables d'environnement de production")
    print("- Ne partagez jamais cette clé")
    print("- Stockez-la de manière sécurisée")
