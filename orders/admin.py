from django.contrib import admin
from .models import Order, OrderItem, OrderStatusHistory
from .utils import send_order_status_update_email
import logging

logger = logging.getLogger(__name__)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('total_price',)


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ('created_at', 'created_by')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'status', 'payment_status', 'total_amount', 'created_at')
    list_filter = ('status', 'payment_status', 'created_at', 'updated_at')
    search_fields = ('order_number', 'user__email', 'user__full_name')
    readonly_fields = ('order_number', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    inlines = [OrderItemInline, OrderStatusHistoryInline]
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('order_number', 'user', 'status', 'payment_status')
        }),
        ('Montants', {
            'fields': ('subtotal', 'shipping_cost', 'tax_amount', 'total_amount')
        }),
        ('Adresse de livraison', {
            'fields': ('shipping_name', 'shipping_address_line1', 'shipping_address_line2', 
                      'shipping_city', 'shipping_postal_code', 'shipping_country')
        }),
        ('Adresse de facturation', {
            'fields': ('billing_name', 'billing_address_line1', 'billing_address_line2',
                      'billing_city', 'billing_postal_code', 'billing_country'),
            'classes': ('collapse',)
        }),
        ('Informations supplémentaires', {
            'fields': ('notes', 'tracking_number')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at', 'shipped_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_as_confirmed', 'mark_as_processing', 'mark_as_shipped', 'mark_as_delivered']

    def save_model(self, request, obj, form, change):
        """Override save to send email when status changes"""
        if change:
            # Get the original object to compare status
            original = Order.objects.get(pk=obj.pk)
            status_changed = original.status != obj.status
        else:
            status_changed = False
        
        super().save_model(request, obj, form, change)
        
        # Send email if status changed
        if status_changed:
            try:
                send_order_status_update_email(obj)
            except Exception as e:
                logger.error(f"Erreur lors de l'envoi de l'email de mise à jour: {e}")

    def mark_as_confirmed(self, request, queryset):
        updated_count = 0
        for order in queryset:
            if order.status != 'confirmed':
                order.status = 'confirmed'
                order.save()
                OrderStatusHistory.objects.create(
                    order=order,
                    status='confirmed',
                    notes='Statut mis à jour par l\'administrateur',
                    created_by=request.user
                )
                # Send email notification
                try:
                    send_order_status_update_email(order)
                except Exception as e:
                    logger.error(f"Erreur email pour commande {order.order_number}: {e}")
                updated_count += 1
        
        self.message_user(request, f'{updated_count} commande(s) marquée(s) comme confirmée(s).')
    mark_as_confirmed.short_description = "Marquer comme confirmée"

    def mark_as_processing(self, request, queryset):
        updated_count = 0
        for order in queryset:
            if order.status != 'processing':
                order.status = 'processing'
                order.save()
                OrderStatusHistory.objects.create(
                    order=order,
                    status='processing',
                    notes='Statut mis à jour par l\'administrateur',
                    created_by=request.user
                )
                # Send email notification
                try:
                    send_order_status_update_email(order)
                except Exception as e:
                    logger.error(f"Erreur email pour commande {order.order_number}: {e}")
                updated_count += 1
        
        self.message_user(request, f'{updated_count} commande(s) marquée(s) comme en préparation.')
    mark_as_processing.short_description = "Marquer comme en préparation"

    def mark_as_shipped(self, request, queryset):
        updated_count = 0
        for order in queryset:
            if order.status != 'shipped':
                order.status = 'shipped'
                order.save()
                OrderStatusHistory.objects.create(
                    order=order,
                    status='shipped',
                    notes='Statut mis à jour par l\'administrateur',
                    created_by=request.user
                )
                # Send email notification
                try:
                    send_order_status_update_email(order)
                except Exception as e:
                    logger.error(f"Erreur email pour commande {order.order_number}: {e}")
                updated_count += 1
        
        self.message_user(request, f'{updated_count} commande(s) marquée(s) comme expédiée(s).')
    mark_as_shipped.short_description = "Marquer comme expédiée"

    def mark_as_delivered(self, request, queryset):
        updated_count = 0
        for order in queryset:
            if order.status != 'delivered':
                order.status = 'delivered'
                order.save()
                OrderStatusHistory.objects.create(
                    order=order,
                    status='delivered',
                    notes='Statut mis à jour par l\'administrateur',
                    created_by=request.user
                )
                # Send email notification
                try:
                    send_order_status_update_email(order)
                except Exception as e:
                    logger.error(f"Erreur email pour commande {order.order_number}: {e}")
                updated_count += 1
        
        self.message_user(request, f'{updated_count} commande(s) marquée(s) comme livrée(s).')
    mark_as_delivered.short_description = "Marquer comme livrée"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_name', 'quantity', 'product_price', 'total_price')
    list_filter = ('order__created_at',)
    search_fields = ('order__order_number', 'product_name', 'product__name')
    readonly_fields = ('total_price',)


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('order', 'status', 'created_at', 'created_by')
    list_filter = ('status', 'created_at')
    search_fields = ('order__order_number', 'notes')
    readonly_fields = ('created_at',)