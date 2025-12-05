from django.db import models
from django.conf import settings
from assets.models import Asset
from categories.models import Category

class AssetRequest(models.Model):
    REQUEST_TYPES = [
        ('new', 'New Asset Request'),
        ('return', 'Return Request'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('manager_approved', 'Manager Approved'),
        ('admin_approved', 'Admin Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]
    
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='asset_requests')
    request_type = models.CharField(max_length=10, choices=REQUEST_TYPES)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, null=True, blank=True)  # For return requests or specific asset requests
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)  # For new requests
    requested_asset = models.ForeignKey(Asset, on_delete=models.CASCADE, null=True, blank=True, related_name='asset_requests')  # Specific asset requested
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    manager_approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='manager_approvals')
    manager_approved_at = models.DateTimeField(null=True, blank=True)
    manager_comments = models.TextField(blank=True)
    
    admin_approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='admin_approvals')
    admin_approved_at = models.DateTimeField(null=True, blank=True)
    admin_comments = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.get_request_type_display()} by {self.employee.username} - {self.get_status_display()}"