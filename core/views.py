from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from products.models import Product, Category


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


class ContactView(TemplateView):
    template_name = 'contact.html'

    def post(self, request, *args, **kwargs):
        # Get form data
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        subject = request.POST.get('subject', '')
        message = request.POST.get('message', '')
        
        # Basic validation
        if not all([name, email, subject, message]):
            messages.error(request, 'Tous les champs sont obligatoires.')
            return self.get(request, *args, **kwargs)
        
        # Prepare email content
        email_subject = f"[La P'tit Pastèk] {subject}"
        email_message = f"""
        Nouveau message de contact:
        
        Nom: {name}
        Email: {email}
        Sujet: {subject}
        
        Message:
        {message}
        """
        
        try:
            # Send email (in production, configure proper email backend)
            send_mail(
                email_subject,
                email_message,
                email,
                ['contact@laptitpastek.fr'],  # Replace with actual email
                fail_silently=False,
            )
            
            messages.success(request, 'Votre message a été envoyé avec succès ! Nous vous répondrons dans les plus brefs délais.')
            
        except Exception as e:
            messages.error(request, 'Une erreur est survenue lors de l\'envoi de votre message. Veuillez réessayer.')
        
        return self.get(request, *args, **kwargs)