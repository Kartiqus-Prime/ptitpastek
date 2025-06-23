from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_email_with_template(subject, template_name, context, recipient_list, from_email=None):
    """
    Fonction utilitaire pour envoyer des emails avec template HTML
    """
    if from_email is None:
        from_email = settings.DEFAULT_FROM_EMAIL
    
    try:
        # Render HTML email
        html_message = render_to_string(template_name, context)
        
        # Create plain text version
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=from_email,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Email envoyé avec succès à {recipient_list}")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'email: {e}")
        return False

def send_admin_notification(subject, message, context=None):
    """
    Envoie une notification aux administrateurs
    """
    admin_emails = [settings.COMPANY_EMAIL]
    
    if context:
        html_message = render_to_string('emails/admin_notification.html', context)
        plain_message = strip_tags(html_message)
    else:
        html_message = None
        plain_message = message
    
    try:
        send_mail(
            subject=f"[{settings.COMPANY_NAME}] {subject}",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=admin_emails,
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de notification admin: {e}")
        return False