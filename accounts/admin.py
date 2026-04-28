from django.contrib import admin

from .models import SupermarketUser


@admin.register(SupermarketUser)
class SupermarketUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'supermarket', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'supermarket']
    search_fields = ['user__username', 'user__email', 'supermarket__name']
