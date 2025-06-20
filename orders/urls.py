from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.OrderListView.as_view(), name='list'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('<int:order_id>/', views.OrderDetailView.as_view(), name='detail'),
    path('<int:order_id>/cancel/', views.cancel_order, name='cancel'),
    path('<int:order_id>/reorder/', views.reorder, name='reorder'),
]