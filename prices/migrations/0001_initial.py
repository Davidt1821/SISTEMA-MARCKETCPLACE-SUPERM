# Generated manually for the initial backend structure.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('products', '0001_initial'),
        ('supermarkets', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('old_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('available', models.BooleanField(default=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prices', to='products.product')),
                ('supermarket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prices', to='supermarkets.supermarket')),
            ],
            options={
                'ordering': ['price'],
            },
        ),
        migrations.AddConstraint(
            model_name='productprice',
            constraint=models.UniqueConstraint(fields=('product', 'supermarket'), name='unique_product_price_per_supermarket'),
        ),
    ]
