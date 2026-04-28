from django.db import models


class Supermarket(models.Model):
    name = models.CharField('nome', max_length=150)
    cnpj = models.CharField('CNPJ', max_length=18, unique=True, blank=True, null=True)
    phone = models.CharField('telefone', max_length=20, blank=True)
    address = models.CharField('endereco', max_length=255)
    district = models.CharField('bairro', max_length=100)
    city = models.CharField('cidade', max_length=100)
    logo = models.ImageField('logo', upload_to='supermarkets/logos/', blank=True, null=True)
    is_active = models.BooleanField('ativo', default=True)
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'supermercado'
        verbose_name_plural = 'supermercados'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.cnpj == '':
            self.cnpj = None
        super().save(*args, **kwargs)
