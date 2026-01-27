from django import forms

from .base import BaseEntryForm
from .constants import PORTION_CHOICES_WITH_BLANK, TIME_CHOICES
from .mixins import MoodFieldMixin


class OvernightForm(MoodFieldMixin, BaseEntryForm):
    """
    Overnight routine tracking form.
    Tracks dinner, sleep, breakfast, mood, and notes.
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

    # Field ordering: routine fields, then mood, then notes
    field_order = ['dinner', 'bedtime', 'woke_up', 'breakfast', 'mood', 'mood_notes', 'notes']

    def clean(self):
        """Custom validation for overnight form"""
        cleaned_data = super().clean()

        # Ensure at least some data is provided
        required_fields = ['dinner', 'bedtime', 'woke_up', 'breakfast']
        if not any(cleaned_data.get(field) for field in required_fields):
            raise forms.ValidationError("Please fill in at least one field.")

        return cleaned_data

    def get_json_data(self):
        """Convert cleaned_data to JSON-serializable dict for storage."""
        data = {}
        for field_name, value in self.cleaned_data.items():
            # Skip image fields - those are handled separately
            if isinstance(self.fields[field_name], forms.ImageField):
                continue

            # Skip empty values
            if value is None or value == '' or value == []:
                continue

            # Convert list fields (like mood) to comma-separated strings
            if isinstance(value, list):
                data[field_name] = ', '.join(value)
            else:
                data[field_name] = value

        return data
