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
            name='Promotion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('promotional_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('description', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='promotions', to='products.product')),
                ('supermarket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='promotions', to='supermarkets.supermarket')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
