from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('supermarkets', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supermarket',
            name='cnpj',
            field=models.CharField(blank=True, max_length=18, null=True, unique=True, verbose_name='CNPJ'),
        ),
    ]
