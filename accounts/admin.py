from django.contrib import admin

from .models import CustomerProfile, SupermarketUser


@admin.register(SupermarketUser)
class SupermarketUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'supermarket', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'supermarket']
    search_fields = ['user__username', 'user__email', 'supermarket__name']


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'default_city', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'phone']
