from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import Order, OrderItem, OrderStatusHistory
from cart.utils import get_or_create_cart
from accounts.models import Address
from .forms import CheckoutForm


@login_required
def checkout_view(request):
    cart = get_or_create_cart(request)
    
    if not cart or not cart.items.exists():
        messages.error(request, 'Votre panier est vide.')
        return redirect('cart:view')
    
    # Vérifier la disponibilité des produits
    for item in cart.items.all():
        if not item.product.is_active:
            messages.error(request, f'Le produit {item.product.name} n\'est plus disponible.')
            item.delete()
            return redirect('cart:view')
        
        if not item.product.in_stock or item.product.stock_quantity < item.quantity:
            messages.error(request, f'Stock insuffisant pour {item.product.name}.')
            return redirect('cart:view')
    
    # Get user's addresses
    addresses = request.user.addresses.all()
    default_address = addresses.filter(is_default=True).first()
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Create order
                    order = Order.objects.create(
                        user=request.user,
                        subtotal=cart.total_price,
                        shipping_cost=cart.shipping_cost,
                        total_amount=cart.final_total,
                        payment_method=form.cleaned_data['payment_method'],
                        shipping_address=form.cleaned_data.get('shipping_address'),
                        shipping_name=form.cleaned_data['shipping_name'],
                        shipping_phone=form.cleaned_data['shipping_phone'],
                        shipping_address_line1=form.cleaned_data['shipping_address_line1'],
                        shipping_address_line2=form.cleaned_data.get('shipping_address_line2', ''),
                        shipping_city=form.cleaned_data['shipping_city'],
                        shipping_postal_code=form.cleaned_data.get('shipping_postal_code', ''),
                        shipping_country=form.cleaned_data.get('shipping_country', 'Cameroun'),
                        notes=form.cleaned_data.get('notes', ''),
                    )
                    
                    # Create order items and update stock
                    for cart_item in cart.items.all():
                        # Vérifier à nouveau le stock
                        if cart_item.product.stock_quantity < cart_item.quantity:
                            raise Exception(f'Stock insuffisant pour {cart_item.product.name}')
                        
                        OrderItem.objects.create(
                            order=order,
                            product=cart_item.product,
                            product_name=cart_item.product.name,
                            product_price=cart_item.product.price,
                            quantity=cart_item.quantity,
                        )
                        
                        # Update stock
                        cart_item.product.stock_quantity -= cart_item.quantity
                        if cart_item.product.stock_quantity <= 0:
                            cart_item.product.in_stock = False
                        cart_item.product.save()
                    
                    # Create status history
                    OrderStatusHistory.objects.create(
                        order=order,
                        status='pending',
                        notes='Commande créée',
                        created_by=request.user
                    )
                    
                    # Send confirmation email
                    try:
                        send_order_confirmation_email(order)
                    except Exception as e:
                        # Log email error but don't fail the order
                        print(f"Email error: {e}")
                    
                    # Clear cart
                    cart.items.all().delete()
                    
                    messages.success(request, f'Commande #{order.order_number} créée avec succès !')
                    return redirect('orders:detail', order_id=order.id)
                    
            except Exception as e:
                messages.error(request, f'Une erreur est survenue lors de la création de la commande: {str(e)}')
                
    else:
        initial_data = {}
        if default_address:
            initial_data = {
                'shipping_address': default_address,
                'shipping_name': default_address.name,
                'shipping_address_line1': default_address.address_line1,
                'shipping_address_line2': default_address.address_line2,
                'shipping_city': default_address.city,
                'shipping_postal_code': default_address.postal_code,
                'shipping_country': default_address.country,
            }
        
        form = CheckoutForm(initial=initial_data, user=request.user)
    
    context = {
        'form': form,
        'cart': cart,
        'addresses': addresses,
        'cart_items': cart.items.select_related('product').all(),
    }
    
    return render(request, 'orders/checkout.html', context)


def send_order_confirmation_email(order):
    """Send order confirmation email"""
    subject = f'Confirmation de commande #{order.order_number} - La P\'tit Pastèk'
    
    # Email content
    message = f"""
    Bonjour {order.shipping_name},

    Votre commande #{order.order_number} a été confirmée !

    Détails de la commande:
    - Total: {order.formatted_total}
    - Mode de paiement: {order.get_payment_method_display()}
    - Adresse de livraison: {order.shipping_address_line1}, {order.shipping_city}

    Nous vous contacterons bientôt pour organiser la livraison.

    Merci de votre confiance !

    L'équipe La P'tit Pastèk
    """
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [order.user.email],
        fail_silently=False,
    )


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/list.html'
    context_object_name = 'orders'
    paginate_by = 10

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items')


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'orders/detail.html'
    context_object_name = 'order'
    pk_url_kwarg = 'order_id'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related(
            'items__product',
            'status_history'
        )


@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.can_be_cancelled:
        with transaction.atomic():
            # Restore stock
            for item in order.items.all():
                item.product.stock_quantity += item.quantity
                item.product.in_stock = True
                item.product.save()
            
            # Update order status
            order.status = 'cancelled'
            order.save()
            
            # Add status history
            OrderStatusHistory.objects.create(
                order=order,
                status='cancelled',
                notes='Commande annulée par le client',
                created_by=request.user
            )
        
        messages.success(request, f'Commande #{order.order_number} annulée avec succès.')
    else:
        messages.error(request, 'Cette commande ne peut plus être annulée.')
    
    return redirect('orders:detail', order_id=order.id)


@login_required
def reorder(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    cart = get_or_create_cart(request)
    
    # Add order items to cart
    items_added = 0
    for order_item in order.items.all():
        if order_item.product.is_active and order_item.product.in_stock:
            # Check stock availability
            available_quantity = min(order_item.quantity, order_item.product.stock_quantity)
            
            if available_quantity > 0:
                cart_item, created = cart.items.get_or_create(
                    product=order_item.product,
                    defaults={'quantity': available_quantity}
                )
                if not created:
                    new_quantity = cart_item.quantity + available_quantity
                    if new_quantity <= order_item.product.stock_quantity:
                        cart_item.quantity = new_quantity
                        cart_item.save()
                    else:
                        # Add only what's available
                        cart_item.quantity = order_item.product.stock_quantity
                        cart_item.save()
                items_added += 1
    
    if items_added > 0:
        messages.success(request, f'{items_added} article(s) ajouté(s) au panier.')
    else:
        messages.warning(request, 'Aucun article de cette commande n\'est disponible.')
    
    return redirect('cart:view')