from django.contrib import admin
from .models import Product, Cart, CartItem
from .models import CustomUser

admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartItem)

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'real_name', 'first_name', 'last_name')
    search_fields = ('username', 'email', 'real_name')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
