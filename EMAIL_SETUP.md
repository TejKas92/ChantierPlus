# Configuration de l'envoi d'emails

## Configuration SMTP AlwaysData

L'application utilise le serveur SMTP d'AlwaysData pour envoyer des emails.

### Étape 1 : Copier le fichier d'environnement

```bash
cd backend
cp .env.example .env
```

### Étape 2 : Configurer les variables SMTP dans le fichier `.env`

Ouvrez le fichier `backend/.env` et remplissez les variables suivantes :

```env
# SMTP Configuration (AlwaysData)
SMTP_HOST=smtp-croqlab.alwaysdata.net
SMTP_PORT=587
SMTP_USERNAME=votre-email@votre-domaine.com
SMTP_PASSWORD=votre-mot-de-passe-smtp
SMTP_FROM_EMAIL=votre-email@votre-domaine.com
SMTP_FROM_NAME=ChantierPlus
```

### Étape 3 : Obtenir vos identifiants SMTP AlwaysData

1. Connectez-vous à votre compte AlwaysData
2. Allez dans **Emails > Boîtes email**
3. Sélectionnez ou créez une boîte email
4. Utilisez les identifiants SMTP fournis

### Fonctionnalités d'envoi d'email

#### 1. Envoi automatique d'avenant par email (avec PDF)

Lors de la création et signature d'un avenant, l'envoi par email est **automatique** :

1. Créez un avenant avec photo et signature
2. Cliquez sur "Valider et Envoyer par Email"
3. Le système génère automatiquement un PDF professionnel
4. Le PDF est envoyé par email à :
   - Le client (email du chantier)
   - L'employé qui a créé l'avenant
   - Tous les propriétaires de l'entreprise
5. Les fichiers temporaires (photo, signature, PDF) sont automatiquement supprimés

**Contenu de l'email** :
- Résumé des informations (description, type, montant)
- PDF complet en pièce jointe avec :
  - Informations du chantier
  - Description détaillée des travaux
  - Détails financiers
  - Photo des travaux
  - Signature du client
  - En-tête et footer professionnels

#### 2. Invitation d'employés

Lors de l'invitation d'un nouvel employé :

1. L'administrateur invite un employé via l'interface
2. Un email d'invitation est automatiquement envoyé
3. L'email contient un lien d'activation valide 7 jours

**Contenu de l'email** :
- Nom de l'entreprise
- Lien d'activation du compte
- Instructions pour créer le mot de passe

#### 3. Réinitialisation de mot de passe

Lorsqu'un utilisateur demande une réinitialisation :

1. L'utilisateur clique sur "Mot de passe oublié"
2. Un email de réinitialisation est envoyé
3. Le lien est valide pendant 1 heure

**Contenu de l'email** :
- Lien de réinitialisation sécurisé
- Avertissement sur l'expiration du lien
- Note de sécurité si la demande n'est pas de l'utilisateur

## Test de la configuration

Pour tester que l'envoi d'emails fonctionne :

1. Créez un chantier avec une adresse email valide
2. Créez un avenant pour ce chantier (avec photo et signature)
3. Cliquez sur "Valider et Envoyer par Email"
4. Vérifiez que les emails avec PDF ont bien été reçus par :
   - Le client (email du chantier)
   - Vous-même (employé créateur)
   - Les propriétaires de l'entreprise

## Dépannage

### Erreur "Authentication failed"
- Vérifiez que le nom d'utilisateur et le mot de passe SMTP sont corrects
- Vérifiez que vous utilisez le bon serveur SMTP : `smtp-croqlab.alwaysdata.net`

### Erreur "Connection timeout"
- Vérifiez que le port 587 n'est pas bloqué par votre pare-feu
- Vérifiez votre connexion Internet

### L'email n'arrive pas
- Vérifiez le dossier spam/courrier indésirable
- Vérifiez que l'adresse email du chantier est correcte
- Vérifiez les logs du serveur pour voir les erreurs détaillées

## Sécurité

⚠️ **IMPORTANT** : Ne committez JAMAIS le fichier `.env` dans Git !

Le fichier `.env` contient des informations sensibles (mot de passe SMTP). Il est déjà inclus dans le `.gitignore` et ne sera pas versionné.
