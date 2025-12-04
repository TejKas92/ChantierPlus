"""
PDF generation for avenants using WeasyPrint
"""
from weasyprint import HTML, CSS
from jinja2 import Template
import base64
from pathlib import Path
from typing import Optional
import os

def generate_avenant_pdf(
    avenant_id: str,
    chantier_name: str,
    chantier_address: str,
    description: str,
    avenant_type: str,
    total_ht: float,
    photo_path: Optional[str],
    signature_path: Optional[str],
    company_name: str,
    created_at: str,
    price: Optional[float] = None,
    hours: Optional[float] = None,
    hourly_rate: Optional[float] = None
) -> str:
    """
    Generate a PDF for an avenant

    Returns:
        Path to the generated PDF file
    """

    # Read and encode images as base64
    photo_base64 = None
    if photo_path and os.path.exists(photo_path):
        with open(photo_path, "rb") as f:
            photo_data = f.read()
            photo_base64 = base64.b64encode(photo_data).decode()

    signature_base64 = None
    if signature_path and os.path.exists(signature_path):
        with open(signature_path, "rb") as f:
            signature_data = f.read()
            signature_base64 = base64.b64encode(signature_data).decode()

    # HTML template for the PDF
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @page {
                size: A4;
                margin: 2cm;
            }
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }
            .header {
                text-align: center;
                margin-bottom: 30px;
                padding-bottom: 20px;
                border-bottom: 3px solid #f59e0b;
            }
            .header h1 {
                color: #f59e0b;
                margin: 0;
                font-size: 28px;
            }
            .company-info {
                background-color: #f9fafb;
                padding: 15px;
                margin-bottom: 20px;
                border-left: 4px solid #f59e0b;
            }
            .section {
                margin-bottom: 25px;
            }
            .section-title {
                font-size: 18px;
                font-weight: bold;
                color: #f59e0b;
                margin-bottom: 10px;
                border-bottom: 2px solid #f59e0b;
                padding-bottom: 5px;
            }
            .detail-row {
                padding: 8px 0;
                border-bottom: 1px solid #e5e7eb;
            }
            .label {
                font-weight: bold;
                color: #6b7280;
                display: inline-block;
                width: 150px;
            }
            .value {
                color: #111827;
            }
            .total-box {
                background-color: #fef3c7;
                padding: 20px;
                text-align: center;
                font-size: 24px;
                font-weight: bold;
                margin: 20px 0;
                border: 2px solid #f59e0b;
                border-radius: 5px;
            }
            .photo {
                max-width: 100%;
                max-height: 400px;
                display: block;
                margin: 20px auto;
                border: 1px solid #e5e7eb;
                border-radius: 5px;
            }
            .signature {
                max-width: 300px;
                max-height: 150px;
                display: block;
                margin: 20px auto;
                border: 1px solid #e5e7eb;
                padding: 10px;
                background-color: white;
            }
            .footer {
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                text-align: center;
                font-size: 10px;
                color: #6b7280;
                padding: 10px;
                border-top: 1px solid #e5e7eb;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 15px 0;
            }
            td {
                padding: 8px;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>AVENANT DE TRAVAUX</h1>
            <p style="margin: 5px 0;">{{ company_name }}</p>
            <p style="margin: 5px 0; font-size: 12px; color: #6b7280;">Document généré le {{ created_at }}</p>
        </div>

        <div class="company-info">
            <strong>Chantier :</strong> {{ chantier_name }}<br>
            <strong>Adresse :</strong> {{ chantier_address }}
        </div>

        <div class="section">
            <div class="section-title">Informations Générales</div>
            <div class="detail-row">
                <span class="label">ID Avenant :</span>
                <span class="value">{{ avenant_id }}</span>
            </div>
            <div class="detail-row">
                <span class="label">Type :</span>
                <span class="value">{{ avenant_type }}</span>
            </div>
            <div class="detail-row">
                <span class="label">Date :</span>
                <span class="value">{{ created_at }}</span>
            </div>
        </div>

        <div class="section">
            <div class="section-title">Description des Travaux</div>
            <p style="padding: 10px; background-color: #f9fafb; border-radius: 5px;">
                {{ description }}
            </p>
        </div>

        <div class="section">
            <div class="section-title">Détails Financiers</div>
            {% if avenant_type == "FORFAIT" %}
            <div class="detail-row">
                <span class="label">Montant Forfaitaire :</span>
                <span class="value">{{ "%.2f"|format(price) }} € HT</span>
            </div>
            {% else %}
            <div class="detail-row">
                <span class="label">Nombre d'heures :</span>
                <span class="value">{{ "%.2f"|format(hours) }}</span>
            </div>
            <div class="detail-row">
                <span class="label">Taux horaire :</span>
                <span class="value">{{ "%.2f"|format(hourly_rate) }} € HT</span>
            </div>
            {% endif %}
        </div>

        <div class="total-box">
            Total HT : {{ "%.2f"|format(total_ht) }} €
        </div>

        {% if photo_base64 %}
        <div class="section">
            <div class="section-title">Photo des Travaux</div>
            <img src="data:image/png;base64,{{ photo_base64 }}" class="photo" alt="Photo des travaux">
        </div>
        {% endif %}

        {% if signature_base64 %}
        <div class="section">
            <div class="section-title">Signature du Client</div>
            <img src="data:image/png;base64,{{ signature_base64 }}" class="signature" alt="Signature">
            <p style="text-align: center; color: #6b7280; font-size: 12px;">
                Document signé le {{ created_at }}
            </p>
        </div>
        {% endif %}

        <div class="footer">
            <p>Document généré par ChantierPlus - {{ company_name }}</p>
            <p>ID: {{ avenant_id }}</p>
        </div>
    </body>
    </html>
    """

    template = Template(html_template)
    html_content = template.render(
        avenant_id=avenant_id,
        chantier_name=chantier_name,
        chantier_address=chantier_address,
        description=description,
        avenant_type=avenant_type,
        total_ht=total_ht,
        photo_base64=photo_base64,
        signature_base64=signature_base64,
        company_name=company_name,
        created_at=created_at,
        price=price,
        hours=hours,
        hourly_rate=hourly_rate
    )

    # Generate PDF
    pdf_filename = f"{avenant_id}.pdf"
    pdf_path = f"uploads/{pdf_filename}"

    # Create uploads directory if it doesn't exist
    os.makedirs("uploads", exist_ok=True)

    # Generate PDF from HTML
    HTML(string=html_content).write_pdf(pdf_path)

    return pdf_path
