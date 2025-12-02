import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
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
print(f"🔧 SMTP Configuration loaded: {SMTP_HOST}:{SMTP_PORT} from {SMTP_FROM_EMAIL}")


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
            else:
                attachment = MIMEText(file_data, "base64")
                attachment.add_header("Content-Disposition", f"attachment; filename={filename}")
            message.attach(attachment)

    # Send email
    try:
        logger.info(f"📧 Sending email to {to_email} via {SMTP_HOST}:{SMTP_PORT}")
        print(f"📧 Attempting to send email to {to_email}...")

        await aiosmtplib.send(
            message,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            username=SMTP_USERNAME,
            password=SMTP_PASSWORD,
            start_tls=True,
        )

        logger.info(f"✅ Email sent successfully to {to_email}")
        print(f"✅ Email sent successfully to {to_email}")
        return True
    except Exception as e:
        error_msg = f"❌ Error sending email to {to_email}: {e}"
        logger.error(error_msg)
        print(error_msg)
        raise


async def send_avenant_email(
    to_email: str,
    chantier_name: str,
    avenant_description: str,
    total_ht: float,
    avenant_type: str,
    avenant_id: str,
    company_name: str,
    photo_path: Optional[str] = None,
    signature_data: Optional[str] = None
):
    """
    Send an avenant email to the client
    """
    # HTML template for the email
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
            .detail-row {
                margin: 15px 0;
                padding: 10px;
                background-color: white;
                border-radius: 5px;
            }
            .label {
                font-weight: bold;
                color: #6b7280;
            }
            .value {
                color: #111827;
                font-size: 16px;
            }
            .total {
                background-color: #fef3c7;
                padding: 15px;
                border-radius: 5px;
                font-size: 20px;
                font-weight: bold;
                text-align: center;
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
            .button {
                display: inline-block;
                padding: 12px 24px;
                background-color: #f59e0b;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin: 20px 0;
            }
            .signature {
                max-width: 300px;
                border: 1px solid #e5e7eb;
                border-radius: 5px;
                padding: 10px;
                margin: 20px auto;
                display: block;
            }
            .photo {
                max-width: 100%;
                border-radius: 5px;
                margin: 20px 0;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Nouvel Avenant</h1>
        </div>

        <div class="content">
            <p>Bonjour,</p>
            <p>Un nouvel avenant a été créé et signé pour le chantier <strong>{{ chantier_name }}</strong>.</p>

            <div class="detail-row">
                <div class="label">Description des travaux :</div>
                <div class="value">{{ avenant_description }}</div>
            </div>

            <div class="detail-row">
                <div class="label">Type :</div>
                <div class="value">{{ avenant_type }}</div>
            </div>

            <div class="total">
                Total HT : {{ "%.2f"|format(total_ht) }} €
            </div>

            {% if has_photo %}
            <div class="detail-row">
                <div class="label">Photo jointe :</div>
                <p style="color: #6b7280; font-size: 14px;">Voir la pièce jointe de cet email.</p>
            </div>
            {% endif %}

            {% if has_signature %}
            <div class="detail-row">
                <div class="label">Signature du client :</div>
                <img src="data:image/png;base64,{{ signature_b64 }}" class="signature" alt="Signature" />
            </div>
            {% endif %}

            <p style="text-align: center;">
                <a href="{{ frontend_url }}/avenant/{{ avenant_id }}" class="button">
                    Voir l'avenant
                </a>
            </p>
        </div>

        <div class="footer">
            <p>Cet email a été envoyé par {{ company_name }} via ChantierPlus.</p>
            <p>ID Avenant : {{ avenant_id }}</p>
        </div>
    </body>
    </html>
    """

    template = Template(html_template)

    # Extract base64 data from signature if present
    signature_b64 = None
    if signature_data and signature_data.startswith("data:image"):
        signature_b64 = signature_data.split(",")[1]

    html_content = template.render(
        chantier_name=chantier_name,
        avenant_description=avenant_description,
        total_ht=total_ht,
        avenant_type=avenant_type,
        avenant_id=avenant_id,
        company_name=company_name,
        frontend_url=FRONTEND_URL,
        has_photo=photo_path is not None,
        has_signature=signature_data is not None,
        signature_b64=signature_b64
    )

    # Prepare attachments
    attachments = []
    if photo_path and os.path.exists(photo_path):
        with open(photo_path, "rb") as f:
            photo_data = f.read()
            photo_ext = Path(photo_path).suffix.lower()
            mime_type = {
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".png": "image/png",
                ".gif": "image/gif",
                ".webp": "image/webp"
            }.get(photo_ext, "image/jpeg")
            attachments.append((f"photo{photo_ext}", photo_data, mime_type))

    subject = f"Nouvel Avenant - {chantier_name}"

    await send_email(to_email, subject, html_content, attachments if attachments else None)


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
