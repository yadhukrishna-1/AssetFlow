# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    role = forms.ChoiceField(choices=User.ROLE_CHOICES)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Check if admin already exists and remove from choices if so
        if User.objects.filter(role='admin').exists():
            self.fields['role'].choices = [choice for choice in User.ROLE_CHOICES if choice[0] != 'admin']

    def clean_role(self):
        role = self.cleaned_data.get('role')
        if role == 'admin' and User.objects.filter(role='admin').exists():
            raise forms.ValidationError("Only one admin user is allowed.")
        return role