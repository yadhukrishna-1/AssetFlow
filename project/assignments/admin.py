# assignments/admin.py
from django.contrib import admin
from .models import Assignment

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('asset','employee','assigned_by','assigned_date','returned_date','active')
    list_filter = ('active','assigned_date')
    search_fields = ('asset__name','asset__serial_number','employee__username')
