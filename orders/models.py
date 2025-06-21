from django.db import models
from django.conf import settings
from django.utils import timezone
from products.models import Product
from accounts.models import Address
import uuid


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('confirmed', 'Confirmée'),
        ('processing', 'En préparation'),
        ('shipped', 'Expédiée'),
        ('delivered', 'Livrée'),
        ('cancelled', 'Annulée'),
        ('refunded', 'Remboursée'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('paid', 'Payée'),
        ('failed', 'Échouée'),
        ('refunded', 'Remboursée'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cash_on_delivery', 'Paiement à la livraison'),
        ('mobile_money', 'Mobile Money'),
        ('bank_transfer', 'Virement bancaire'),
    ]

    # Order identification
    order_number = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    
    # Order status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash_on_delivery')
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=0, default=0)  # FCFA sans décimales
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    
    # Shipping information
    shipping_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    shipping_name = models.CharField(max_length=255)
    shipping_phone = models.CharField(max_length=20, blank=True)
    shipping_address_line1 = models.CharField(max_length=255)
    shipping_address_line2 = models.CharField(max_length=255, blank=True)
    shipping_city = models.CharField(max_length=100)
    shipping_postal_code = models.CharField(max_length=10, blank=True)
    shipping_country = models.CharField(max_length=100, default='Cameroun')
    
    # Billing information (if different from shipping)
    billing_name = models.CharField(max_length=255, blank=True)
    billing_address_line1 = models.CharField(max_length=255, blank=True)
    billing_address_line2 = models.CharField(max_length=255, blank=True)
    billing_city = models.CharField(max_length=100, blank=True)
    billing_postal_code = models.CharField(max_length=10, blank=True)
    billing_country = models.CharField(max_length=100, blank=True)
    
    # Additional information
    notes = models.TextField(blank=True)
    tracking_number = models.CharField(max_length=100, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"
        ordering = ['-created_at']

    def __str__(self):
        return f"Commande #{self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)

    def generate_order_number(self):
        """Generate a unique order number"""
        timestamp = timezone.now().strftime('%Y%m%d')
        unique_id = str(uuid.uuid4())[:8].upper()
        return f"LP{timestamp}{unique_id}"

    @property
    def can_be_cancelled(self):
        return self.status in ['pending', 'confirmed']

    @property
    def is_paid(self):
        return self.payment_status == 'paid'

    def get_total_items(self):
        return sum(item.quantity for item in self.items.all())

    def format_price(self, amount):
        """Format price with FCFA currency"""
        return f"{int(amount):,} FCFA".replace(',', ' ')

    @property
    def formatted_total(self):
        return self.format_price(self.total_amount)

    @property
    def formatted_subtotal(self):
        return self.format_price(self.subtotal)

    @property
    def formatted_shipping(self):
        return self.format_price(self.shipping_cost)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)  # Store product name at time of order
    product_price = models.DecimalField(max_digits=10, decimal_places=0, default=0)  # Store price at time of order
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=0, default=0)

    class Meta:
        verbose_name = "Article de commande"
        verbose_name_plural = "Articles de commande"

    def __str__(self):
        return f"{self.quantity}x {self.product_name}"

    def save(self, *args, **kwargs):
        if not self.product_name:
            self.product_name = self.product.name
        if not self.product_price:
            self.product_price = self.product.price
        self.total_price = self.quantity * self.product_price
        super().save(*args, **kwargs)

    def format_price(self, amount):
        """Format price with FCFA currency"""
        return f"{int(amount):,} FCFA".replace(',', ' ')

    @property
    def formatted_total(self):
        return self.format_price(self.total_price)

    @property
    def formatted_unit_price(self):
        return self.format_price(self.product_price)


class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Historique de statut"
        verbose_name_plural = "Historiques de statut"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.order.order_number} - {self.get_status_display()}"