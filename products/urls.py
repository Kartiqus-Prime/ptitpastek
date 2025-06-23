from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.ProductListView.as_view(), name='list'),
    path('search/', views.search_products, name='search'),
    path('category/<slug:slug>/', views.CategoryView.as_view(), name='category'),
    path('<slug:slug>/', views.ProductDetailView.as_view(), name='detail'),
    path('add/', views.add_product, name='add'),  # Add this missing URL
]