# assignments/forms.py
from django import forms
from .models import Assignment
from accounts.models import User
from assets.models import Asset

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['asset', 'employee', 'expected_return_date', 'remarks']
        widgets = {
            'expected_return_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['asset'].queryset = Asset.objects.filter(status='available')
        self.fields['employee'].queryset = User.objects.filter(role='employee')
