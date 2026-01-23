from django import forms
from .base import BaseEntryForm


class OvernightForm(BaseEntryForm):
    """
    Overnight routine tracking form.
    Tracks dinner, sleep, breakfast, and notes.
    """
    PORTION_CHOICES = [
        ('', '-- Select --'),
        ('None', 'None'),
        ('Some', 'Some'),
        ('Most', 'Most'),
        ('All', 'All'),
    ]
    
    TIME_CHOICES = [
        ('', '-- Select --'),
        ('Early', 'Early'),
        ('Normal', 'Normal'),
        ('Late', 'Late'),
    ]
    
    dinner = forms.ChoiceField(
        choices=PORTION_CHOICES,
        required=True,
        label="Dinner Last Night",
        widget=forms.Select()
    )
    
    bedtime = forms.ChoiceField(
        choices=TIME_CHOICES,
        required=True,
        label="Bedtime",
        widget=forms.Select()
    )
    
    woke_up = forms.ChoiceField(
        choices=TIME_CHOICES,
        required=True,
        label="Woke Up",
        widget=forms.Select()
    )
    
    breakfast = forms.ChoiceField(
        choices=PORTION_CHOICES,
        required=True,
        label="Breakfast",
        widget=forms.Select()
    )
    
    notes = forms.CharField(
        required=False,
        label="Notes",
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Any additional notes about your night/morning...'
        })
    )
    
    def clean(self):
        """Custom validation for overnight form"""
        cleaned_data = super().clean()
        
        # Ensure at least some data is provided
        required_fields = ['dinner', 'bedtime', 'woke_up', 'breakfast']
        if not any(cleaned_data.get(field) for field in required_fields):
            raise forms.ValidationError("Please fill in at least one field.")
        
        return cleaned_data
