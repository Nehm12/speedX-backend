# 🚀 Guide de Déploiement SpeedX

## Architecture de Déploiement
- **Backend** : Render (avec PostgreSQL)
- **Frontend** : Vercel

## 📋 Étapes de Déploiement

### 1. Déploiement du Backend sur Render

#### A. Préparation
1. Créez un compte sur [Render](https://render.com)
2. Connectez votre repository GitHub à Render

#### B. Création de la base de données PostgreSQL
1. Dans le dashboard Render, cliquez sur "New +"
2. Sélectionnez "PostgreSQL"
3. Configurez :
   - **Name** : `speedx-db`
   - **Database** : `speedx`
   - **User** : `speedx_user`
   - **Region** : Choisissez la plus proche de vos utilisateurs
4. Cliquez sur "Create Database"
5. **Important** : Notez l'URL de connexion générée

#### C. Déploiement du service web
1. Cliquez sur "New +" → "Web Service"
2. Connectez votre repository `speedX-backend`
3. Configurez :
   - **Name** : `speedx-backend`
   - **Environment** : `Python 3`
   - **Build Command** : `pip install -r requirements.txt`
   - **Start Command** : `gunicorn app.main:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`

#### D. Variables d'environnement à configurer dans Render
```
DATABASE_URL=postgresql://speedx_user:password@hostname:port/speedx
SECRET_KEY=your_generated_secret_key
GOOGLE_API_KEY=AIzaSyBqeykrjFZmFB9_zqxd41j7cb2FHur8dXg
FRONTEND_URL=https://your-speedx-frontend.vercel.app
BACKEND_URL=https://speedx-backend.onrender.com
APP_ENV=prod
LOG_LEVEL=INFO
RATE_LIMIT=10/minute
CORS_ORIGINS=https://your-speedx-frontend.vercel.app
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_smtp_username
SMTP_PASSWORD=your_smtp_password
FROM_EMAIL=your_from_email@example.com
FROM_NAME=SpeedX
```

### 2. Déploiement du Frontend sur Vercel

#### A. Préparation
1. Créez un compte sur [Vercel](https://vercel.com)
2. Installez la CLI Vercel : `npm i -g vercel`

#### B. Déploiement automatique
1. Dans le dossier `speedX-frontend`, exécutez :
   ```bash
   vercel
   ```
2. Suivez les instructions :
   - Link to existing project? **N**
   - Project name: `speedx-frontend`
   - Directory: `./` (current directory)
   - Override settings? **N**

#### C. Configuration des variables d'environnement
Dans le dashboard Vercel :
1. Allez dans votre projet → Settings → Environment Variables
2. Ajoutez :
   ```
   NEXT_PUBLIC_API_URL = https://speedx-backend.onrender.com
   ```

### 3. Mise à jour des URLs

#### A. Backend - Mettre à jour CORS et FRONTEND_URL
Une fois le frontend déployé, mettez à jour dans Render :
```
FRONTEND_URL=https://your-actual-vercel-url.vercel.app
CORS_ORIGINS=https://your-actual-vercel-url.vercel.app
```

#### B. Frontend - Vérifier l'URL de l'API
Vérifiez que `NEXT_PUBLIC_API_URL` pointe vers votre backend Render.

## 🔧 Commandes Utiles

### Backend (Render)
```bash
# Voir les logs
render logs --service speedx-backend

# Redéployer
git push origin main
```

### Frontend (Vercel)
```bash
# Déploiement local
vercel --prod

# Voir les logs
vercel logs

# Redéployer
vercel --prod
```

## 🔐 Sécurité

### Variables sensibles à configurer :
1. **SECRET_KEY** : Générez une nouvelle clé pour la production
2. **GOOGLE_API_KEY** : Votre clé API Google Gemini
3. **SMTP credentials** : Pour l'envoi d'emails
4. **DATABASE_URL** : Fournie automatiquement par Render

### Générer une nouvelle SECRET_KEY :
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 📊 Monitoring

### Health Checks
- Backend : `https://speedx-backend.onrender.com/health`
- Frontend : Vercel fournit automatiquement le monitoring

### Logs
- **Render** : Dashboard → Service → Logs
- **Vercel** : Dashboard → Project → Functions → View Logs

## 🚨 Troubleshooting

### Problèmes courants :

1. **CORS Errors** : Vérifiez que `CORS_ORIGINS` inclut l'URL exacte de Vercel
2. **Database Connection** : Vérifiez que `DATABASE_URL` est correctement configurée
3. **Build Failures** : Vérifiez les logs de build dans Render/Vercel
4. **Environment Variables** : Assurez-vous que toutes les variables sont définies

### Migration de données (si nécessaire)
Si vous avez des données dans SQLite à migrer :
1. Exportez les données depuis SQLite
2. Importez dans PostgreSQL via le dashboard Render ou pgAdmin