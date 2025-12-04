import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from jinja2 import Template
import os
from pathlib import Path
from typing import List, Optional
import base64
import logging

# Configure logging
logger = logging.getLogger(__name__)

# SMTP Configuration from environment variables
SMTP_HOST = os.getenv("SMTP_HOST", "smtp-croqlab.alwaysdata.net")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "")
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "ChantierPlus")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# Log SMTP configuration (without password)
logger.info(f"SMTP Configuration: Host={SMTP_HOST}, Port={SMTP_PORT}, Username={SMTP_USERNAME}, From={SMTP_FROM_EMAIL}")
print(f"[CONFIG] SMTP Configuration loaded: {SMTP_HOST}:{SMTP_PORT} from {SMTP_FROM_EMAIL}")


async def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    attachments: Optional[List[tuple[str, bytes, str]]] = None
):
    """
    Send an email via SMTP

    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML content of the email
        attachments: List of tuples (filename, file_data, mime_type)
    """
    message = MIMEMultipart()
    message["From"] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
    message["To"] = to_email
    message["Subject"] = subject

    # Add HTML content
    message.attach(MIMEText(html_content, "html"))

    # Add attachments if any
    if attachments:
        for filename, file_data, mime_type in attachments:
            if mime_type.startswith("image/"):
                attachment = MIMEImage(file_data)
                attachment.add_header("Content-Disposition", f"attachment; filename={filename}")
            elif mime_type == "application/pdf":
                attachment = MIMEApplication(file_data, _subtype="pdf")
                attachment.add_header("Content-Disposition", f"attachment; filename={filename}")
            else:
                attachment = MIMEApplication(file_data)
                attachment.add_header("Content-Disposition", f"attachment; filename={filename}")
            message.attach(attachment)

    # Send email
    try:
        logger.info(f"[EMAIL] Sending email to {to_email} via {SMTP_HOST}:{SMTP_PORT}")
        print(f"[EMAIL] Attempting to send email to {to_email}...")

        await aiosmtplib.send(
            message,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            username=SMTP_USERNAME,
            password=SMTP_PASSWORD,
            start_tls=True,
        )

        logger.info(f"[SUCCESS] Email sent successfully to {to_email}")
        print(f"[SUCCESS] Email sent successfully to {to_email}")
        return True
    except Exception as e:
        error_msg = f"[ERROR] Error sending email to {to_email}: {e}"
        logger.error(error_msg)
        print(error_msg)
        raise


async def send_invitation_email(email: str, token: str, company_name: str):
    """
    Send an invitation email to a new employee.
    """
    invitation_link = f"{FRONTEND_URL}/activate?token={token}"

    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }
            .header {
                background-color: #f59e0b;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 5px 5px 0 0;
            }
            .content {
                background-color: #f9fafb;
                padding: 30px;
                border: 1px solid #e5e7eb;
            }
            .button {
                display: inline-block;
                padding: 12px 24px;
                background-color: #f59e0b;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin: 20px 0;
            }
            .footer {
                text-align: center;
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #e5e7eb;
                color: #6b7280;
                font-size: 14px;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Invitation à rejoindre {{ company_name }}</h1>
        </div>

        <div class="content">
            <p>Bonjour,</p>
            <p>Vous avez été invité à rejoindre <strong>{{ company_name }}</strong> sur ChantierPlus.</p>
            <p>Cliquez sur le bouton ci-dessous pour créer votre compte :</p>

            <p style="text-align: center;">
                <a href="{{ invitation_link }}" class="button">
                    Activer mon compte
                </a>
            </p>

            <p style="color: #6b7280; font-size: 14px;">
                Ce lien expirera dans 7 jours.
            </p>

            <p style="color: #6b7280; font-size: 14px;">
                Si vous ne pouvez pas cliquer sur le bouton, copiez et collez ce lien dans votre navigateur :
                <br>
                <a href="{{ invitation_link }}">{{ invitation_link }}</a>
            </p>
        </div>

        <div class="footer">
            <p>Cet email a été envoyé par ChantierPlus.</p>
        </div>
    </body>
    </html>
    """

    template = Template(html_template)
    html_content = template.render(
        company_name=company_name,
        invitation_link=invitation_link
    )

    subject = f"Invitation à rejoindre {company_name} sur ChantierPlus"

    await send_email(email, subject, html_content)

    logger.info(f"Invitation email sent to {email} for company {company_name}")
    return True


async def send_password_reset_email(email: str, token: str):
    """
    Send a password reset email.
    """
    reset_link = f"{FRONTEND_URL}/reset-password?token={token}"

    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }
            .header {
                background-color: #f59e0b;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 5px 5px 0 0;
            }
            .content {
                background-color: #f9fafb;
                padding: 30px;
                border: 1px solid #e5e7eb;
            }
            .button {
                display: inline-block;
                padding: 12px 24px;
                background-color: #f59e0b;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin: 20px 0;
            }
            .footer {
                text-align: center;
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #e5e7eb;
                color: #6b7280;
                font-size: 14px;
            }
            .warning {
                background-color: #fef3c7;
                border-left: 4px solid #f59e0b;
                padding: 15px;
                margin: 20px 0;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Réinitialisation de mot de passe</h1>
        </div>

        <div class="content">
            <p>Bonjour,</p>
            <p>Vous avez demandé une réinitialisation de votre mot de passe sur ChantierPlus.</p>
            <p>Cliquez sur le bouton ci-dessous pour définir un nouveau mot de passe :</p>

            <p style="text-align: center;">
                <a href="{{ reset_link }}" class="button">
                    Réinitialiser mon mot de passe
                </a>
            </p>

            <div class="warning">
                <strong>⚠️ Important :</strong> Ce lien expirera dans 1 heure.
            </div>

            <p style="color: #6b7280; font-size: 14px;">
                Si vous n'avez pas fait cette demande, ignorez cet email. Votre mot de passe restera inchangé.
            </p>

            <p style="color: #6b7280; font-size: 14px;">
                Si vous ne pouvez pas cliquer sur le bouton, copiez et collez ce lien dans votre navigateur :
                <br>
                <a href="{{ reset_link }}">{{ reset_link }}</a>
            </p>
        </div>

        <div class="footer">
            <p>Cet email a été envoyé par ChantierPlus.</p>
        </div>
    </body>
    </html>
    """

    template = Template(html_template)
    html_content = template.render(reset_link=reset_link)

    subject = "Réinitialisation de votre mot de passe ChantierPlus"

    await send_email(email, subject, html_content)

    logger.info(f"Password reset email sent to {email}")
    return True
