from django import forms

from .base import BaseEntryForm
from .constants import PORTION_CHOICES_WITH_BLANK, TIME_CHOICES


class OvernightForm(BaseEntryForm):
    """
    Overnight routine tracking form.
    Tracks dinner, sleep, breakfast, and notes.
    """
    dinner = forms.ChoiceField(
        choices=PORTION_CHOICES_WITH_BLANK,
        required=True,
        label="Dinner Last Night",
    )

    bedtime = forms.ChoiceField(
        choices=TIME_CHOICES,
        required=True,
        label="Bedtime",
    )

    woke_up = forms.ChoiceField(
        choices=TIME_CHOICES,
        required=True,
        label="Woke Up",
    )
    
    breakfast = forms.ChoiceField(
        choices=PORTION_CHOICES_WITH_BLANK,
        required=True,
        label="Breakfast",
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
