"""
User registration and profile forms.
"""
from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
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


class UserProfileEditForm(forms.Form):
    """
    Form for users to edit their own profile information.
    Does not include permissions - those are admin-controlled.
    """
    display_name = forms.CharField(
        max_length=100,
        required=True,
        label="Display Name",
        help_text="Name shown on your posts (e.g., 'Ms. Johnson')",
        widget=forms.TextInput(attrs={'placeholder': 'Ms. Johnson'})
    )
    email_address = forms.EmailField(
        required=True,
        label="Email Address",
        help_text="Your contact email address",
        widget=forms.EmailInput(attrs={'placeholder': 'your.email@example.com'})
    )
    first_name = forms.CharField(
        max_length=50,
        required=True,
        label="First Name",
        help_text="Your first name",
        widget=forms.TextInput(attrs={'placeholder': 'Jane'})
    )
    last_name = forms.CharField(
        max_length=50,
        required=True,
        label="Last Name",
        help_text="Your last name",
        widget=forms.TextInput(attrs={'placeholder': 'Doe'})
    )
    position_role = forms.CharField(
        max_length=100,
        required=False,
        label="Position/Role",
        help_text="Your role (e.g., 'Teacher', 'Parent', 'Administrator')",
        widget=forms.TextInput(attrs={'placeholder': 'Teacher'})
    )

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        # Pre-populate fields if user provided
        if user and hasattr(user, 'profile'):
            profile = user.profile
            self.fields['display_name'].initial = profile.display_name
            self.fields['email_address'].initial = profile.email_address
            self.fields['first_name'].initial = profile.first_name
            self.fields['last_name'].initial = profile.last_name
            self.fields['position_role'].initial = profile.position_role

    def clean_email_address(self):
        """Validate email uniqueness (excluding current user)"""
        email = self.cleaned_data.get('email_address')
        if email and self.user:
            existing = UserProfile.objects.filter(email_address=email).exclude(user=self.user)
            if existing.exists():
                raise forms.ValidationError('This email address is already registered by another user.')
        return email

    def save(self):
        """Update the user's profile with the form data"""
        if not self.user or not hasattr(self.user, 'profile'):
            raise ValueError("Cannot save without a valid user with profile")

        profile = self.user.profile
        profile.display_name = self.cleaned_data['display_name']
        profile.email_address = self.cleaned_data['email_address']
        profile.first_name = self.cleaned_data['first_name']
        profile.last_name = self.cleaned_data['last_name']
        profile.position_role = self.cleaned_data.get('position_role', '')
        profile.save()

        # Also update the User model's email and names
        self.user.email = self.cleaned_data['email_address']
        self.user.first_name = self.cleaned_data['first_name']
        self.user.last_name = self.cleaned_data['last_name']
        self.user.save()

        return profile


class StyledPasswordChangeForm(PasswordChangeForm):
    """
    Custom password change form with styled widgets.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add placeholders and consistent styling
        self.fields['old_password'].widget.attrs.update({
            'placeholder': 'Current password',
            'class': 'form-control'
        })
        self.fields['new_password1'].widget.attrs.update({
            'placeholder': 'New password',
            'class': 'form-control'
        })
        self.fields['new_password2'].widget.attrs.update({
            'placeholder': 'Confirm new password',
            'class': 'form-control'
        })
