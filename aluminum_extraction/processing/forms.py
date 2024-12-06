""" # forms.py
from django import forms
from django.contrib.auth.models import User
from .models import UserProfile

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['role'] """

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import ByProduct

class RegistrationForm(UserCreationForm):
    role = forms.ChoiceField(choices=[('Admin', 'Admin'), ('Operator', 'Operator'), ('Viewer', 'Viewer')])

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role']

class ByProductForm(forms.ModelForm):
    class Meta:
        model = ByProduct
        fields = ['name', 'quantity']
