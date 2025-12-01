"""
Email service for sending invitations and password reset emails.
For now, this is a mock service that prints to console.
In production, integrate with SMTP or services like SendGrid, AWS SES, etc.
"""
import logging

logger = logging.getLogger(__name__)

FRONTEND_URL = "http://localhost:5173"  # TODO: Move to .env

async def send_invitation_email(email: str, token: str, company_name: str):
    """
    Send an invitation email to a new employee.
    """
    invitation_link = f"{FRONTEND_URL}/activate?token={token}"

    # Print to console
    message = f"""
    ========================================
    EMAIL INVITATION
    ========================================
    To: {email}
    Subject: Invitation à rejoindre {company_name} sur ChantierPlus

    Bonjour,

    Vous avez été invité à rejoindre {company_name} sur ChantierPlus.

    Cliquez sur le lien ci-dessous pour créer votre compte :
    {invitation_link}

    Ce lien expirera dans 7 jours.

    Cordialement,
    L'équipe ChantierPlus
    ========================================
    """

    print(message)
    print(f"\n🔗 INVITATION LINK: {invitation_link}\n")

    # Also log
    logger.info(message)

    return True

async def send_password_reset_email(email: str, token: str):
    """
    Send a password reset email.
    """
    reset_link = f"{FRONTEND_URL}/reset-password?token={token}"

    # Print to console
    message = f"""
    ========================================
    EMAIL PASSWORD RESET
    ========================================
    To: {email}
    Subject: Réinitialisation de votre mot de passe ChantierPlus

    Bonjour,

    Vous avez demandé une réinitialisation de votre mot de passe.

    Cliquez sur le lien ci-dessous pour définir un nouveau mot de passe :
    {reset_link}

    Ce lien expirera dans 1 heure.

    Si vous n'avez pas fait cette demande, ignorez cet email.

    Cordialement,
    L'équipe ChantierPlus
    ========================================
    """

    print(message)
    print(f"\n🔗 PASSWORD RESET LINK: {reset_link}\n")

    # Also log
    logger.info(message)

    return True
