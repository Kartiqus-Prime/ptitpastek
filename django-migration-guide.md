
# Migration Guide: La P'tit Pastèk - React vers Django

## Vue d'ensemble du projet

La P'tit Pastèk est une application e-commerce spécialisée dans les produits à base de pastèque. Le projet React actuel utilise Supabase comme backend et comprend les fonctionnalités suivantes :

### Fonctionnalités principales

1. **Authentification utilisateur**
   - Inscription/Connexion
   - Gestion de profil
   - Mot de passe oublié
   - Gestion des adresses

2. **Catalogue produits**
   - Liste des produits
   - Détail produit
   - Catégories
   - Recherche et filtres

3. **E-commerce**
   - Panier d'achat
   - Processus de commande
   - Gestion des favoris
   - Historique des commandes

4. **Administration**
   - Gestion des produits
   - Gestion des utilisateurs
   - Gestion des commandes
   - Analytics

### Architecture Django recommandée

```
django_version/
├── manage.py
├── requirements.txt
├── laptitpastek/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── accounts/      # Gestion utilisateurs
│   ├── products/      # Catalogue produits
│   ├── orders/        # Commandes
│   ├── cart/          # Panier
│   └── core/          # Fonctionnalités communes
├── templates/
├── static/
│   ├── css/
│   ├── js/
│   └── images/
└── media/
```

## Modèles Django basés sur Supabase

### 1. Modèle User (accounts/models.py)
```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    full_name = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    zone = models.ForeignKey('Zone', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Address(models.Model):
    TYPE_CHOICES = [
        ('home', 'Domicile'),
        ('work', 'Travail'),
        ('other', 'Autre'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    name = models.CharField(max_length=255)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='home')
    is_default = models.BooleanField(default=False)
    zone = models.ForeignKey('Zone', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### 2. Modèles Produits (products/models.py)
```python
class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    full_description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='products/')
    additional_images = models.JSONField(default=list, blank=True)
    ingredients = models.JSONField(default=list, blank=True)
    nutrition_info = models.JSONField(default=dict, blank=True)
    is_new = models.BooleanField(default=False)
    in_stock = models.BooleanField(default=True)
    stock_quantity = models.IntegerField(default=0)
    categories = models.ManyToManyField(Category, through='ProductCategory')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## Configuration TailwindCSS

### 1. Installation
```bash
pip install django-tailwind
python manage.py tailwind install
```

### 2. Configuration settings.py
```python
INSTALLED_APPS = [
    'tailwind',
    'theme',  # votre app theme
    # ... autres apps
]

TAILWIND_APP_NAME = 'theme'
```

### Couleurs personnalisées (theme/static_src/tailwind.config.js)
```javascript
module.exports = {
  content: [
    '../templates/**/*.html',
    '../../templates/**/*.html',
    '../../**/templates/**/*.html',
  ],
  theme: {
    extend: {
      colors: {
        'watermelon-red': {
          DEFAULT: 'hsl(0, 85%, 65%)',
          light: 'hsl(0, 75%, 75%)',
          dark: 'hsl(0, 95%, 55%)',
        },
        'watermelon-green': {
          DEFAULT: 'hsl(140, 80%, 25%)',
          light: 'hsl(140, 60%, 35%)',
          dark: 'hsl(140, 90%, 15%)',
        },
        'watermelon-pink': 'hsl(350, 85%, 75%)',
        'watermelon-cream': 'hsl(45, 30%, 95%)',
        'brand-primary': 'hsl(0, 85%, 65%)',
        'brand-secondary': 'hsl(140, 80%, 25%)',
      }
    }
  }
}
```
