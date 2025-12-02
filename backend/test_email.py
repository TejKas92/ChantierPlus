"""
Script de test pour vérifier la configuration SMTP et envoyer un email de test.
"""
import asyncio
import sys
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Print configuration
print("=" * 50)
print("TEST DE CONFIGURATION SMTP")
print("=" * 50)
print(f"SMTP_HOST: {os.getenv('SMTP_HOST')}")
print(f"SMTP_PORT: {os.getenv('SMTP_PORT')}")
print(f"SMTP_USERNAME: {os.getenv('SMTP_USERNAME')}")
print(f"SMTP_PASSWORD: {'*' * len(os.getenv('SMTP_PASSWORD', ''))}")
print(f"SMTP_FROM_EMAIL: {os.getenv('SMTP_FROM_EMAIL')}")
print(f"SMTP_FROM_NAME: {os.getenv('SMTP_FROM_NAME')}")
print("=" * 50)

# Import after loading env
from app.email import send_email

async def test_send_email():
    """Send a test email"""
    to_email = input("\nEntrez l'adresse email de destination pour le test: ")

    if not to_email:
        print("❌ Adresse email requise")
        return

    html_content = """
    <html>
    <body>
        <h1>Email de Test - ChantierPlus</h1>
        <p>Ceci est un email de test pour vérifier la configuration SMTP.</p>
        <p>Si vous recevez cet email, la configuration est correcte !</p>
    </body>
    </html>
    """

    try:
        print(f"\n📧 Envoi de l'email de test à {to_email}...")
        await send_email(
            to_email=to_email,
            subject="Test - ChantierPlus",
            html_content=html_content
        )
        print("\n✅ Email envoyé avec succès !")
        print(f"Vérifiez la boîte de réception de {to_email}")
    except Exception as e:
        print(f"\n❌ Erreur lors de l'envoi: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_send_email())
