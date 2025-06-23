from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_order_confirmation_email(order):
    """Send order confirmation email with HTML template"""
    subject = f'Confirmation de commande #{order.order_number} - La P\'tit Pastèk'
    
    try:
        # Render HTML email
        html_message = render_to_string('emails/order_confirmation.html', {
            'order': order,
            'user': order.user,
        })
        
        # Create plain text version
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Email de confirmation de commande envoyé à {order.user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'email de confirmation: {e}")
        return False


def send_order_status_update_email(order):
    """Send order status update email with HTML template"""
    subject = f'Mise à jour de votre commande #{order.order_number} - La P\'tit Pastèk'
    
    try:
        # Render HTML email
        html_message = render_to_string('emails/order_status_update.html', {
            'order': order,
            'user': order.user,
        })
        
        # Create plain text version
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Email de mise à jour de commande envoyé à {order.user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'email de mise à jour: {e}")
        return False


def send_welcome_email(user):
    """Send welcome email to new users"""
    subject = 'Bienvenue chez La P\'tit Pastèk !'
    
    try:
        # Render HTML email
        html_message = render_to_string('emails/welcome.html', {
            'user': user,
        })
        
        # Create plain text version
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Email de bienvenue envoyé à {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'email de bienvenue: {e}")
        return False


def send_contact_confirmation_email(name, email, subject_text, message):
    """Send contact form confirmation email"""
    subject = 'Merci pour votre message - La P\'tit Pastèk'
    
    try:
        # Render HTML email
        html_message = render_to_string('emails/contact_confirmation.html', {
            'name': name,
            'email': email,
            'subject': subject_text,
            'message': message,
        })
        
        # Create plain text version
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Email de confirmation de contact envoyé à {email}")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'email de confirmation de contact: {e}")
        return False


def send_admin_contact_notification(name, email, subject_text, message):
    """Send contact form notification to admin"""
    admin_subject = f"[La P'tit Pastèk] Nouveau message de contact - {subject_text}"
    
    try:
        # Render HTML email
        html_message = render_to_string('emails/contact_admin_notification.html', {
            'name': name,
            'email': email,
            'subject': subject_text,
            'message': message,
        })
        
        # Create plain text version
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=admin_subject,
            message=plain_message,
            from_email=email,  # Reply-to sera l'email du contact
            recipient_list=[settings.COMPANY_EMAIL],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Notification admin de contact envoyée pour {email}")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de la notification admin: {e}")
        return False