from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import Cart, CartItem
from products.models import Product
from .utils import get_or_create_cart


def cart_view(request):
    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related('product').all() if cart else []
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'cart_total': cart.total_price if cart else 0,
        'shipping_fee': cart.shipping_cost if cart else 5.90,
        'final_total': cart.final_total if cart else 0,
    }
    
    return render(request, 'cart/view.html', context)


@require_POST
def add_to_cart(request):
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))
    
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart = get_or_create_cart(request)
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )
    
    if not created:
        cart_item.quantity += quantity
        cart_item.save()
    
    messages.success(request, f'{product.name} ajouté au panier !')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'{product.name} ajouté au panier !',
            'cart_total_items': cart.total_items,
            'cart_total_price': float(cart.total_price)
        })
    
    return redirect('cart:view')


@require_POST
def update_cart_item(request, item_id):
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, 'Quantité mise à jour !')
    else:
        cart_item.delete()
        messages.success(request, 'Article retiré du panier !')
    
    return redirect('cart:view')


@require_POST
def remove_from_cart(request, item_id):
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    
    product_name = cart_item.product.name
    cart_item.delete()
    
    messages.success(request, f'{product_name} retiré du panier !')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'{product_name} retiré du panier !',
            'cart_total_items': cart.total_items,
            'cart_total_price': float(cart.total_price)
        })
    
    return redirect('cart:view')


def clear_cart(request):
    cart = get_or_create_cart(request)
    if cart:
        cart.items.all().delete()
        messages.success(request, 'Panier vidé !')
    
    return redirect('cart:view')


def cart_summary(request):
    """API endpoint for cart summary"""
    cart = get_or_create_cart(request)
    
    data = {
        'total_items': cart.total_items if cart else 0,
        'total_price': float(cart.total_price) if cart else 0,
        'shipping_cost': float(cart.shipping_cost) if cart else 5.90,
        'final_total': float(cart.final_total) if cart else 0,
    }
    
    return JsonResponse(data)