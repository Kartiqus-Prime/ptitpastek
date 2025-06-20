from django.contrib import admin
from .models import Category, Product, ProductCategory, ProductImage, ProductReview


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'is_active', 'created_at')
    list_filter = ('is_active', 'parent', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductCategoryInline(admin.TabularInline):
    model = ProductCategory
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'old_price', 'is_new', 'is_featured', 'in_stock', 'stock_quantity', 'created_at')
    list_filter = ('is_new', 'is_featured', 'is_active', 'in_stock', 'categories', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('-created_at',)
    inlines = [ProductCategoryInline, ProductImageInline]
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('name', 'slug', 'description', 'full_description')
        }),
        ('Prix', {
            'fields': ('price', 'old_price')
        }),
        ('Images', {
            'fields': ('image',)
        }),
        ('Données produit', {
            'fields': ('ingredients', 'nutrition_info', 'additional_images')
        }),
        ('Statut', {
            'fields': ('is_new', 'is_featured', 'is_active', 'in_stock', 'stock_quantity')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'title', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_approved', 'is_verified_purchase', 'created_at')
    search_fields = ('product__name', 'user__email', 'title', 'comment')
    ordering = ('-created_at',)
    actions = ['approve_reviews', 'disapprove_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
    approve_reviews.short_description = "Approuver les avis sélectionnés"

    def disapprove_reviews(self, request, queryset):
        queryset.update(is_approved=False)
    disapprove_reviews.short_description = "Désapprouver les avis sélectionnés"