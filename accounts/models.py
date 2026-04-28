from django.db import models
from django.contrib.auth.models import User

from supermarkets.models import Supermarket


class SupermarketUser(models.Model):
    ROLE_OWNER = 'owner'
    ROLE_MANAGER = 'manager'
    ROLE_STAFF = 'staff'

    ROLE_CHOICES = [
        (ROLE_OWNER, 'Proprietario'),
        (ROLE_MANAGER, 'Gerente'),
        (ROLE_STAFF, 'Funcionario'),
    ]

    user = models.OneToOneField(User, verbose_name='usuario', on_delete=models.CASCADE, related_name='supermarket_profile')
    supermarket = models.ForeignKey(
        Supermarket,
        verbose_name='supermercado',
        on_delete=models.CASCADE,
        related_name='users',
    )
    role = models.CharField('funcao', max_length=20, choices=ROLE_CHOICES, default=ROLE_STAFF)
    is_active = models.BooleanField('ativo', default=True)
    created_at = models.DateTimeField('criado em', auto_now_add=True)

    class Meta:
        ordering = ['supermarket__name', 'user__username']
        verbose_name = 'usuario de supermercado'
        verbose_name_plural = 'usuarios de supermercados'

    def __str__(self):
        return f'{self.user} - {self.supermarket}'


class CustomerProfile(models.Model):
    user = models.OneToOneField(User, verbose_name='usuario', on_delete=models.CASCADE, related_name='customer_profile')
    phone = models.CharField('telefone', max_length=30)
    default_street = models.CharField('rua padrao', max_length=150, blank=True)
    default_number = models.CharField('numero padrao', max_length=30, blank=True)
    default_district = models.CharField('bairro padrao', max_length=100, blank=True)
    default_city = models.CharField('cidade padrao', max_length=100, blank=True)
    default_complement = models.CharField('complemento padrao', max_length=150, blank=True)
    default_reference = models.CharField('referencia padrao', max_length=150, blank=True)
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        ordering = ['user__first_name', 'user__email']
        verbose_name = 'perfil de cliente'
        verbose_name_plural = 'perfis de clientes'

    def __str__(self):
        return self.user.get_full_name() or self.user.email or self.user.username
