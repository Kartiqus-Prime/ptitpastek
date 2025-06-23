from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from products.models import Product, Category
from orders.utils import send_contact_confirmation_email, send_admin_contact_notification
import logging

logger = logging.getLogger(__name__)


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get featured products
        featured_products = Product.objects.filter(
            is_featured=True, 
            is_active=True
        ).select_related().prefetch_related('categories')[:8]
        
        # Get new products
        new_products = Product.objects.filter(
            is_new=True, 
            is_active=True
        ).select_related().prefetch_related('categories')[:4]
        
        # Get categories
        categories = Category.objects.filter(
            is_active=True, 
            parent=None
        )[:6]
        
        context.update({
            'featured_products': featured_products,
            'new_products': new_products,
            'categories': categories,
        })
        
        return context


class AboutView(TemplateView):
    template_name = 'about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add some statistics or company info
        context.update({
            'company_founded': 2018,
            'products_count': Product.objects.filter(is_active=True).count(),
            'team_size': 12,
        })
        
        return context


class ContactView(TemplateView):
    template_name = 'contact.html'

    def post(self, request, *args, **kwargs):
        # Get form data
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()
        
        # Basic validation
        if not all([name, email, subject, message]):
            messages.error(request, 'Tous les champs sont obligatoires.')
            return self.get(request, *args, **kwargs)
        
        # Email validation
        if '@' not in email or '.' not in email:
            messages.error(request, 'Veuillez saisir une adresse email valide.')
            return self.get(request, *args, **kwargs)
        
        try:
            # Send confirmation email to user
            user_email_sent = send_contact_confirmation_email(name, email, subject, message)
            
            # Send notification email to admin
            admin_email_sent = send_admin_contact_notification(name, email, subject, message)
            
            if user_email_sent or admin_email_sent:
                messages.success(request, 'Votre message a été envoyé avec succès ! Nous vous répondrons dans les plus brefs délais.')
            else:
                messages.warning(request, 'Votre message a été reçu mais il y a eu un problème avec l\'envoi de l\'email de confirmation.')
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement du formulaire de contact: {e}")
            messages.error(request, 'Une erreur est survenue lors de l\'envoi de votre message. Veuillez réessayer.')
        
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Pre-fill form if user is authenticated
        if self.request.user.is_authenticated:
            context.update({
                'user_name': self.request.user.get_full_name(),
                'user_email': self.request.user.email,
            })
        
        return context


@require_http_methods(["GET"])
def search_suggestions(request):
    """API endpoint for search suggestions"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    # Search in products
    products = Product.objects.filter(
        name__icontains=query,
        is_active=True
    ).values('name', 'slug')[:5]
    
    # Search in categories
    categories = Category.objects.filter(
        name__icontains=query,
        is_active=True
    ).values('name', 'slug')[:3]
    
    suggestions = {
        'products': list(products),
        'categories': list(categories),
    }
    
    return JsonResponse({'suggestions': suggestions})