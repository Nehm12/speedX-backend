import os
import smtplib
import ssl
from dotenv import load_dotenv

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.utils.logs import logger

load_dotenv()

FRONTEND_URL = os.getenv("FRONTEND_URL")

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_username)
        self.from_name = os.getenv("FROM_NAME", "Fluxy")
        
    def is_configured(self) -> bool:
        """Vérifie si le service email est configuré"""
        return bool(self.smtp_username and self.smtp_password)
    
    async def send_password_reset_email(self, email: str, token: str, base_url: str = FRONTEND_URL) -> bool:
        """
        Envoie un email de réinitialisation de mot de passe
        """
        if not self.is_configured():
            logger.warning("Service email non configuré - impossible d'envoyer l'email")
            return False
        
        reset_url = f"{base_url}/reset-password?token={token}"
        
        # Template HTML pour l'email
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Réinitialisation de mot de passe - Fluxy</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: #2563eb; text-align: center;">Fluxy</h1>
                <h2>Réinitialisation de mot de passe</h2>
                <p>Bonjour,</p>
                <p>Vous avez demandé la réinitialisation de votre mot de passe pour votre compte Fluxy.</p>
                <p>Cliquez sur le lien ci-dessous pour créer un nouveau mot de passe :</p>
                <p style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}" style="background-color: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">
                        Réinitialiser mon mot de passe
                    </a>
                </p>
                <p><strong>Ce lien expire dans 1 heure.</strong></p>
                <p>Si vous n'avez pas demandé cette réinitialisation, vous pouvez ignorer cet email.</p>
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
                <p style="font-size: 12px; color: #666;">
                    Cet email a été envoyé automatiquement, merci de ne pas y répondre.
                </p>
            </div>
        </body>
        </html>
        """
        
        # Version texte simple
        text_content = f"""
        Réinitialisation de mot de passe - Fluxy
        
        Bonjour,
        
        Vous avez demandé la réinitialisation de votre mot de passe pour votre compte Fluxy.
        
        Copiez et collez ce lien dans votre navigateur pour créer un nouveau mot de passe :
        {reset_url}
        
        Ce lien expire dans 1 heure.
        
        Si vous n'avez pas demandé cette réinitialisation, vous pouvez ignorer cet email.
        """
        
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = "Réinitialisation de mot de passe - Fluxy"
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = email
            
            text_part = MIMEText(text_content, "plain", "utf-8")
            html_part = MIMEText(html_content, "html", "utf-8")
            
            message.attach(text_part)
            message.attach(html_part)
            
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(message)
            
            logger.info(f"Email de réinitialisation envoyé avec succès à {email}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de l'email à {email}: {str(e)}")
            return False

email_service = EmailService()
