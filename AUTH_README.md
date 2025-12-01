# Système d'Authentification ChantierPlus

## Vue d'ensemble

ChantierPlus dispose maintenant d'un système d'authentification complet avec :

- ✅ Inscription de société (propriétaire)
- ✅ Connexion avec email/mot de passe
- ✅ Authentification JWT
- ✅ Invitation d'employés par email
- ✅ Activation de compte employé
- ✅ Réinitialisation de mot de passe
- ✅ Routes protégées
- ✅ Gestion des rôles (OWNER / EMPLOYEE)

## Architecture

### Backend (FastAPI)

#### Modèles de données

**UserProfile** - Table `user_profiles`
- `id` : UUID unique
- `company_id` : Référence à la société
- `email` : Email unique
- `password_hash` : Hash du mot de passe (bcrypt)
- `role` : OWNER ou EMPLOYEE
- `is_active` : Compte activé ou non
- `invitation_token` : Token pour invitation employé
- `reset_token` : Token pour réinitialisation mot de passe
- `token_expires_at` : Expiration des tokens
- `created_at` : Date de création

**Company** - Table `companies`
- `id` : UUID unique
- `name` : Nom de la société (unique)
- `created_at` : Date de création

#### Endpoints API

**Authentification**

```
POST /auth/register
Body: { email, password, company_name }
Retour: { access_token, token_type, user }
Description: Crée une nouvelle société avec un compte propriétaire
```

```
POST /auth/login
Body: { email, password }
Retour: { access_token, token_type, user }
Description: Authentifie un utilisateur et retourne un JWT
```

```
GET /auth/me
Headers: Authorization: Bearer <token>
Retour: UserProfile
Description: Récupère les informations de l'utilisateur connecté
```

**Gestion des employés**

```
POST /auth/invite-employee
Headers: Authorization: Bearer <token>
Body: { email }
Retour: { message }
Description: Invite un employé (OWNER uniquement)
Note: Envoie un email avec un lien d'activation
```

```
POST /auth/activate
Body: { token, password }
Retour: { access_token, token_type, user }
Description: Active le compte d'un employé avec le token d'invitation
```

**Réinitialisation de mot de passe**

```
POST /auth/request-password-reset
Body: { email }
Retour: { message }
Description: Demande un lien de réinitialisation de mot de passe
```

```
POST /auth/reset-password
Body: { token, password }
Retour: { access_token, token_type, user }
Description: Réinitialise le mot de passe avec le token
```

#### Sécurité

- **Hashing des mots de passe** : Utilisation de bcrypt via passlib
- **JWT** : Tokens JWT avec une durée de validité de 7 jours
- **Tokens sécurisés** : Génération de tokens aléatoires avec `secrets.token_urlsafe(32)`
- **Expiration des tokens** :
  - Invitation employé : 7 jours
  - Réinitialisation mot de passe : 1 heure

### Frontend (React + TypeScript)

#### Contexte d'authentification

`AuthContext` fournit :
- `user` : Utilisateur connecté
- `token` : JWT token
- `loading` : État de chargement
- `login(email, password)` : Connexion
- `register(email, password, companyName)` : Inscription
- `logout()` : Déconnexion
- `isAuthenticated` : Boolean

#### Pages

1. **Login** (`/login`)
   - Formulaire de connexion
   - Lien "Mot de passe oublié"
   - Bouton "Créer une société"

2. **Register** (`/register`)
   - Formulaire d'inscription de société
   - Création du compte propriétaire

3. **ForgotPassword** (`/forgot-password`)
   - Demande de réinitialisation de mot de passe

4. **ResetPassword** (`/reset-password?token=xxx`)
   - Formulaire de nouveau mot de passe

5. **ActivateAccount** (`/activate?token=xxx`)
   - Activation de compte employé
   - Définition du mot de passe

#### Composants

- **ProtectedRoute** : Protège les routes nécessitant une authentification
- **InviteEmployeeModal** : Modal pour inviter des employés (OWNER uniquement)
- **Layout** : Header avec bouton d'invitation et informations utilisateur

#### Routes

```
Routes publiques:
- /login
- /register
- /forgot-password
- /reset-password?token=xxx
- /activate?token=xxx

Routes protégées:
- / (Dashboard)
- /create-avenant/:clientId
- /avenant/:id
```

## Utilisation

### Pour démarrer

1. **Backend** :
```bash
cd backend
uvicorn app.main:app --reload
```

2. **Frontend** :
```bash
cd frontend
npm run dev
```

3. **Créer un utilisateur de test** :
```bash
python create_test_user.py
```

Utilisateurs de test créés :
- **Propriétaire** : owner@test.com / password123
- **Employé** : employee@test.com / password123

### Flux d'inscription d'une nouvelle société

1. L'utilisateur clique sur "Créer une société" depuis `/login`
2. Remplir le formulaire avec :
   - Nom de la société
   - Email
   - Mot de passe
3. Le système crée :
   - Une nouvelle société
   - Un compte propriétaire (OWNER)
4. L'utilisateur est automatiquement connecté et redirigé vers le dashboard

### Flux d'invitation d'employé

1. Le propriétaire se connecte
2. Clique sur "Inviter un employé" dans le header
3. Entre l'email de l'employé
4. Un email est envoyé avec un lien d'activation (token)
5. L'employé clique sur le lien : `/activate?token=xxx`
6. L'employé définit son mot de passe
7. Le compte est activé et l'employé est connecté

### Flux de réinitialisation de mot de passe

1. Utilisateur clique sur "Mot de passe oublié"
2. Entre son email
3. Reçoit un email avec un lien de réinitialisation (token)
4. Clique sur le lien : `/reset-password?token=xxx`
5. Définit un nouveau mot de passe
6. Est connecté automatiquement

## Service d'envoi d'emails

Pour le moment, le service d'email est une **simulation** qui affiche les emails dans la console du backend.

Les liens sont affichés dans la console pour faciliter les tests :

```
🔗 INVITATION LINK: http://localhost:5173/activate?token=xxx
🔗 PASSWORD RESET LINK: http://localhost:5173/reset-password?token=xxx
```

### Intégration d'un vrai service d'email

Pour la production, modifiez `backend/app/email_service.py` pour intégrer :
- **SMTP** (Gmail, Outlook, etc.)
- **SendGrid**
- **AWS SES**
- **Mailgun**
- Etc.

## Configuration

### Variables d'environnement recommandées

Créez un fichier `.env` à la racine du backend :

```env
# JWT Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7 days

# Frontend URL (pour les liens dans les emails)
FRONTEND_URL=http://localhost:5173

# Email Service (optionnel)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=noreply@chantierplus.com
```

## Sécurité

### Points importants

1. **SECRET_KEY** : Changez absolument la clé secrète en production dans `backend/app/auth_utils.py`
2. **HTTPS** : Utilisez HTTPS en production pour protéger les tokens JWT
3. **CORS** : Configurez correctement les origines autorisées dans `backend/app/main.py`
4. **Rate limiting** : Considérez ajouter du rate limiting sur les endpoints d'authentification
5. **Validation des mots de passe** : Le minimum actuel est 6 caractères, augmentez si nécessaire

## Tests

### Test manuel

1. **Inscription** :
   - Aller sur `/register`
   - Créer une société avec email/mot de passe
   - Vérifier la redirection vers le dashboard

2. **Connexion** :
   - Se déconnecter
   - Aller sur `/login`
   - Se connecter avec les identifiants
   - Vérifier la redirection vers le dashboard

3. **Invitation employé** :
   - Se connecter en tant que propriétaire
   - Cliquer sur "Inviter un employé"
   - Copier le lien d'activation de la console
   - Ouvrir le lien dans un autre navigateur (navigation privée)
   - Activer le compte

4. **Réinitialisation mot de passe** :
   - Cliquer sur "Mot de passe oublié"
   - Entrer un email
   - Copier le lien de la console
   - Réinitialiser le mot de passe

## Structure des fichiers

```
ChantierPlus/
├── backend/
│   └── app/
│       ├── models.py              # Modèles SQLAlchemy (UserProfile, Company)
│       ├── schemas.py             # Schémas Pydantic (validation)
│       ├── auth_utils.py          # Utilitaires auth (JWT, hashing)
│       ├── email_service.py       # Service d'envoi d'emails
│       └── routers/
│           └── auth.py            # Routes d'authentification
│
├── frontend/
│   └── src/
│       ├── contexts/
│       │   └── AuthContext.tsx    # Contexte React d'authentification
│       ├── components/
│       │   ├── ProtectedRoute.tsx # Route protégée
│       │   ├── InviteEmployeeModal.tsx
│       │   └── Layout.tsx         # Header avec boutons auth
│       └── pages/
│           ├── Login.tsx
│           ├── Register.tsx
│           ├── ForgotPassword.tsx
│           ├── ResetPassword.tsx
│           └── ActivateAccount.tsx
│
├── create_test_user.py            # Script création utilisateurs test
└── AUTH_README.md                 # Ce fichier
```

## Prochaines étapes possibles

- [ ] Ajouter la vérification d'email à l'inscription
- [ ] Implémenter le 2FA (authentification à deux facteurs)
- [ ] Ajouter un système de permissions plus granulaire
- [ ] Implémenter la gestion des sessions
- [ ] Ajouter des logs d'audit pour les actions sensibles
- [ ] Implémenter un vrai service d'envoi d'emails
- [ ] Ajouter des tests automatisés
- [ ] Implémenter le refresh token
- [ ] Ajouter une page de gestion des employés pour le propriétaire
- [ ] Implémenter la révocation de tokens
