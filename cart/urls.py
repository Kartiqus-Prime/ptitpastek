from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_view, name='view'),
    path('add/', views.add_to_cart, name='add_item'),
    path('update/<int:item_id>/', views.update_cart_item, name='update_quantity'),
    path('remove/<int:item_id>/', views.remove_from_cart, name='remove_item'),
    path('clear/', views.clear_cart, name='clear'),
    path('summary/', views.cart_summary, name='summary'),
]