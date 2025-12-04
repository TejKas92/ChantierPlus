# Guide de Déploiement ChantierPlus

## Prérequis Installation

Avant de déployer, vous devez installer les nouvelles dépendances :

```bash
cd backend
pip install weasyprint pillow
```

**Note importante pour WeasyPrint** : WeasyPrint nécessite des dépendances système :
- **Windows** : Téléchargez GTK3 Runtime depuis https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases
- **Linux** : `sudo apt-get install libpango-1.0-0 libpangoft2-1.0-0`
- **macOS** : `brew install pango`

## Migrations de Base de Données

Les modifications apportées au modèle nécessitent une migration :

### Changements dans la base de données :
1. `signature_data` (Text) → `signature_url` (Text)
2. Ajout de `employee_id` (UUID) - Référence à l'employé qui a créé l'avenant

### Option 1 : Recréer la base de données (Développement uniquement)

```bash
cd backend
rm chantierplus.db  # Supprime l'ancienne base
# Le serveur recréera automatiquement la base au démarrage
python -m uvicorn app.main:app --reload
```

### Option 2 : Migration Alembic (Production)

```bash
cd backend

# Créer une migration
alembic revision --autogenerate -m "Add signature_url and employee_id to avenant"

# Appliquer la migration
alembic upgrade head
```

Si vous obtenez des erreurs, vous pouvez écrire la migration manuellement :

```python
# Dans le fichier de migration généré

def upgrade():
    # Renommer signature_data en signature_url
    op.alter_column('avenants', 'signature_data',
                    new_column_name='signature_url',
                    existing_type=sa.Text())

    # Ajouter employee_id
    op.add_column('avenants',
                  sa.Column('employee_id', sa.UUID(), nullable=True))
    op.create_foreign_key(None, 'avenants', 'user_profiles',
                         ['employee_id'], ['id'])

def downgrade():
    op.drop_constraint(None, 'avenants', type_='foreignkey')
    op.drop_column('avenants', 'employee_id')
    op.alter_column('avenants', 'signature_url',
                    new_column_name='signature_data',
                    existing_type=sa.Text())
```

## Configuration Email SMTP

Assurez-vous que votre fichier `.env` contient :

```env
SMTP_HOST=smtp-croqlab.alwaysdata.net
SMTP_PORT=587
SMTP_USERNAME=votre-email@domaine.com
SMTP_PASSWORD=votre-mot-de-passe
SMTP_FROM_EMAIL=votre-email@domaine.com
SMTP_FROM_NAME=ChantierPlus
```

## Test de la Nouvelle Fonctionnalité

1. **Créer un avenant** :
   - Remplissez tous les champs
   - Ajoutez une photo
   - Signez l'avenant
   - Cliquez sur "Valider et Envoyer par Email"

2. **Vérifier les emails** :
   - Le client doit recevoir un email avec le PDF en pièce jointe
   - L'employé qui a créé l'avenant doit recevoir l'email
   - Tous les propriétaires de l'entreprise doivent recevoir l'email

3. **Vérifier la suppression des fichiers** :
   - Les fichiers photo, signature et PDF doivent être supprimés du serveur après l'envoi
   - Vérifiez que le dossier `uploads/` ne contient pas de fichiers temporaires

## Logs à Surveiller

Lors de la création d'un avenant, vous devriez voir dans la console :

```
📧 Attempting to send email to client@example.com...
✅ Email sent successfully to client@example.com
📧 Attempting to send email to employee@company.com...
✅ Email sent successfully to employee@company.com
📧 Attempting to send email to owner@company.com...
✅ Email sent successfully to owner@company.com
✅ Deleted temporary file: uploads/xxx-photo.jpg
✅ Deleted temporary file: uploads/xxx-signature.png
✅ Deleted temporary file: uploads/xxx.pdf
```

## Dépannage

### Erreur "No module named 'weasyprint'"
```bash
pip install weasyprint pillow
```

### Erreur "Cannot load library gobject-2.0"
Installez GTK3 Runtime (voir section Prérequis)

### Les PDFs ne sont pas générés
Vérifiez les logs du serveur pour voir les erreurs détaillées

### Les emails ne sont pas envoyés
- Vérifiez la configuration SMTP dans `.env`
- Testez avec le script `backend/test_email.py`

### Les fichiers ne sont pas supprimés
- Vérifiez les permissions du dossier `uploads/`
- Regardez les logs pour voir s'il y a des erreurs

## Structure des Fichiers

```
uploads/
  ├── <uuid>.jpg     # Photo (temporaire, supprimée après envoi)
  ├── <uuid>.png     # Signature (temporaire, supprimée après envoi)
  └── <uuid>.pdf     # PDF généré (temporaire, supprimé après envoi)
```

## Workflow Complet

1. L'utilisateur crée un avenant avec photo et signature
2. Le backend sauvegarde temporairement la photo et convertit la signature en fichier PNG
3. L'avenant est créé en base de données avec `employee_id`
4. Un PDF professionnel est généré avec toutes les informations
5. Le PDF est envoyé par email à :
   - Le client (email du chantier)
   - L'employé qui a créé l'avenant
   - Tous les propriétaires de l'entreprise
6. Les fichiers temporaires (photo, signature, PDF) sont automatiquement supprimés
7. L'utilisateur est redirigé vers la page de confirmation

## Sécurité

- ✅ Les fichiers sont générés avec des UUIDs uniques
- ✅ Les fichiers temporaires sont automatiquement supprimés
- ✅ Validation des types et tailles de fichiers
- ✅ Authentification JWT requise
- ✅ Vérification des permissions (company_id)
