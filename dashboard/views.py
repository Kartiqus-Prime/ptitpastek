from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db import transaction

from accounts.models import User
from products.models import Product, Category
from orders.models import Order, OrderItem
from cart.models import Cart


def is_staff_user(user):
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(is_staff_user)
def dashboard_home(request):
    """Vue principale du dashboard"""
    # Statistiques générales
    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)
    
    # Comptes
    total_users = User.objects.count()
    new_users_today = User.objects.filter(date_joined__date=today).count()
    new_users_month = User.objects.filter(date_joined__date__gte=last_30_days).count()
    
    # Produits
    total_products = Product.objects.count()
    active_products = Product.objects.filter(is_active=True).count()
    out_of_stock = Product.objects.filter(Q(stock_quantity=0) | Q(in_stock=False)).count()
    
    # Commandes
    total_orders = Order.objects.count()
    orders_today = Order.objects.filter(created_at__date=today).count()
    orders_month = Order.objects.filter(created_at__date__gte=last_30_days).count()
    pending_orders = Order.objects.filter(status='pending').count()
    
    # Revenus
    total_revenue = Order.objects.filter(payment_status='paid').aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    revenue_month = Order.objects.filter(
        created_at__date__gte=last_30_days,
        payment_status='paid'
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Commandes récentes
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:5]
    
    # Produits populaires
    popular_products = Product.objects.annotate(
        order_count=Count('orderitem')
    ).order_by('-order_count')[:5]
    
    # Graphique des ventes (7 derniers jours)
    sales_data = []
    for i in range(7):
        date = today - timedelta(days=i)
        daily_sales = Order.objects.filter(
            created_at__date=date,
            payment_status='paid'
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        sales_data.append({
            'date': date.strftime('%d/%m'),
            'sales': float(daily_sales)
        })
    sales_data.reverse()
    
    context = {
        'total_users': total_users,
        'new_users_today': new_users_today,
        'new_users_month': new_users_month,
        'total_products': total_products,
        'active_products': active_products,
        'out_of_stock': out_of_stock,
        'total_orders': total_orders,
        'orders_today': orders_today,
        'orders_month': orders_month,
        'pending_orders': pending_orders,
        'total_revenue': total_revenue,
        'revenue_month': revenue_month,
        'recent_orders': recent_orders,
        'popular_products': popular_products,
        'sales_data': sales_data,
    }
    
    return render(request, 'dashboard/home.html', context)


@login_required
@user_passes_test(is_staff_user)
def dashboard_orders(request):
    """Gestion des commandes"""
    status_filter = request.GET.get('status', '')
    search = request.GET.get('search', '')
    
    orders = Order.objects.select_related('user').order_by('-created_at')
    
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    if search:
        orders = orders.filter(
            Q(order_number__icontains=search) |
            Q(user__email__icontains=search) |
            Q(user__full_name__icontains=search)
        )
    
    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'search': search,
        'status_choices': Order.STATUS_CHOICES,
    }
    
    return render(request, 'dashboard/orders.html', context)


@login_required
@user_passes_test(is_staff_user)
def dashboard_products(request):
    """Gestion des produits"""
    category_filter = request.GET.get('category', '')
    search = request.GET.get('search', '')
    stock_filter = request.GET.get('stock', '')
    
    products = Product.objects.select_related().prefetch_related('categories').order_by('-created_at')
    
    if category_filter:
        products = products.filter(categories__slug=category_filter)
    
    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )
    
    if stock_filter == 'low':
        products = products.filter(stock_quantity__lte=5, stock_quantity__gt=0)
    elif stock_filter == 'out':
        products = products.filter(Q(stock_quantity=0) | Q(in_stock=False))
    
    paginator = Paginator(products, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.filter(is_active=True)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'category_filter': category_filter,
        'search': search,
        'stock_filter': stock_filter,
    }
    
    return render(request, 'dashboard/products.html', context)


@login_required
@user_passes_test(is_staff_user)
def dashboard_users(request):
    """Gestion des utilisateurs"""
    search = request.GET.get('search', '')
    
    users = User.objects.order_by('-date_joined')
    
    if search:
        users = users.filter(
            Q(email__icontains=search) |
            Q(full_name__icontains=search) |
            Q(username__icontains=search)
        )
    
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
    }
    
    return render(request, 'dashboard/users.html', context)


@login_required
@user_passes_test(is_staff_user)
def update_order_status(request, order_id):
    """Mettre à jour le statut d'une commande"""
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('status')
        
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            
            # Créer un historique
            from orders.models import OrderStatusHistory
            OrderStatusHistory.objects.create(
                order=order,
                status=new_status,
                notes=f'Statut mis à jour par {request.user.get_full_name()}',
                created_by=request.user
            )
            
            messages.success(request, f'Statut de la commande #{order.order_number} mis à jour.')
        else:
            messages.error(request, 'Statut invalide.')
    
    return redirect('dashboard:orders')


@login_required
@user_passes_test(is_staff_user)
def update_product_stock(request, product_id):
    """Mettre à jour le stock d'un produit"""
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        new_stock = request.POST.get('stock_quantity')
        
        try:
            new_stock = int(new_stock)
            if new_stock >= 0:
                product.stock_quantity = new_stock
                product.in_stock = new_stock > 0
                product.save()
                messages.success(request, f'Stock de {product.name} mis à jour.')
            else:
                messages.error(request, 'Le stock ne peut pas être négatif.')
        except ValueError:
            messages.error(request, 'Valeur de stock invalide.')
    
    return redirect('dashboard:products')


@login_required
@user_passes_test(is_staff_user)
def dashboard_analytics(request):
    """Analytics et rapports"""
    # Période sélectionnée
    period = request.GET.get('period', '30')
    try:
        days = int(period)
    except ValueError:
        days = 30
    
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    # Ventes par jour
    daily_sales = []
    for i in range(days):
        date = start_date + timedelta(days=i)
        daily_revenue = Order.objects.filter(
            created_at__date=date,
            payment_status='paid'
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        daily_orders = Order.objects.filter(created_at__date=date).count()
        
        daily_sales.append({
            'date': date.strftime('%d/%m'),
            'revenue': float(daily_revenue),
            'orders': daily_orders
        })
    
    # Top produits
    top_products = Product.objects.annotate(
        total_sold=Sum('orderitem__quantity'),
        revenue=Sum('orderitem__total_price')
    ).filter(
        orderitem__order__created_at__date__gte=start_date
    ).order_by('-total_sold')[:10]
    
    # Statuts des commandes
    order_status_data = []
    for status, label in Order.STATUS_CHOICES:
        count = Order.objects.filter(
            status=status,
            created_at__date__gte=start_date
        ).count()
        order_status_data.append({
            'status': label,
            'count': count
        })
    
    context = {
        'period': period,
        'daily_sales': daily_sales,
        'top_products': top_products,
        'order_status_data': order_status_data,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'dashboard/analytics.html', context)


@login_required
@user_passes_test(is_staff_user)
def dashboard_settings(request):
    """Paramètres du site"""
    if request.method == 'POST':
        # Ici vous pouvez ajouter la logique pour sauvegarder les paramètres
        messages.success(request, 'Paramètres sauvegardés avec succès.')
        return redirect('dashboard:settings')
    
    context = {
        # Ajoutez ici les paramètres actuels
    }
    
    return render(request, 'dashboard/settings.html', context)