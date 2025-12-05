from django.contrib import admin
from .models import AssetRequest

@admin.register(AssetRequest)
class AssetRequestAdmin(admin.ModelAdmin):
    list_display = ['employee', 'request_type', 'status', 'created_at']
    list_filter = ['request_type', 'status', 'created_at']
    search_fields = ['employee__username', 'description']