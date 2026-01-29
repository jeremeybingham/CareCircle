from django import forms

from .base import BaseEntryForm
from .mixins import MealFieldMixin, MoodFieldMixin


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
    ('ABA', 'ABA'),
    ('Other', 'Other (specify in notes)'),
]


class PickupForm(MealFieldMixin, MoodFieldMixin, BaseEntryForm):
    """
    Form for tracking pickup and dropoff information.
    Useful for babysitters, family members, or other caregivers
    who pick up and drop off Eddie.

    Meal fields (lunch_portion, lunch_food) are injected by MealFieldMixin
    using standardized PORTION_CHOICES. The "Not specified" option replaces
    the old had_lunch boolean toggle.
    """

    meal_fields = ['lunch']
    meal_labels = {'lunch': 'Lunch/Snack'}

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

    # Field ordering: mood at the bottom, after all other fields
    field_order = [
        'pickup_time',
        'pickup_location',
        'stops_notes',
        'lunch_portion',
        'lunch_food',
        'dropoff_time',
        'dropoff_location',
        'mood',
    ]

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
