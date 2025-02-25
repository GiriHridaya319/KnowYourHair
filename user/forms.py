from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from .models import Profile


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image', 'phone_number', 'address', 'gender', 'age']


class CustomPasswordResetForm(PasswordResetForm):
    """Custom form for initiating the password reset process"""
    email = forms.EmailField(
        label="Email",
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address',
            'autocomplete': 'email'
        })
    )


class CustomSetPasswordForm(SetPasswordForm):
    """Custom form for setting a new password"""
    new_password1 = forms.CharField(
        label="New password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'id': 'id_new_password1',
            'autocomplete': 'new-password'
        }),
        strip=False,
    )
    new_password2 = forms.CharField(
        label="Confirm new password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'id': 'id_new_password2',
            'autocomplete': 'new-password'
        }),
        strip=False,
    )
