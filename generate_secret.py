import secrets

# Générer une clé secrète aléatoire de 32 caractères
SECRET_KEY = secrets.token_hex(32)
print(SECRET_KEY)
