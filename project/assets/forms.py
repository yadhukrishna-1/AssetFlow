# assets/forms.py
from django import forms
from .models import Asset

class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = [
            'name', 'category', 'brand', 'serial_number', 'purchase_date',
            'cost', 'warranty_expiry', 'status', 'image', 'description'
        ]
        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date'}),
            'warranty_expiry': forms.DateInput(attrs={'type': 'date'}),
        }
