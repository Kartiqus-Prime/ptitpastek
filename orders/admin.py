from django.contrib import admin
from .models import Order, OrderItem, OrderStatusHistory


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

    def mark_as_confirmed(self, request, queryset):
        queryset.update(status='confirmed')
        for order in queryset:
            OrderStatusHistory.objects.create(
                order=order,
                status='confirmed',
                notes='Statut mis à jour par l\'administrateur',
                created_by=request.user
            )
    mark_as_confirmed.short_description = "Marquer comme confirmée"

    def mark_as_processing(self, request, queryset):
        queryset.update(status='processing')
        for order in queryset:
            OrderStatusHistory.objects.create(
                order=order,
                status='processing',
                notes='Statut mis à jour par l\'administrateur',
                created_by=request.user
            )
    mark_as_processing.short_description = "Marquer comme en préparation"

    def mark_as_shipped(self, request, queryset):
        queryset.update(status='shipped')
        for order in queryset:
            OrderStatusHistory.objects.create(
                order=order,
                status='shipped',
                notes='Statut mis à jour par l\'administrateur',
                created_by=request.user
            )
    mark_as_shipped.short_description = "Marquer comme expédiée"

    def mark_as_delivered(self, request, queryset):
        queryset.update(status='delivered')
        for order in queryset:
            OrderStatusHistory.objects.create(
                order=order,
                status='delivered',
                notes='Statut mis à jour par l\'administrateur',
                created_by=request.user
            )
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