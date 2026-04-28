from django.db import models


class Category(models.Model):
    name = models.CharField('nome', max_length=100, unique=True)
    description = models.TextField('descricao', blank=True)
    is_active = models.BooleanField('ativa', default=True)
    created_at = models.DateTimeField('criada em', auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'categoria'
        verbose_name_plural = 'categorias'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField('nome', max_length=150)
    brand = models.CharField('marca', max_length=100, blank=True)
    category = models.ForeignKey(
        Category,
        verbose_name='categoria',
        on_delete=models.PROTECT,
        related_name='products',
    )
    barcode = models.CharField('codigo de barras', max_length=50, unique=True, blank=True, null=True)
    description = models.TextField('descricao', blank=True)
    image = models.ImageField('imagem', upload_to='products/images/', blank=True, null=True)
    is_active = models.BooleanField('ativo', default=True)
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'produto'
        verbose_name_plural = 'produtos'

    def __str__(self):
        if self.brand:
            return f'{self.name} - {self.brand}'
        return self.name

    def save(self, *args, **kwargs):
        if self.barcode == '':
            self.barcode = None
        super().save(*args, **kwargs)
