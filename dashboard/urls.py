from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('orders/', views.dashboard_orders, name='orders'),
    path('products/', views.dashboard_products, name='products'),
    path('users/', views.dashboard_users, name='users'),
    path('analytics/', views.dashboard_analytics, name='analytics'),
    path('settings/', views.dashboard_settings, name='settings'),
    
    # Actions
    path('orders/<int:order_id>/update-status/', views.update_order_status, name='update_order_status'),
    path('products/<int:product_id>/update-stock/', views.update_product_stock, name='update_product_stock'),
]