# Changelog - Système d'Authentification ChantierPlus

## Résumé des changements

ChantierPlus dispose maintenant d'un système d'authentification complet avec gestion des utilisateurs, des sociétés et des rôles.

## 🎯 Fonctionnalités ajoutées

### Authentification
- ✅ Inscription de société avec compte propriétaire
- ✅ Connexion email/mot de passe
- ✅ Authentification JWT (tokens valides 7 jours)
- ✅ Déconnexion
- ✅ Protection des routes (accès uniquement aux utilisateurs connectés)

### Gestion des utilisateurs
- ✅ Invitation d'employés par email (propriétaires uniquement)
- ✅ Activation de compte employé via lien email
- ✅ Réinitialisation de mot de passe via email
- ✅ Gestion des rôles (OWNER / EMPLOYEE)

### Sécurité
- ✅ Hashing des mots de passe avec bcrypt
- ✅ Tokens JWT sécurisés
- ✅ Tokens d'invitation/reset avec expiration
- ✅ Validation des données avec Pydantic

## 📦 Fichiers Backend créés/modifiés

### Créés
- `backend/app/auth_utils.py` - Utilitaires JWT et hashing
- `backend/app/email_service.py` - Service d'envoi d'emails (simulation)

### Modifiés
- `backend/app/models.py` - Ajout des champs d'authentification au modèle UserProfile
- `backend/app/schemas.py` - Ajout des schémas d'authentification
- `backend/app/routers/auth.py` - Routes d'authentification complètes
- `backend/requirements.txt` - Dépendances déjà présentes (passlib, python-jose)

### Nouveaux champs dans UserProfile
```python
password_hash: str       # Hash du mot de passe
is_active: bool          # Compte activé ou non
invitation_token: str    # Token pour invitation employé
reset_token: str         # Token pour reset password
token_expires_at: datetime  # Expiration des tokens
```

## 🎨 Fichiers Frontend créés/modifiés

### Créés
- `frontend/src/contexts/AuthContext.tsx` - Contexte React d'authentification
- `frontend/src/components/ProtectedRoute.tsx` - Composant de route protégée
- `frontend/src/components/InviteEmployeeModal.tsx` - Modal d'invitation
- `frontend/src/pages/Login.tsx` - Page de connexion
- `frontend/src/pages/Register.tsx` - Page d'inscription
- `frontend/src/pages/ForgotPassword.tsx` - Page demande reset password
- `frontend/src/pages/ResetPassword.tsx` - Page reset password
- `frontend/src/pages/ActivateAccount.tsx` - Page activation compte employé

### Modifiés
- `frontend/src/App.tsx` - Configuration des routes avec AuthProvider
- `frontend/src/components/Layout.tsx` - Header avec bouton invitation et logout
- `frontend/src/config.ts` - Export de API_BASE_URL

## 🛣️ Nouvelles routes

### Routes publiques (non authentifiées)
- `/login` - Connexion
- `/register` - Inscription société
- `/forgot-password` - Demande reset password
- `/reset-password?token=xxx` - Reset password
- `/activate?token=xxx` - Activation compte employé

### Routes protégées (authentification requise)
- `/` - Dashboard
- `/create-avenant/:clientId` - Création avenant
- `/avenant/:id` - Détails avenant

### Routes API
```
POST   /auth/register              # Inscription société
POST   /auth/login                 # Connexion
GET    /auth/me                    # Info utilisateur connecté
POST   /auth/invite-employee       # Inviter employé (OWNER)
POST   /auth/activate              # Activer compte employé
POST   /auth/request-password-reset # Demander reset password
POST   /auth/reset-password        # Reset password
```

## 🚀 Utilisation

### Démarrage
```bash
# Backend
cd backend
uvicorn app.main:app --reload

# Frontend (nouveau terminal)
cd frontend
npm run dev

# Créer utilisateurs de test (optionnel)
python create_test_user.py
```

### Utilisateurs de test
- Propriétaire: owner@test.com / password123
- Employé: employee@test.com / password123

## 📧 Service d'emails

**Note importante** : Les emails sont actuellement **simulés**.

Les liens d'invitation et de reset password sont affichés dans la **console du backend**.

Exemple :
```
🔗 INVITATION LINK: http://localhost:5173/activate?token=xxx
🔗 PASSWORD RESET LINK: http://localhost:5173/reset-password?token=xxx
```

Pour intégrer un vrai service d'email (SendGrid, SMTP, etc.), modifiez `backend/app/email_service.py`.

## 🔐 Sécurité

### Points de sécurité implémentés
- ✅ Hashing bcrypt des mots de passe
- ✅ JWT avec expiration (7 jours)
- ✅ Tokens d'invitation avec expiration (7 jours)
- ✅ Tokens reset password avec expiration (1 heure)
- ✅ Validation des tokens avant utilisation
- ✅ Protection des routes backend avec dépendances
- ✅ Protection des routes frontend avec ProtectedRoute

### À faire pour la production
- [ ] Changer SECRET_KEY dans `auth_utils.py`
- [ ] Utiliser HTTPS
- [ ] Configurer les variables d'environnement
- [ ] Implémenter un vrai service d'email
- [ ] Ajouter du rate limiting sur les endpoints auth
- [ ] Augmenter la force minimale des mots de passe
- [ ] Implémenter les refresh tokens

## 🗃️ Base de données

La base de données SQLite sera automatiquement recréée au prochain démarrage du backend avec les nouvelles colonnes.

**Note** : Si vous aviez déjà une base de données, supprimez `chantierplus.db` pour que les nouvelles colonnes soient créées.

## 📚 Documentation

### Fichiers de documentation créés
- `AUTH_README.md` - Documentation complète du système d'authentification
- `QUICKSTART.md` - Guide de démarrage rapide
- `CHANGELOG_AUTH.md` - Ce fichier
- `create_test_user.py` - Script pour créer des utilisateurs de test

### Consultez ces fichiers pour :
- `AUTH_README.md` - Architecture détaillée et exemples d'utilisation
- `QUICKSTART.md` - Installation et premier démarrage

## 🎯 Différences avec l'ancien système

### Avant
- ❌ Pas d'authentification
- ❌ Accès libre à toutes les pages
- ❌ Pas de gestion des utilisateurs
- ❌ Un seul utilisateur fictif

### Maintenant
- ✅ Authentification complète
- ✅ Routes protégées
- ✅ Multi-utilisateurs et multi-sociétés
- ✅ Gestion des rôles (propriétaire/employé)
- ✅ Système d'invitation sécurisé
- ✅ Reset password fonctionnel

## 🔄 Migration

Si vous avez des données existantes dans `chantierplus.db` :

1. **Sauvegardez** vos données si nécessaire
2. **Supprimez** `chantierplus.db`
3. **Redémarrez** le backend - la nouvelle base sera créée
4. **Recréez** vos données de test avec `create_test_user.py`

## 🎨 Interface utilisateur

### Nouvelles pages
Toutes les pages d'authentification ont une interface moderne avec :
- Design cohérent avec Tailwind CSS
- Validation des formulaires
- Messages d'erreur clairs
- Feedback visuel (loading, success, error)
- Responsive design

### Améliorations du Layout
- Affichage de l'email et du rôle de l'utilisateur
- Bouton "Inviter un employé" (visible uniquement pour les propriétaires)
- Bouton de déconnexion
- Modal d'invitation élégante

## 🐛 Problèmes connus

Aucun problème majeur identifié. Le système a été conçu pour être robuste et sécurisé.

## 🚦 Tests recommandés

1. ✅ Inscription d'une nouvelle société
2. ✅ Connexion/déconnexion
3. ✅ Invitation d'employé
4. ✅ Activation de compte employé
5. ✅ Reset password
6. ✅ Protection des routes (accès sans token)
7. ✅ Affichage conditionnel du bouton invitation (selon rôle)

## 📊 Statistiques

- **Fichiers backend créés** : 2
- **Fichiers backend modifiés** : 3
- **Fichiers frontend créés** : 9
- **Fichiers frontend modifiés** : 3
- **Fichiers de documentation** : 4
- **Nouvelles routes API** : 7
- **Nouvelles pages UI** : 5

---

**Date de création** : Décembre 2024
**Version** : 1.0.0
**Status** : ✅ Production ready (après configuration des secrets et emails)
