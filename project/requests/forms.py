from django import forms
from .models import AssetRequest
from categories.models import Category
from assets.models import Asset

class NewAssetRequestForm(forms.ModelForm):
    class Meta:
        model = AssetRequest
        fields = ['category', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe why you need this asset...'})
        }

class ReturnRequestForm(forms.ModelForm):
    class Meta:
        model = AssetRequest
        fields = ['asset', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Please specify the reason for return (repair needed, no longer required, damaged, etc.) and any additional comments...'})
        }
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['asset'].queryset = Asset.objects.filter(assignments__employee=user, assignments__active=True)

class ManagerAssetSelectionForm(forms.Form):
    selected_asset = forms.ModelChoiceField(
        queryset=Asset.objects.none(),
        empty_label="Select an asset to assign",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, category, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['selected_asset'].queryset = Asset.objects.filter(
            category=category,
            status=Asset.STATUS_AVAILABLE
        )