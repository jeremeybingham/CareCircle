from django import forms

from .base import BaseEntryForm
from .constants import (
    INCLUSION_SPECIALS_CHOICES,
    RELATED_SERVICES_CHOICES,
    SMALL_GROUP_SPECIALS_CHOICES,
)
from .mixins import MealFieldMixin, MoodFieldMixin


class SchoolDayForm(MealFieldMixin, MoodFieldMixin, BaseEntryForm):
    """
    School day tracking form.
    Tracks bathroom, meals, activities, services, mood, and notes.

    Meal fields (snack_portion, snack_food, lunch_portion, lunch_food)
    are injected by MealFieldMixin using standardized PORTION_CHOICES.
    """

    meal_fields = ['snack', 'lunch']
    meal_labels = {'snack': 'Snacks', 'lunch': 'Lunch from Home'}

    # Field ordering: mood at the bottom, after all other fields
    field_order = [
        'bathroom',
        'snack_portion', 'snack_food',
        'lunch_portion', 'lunch_food',
        'other_food',
        'inclusion_specials',
        'small_group_specials',
        'related_services', 'related_other',
        'notes_about_day',
        'mood',
    ]

    # Bathroom
    bathroom = forms.CharField(
        required=False,
        label="Bathroom Times",
        max_length=200,
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g., 11:00, 10:40, 1:00'
        }),
        help_text="Enter times separated by commas or spaces"
    )

    # Other Food (catch-all for food not covered by snack/lunch)
    other_food = forms.CharField(
        required=False,
        label="Other Food",
        max_length=200,
        widget=forms.TextInput(attrs={
            'placeholder': 'Any other food?'
        })
    )

    # Inclusion Specials
    inclusion_specials = forms.MultipleChoiceField(
        choices=INCLUSION_SPECIALS_CHOICES,
        required=False,
        label="Inclusion Specials",
        widget=forms.CheckboxSelectMultiple()
    )

    # Small Group Specials
    small_group_specials = forms.MultipleChoiceField(
        choices=SMALL_GROUP_SPECIALS_CHOICES,
        required=False,
        label="Small Group Specials",
        widget=forms.CheckboxSelectMultiple()
    )

    # Related Services
    related_services = forms.MultipleChoiceField(
        choices=RELATED_SERVICES_CHOICES,
        required=False,
        label="Related Services",
        widget=forms.CheckboxSelectMultiple()
    )

    related_other = forms.CharField(
        required=False,
        label="Related Services - Other",
        max_length=200,
        widget=forms.TextInput(attrs={
            'placeholder': 'Other services'
        })
    )

    # Notes
    notes_about_day = forms.CharField(
        required=False,
        label="Notes About My Day",
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': 'How was the day?'
        })
    )

    def get_json_data(self):
        """
        Override to convert MultipleChoiceField lists to comma-separated strings
        for consistency with the display templates
        """
        data = {}
        for field_name, value in self.cleaned_data.items():
            if value is None or value == '':
                continue

            # Convert list fields to comma-separated strings
            if isinstance(value, list):
                if value:  # Only include if not empty list
                    data[field_name] = ', '.join(value)
            else:
                data[field_name] = value

        return data
