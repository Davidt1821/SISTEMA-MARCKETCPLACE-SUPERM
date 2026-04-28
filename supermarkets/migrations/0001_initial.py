# Generated manually for the initial backend structure.

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Supermarket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('cnpj', models.CharField(max_length=18, unique=True)),
                ('phone', models.CharField(blank=True, max_length=20)),
                ('address', models.CharField(max_length=255)),
                ('district', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=100)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='supermarkets/logos/')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
    ]
