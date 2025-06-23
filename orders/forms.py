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
        label="Nom complet",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-watermelon-red/20',
            'placeholder': 'Nom complet'
        })
    )
    
    shipping_phone = forms.CharField(
        max_length=20,
        label="Téléphone",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-watermelon-red/20',
            'placeholder': '+237 6XX XX XX XX'
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
    
    # Payment method
    payment_method = forms.ChoiceField(
        choices=Order.PAYMENT_METHOD_CHOICES,
        initial='cash_on_delivery',
        label="Mode de paiement",
        widget=forms.RadioSelect(attrs={
            'class': 'text-watermelon-red focus:ring-watermelon-red'
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
        
        if user and user.is_authenticated:
            self.fields['shipping_address'].queryset = user.addresses.all()
            # Pre-fill with user data
            if user.get_full_name():
                self.fields['shipping_name'].initial = user.get_full_name()
            if user.phone:
                self.fields['shipping_phone'].initial = user.phone

    def clean_shipping_phone(self):
        phone = self.cleaned_data.get('shipping_phone')
        if phone and not phone.startswith('+237'):
            # Auto-format Cameroon phone numbers
            if phone.startswith('6') and len(phone) == 9:
                phone = f'+237 {phone}'
            elif phone.startswith('237'):
                phone = f'+{phone}'
        return phone