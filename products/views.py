from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.db.models import Q, Avg, Count
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Category, ProductReview


class ProductListView(ListView):
    model = Product
    template_name = 'products/list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related().prefetch_related('categories')
        
        # Filter by category
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(categories__slug=category_slug)
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        # Filter by price range
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Filter by availability
        in_stock = self.request.GET.get('in_stock')
        if in_stock:
            queryset = queryset.filter(in_stock=True)
        
        # Sorting
        sort_by = self.request.GET.get('sort', '-created_at')
        if sort_by in ['price', '-price', 'name', '-name', 'created_at', '-created_at']:
            queryset = queryset.order_by(sort_by)
        
        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True, parent=None)
        context['current_category'] = self.request.GET.get('category')
        context['search_query'] = self.request.GET.get('search', '')
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/detail.html'
    context_object_name = 'product'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Product.objects.filter(is_active=True).prefetch_related('categories', 'reviews')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        
        # Get reviews
        reviews = ProductReview.objects.filter(
            product=product, 
            is_approved=True
        ).select_related('user').order_by('-created_at')
        
        # Calculate average rating
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
        
        # Get related products
        related_products = Product.objects.filter(
            categories__in=product.categories.all(),
            is_active=True
        ).exclude(id=product.id).distinct()[:4]
        
        context.update({
            'reviews': reviews,
            'avg_rating': avg_rating,
            'review_count': reviews.count(),
            'related_products': related_products,
        })
        
        return context


class CategoryView(ListView):
    model = Product
    template_name = 'products/category.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'], is_active=True)
        return Product.objects.filter(
            categories=self.category,
            is_active=True
        ).select_related().prefetch_related('categories')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['categories'] = Category.objects.filter(is_active=True, parent=None)
        return context


def search_products(request):
    query = request.GET.get('q', '')
    products = []
    
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query),
            is_active=True
        ).select_related().prefetch_related('categories')
    
    context = {
        'products': products,
        'query': query,
        'categories': Category.objects.filter(is_active=True, parent=None)
    }
    
    return render(request, 'products/search.html', context)


@login_required
def add_product(request):
    """Placeholder view for adding products - should be implemented based on requirements"""
    messages.info(request, 'Fonctionnalité d\'ajout de produit en cours de développement.')
    return redirect('products:list')