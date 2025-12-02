# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_ADMIN = 'admin'
    ROLE_MANAGER = 'asset_manager'
    ROLE_EMPLOYEE = 'employee'
    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Admin'),
        (ROLE_MANAGER, 'Asset Manager'),
        (ROLE_EMPLOYEE, 'Employee'),
    ]
    role = models.CharField(max_length=32, choices=ROLE_CHOICES, default=ROLE_EMPLOYEE)
    department = models.CharField(max_length=100, blank=True, null=True)

    def is_admin(self):
        return self.role == self.ROLE_ADMIN or self.is_superuser

    def is_asset_manager(self):
        return self.role == self.ROLE_MANAGER
