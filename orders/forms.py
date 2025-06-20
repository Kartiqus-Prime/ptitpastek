from django import forms
from .models import Order
from accounts.models import Address


class CheckoutForm(forms.Form):
    # Shipping address selection
    shipping_address = forms.ModelChoiceField(
        queryset=Address.objects.none(),
        required=False,
        empty_label="Nouvelle adresse",
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-watermelon-red/20'
        })
    )
    
    # Shipping details
    shipping_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-watermelon-red/20',
            'placeholder': 'Nom complet'
        })
    )
    
    shipping_address_line1 = forms.CharField(
        max_length=255,
        label="Adresse",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-watermelon-red/20',
            'placeholder': 'Numéro et nom de rue'
        })
    )
    
    shipping_address_line2 = forms.CharField(
        max_length=255,
        required=False,
        label="Complément d'adresse",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-watermelon-red/20',
            'placeholder': 'Appartement, étage, etc. (optionnel)'
        })
    )
    
    shipping_city = forms.CharField(
        max_length=100,
        label="Ville",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-watermelon-red/20',
            'placeholder': 'Ville'
        })
    )
    
    shipping_postal_code = forms.CharField(
        max_length=10,
        label="Code postal",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-watermelon-red/20',
            'placeholder': 'Code postal'
        })
    )
    
    shipping_country = forms.CharField(
        max_length=100,
        initial="France",
        label="Pays",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-watermelon-red/20'
        })
    )
    
    # Order notes
    notes = forms.CharField(
        required=False,
        label="Notes de commande",
        widget=forms.Textarea(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-watermelon-red/20',
            'rows': 3,
            'placeholder': 'Instructions de livraison, commentaires...'
        })
    )
    
    # Terms and conditions
    accept_terms = forms.BooleanField(
        required=True,
        label="J'accepte les conditions générales de vente",
        widget=forms.CheckboxInput(attrs={
            'class': 'rounded border-gray-300 text-watermelon-red focus:ring-watermelon-red'
        })
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['shipping_address'].queryset = user.addresses.all()