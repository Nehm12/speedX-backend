# FLUXY - Extracteur Automatique de Relevés Bancaires

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116%2B-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Fluxy** est une solution d'extraction automatique de données à partir de relevés bancaires PDF, conçue spécialement pour les besoins des cabinets d'expertise comptable. Le système utilise l'intelligence artificielle (Google Gemini) pour analyser et extraire automatiquement les informations bancaires, puis génère des fichiers Excel formatés prêts à l'emploi.

## 🎯 Fonctionnalités Principales

- **Extraction automatique** : Analyse intelligente des relevés bancaires PDF
- **Traitement par lot** : Support du traitement simultané de plusieurs documents
- **Export Excel** : Génération automatique de fichiers Excel structurés
- **Interface web** : Interface utilisateur intuitive pour une utilisation simplifiée
- **API REST** : Endpoints robustes pour l'intégration dans d'autres systèmes
- **Logging avancé** : Système de journalisation détaillé pour le suivi et le débogage

## 🏗️ Architecture Technique

### Structure du Projet

```
fluxy/
├── app/
│   ├── main.py              # Point d'entrée FastAPI avec lifespan
│   ├── database.py          # Configuration base de données SQLAlchemy
│   ├── models/              # Modèles SQLAlchemy
│   │   ├── base.py          # Classe de base pour tous les modèles
│   │   ├── users.py         # Modèle utilisateur avec rôles
│   │   ├── extraction_job.py # Modèle pour le suivi des jobs d'extraction
│   │   └── users_consumption.py # Modèle de consommation utilisateur
│   ├── routes/              # Routes et endpoints API
│   │   ├── extractor.py     # Endpoints d'extraction de données
│   │   ├── auth.py          # Routes d'authentification FastAPI Users
│   │   └── api.py           # Routes API générales
│   ├── schemas/             # Schémas Pydantic pour validation
│   │   ├── extractor.py     # Schémas pour les données bancaires
│   │   └── users.py         # Schémas pour les utilisateurs
│   ├── services/            # Services métier
│   │   ├── llm/             # Service d'extraction IA avec Google Gemini
│   │   ├── excel/           # Service de génération Excel
│   │   ├── auth/            # Service d'authentification personnalisé
│   │   └── email/           # Service d'envoi d'emails
│   ├── scripts/             # Scripts utilitaires
│   │   └── init_db.py       # Initialisation de la base de données
│   └── utils/               # Utilitaires
│       └── logs.py          # Configuration du logging
├── pyproject.toml           # Configuration des dépendances (uv/pip)
├── requirements.txt         # Liste des dépendances (fallback pip)
├── uv.lock                  # Lock file uv
├── start.sh                 # Script de démarrage intelligent
├── .env.example             # Exemple de configuration
└── README.md
```

### Technologies Utilisées

- **Backend** : FastAPI (Python 3.12+)
- **IA/ML** : Google Gemini 2.5 Flash Lite
- **Authentification** : FastAPI Users avec JWT et sessions cookies
- **Traitement de données** : Pandas, Pydantic v2
- **Export Excel** : OpenPyXL, XlsxWriter
- **Interface web** : Jinja2 Templates (optionnel)
- **Base de données** : SQLAlchemy 2.0+ (avec support SQLite/PostgreSQL)
- **Serveur ASGI** : Uvicorn avec uvloop
- **Rate Limiting** : SlowAPI
- **Gestionnaire de paquets** : uv (recommandé) ou pip
- **Logging** : Logging Python avancé avec rotation

## 📋 Prérequis

- Python 3.12 ou version supérieure
- Gestionnaire de paquets `uv` ou `pip`
- Clé API Google Gemini (configurée dans les variables d'environnement)

## ⚡ Installation et Configuration

### 1. Clonage du Projet

```bash
git clone <repository-url>
cd fluxy
```

## ⚡ Installation et Configuration

### 1. Prérequis

- Python 3.12 ou version supérieure
- Gestionnaire de paquets `uv` (recommandé) ou `pip`
- Clé API Google Gemini (configurée dans les variables d'environnement)

### 2. Installation des Dépendances

**Avec `uv` (recommandé) :**
```bash
# Installation rapide et moderne de Python
uv sync
```

**Avec `pip` (fallback) :**
```bash
pip install -r requirements.txt
```

### 3. Configuration de l'Environnement

Créez un fichier `.env` à la racine du projet basé sur `.env.example` :

```bash
cp .env.example .env
```

Éditez `.env` avec vos valeurs :

```env
# Configuration Google Gemini (obligatoire)
GOOGLE_API_KEY=votre_clé_api_google_gemini

# Sécurité (obligatoire - changez cette valeur)
SECRET_KEY=votre_clé_secrète_unique

# URLs de l'application
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000

# Base de données (SQLite par défaut)
DATABASE_URL=sqlite+aiosqlite:///./fluxy.db
```

### 4. Démarrage de l'Application

#### Option 1 : Avec le script de démarrage (Recommandé)

Le projet inclut un script de démarrage intelligent qui vérifie automatiquement les prérequis et démarre l'application :

```bash
# Rendre le script exécutable (première fois seulement)
chmod +x start.sh

# Démarrage simple
./start.sh

# Démarrage en mode développement
./start.sh --dev

# Démarrage en mode production
./start.sh --prod

# Démarrage sur un port spécifique
./start.sh --port 3000

# Afficher l'aide complète
./start.sh --help
```

**Options disponibles :**
- `--dev` : Mode développement (rechargement automatique, logs détaillés)
- `--prod` : Mode production (multiple workers, logs optimisés)
- `--port PORT` : Spécifier le port d'écoute
- `--host HOST` : Spécifier l'adresse d'écoute
- `--workers N` : Nombre de workers (mode production uniquement)
- `--log-level LEVEL` : Niveau de logging (debug, info, warning, error)

#### Option 2 : Démarrage manuel

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

L'application sera accessible sur `http://localhost:8000`

### 5. Vérification de l'Installation

Accédez aux URLs suivantes pour vérifier que l'application fonctionne :

- **Interface principale** : http://localhost:8000
- **Documentation API** : http://localhost:8000/docs
- **Health Check** : http://localhost:8000/health

## 🚀 Utilisation

### Interface Web

1. **Page d'accueil** (`/`) : Présentation du service
2. **Démonstration** (`/demo`) : Upload et traitement d'un seul fichier
3. **Traitement par lot** (`/batch`) : Upload et traitement de plusieurs fichiers
4. **Interface comptable** (`/comptable`) : Vue spécialisée pour les comptables

### API REST

#### Endpoints Principaux

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/health` | Vérification de l'état de l'API |
| `POST` | `/api/statements/extract/` | Extraction depuis un seul PDF |
| `POST` | `/api/statements/extract/batch` | Extraction par lot (plusieurs PDFs) |

#### Exemple d'Utilisation de l'API

**Extraction d'un seul document :**

```bash
curl -X POST "http://localhost:8000/api/statements/extract/" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "document_number=DOC001" \
     -F "bank_code=BNK123" \
     -F "account_number=ACC456789" \
     -F "file=@relevé_bancaire.pdf"
```

**Traitement par lot :**

```bash
curl -X POST "http://localhost:8000/api/statements/extract/batch" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "document_number=DOC001" \
     -F "bank_code=BNK123" \
     -F "account_number=ACC456789" \
     -F "files=@relevé1.pdf" \
     -F "files=@relevé2.pdf" \
     -F "files=@relevé3.pdf"
```

## 📊 Schéma de Données

### Structure des Transactions

```python
class Transaction(BaseModel):
    date: Optional[str]                # Date de la transaction (JJ/MM/AAAA)
    document_number: Optional[str]     # Numéro de document
    bank_code: Optional[str]           # Code banque
    account_number: Optional[str]      # Numéro de compte
    description: str                   # Libellé de l'opération
    debit: float                       # Montant débit
    credit: float                      # Montant crédit

class BankStatementResponse(BaseModel):
    bank_name: str                   # Nom de la banque
    account_number: Optional[str]    # Numéro de compte
    account_holder: Optional[str]    # Titulaire du compte
    transactions: List[Transaction]  # Liste des transactions
    starting_date: Optional[str]     # Date de début du relevé
    closing_date: Optional[str]      # Date de fin du relevé
    starting_balance: Optional[float] # Solde initial
    closing_balance: Optional[float]  # Solde final
    currency: Optional[str]          # Devise (EUR, USD, etc.)
```

## 🔧 Configuration Avancée

### Variables d'Environnement

| Variable | Description | Obligatoire | Valeur par défaut |
|----------|-------------|-------------|-------------------|
| `GOOGLE_API_KEY` | Clé API Google Gemini | Oui | - |
| `SECRET_KEY` | Secret pour tokens JWT | Oui | - |
| `FRONTEND_URL` | URL du frontend | Oui | `http://localhost:3000` |
| `BACKEND_URL` | URL du backend | Oui | `http://localhost:8000` |
| `DATABASE_URL` | Chaîne connexion DB (async) | Oui | `sqlite+aiosqlite:///./fluxy.db` |
| `LOG_LEVEL` | Niveau de logs | Non | `INFO` |
| `SMTP_SERVER` | Serveur SMTP | Non (dev) / Oui (prod) | `smtp.gmail.com` |
| `SMTP_PORT` | Port SMTP | Non | `587` |
| `SMTP_USERNAME` | Identifiant SMTP | Non (dev) / Oui (prod) | - |
| `SMTP_PASSWORD` | Mot de passe SMTP | Non (dev) / Oui (prod) | - |
| `FROM_EMAIL` | Email expéditeur | Non (dev) / Oui (prod) | `SMTP_USERNAME` |
| `FROM_NAME` | Nom expéditeur | Non | `Fluxy` |
| `CORS_ORIGINS` | Origines autorisées (CSV) | Oui | `http://localhost:3000,http://127.0.0.1:3000` |
| `APP_ENV` | Environnement (`dev` / `prod`) | Non | `dev` |
| `RATE_LIMIT` | Limite de requêtes | Non | `10/minute` |

### Exemple minimal `.env`

```env
GOOGLE_API_KEY=sk-xxxxxxxx
SECRET_KEY=change_me_in_production
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
DATABASE_URL=sqlite+aiosqlite:///./fluxy.db
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Exemple complet `.env`

```env
# Configuration IA (obligatoire)
GOOGLE_API_KEY=sk-xxxxxxxx

# Sécurité (obligatoire - changez cette valeur !)
SECRET_KEY=your_unique_secret_key_here

# URLs de l'application
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000

# Base de données
DATABASE_URL=sqlite+aiosqlite:///./fluxy.db
# Pour PostgreSQL :
# DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/fluxy

# Logging
LOG_LEVEL=DEBUG

# Email/SMTP (optionnel en développement)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=votre@email.com
SMTP_PASSWORD=votre_app_password
FROM_EMAIL=fluxy@votre-domaine.com
FROM_NAME=Fluxy

# Sécurité et performance
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
APP_ENV=dev
RATE_LIMIT=10/minute
```

## 🔐 Authentification & Gestion Utilisateurs

Fluxy utilise **FastAPI Users** pour la gestion complète des utilisateurs avec authentification JWT et sessions cookies.

### Rôles Utilisateurs

- **Utilisateur Standard** : Accès aux fonctionnalités d'extraction de base
- **Administrateur** : Gestion complète des utilisateurs, accès aux statistiques

### Endpoints d'Authentification

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `POST` | `/api/auth/register` | Inscription d'un nouvel utilisateur |
| `POST` | `/api/auth/jwt/login` | Connexion JWT |
| `POST` | `/api/auth/cookie/login` | Connexion avec cookie de session |
| `POST` | `/api/auth/forgot-password` | Demande de réinitialisation mot de passe |
| `POST` | `/api/auth/reset-password` | Réinitialisation du mot de passe |
| `GET` | `/api/users/me` | Informations de l'utilisateur connecté |

### Endpoints d'Administration (Admin uniquement)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/users/` | Liste de tous les utilisateurs |
| `POST` | `/api/admin/users` | Créer un utilisateur (admin) |
| `PUT` | `/api/users/{id}` | Modifier un utilisateur |
| `DELETE` | `/api/users/{id}` | Supprimer un utilisateur |

## 📊 Système de Jobs d'Extraction

Fluxy suit automatiquement chaque demande d'extraction avec un système de jobs robuste.

### Statuts des Jobs

- **pending** : Job créé, en attente de traitement
- **processing** : Extraction en cours
- **success** : Extraction terminée avec succès
- **failed** : Échec de l'extraction

### Suivi des Jobs

Chaque job d'extraction enregistre :
- ID unique du job
- ID de l'utilisateur
- Nom du fichier PDF original
- Horodatage de soumission et de completion
- Statut actuel du traitement

## Téléchargement des Fichiers

Les endpoints de génération Excel / ZIP renvoient maintenant un header `Content-Disposition` exposé (`expose_headers`). Si le navigateur force toujours `download.xlsx`, vérifier :
1. CORS expose `Content-Disposition` (fait dans `app/main.py`)
2. Pas de proxy supprimant les headers
3. Parsing côté frontend (`getFilenameFromResponse`) gère bien `filename` et éventuellement `filename*`

## Frontend Next.js

Le dossier `frontend/` contient l'interface (pages : login, dashboard, batch, admin, comptable, reset/forgot password). Lancer en dev :

```bash
cd frontend
npm install
npm run dev
```

Configurer `NEXT_PUBLIC_API_URL` dans `frontend/.env.local` si différent :
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Notes d'Utilisation

- Assurez-vous que le backend FastAPI est en cours d'exécution avant de démarrer le frontend Next.js.
- Utilisez des mots de passe forts et uniques pour les comptes utilisateurs.
- Vérifiez les logs en cas d'erreurs pour un dépannage rapide.

## 🛠️ Développement

### Structure des Services

- **`services/llm/`** : Intégration avec Google Gemini pour l'extraction
- **`services/excel/`** : Génération et formatage des fichiers Excel
- **`routes/`** : Définition des endpoints API et web
- **`schemas/`** : Validation des données avec Pydantic

### Script de Démarrage Intelligent

Le script `start.sh` inclut plusieurs fonctionnalités avancées :

- **Détection automatique** : Python 3.12+, dépendances, structure du projet
- **Gestionnaire de paquets intelligent** : Détection automatique de `uv` (recommandé) ou `pip`
- **Installation automatique** : Détection et installation des dépendances manquantes
- **Support multi-gestionnaire** : Compatible avec `uv` et `pip`
- **Modes prédéfinis** : Développement (`--dev`) et production (`--prod`)
- **Configuration flexible** : Variables d'environnement et arguments en ligne de commande
- **Affichage coloré** : Interface utilisateur améliorée avec codes couleur
- **Gestion d'erreurs** : Arrêt propre en cas de problème

**Variables d'environnement supportées :**
```bash
export HOST="127.0.0.1"
export PORT="3000"
export WORKERS="4"
export LOG_LEVEL="debug"
export RELOAD="false"
export GOOGLE_API_KEY="your_api_key"
```


### Commandes Utiles

```bash
# Démarrage en mode développement avec le script
./start.sh --dev

# Démarrage en mode production
./start.sh --prod

# Démarrage manuel avec uvicorn
uvicorn app.main:app --reload

# Installation/Mise à jour des dépendances
uv sync                    # Avec uv (recommandé)
pip install -r requirements.txt  # Avec pip

# Tests (à implémenter)
pytest tests/

# Formatage du code
black app/
isort app/

# Vérification du code
flake8 app/
mypy app/
```

## 🐛 Résolution de Problèmes

### Problèmes Courants

1. **Erreur d'API Gemini** : Vérifiez que `GOOGLE_API_KEY` est correctement configurée
2. **Fichier non supporté** : Seuls les fichiers PDF sont acceptés
3. **Extraction échouée** : Vérifiez la qualité et la lisibilité du PDF

### Logs de Débogage

Les logs sont disponibles dans la console avec le format :
```
YYYY-MM-DD HH:MM:SS - FLUXY - LEVEL - MESSAGE
```

## 🤝 Contribution

1. Fork du projet
2. Création d'une branche feature (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commit des modifications (`git commit -am 'Ajout nouvelle fonctionnalité'`)
4. Push de la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Création d'une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 📞 Support

Pour toute question ou problème, veuillez ouvrir une issue sur le dépôt GitHub ou contacter l'équipe de développement.

---

**Fluxy** - Automatisation intelligente pour les professionnels de la comptabilité