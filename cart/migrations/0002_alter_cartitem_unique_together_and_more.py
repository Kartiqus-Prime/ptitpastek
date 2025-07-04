# Generated by Django 4.2.7 on 2025-06-21 14:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0003_remove_product_in_stock_remove_product_old_price_and_more"),
        ("cart", "0001_initial"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="cartitem",
            unique_together=set(),
        ),
        migrations.AddField(
            model_name="cartitem",
            name="product_format",
            field=models.ForeignKey(
                default=0,
                on_delete=django.db.models.deletion.CASCADE,
                to="products.productformat",
            ),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name="cartitem",
            unique_together={("cart", "product", "product_format")},
        ),
    ]
