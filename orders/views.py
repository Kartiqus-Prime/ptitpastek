from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
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
                        shipping_address=form.cleaned_data.get('shipping_address'),
                        shipping_name=form.cleaned_data['shipping_name'],
                        shipping_address_line1=form.cleaned_data['shipping_address_line1'],
                        shipping_address_line2=form.cleaned_data.get('shipping_address_line2', ''),
                        shipping_city=form.cleaned_data['shipping_city'],
                        shipping_postal_code=form.cleaned_data['shipping_postal_code'],
                        shipping_country=form.cleaned_data.get('shipping_country', 'France'),
                        notes=form.cleaned_data.get('notes', ''),
                    )
                    
                    # Create order items
                    for cart_item in cart.items.all():
                        OrderItem.objects.create(
                            order=order,
                            product=cart_item.product,
                            product_name=cart_item.product.name,
                            product_price=cart_item.product.price,
                            quantity=cart_item.quantity,
                        )
                    
                    # Create status history
                    OrderStatusHistory.objects.create(
                        order=order,
                        status='pending',
                        notes='Commande créée',
                        created_by=request.user
                    )
                    
                    # Clear cart
                    cart.items.all().delete()
                    
                    messages.success(request, f'Commande #{order.order_number} créée avec succès !')
                    return redirect('orders:detail', order_id=order.id)
                    
            except Exception as e:
                messages.error(request, 'Une erreur est survenue lors de la création de la commande.')
                
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
            cart_item, created = cart.items.get_or_create(
                product=order_item.product,
                defaults={'quantity': order_item.quantity}
            )
            if not created:
                cart_item.quantity += order_item.quantity
                cart_item.save()
            items_added += 1
    
    if items_added > 0:
        messages.success(request, f'{items_added} article(s) ajouté(s) au panier.')
    else:
        messages.warning(request, 'Aucun article de cette commande n\'est disponible.')
    
    return redirect('cart:view')