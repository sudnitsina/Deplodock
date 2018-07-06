from django.contrib import admin

from .models import *

admin.site.register(Variable)
admin.site.register(Machine)
admin.site.register(HostVariable)
admin.site.register(Host)
admin.site.register(Child)


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('inventory', 'user')
    list_filter = ('user__username',)
    search_fields = ('user__username',)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('group', 'inventory')
