# assets/models.py
from django.db import models
from categories.models import Category
from django.conf import settings

class Asset(models.Model):
    STATUS_AVAILABLE = 'available'
    STATUS_ASSIGNED = 'assigned'
    STATUS_REPAIR = 'under_repair'
    STATUS_CHOICES = [
        (STATUS_AVAILABLE, 'Available'),
        (STATUS_ASSIGNED, 'Assigned'),
        (STATUS_REPAIR, 'Under Repair'),
    ]

    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='assets')
    brand = models.CharField(max_length=120, blank=True, null=True)
    serial_number = models.CharField(max_length=200, unique=True)
    purchase_date = models.DateField(blank=True, null=True)
    cost = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    warranty_expiry = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
    image = models.ImageField(upload_to='assets/images/', blank=True, null=True)
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_warranty_expiring_within(self, days=30):
        if not self.warranty_expiry:
            return False
        from datetime import date, timedelta
        return date.today() <= self.warranty_expiry <= date.today() + timedelta(days=days)

    def __str__(self):
        return f"{self.name} ({self.serial_number})"
