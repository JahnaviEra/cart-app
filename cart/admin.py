from django.contrib import admin
from .models import Cart,Cart_Items,Orders
# Register your models here.
admin.site.register(Cart)
admin.site.register(Cart_Items)
admin.site.register(Orders)