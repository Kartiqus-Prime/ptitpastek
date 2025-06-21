"""
URL configuration for petitpastek project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views as core_views

urlpatterns = [
    path("admin/", admin.site.urls),
    
    # Core pages
    path("", core_views.HomeView.as_view(), name="home"),
    path("about/", core_views.AboutView.as_view(), name="about"),
    path("contact/", core_views.ContactView.as_view(), name="contact"),
    
    # Apps URLs
    path("accounts/", include("accounts.urls")),
    path("products/", include("products.urls")),
    path("cart/", include("cart.urls")),
    path("orders/", include("orders.urls")),
]

# Admin site customization
admin.site.site_header = "La P'tit Pastèk Administration"
admin.site.site_title = "La P'tit Pastèk Admin"
admin.site.index_title = "Bienvenue dans l'administration"

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)