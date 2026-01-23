from django import forms
from .base import BaseEntryForm


class SchoolDayForm(BaseEntryForm):
    """
    School day tracking form.
    Tracks bathroom, meals, activities, services, and notes.
    """
    PORTION_CHOICES = [
        ('None', 'None'),
        ('Some', 'Some'),
        ('All', 'All'),
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
    
    # Food Log
    snacks = forms.ChoiceField(
        choices=[('', 'Not specified')] + [(c, c) for c in ['None', 'Some', 'All']],
        required=False,
        label="Snacks",
        widget=forms.RadioSelect()
    )
    
    lunch_from_home = forms.ChoiceField(
        choices=[('', 'Not specified')] + [(c, c) for c in ['None', 'Some', 'All']],
        required=False,
        label="Lunch from Home",
        widget=forms.RadioSelect()
    )
    
    other_food = forms.CharField(
        required=False,
        label="Other Food",
        max_length=200,
        widget=forms.TextInput(attrs={
            'placeholder': 'Any other food consumed'
        })
    )
    
    # Inclusion Specials
    inclusion_specials = forms.MultipleChoiceField(
        choices=[
            ('Art', 'Art'),
            ('Music', 'Music'),
            ('Gym', 'Gym'),
            ('Library', 'Library'),
        ],
        required=False,
        label="Inclusion Specials",
        widget=forms.CheckboxSelectMultiple()
    )
    
    inclusion_other = forms.CharField(
        required=False,
        label="Inclusion Specials - Other",
        max_length=200,
        widget=forms.TextInput(attrs={
            'placeholder': 'Other inclusion activities'
        })
    )
    
    # Small Group Specials
    small_group_specials = forms.MultipleChoiceField(
        choices=[
            ('Art', 'Art'),
            ('Music', 'Music'),
            ('Library', 'Library'),
        ],
        required=False,
        label="Small Group Specials",
        widget=forms.CheckboxSelectMultiple()
    )
    
    small_group_other = forms.CharField(
        required=False,
        label="Small Group - Other",
        max_length=200,
        widget=forms.TextInput(attrs={
            'placeholder': 'Other small group activities'
        })
    )
    
    # Related Services
    related_services = forms.MultipleChoiceField(
        choices=[
            ('Speech', 'Speech'),
            ('OT', 'OT'),
        ],
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
    
    additional_notes = forms.CharField(
        required=False,
        label="Additional Notes/Reminders",
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Any additional notes or reminders'
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
