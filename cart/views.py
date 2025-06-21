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
        'shipping_fee': cart.shipping_cost if cart else 2500,
        'final_total': cart.final_total if cart else 0,
    }
    
    return render(request, 'cart/view.html', context)


@require_POST
def add_to_cart(request):
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))
    
    if not product_id:
        messages.error(request, 'Produit non spécifié.')
        return redirect('products:list')
    
    try:
        product = get_object_or_404(Product, id=product_id, is_active=True)
        cart = get_or_create_cart(request)
        
        # Vérifier le stock
        if not product.in_stock or product.stock_quantity < quantity:
            messages.error(request, f'Stock insuffisant pour {product.name}.')
            return redirect('products:detail', slug=product.slug)
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            new_quantity = cart_item.quantity + quantity
            if product.stock_quantity < new_quantity:
                messages.error(request, f'Stock insuffisant. Maximum disponible: {product.stock_quantity}')
                return redirect('products:detail', slug=product.slug)
            cart_item.quantity = new_quantity
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
        
    except Product.DoesNotExist:
        messages.error(request, 'Produit introuvable.')
        return redirect('products:list')
    except Exception as e:
        messages.error(request, 'Une erreur est survenue lors de l\'ajout au panier.')
        return redirect('products:list')


@require_POST
def update_cart_item(request, item_id):
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    
    try:
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity <= 0:
            cart_item.delete()
            messages.success(request, 'Article retiré du panier !')
        else:
            # Vérifier le stock
            if cart_item.product.stock_quantity < quantity:
                messages.error(request, f'Stock insuffisant. Maximum disponible: {cart_item.product.stock_quantity}')
            else:
                cart_item.quantity = quantity
                cart_item.save()
                messages.success(request, 'Quantité mise à jour !')
        
    except ValueError:
        messages.error(request, 'Quantité invalide.')
    except Exception as e:
        messages.error(request, 'Une erreur est survenue.')
    
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
        'shipping_cost': float(cart.shipping_cost) if cart else 2500,
        'final_total': float(cart.final_total) if cart else 0,
    }
    
    return JsonResponse(data)