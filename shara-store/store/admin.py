from django.contrib import admin
from .models import Category, Product, Cart, CartItem, Order, OrderItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock_quantity', 'created_date']
    list_filter = ['category', 'created_date']
    search_fields = ['name', 'description']

class CartItemInline(admin.TabularInline):
    model = CartItem
    raw_id_fields = ['product']

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_date']
    inlines = [CartItemInline]

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_price', 'order_status', 'order_date']
    list_filter = ['order_status', 'order_date']
    search_fields = ['user__username', 'shipping_address']
    inlines = [OrderItemInline]
