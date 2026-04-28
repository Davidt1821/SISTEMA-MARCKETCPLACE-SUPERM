from django.contrib import admin

from .models import Supermarket


@admin.register(Supermarket)
class SupermarketAdmin(admin.ModelAdmin):
    list_display = ['name', 'cnpj', 'city', 'district', 'is_active', 'created_at']
    list_filter = ['city', 'district', 'is_active']
    search_fields = ['name', 'cnpj', 'city', 'district']

# Register your models here.
