from django.contrib import admin
from .models import Profile, Agent, Customer


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'address', 'gender', 'age', 'image')  # Display in admin list
    search_fields = ('user__username', 'phone_number', 'address')  # Add search functionality


class AgentAdmin(admin.ModelAdmin):
    list_display = ('profile', 'specialization')


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('profile', 'preferences')


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Agent, AgentAdmin)
admin.site.register(Customer, CustomerAdmin)
