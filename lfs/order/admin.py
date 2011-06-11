# django imports
from django.contrib import admin

# lfs imports
from lfs.order.models import Order, OrderItem


# Orderitems Inlines
class OrderItemInlines(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('product_name', 'product_price_net', 'product_price_gross')


# Order
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInlines]


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
