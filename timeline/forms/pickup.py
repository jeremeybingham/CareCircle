from django import forms

from .base import BaseEntryForm
from .constants import PORTION_CHOICES_RADIO
from .mixins import MoodFieldMixin


# Time choices for pickup/dropoff times
PICKUP_TIME_CHOICES = [
    ('', '-- Select --'),
    ('11:00 AM', '11:00 AM'),
    ('11:30 AM', '11:30 AM'),
    ('12:00 PM', '12:00 PM'),
    ('12:30 PM', '12:30 PM'),
    ('1:00 PM', '1:00 PM'),
    ('1:30 PM', '1:30 PM'),
    ('2:00 PM', '2:00 PM'),
    ('2:30 PM', '2:30 PM'),
    ('3:00 PM', '3:00 PM'),
    ('3:30 PM', '3:30 PM'),
    ('4:00 PM', '4:00 PM'),
    ('4:30 PM', '4:30 PM'),
    ('5:00 PM', '5:00 PM'),
    ('5:30 PM', '5:30 PM'),
    ('6:00 PM', '6:00 PM'),
]

# Common pickup/dropoff locations
LOCATION_CHOICES = [
    ('', '-- Select --'),
    ('School', 'School'),
    ('Home', 'Home'),
    ('Other', 'Other (specify in notes)'),
]


class PickupForm(MoodFieldMixin, BaseEntryForm):
    """
    Form for tracking pickup and dropoff information.
    Useful for babysitters, family members, or other caregivers
    who pick up and drop off Eddie.
    """

    # Pickup section
    pickup_time = forms.ChoiceField(
        choices=PICKUP_TIME_CHOICES,
        required=True,
        label="Pickup Time",
    )

    pickup_location = forms.ChoiceField(
        choices=LOCATION_CHOICES,
        required=True,
        label="Pickup Location",
    )

    # Activity notes
    stops_notes = forms.CharField(
        required=False,
        label="Any stops or activities?",
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Did you make any stops? What did you do together?'
        })
    )

    # Lunch/snack section
    had_lunch = forms.BooleanField(
        required=False,
        label="Had lunch or snack?",
        help_text="Check if Eddie had a meal during your time together"
    )

    lunch_portion = forms.ChoiceField(
        choices=PORTION_CHOICES_RADIO,
        required=False,
        label="How much did he eat?",
        widget=forms.RadioSelect(),
    )

    lunch_notes = forms.CharField(
        required=False,
        label="Lunch/snack notes",
        widget=forms.Textarea(attrs={
            'rows': 2,
            'placeholder': 'What did he eat? Any preferences noted?'
        })
    )

    # Dropoff section
    dropoff_time = forms.ChoiceField(
        choices=PICKUP_TIME_CHOICES,
        required=False,
        label="Dropoff Time",
    )

    dropoff_location = forms.ChoiceField(
        choices=LOCATION_CHOICES,
        required=False,
        label="Dropoff Location",
    )

    # Field ordering
    field_order = [
        'pickup_time',
        'pickup_location',
        'stops_notes',
        'had_lunch',
        'lunch_portion',
        'lunch_notes',
        'mood',
        'mood_notes',
        'dropoff_time',
        'dropoff_location',
    ]

    def clean(self):
        """Custom validation for pickup form."""
        cleaned_data = super().clean()

        # If had_lunch is checked, lunch_portion is encouraged but not required
        had_lunch = cleaned_data.get('had_lunch')
        lunch_portion = cleaned_data.get('lunch_portion')

        # Clear lunch fields if no lunch was had
        if not had_lunch:
            cleaned_data['lunch_portion'] = ''
            cleaned_data['lunch_notes'] = ''

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

            # Convert boolean to string for JSON storage consistency
            if isinstance(value, bool):
                data[field_name] = value

            # Convert list fields (like mood) to comma-separated strings
            elif isinstance(value, list):
                data[field_name] = ', '.join(value)
            else:
                data[field_name] = value

        return data
