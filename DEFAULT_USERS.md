# SpeedX - Comptes par défaut

## Utilisateurs créés automatiquement au démarrage

L'application crée automatiquement deux comptes utilisateur au premier démarrage :

### 👤 Compte Administrateur
- **Email** : `admin@speedx.com`
- **Mot de passe** : ``
- **Rôle** : Administrateur
- **Permissions** : Accès complet à toutes les fonctionnalités

### 👤 Compte Utilisateur Standard
- **Email** : `user@speedx.com`
- **Mot de passe** : ``
- **Rôle** : Utilisateur standard
- **Permissions** : Accès aux fonctionnalités d'extraction

## 🔒 Sécurité

⚠️ **Important** : Ces comptes par défaut sont créés uniquement pour faciliter le démarrage. 

**Il est fortement recommandé de :**
1. Changer les mots de passe par défaut après le premier déploiement
2. Créer vos propres comptes administrateur avec des identifiants sécurisés
3. Désactiver ou supprimer ces comptes par défaut en production

## 🚀 Fonctionnement

- Les utilisateurs sont créés automatiquement lors du démarrage du serveur
- Si les comptes existent déjà, ils ne sont pas recréés
- La vérification se fait par email (admin@speedx.com et user@speedx.com)
- Les logs indiquent si de nouveaux utilisateurs ont été créés ou s'ils existaient déjà