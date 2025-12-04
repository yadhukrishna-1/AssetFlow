# assignments/forms.py
from django import forms
from .models import Assignment
from assets.models import Asset
from accounts.models import User

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['asset', 'employee', 'expected_return_date', 'remarks']
        widgets = {
            'expected_return_date': forms.DateInput(attrs={'type': 'date'}),
            'remarks': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show available assets
        self.fields['asset'].queryset = Asset.objects.filter(status='available')
        # Only show employees
        self.fields['employee'].queryset = User.objects.filter(role='employee')