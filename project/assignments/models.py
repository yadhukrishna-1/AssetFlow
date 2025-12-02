# assignments/models.py
from django.db import models
from django.conf import settings
from assets.models import Asset

class Assignment(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.PROTECT, related_name='assignments')
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='assignments')
    assigned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='assigned_by')
    assigned_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField(blank=True, null=True)
    returned_date = models.DateField(blank=True, null=True)
    remarks = models.TextField(blank=True)
    active = models.BooleanField(default=True)  # active = currently assigned

    def mark_returned(self, returned_date=None):
        import datetime
        self.returned_date = returned_date or datetime.date.today()
        self.active = False
        self.save()
        # free the asset
        self.asset.status = Asset.STATUS_AVAILABLE
        self.asset.save()

    def save(self, *args, **kwargs):
        # when creating an active assignment set asset status
        creating = self._state.adding
        super().save(*args, **kwargs)
        if creating and self.active:
            self.asset.status = Asset.STATUS_ASSIGNED
            self.asset.save()

    def __str__(self):
        return f"{self.asset} -> {self.employee.username} ({'Active' if self.active else 'Returned'})"
