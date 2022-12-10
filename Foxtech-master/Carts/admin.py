from django.contrib import admin
from .models import Cart

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['identifier', 'user', 'subtotal', 'total', 'create', 'modified']
    search_fields = ['user', 'identifier']
    list_per_page = 15

    fieldsets = (
        (None, {
            'fields': ('user', 'subtotal', 'total')
        }),
    )