from django.contrib import admin
from .models import Order, OrderDetail, Payment

admin.site.register(Order)
admin.site.register(OrderDetail)
admin.site.register(Payment)
