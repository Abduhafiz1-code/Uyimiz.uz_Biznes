from django.contrib import admin

from .models import Agent


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone', 'district', 'rating', 'tier', 'certification', 'total_deals']
    list_filter = ['tier', 'certification', 'district']
    search_fields = ['full_name', 'phone']
