# Generated by Django 4.2.7 on 2025-06-20 15:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("slug", models.SlugField(blank=True, unique=True)),
                ("description", models.TextField(blank=True)),
                (
                    "image",
                    models.ImageField(blank=True, null=True, upload_to="categories/"),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="children",
                        to="products.category",
                    ),
                ),
            ],
            options={
                "verbose_name": "Catégorie",
                "verbose_name_plural": "Catégories",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Product",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("slug", models.SlugField(blank=True, unique=True)),
                ("description", models.TextField()),
                ("full_description", models.TextField(blank=True)),
                ("price", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "old_price",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True
                    ),
                ),
                ("image", models.ImageField(upload_to="products/")),
                ("additional_images", models.JSONField(blank=True, default=list)),
                ("ingredients", models.JSONField(blank=True, default=list)),
                ("nutrition_info", models.JSONField(blank=True, default=dict)),
                ("is_new", models.BooleanField(default=False)),
                ("is_featured", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=True)),
                ("in_stock", models.BooleanField(default=True)),
                ("stock_quantity", models.IntegerField(default=0)),
                ("meta_title", models.CharField(blank=True, max_length=255)),
                ("meta_description", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Produit",
                "verbose_name_plural": "Produits",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="ProductImage",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("image", models.ImageField(upload_to="products/gallery/")),
                ("alt_text", models.CharField(blank=True, max_length=255)),
                ("is_primary", models.BooleanField(default=False)),
                ("order", models.PositiveIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="images",
                        to="products.product",
                    ),
                ),
            ],
            options={
                "verbose_name": "Image de produit",
                "verbose_name_plural": "Images de produits",
                "ordering": ["order", "created_at"],
            },
        ),
        migrations.CreateModel(
            name="ProductCategory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("is_primary", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="products.category",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="products.product",
                    ),
                ),
            ],
            options={
                "verbose_name": "Catégorie de produit",
                "verbose_name_plural": "Catégories de produits",
                "unique_together": {("product", "category")},
            },
        ),
        migrations.AddField(
            model_name="product",
            name="categories",
            field=models.ManyToManyField(
                blank=True, through="products.ProductCategory", to="products.category"
            ),
        ),
        migrations.CreateModel(
            name="ProductReview",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "rating",
                    models.IntegerField(
                        choices=[
                            (1, "1 étoile"),
                            (2, "2 étoiles"),
                            (3, "3 étoiles"),
                            (4, "4 étoiles"),
                            (5, "5 étoiles"),
                        ]
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("comment", models.TextField()),
                ("is_verified_purchase", models.BooleanField(default=False)),
                ("is_approved", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reviews",
                        to="products.product",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Avis produit",
                "verbose_name_plural": "Avis produits",
                "ordering": ["-created_at"],
                "unique_together": {("product", "user")},
            },
        ),
    ]
