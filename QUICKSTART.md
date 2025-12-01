# Guide de Démarrage Rapide - ChantierPlus

## Prérequis

- Python 3.9+
- Node.js 16+
- npm ou yarn

## Installation et Démarrage

### 1. Installation Backend

```bash
cd backend
pip install -r requirements.txt
```

### 2. Installation Frontend

```bash
cd frontend
npm install
```

### 3. Démarrer le Backend

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Le backend sera accessible sur : http://localhost:8000

Vérifiez que ça fonctionne : http://localhost:8000/docs

### 4. Démarrer le Frontend

Dans un nouveau terminal :

```bash
cd frontend
npm run dev
```

Le frontend sera accessible sur : http://localhost:5173

### 5. Créer des utilisateurs de test (optionnel)

Dans un nouveau terminal :

```bash
python create_test_user.py
```

Cela créera :
- **Propriétaire** : owner@test.com / password123
- **Employé** : employee@test.com / password123

## Première utilisation

### Option A : Créer une nouvelle société

1. Ouvrez http://localhost:5173
2. Vous serez redirigé vers la page de connexion
3. Cliquez sur **"Créer une société"**
4. Remplissez le formulaire :
   - Nom de la société : "Ma Société"
   - Email : votre@email.com
   - Mot de passe : (minimum 6 caractères)
5. Vous serez automatiquement connecté et redirigé vers le dashboard

### Option B : Utiliser un compte de test

Si vous avez exécuté `create_test_user.py` :

1. Ouvrez http://localhost:5173
2. Connectez-vous avec :
   - Email : owner@test.com
   - Mot de passe : password123

## Fonctionnalités disponibles

### En tant que Propriétaire (OWNER)

- ✅ Gérer les clients
- ✅ Créer des avenants
- ✅ **Inviter des employés** (bouton dans le header)
- ✅ Voir tous les chantiers de la société

### En tant qu'Employé (EMPLOYEE)

- ✅ Gérer les clients
- ✅ Créer des avenants
- ✅ Voir tous les chantiers de la société

## Tester l'invitation d'employés

1. Connectez-vous en tant que propriétaire
2. Cliquez sur **"Inviter un employé"** dans le header
3. Entrez l'email de l'employé : employe@test.com
4. Un lien d'activation sera affiché dans la console du backend
5. Copiez le lien (ex: http://localhost:5173/activate?token=xxx)
6. Ouvrez-le dans un navigateur en navigation privée
7. Définissez un mot de passe pour activer le compte
8. Vous êtes maintenant connecté en tant qu'employé

## Tester la réinitialisation de mot de passe

1. Sur la page de connexion, cliquez sur **"Mot de passe oublié ?"**
2. Entrez votre email
3. Un lien de réinitialisation sera affiché dans la console du backend
4. Copiez le lien (ex: http://localhost:5173/reset-password?token=xxx)
5. Définissez un nouveau mot de passe
6. Vous serez automatiquement connecté

## URLs importantes

- **Frontend** : http://localhost:5173
- **Backend API** : http://localhost:8000
- **Documentation API** : http://localhost:8000/docs
- **API alternative (ReDoc)** : http://localhost:8000/redoc

## Structure de l'application

```
ChantierPlus/
├── backend/           # API FastAPI
│   └── app/
│       ├── models.py      # Modèles de données
│       ├── schemas.py     # Validation Pydantic
│       ├── database.py    # Configuration DB
│       ├── auth_utils.py  # JWT & hashing
│       ├── email_service.py  # Envoi d'emails
│       └── routers/
│           ├── auth.py        # Authentification
│           ├── clients.py     # Gestion clients
│           ├── avenants.py    # Gestion avenants
│           └── transcribe.py  # Transcription audio
│
├── frontend/          # Application React
│   └── src/
│       ├── contexts/      # AuthContext
│       ├── components/    # Composants réutilisables
│       ├── pages/         # Pages de l'application
│       └── App.tsx        # Configuration des routes
│
└── chantierplus.db    # Base de données SQLite
```

## Problèmes courants

### Le backend ne démarre pas

```bash
# Vérifiez que les dépendances sont installées
cd backend
pip install -r requirements.txt

# Si erreur avec bcrypt ou cryptography
pip install --upgrade pip
pip install passlib[bcrypt] python-jose[cryptography]
```

### Le frontend ne démarre pas

```bash
# Réinstallez les dépendances
cd frontend
rm -rf node_modules
npm install

# Si erreur avec vite
npm install vite --save-dev
```

### Erreur CORS

Le backend est configuré pour accepter les requêtes de :
- http://localhost:5173
- http://localhost:3000
- http://192.168.1.120:5173
- http://192.168.1.120:5174

Si vous utilisez un autre port, modifiez `backend/app/main.py`.

### Les emails ne sont pas envoyés

C'est normal ! Le système d'email est actuellement en mode **simulation**.
Les liens d'invitation et de réinitialisation sont affichés dans la console du backend.

Pour un vrai service d'email, consultez `AUTH_README.md`.

## Prochaines étapes

1. Lisez `AUTH_README.md` pour comprendre le système d'authentification complet
2. Explorez l'API interactive sur http://localhost:8000/docs
3. Créez vos premiers clients et avenants
4. Invitez vos employés

## Support

Pour toute question ou problème :
1. Vérifiez `AUTH_README.md` pour la documentation complète
2. Consultez les logs du backend dans le terminal
3. Consultez la console du navigateur (F12) pour les erreurs frontend

## Base de données

La base de données SQLite est créée automatiquement au premier démarrage du backend.

Pour réinitialiser la base de données :

```bash
# ATTENTION : Cela supprime toutes les données !
rm chantierplus.db
# Redémarrez le backend, la DB sera recréée
```

Bon développement ! 🚀
