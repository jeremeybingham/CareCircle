from django import forms

from .base import BaseEntryForm
from .constants import TIME_CHOICES
from .mixins import MealFieldMixin, MoodFieldMixin


class OvernightForm(MealFieldMixin, MoodFieldMixin, BaseEntryForm):
    """
    Overnight routine tracking form.
    Tracks dinner, sleep, breakfast, mood, and notes.

    Meal fields (dinner_portion, dinner_food, breakfast_portion, breakfast_food)
    are injected by MealFieldMixin using standardized PORTION_CHOICES.
    """

    meal_fields = ['dinner', 'breakfast']
    meal_labels = {'dinner': 'Dinner Last Night'}

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

    notes = forms.CharField(
        required=False,
        label="Notes",
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Any additional notes about your night/morning...'
        })
    )

    # Field ordering: dinner, sleep routine, breakfast, notes, then mood at bottom
    field_order = [
        'dinner_portion', 'dinner_food',
        'bedtime', 'woke_up',
        'breakfast_portion', 'breakfast_food',
        'notes',
        'mood',
    ]

    def clean(self):
        """Custom validation for overnight form"""
        cleaned_data = super().clean()

        # Ensure at least some data is provided
        required_fields = ['dinner_portion', 'bedtime', 'woke_up', 'breakfast_portion']
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
