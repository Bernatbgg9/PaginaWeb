import smtplib
from email.message import EmailMessage
import os

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "bernatbgg9@gmail.com"        # <-- Tu correo
SMTP_PASS = "flki qegy ukcg yuge"         # <-- Contraseña de app
PDF_FOLDER = "ebooks"                     # Carpeta donde guardas los PDFs

def send_confirmation_email(email: str, cart: list):
    msg = EmailMessage()
    msg["Subject"] = "📚 Confirmación de tu pedido"
    msg["From"] = SMTP_USER
    msg["To"] = email

    # ✅ Texto plano de respaldo
    resumen = "Gracias por tu compra. Este es el resumen de tu pedido:\n\n"
    for item in cart:
        resumen += f"- {item['name']} x{item.get('quantity', 1)} - {item['price']} €\n"
    msg.set_content(resumen)

    # ✅ HTML bonito con imagen
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
        <div style="max-width: 600px; margin: auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
            <div style="background: #4CAF50; color: white; padding: 20px; text-align: center;">
                <h1>Gracias por tu pedido 📚</h1>
            </div>
            <div style="padding: 20px;">
                <p style="font-size: 16px;">Hola,</p>
                <p style="font-size: 16px;">Aquí tienes el resumen de tu pedido:</p>
                <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
                    <thead>
                        <tr style="background-color: #f0f0f0;">
                            <th style="padding: 10px; text-align: left; border-bottom: 1px solid #ddd;">Producto</th>
                            <th style="padding: 10px; text-align: left; border-bottom: 1px solid #ddd;">Precio</th>
                            <th style="padding: 10px; text-align: center; border-bottom: 1px solid #ddd;">Imagen</th>
                        </tr>
                    </thead>
                    <tbody>
    """

    for item in cart:
        html += f"""
        <tr>
            <td style="padding: 10px; border-bottom: 1px solid #eee;">{item['name']}</td>
            <td style="padding: 10px; border-bottom: 1px solid #eee;">{item['price']} €</td>
            <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: center;">
                <img src="{item['image_url']}" alt="{item['name']}" width="60" style="border-radius: 5px;" />
            </td>
        </tr>
        """

    html += f"""
                    </tbody>
                </table>
                <p style="font-size: 16px; margin-top: 30px;">📎 Los archivos PDF están adjuntos a este correo.</p>
            </div>
            <div style="background: #f9f9f9; padding: 15px; text-align: center; font-size: 13px; color: #666;">
                Este correo ha sido generado automáticamente. Si tienes dudas, contáctanos en <a href="mailto:{SMTP_USER}">{SMTP_USER}</a>.
            </div>
        </div>
    </body>
    </html>
    """
    msg.add_alternative(html, subtype="html")

    # ✅ Adjuntar PDFs si existen
    for item in cart:
        pdf_path = os.path.join(PDF_FOLDER, f"{item['id']}.pdf")
        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                msg.add_attachment(
                    f.read(),
                    maintype="application",
                    subtype="pdf",
                    filename=f"{item['name']}.pdf"
                )
        else:
            print(f"[ADVERTENCIA] No se encontró el PDF: {pdf_path}")

    # ✅ Enviar el correo usando SMTP con TLS
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
        print(f"✅ Email enviado a {email}")
