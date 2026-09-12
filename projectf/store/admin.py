
from django.contrib import admin

from .models import Product
admin.site.register(Product)

# # Register your models here.
# @admin.register(Product)
# class ProductAdmin(admin.ModelAdmin):
#     list_display = ['name', 'price', 'is_active', 'created_at']
#     list_display_links = ['name']
#     list_editable = ['price', 'is_active']
#     search_fields=['name', 'price', 'content']
#     list_filter=['is_active', 'created_at']