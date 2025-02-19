from django.contrib import admin
from .models import Clinic, Dermatologist, BookingClinic

admin.site.register(Clinic)
admin.site.register(Dermatologist)
admin.site.register(BookingClinic)

# Register your models here.
