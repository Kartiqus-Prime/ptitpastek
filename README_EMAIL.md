# Configuration des Emails - La P'tit Pastèk

## Configuration actuelle

Le système d'email est configuré pour fonctionner en mode développement et production :

### Mode Développement
- Les emails sont affichés dans la console Django
- Aucune configuration SMTP requise
- Parfait pour tester les templates d'emails

### Mode Production
- Configuration SMTP avec Gmail ou Brevo
- Emails HTML avec templates personnalisés
- Gestion des erreurs et logging

## Types d'emails envoyés

1. **Email de bienvenue** - Lors de l'inscription d'un nouvel utilisateur
2. **Confirmation de commande** - Après validation d'une commande
3. **Mise à jour de commande** - Changement de statut de commande
4. **Confirmation de contact** - Après envoi du formulaire de contact
5. **Notification admin** - Nouveau message de contact reçu
6. **Réinitialisation de mot de passe** - Système Django intégré

## Configuration pour la production

### Option 1: Gmail
1. Créer un mot de passe d'application Gmail
2. Configurer les variables d'environnement :
```bash
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe-application
```

### Option 2: Brevo (ex-Sendinblue)
1. Créer un compte Brevo
2. Générer une clé API SMTP
3. Configurer les variables d'environnement :
```bash
BREVO_EMAIL=votre-email@domaine.com
BREVO_API_KEY=votre-cle-api-brevo
```

## Templates d'emails

Tous les templates sont dans `templates/emails/` :
- `base_email.html` - Template de base avec le design La P'tit Pastèk
- `welcome.html` - Email de bienvenue
- `order_confirmation.html` - Confirmation de commande
- `order_status_update.html` - Mise à jour de commande
- `contact_confirmation.html` - Confirmation de contact
- `contact_admin_notification.html` - Notification admin

## Fonctionnalités

- ✅ Templates HTML responsive
- ✅ Version texte automatique
- ✅ Gestion des erreurs
- ✅ Logging des envois
- ✅ Design cohérent avec la marque
- ✅ Support mode sombre
- ✅ Emojis et illustrations

## Test des emails

En mode développement, tous les emails apparaissent dans la console Django. Vous pouvez :
1. Créer un compte utilisateur
2. Passer une commande
3. Envoyer un message via le formulaire de contact
4. Changer le statut d'une commande dans l'admin

## Dépannage

Si les emails ne s'envoient pas :
1. Vérifiez les logs Django
2. Vérifiez la configuration SMTP
3. Vérifiez que les templates existent
4. Testez avec `python manage.py shell` :

```python
from django.core.mail import send_mail
send_mail(
    'Test',
    'Message de test',
    'from@example.com',
    ['to@example.com'],
    fail_silently=False,
)
```