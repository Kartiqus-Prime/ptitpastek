from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('products:category', kwargs={'slug': self.slug})


class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    full_description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=0, default=0)  # FCFA sans décimales
    old_price = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    image = models.ImageField(upload_to='products/')
    
    # Image thumbnails
    image_thumbnail = ImageSpecField(
        source='image',
        processors=[ResizeToFill(300, 300)],
        format='JPEG',
        options={'quality': 80}
    )
    
    additional_images = models.JSONField(default=list, blank=True)
    ingredients = models.JSONField(default=list, blank=True)
    nutrition_info = models.JSONField(default=dict, blank=True)
    
    # Product flags
    is_new = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    in_stock = models.BooleanField(default=True)
    stock_quantity = models.IntegerField(default=0)
    
    # Relationships
    categories = models.ManyToManyField(Category, through='ProductCategory', blank=True)
    
    # SEO
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        
        # Update in_stock based on stock_quantity
        if self.stock_quantity <= 0:
            self.in_stock = False
        
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('products:detail', kwargs={'slug': self.slug})

    @property
    def is_on_sale(self):
        return self.old_price and self.old_price > self.price

    @property
    def discount_percentage(self):
        if self.is_on_sale:
            return int(((self.old_price - self.price) / self.old_price) * 100)
        return 0

    @property
    def main_category(self):
        return self.categories.first()

    def format_price(self, amount):
        """Format price with FCFA currency"""
        return f"{int(amount):,} FCFA".replace(',', ' ')

    @property
    def formatted_price(self):
        return self.format_price(self.price)

    @property
    def formatted_old_price(self):
        if self.old_price:
            return self.format_price(self.old_price)
        return None

    @property
    def stock_status(self):
        if not self.in_stock or self.stock_quantity <= 0:
            return "Rupture de stock"
        elif self.stock_quantity <= 5:
            return f"Plus que {self.stock_quantity} en stock"
        else:
            return "En stock"

    @property
    def stock_status_class(self):
        if not self.in_stock or self.stock_quantity <= 0:
            return "text-red-600"
        elif self.stock_quantity <= 5:
            return "text-orange-600"
        else:
            return "text-green-600"


class ProductCategory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Catégorie de produit"
        verbose_name_plural = "Catégories de produits"
        unique_together = ['product', 'category']

    def __str__(self):
        return f"{self.product.name} - {self.category.name}"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Image de produit"
        verbose_name_plural = "Images de produits"
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"Image de {self.product.name}"


class ProductReview(models.Model):
    RATING_CHOICES = [
        (1, '1 étoile'),
        (2, '2 étoiles'),
        (3, '3 étoiles'),
        (4, '4 étoiles'),
        (5, '5 étoiles'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    title = models.CharField(max_length=255)
    comment = models.TextField()
    is_verified_purchase = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Avis produit"
        verbose_name_plural = "Avis produits"
        unique_together = ['product', 'user']
        ordering = ['-created_at']

    def __str__(self):
        return f"Avis de {self.user.get_full_name()} sur {self.product.name}"