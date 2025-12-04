# accounts/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('asset_manager', 'Asset Manager'),
        ('employee', 'Employee'),
    ]
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='employee'
    )
    
    def is_admin(self):
        """Check if user is admin"""
        return self.role == 'admin' or self.is_superuser
    
    def is_asset_manager(self):
        """Check if user is asset manager"""
        return self.role == 'asset_manager'
    
    def is_employee(self):
        """Check if user is employee"""
        return self.role == 'employee'
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
