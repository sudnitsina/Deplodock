from django.contrib import admin

from .models import InventoryToken, Token


@admin.register(InventoryToken)
class InventoryTokenAdmin(admin.ModelAdmin):
    fields = ('user', 'inventory', 'description')


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ('key', 'user', 'created')
    fields = ('user',)
    ordering = ('-created',)
