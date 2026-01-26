"""
User registration and profile forms.
"""
from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from timeline.models import UserProfile


class CustomUserCreationForm(UserCreationForm):
    """
    Extended user registration form that includes UserProfile fields.
    """
    # Registration code field
    registration_code = forms.CharField(
        max_length=50,
        required=True,
        label="Registration Code",
        help_text="Enter the registration code to create an account",
        widget=forms.TextInput(attrs={'placeholder': 'Enter code'})
    )

    # UserProfile fields
    display_name = forms.CharField(
        max_length=100,
        required=True,
        help_text="Name shown on your posts (e.g., 'Ms. Johnson')",
        widget=forms.TextInput(attrs={'placeholder': 'Ms. Johnson'})
    )
    email_address = forms.EmailField(
        required=True,
        help_text="Your contact email address",
        widget=forms.EmailInput(attrs={'placeholder': 'your.email@example.com'})
    )
    first_name = forms.CharField(
        max_length=50,
        required=True,
        help_text="Your first name",
        widget=forms.TextInput(attrs={'placeholder': 'Jane'})
    )
    last_name = forms.CharField(
        max_length=50,
        required=True,
        help_text="Your last name",
        widget=forms.TextInput(attrs={'placeholder': 'Doe'})
    )
    position_role = forms.CharField(
        max_length=100,
        required=False,
        help_text="Your role (e.g., 'Teacher', 'Parent', 'Administrator')",
        widget=forms.TextInput(attrs={'placeholder': 'Teacher'})
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email_address',
                  'display_name', 'position_role', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add placeholders to default fields
        self.fields['username'].widget.attrs['placeholder'] = 'username'
        self.fields['password1'].widget.attrs['placeholder'] = 'Enter password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm password'

    def clean_registration_code(self):
        """Validate registration code"""
        code = self.cleaned_data.get('registration_code')
        if code != settings.REGISTRATION_CODE:
            raise forms.ValidationError(
                'Invalid registration code. Please contact an administrator for access.'
            )
        return code

    def clean_email_address(self):
        """Validate email uniqueness"""
        email = self.cleaned_data.get('email_address')
        if email and UserProfile.objects.filter(email_address=email).exists():
            raise forms.ValidationError('This email address is already registered.')
        return email

    def save(self, commit=True):
        """Save both User and UserProfile"""
        # Save the User instance
        user = super().save(commit=False)
        user.email = self.cleaned_data['email_address']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if commit:
            user.save()
            # Create or update the UserProfile
            UserProfile.objects.update_or_create(
                user=user,
                defaults={
                    'display_name': self.cleaned_data['display_name'],
                    'email_address': self.cleaned_data['email_address'],
                    'first_name': self.cleaned_data['first_name'],
                    'last_name': self.cleaned_data['last_name'],
                    'position_role': self.cleaned_data.get('position_role', '')
                }
            )

        return user
