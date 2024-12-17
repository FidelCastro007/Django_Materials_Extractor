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
from processing.models import RawMaterial, Processing, ByProduct
from django.contrib.auth.models import User
from .models import ByProduct
from processing.models import UserProfile

class RegistrationForm(UserCreationForm):
    role = forms.ChoiceField(choices=[('Admin', 'Admin'), ('Operator', 'Operator'), ('Viewer', 'Viewer')])

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role']

class ByProductForm(forms.ModelForm):
    quality = forms.ChoiceField(
        choices=[('High', 'High'), ('Medium', 'Medium'), ('Low', 'Low')],
        required=True,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})  # Use radio buttons for quality
    )
    processing = forms.ModelChoiceField(
        queryset=Processing.objects.all(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})  # Ensure consistent styling for dropdown
    )

    class Meta:
        model = ByProduct
        fields = ['name', 'quantity', 'quality', 'processing']

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Byproduct Name',
                'required': True
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Quantity',
                'required': True
            }),
        }

        labels = {
            'name': 'Byproduct Name',
            'quantity': 'Quantity',
            'quality': 'Quality',
            'processing': 'Processing',
        }


class RawMaterialForm(forms.ModelForm):
    class Meta:
        model = RawMaterial
        fields = ['name', 'quantity', 'quality']

class ProcessingForm(forms.ModelForm):
    class Meta:
        model = Processing
        fields = ['raw_material', 'aluminum_output_estimate', 'status']

class ByProductForm(forms.ModelForm):
    class Meta:
        model = ByProduct
        fields = ['name', 'quantity', 'processing']

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    
    class Meta:
        model = User
        fields = ['username', 'password']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['role']
