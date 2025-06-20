from .models import Cart


def get_or_create_cart(request):
    """Get or create a cart for the current user or session"""
    cart = None
    
    if request.user.is_authenticated:
        # For authenticated users
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        # Merge session cart if exists
        if not created and request.session.session_key:
            session_cart = Cart.objects.filter(session_key=request.session.session_key).first()
            if session_cart:
                # Merge session cart items into user cart
                for item in session_cart.items.all():
                    cart_item, item_created = cart.items.get_or_create(
                        product=item.product,
                        defaults={'quantity': item.quantity}
                    )
                    if not item_created:
                        cart_item.quantity += item.quantity
                        cart_item.save()
                
                # Delete session cart
                session_cart.delete()
    else:
        # For anonymous users
        if not request.session.session_key:
            request.session.create()
        
        cart, created = Cart.objects.get_or_create(session_key=request.session.session_key)
    
    return cart


def get_cart_items_count(request):
    """Get the number of items in the cart"""
    cart = get_or_create_cart(request)
    return cart.total_items if cart else 0


def get_cart_total(request):
    """Get the total price of items in the cart"""
    cart = get_or_create_cart(request)
    return cart.total_price if cart else 0