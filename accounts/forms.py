from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from .models import User, Address


class CustomUserCreationForm(UserCreationForm):
    full_name = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full h-11 sm:h-12 border border-watermelon-red/30 focus:border-watermelon-green dark:border-gray-600 dark:focus:border-watermelon-green rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-watermelon-green/20',
            'placeholder': 'Votre nom complet'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full h-11 sm:h-12 border border-watermelon-red/30 focus:border-watermelon-green dark:border-gray-600 dark:focus:border-watermelon-green rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-watermelon-green/20',
            'placeholder': 'votre@email.com'
        })
    )

    class Meta:
        model = User
        fields = ('full_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'w-full h-11 sm:h-12 border border-watermelon-red/30 focus:border-watermelon-green dark:border-gray-600 dark:focus:border-watermelon-green rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-watermelon-green/20',
            'placeholder': '••••••••'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'w-full h-11 sm:h-12 border border-watermelon-red/30 focus:border-watermelon-green dark:border-gray-600 dark:focus:border-watermelon-green rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-watermelon-green/20',
            'placeholder': '••••••••'
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['email']
        user.full_name = self.cleaned_data['full_name']
        if commit:
            user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full h-11 sm:h-12 border border-watermelon-red/30 focus:border-watermelon-green dark:border-gray-600 dark:focus:border-watermelon-green rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-watermelon-green/20',
            'placeholder': 'votre@email.com'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full h-11 sm:h-12 border border-watermelon-red/30 focus:border-watermelon-green dark:border-gray-600 dark:focus:border-watermelon-green rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-watermelon-green/20',
            'placeholder': '••••••••'
        })
    )


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['full_name', 'email', 'phone', 'avatar']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-watermelon-red/20 bg-white dark:bg-gray-700 text-gray-900 dark:text-white'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-watermelon-red/20 bg-white dark:bg-gray-700 text-gray-900 dark:text-white'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-watermelon-red/20 bg-white dark:bg-gray-700 text-gray-900 dark:text-white'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-watermelon-red/20 bg-white dark:bg-gray-700 text-gray-900 dark:text-white'
            }),
        }


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['name', 'address_line1', 'address_line2', 'city', 'postal_code', 'country', 'type', 'is_default']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-watermelon-red/20 bg-white dark:bg-gray-700 text-gray-900 dark:text-white'
            }),
            'address_line1': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-watermelon-red/20 bg-white dark:bg-gray-700 text-gray-900 dark:text-white'
            }),
            'address_line2': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-watermelon-red/20 bg-white dark:bg-gray-700 text-gray-900 dark:text-white'
            }),
            'city': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-watermelon-red/20 bg-white dark:bg-gray-700 text-gray-900 dark:text-white'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-watermelon-red/20 bg-white dark:bg-gray-700 text-gray-900 dark:text-white'
            }),
            'country': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-watermelon-red/20 bg-white dark:bg-gray-700 text-gray-900 dark:text-white'
            }),
            'type': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-watermelon-red/20 bg-white dark:bg-gray-700 text-gray-900 dark:text-white'
            }),
        }