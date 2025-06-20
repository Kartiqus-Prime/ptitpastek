from .utils import get_or_create_cart


def cart(request):
    """Add cart information to all templates"""
    cart = get_or_create_cart(request)
    
    return {
        'cart': cart,
        'cart_items_count': cart.total_items if cart else 0,
        'cart_total': cart.total_price if cart else 0,
    }