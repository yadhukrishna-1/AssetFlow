# assets/admin.py
from django.contrib import admin
from .models import Asset

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('name','serial_number','category','status','purchase_date','warranty_expiry')
    search_fields = ('name','serial_number','brand')
    list_filter = ('status','category')
