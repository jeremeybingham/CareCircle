"""
Form field mixins for Timeline.

Contains reusable field groups that can be added to any form.
"""

from django import forms

from .constants import MOOD_CHOICES
from .widgets import MoodGridWidget


class MoodFieldMixin:
    """
    Mixin to add standardized mood tracking fields to any form.

    Provides a multi-select mood grid and optional notes field.

    Usage:
        class MyForm(MoodFieldMixin, BaseEntryForm):
            # mood and mood_notes fields are automatically included
            other_field = forms.CharField()

    The mixin adds these fields:
        - mood: MultipleChoiceField with MoodGridWidget (optional)
        - mood_notes: CharField textarea for additional context (optional)

    Note: The mixin injects fields in __init__ to work around Django's
    form metaclass only collecting fields from actual Form subclasses.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add mood field
        self.fields['mood'] = forms.MultipleChoiceField(
            choices=MOOD_CHOICES,
            required=False,
            label="How was Eddie's mood?",
            widget=MoodGridWidget(),
            help_text="Select all that apply"
        )

        # Add mood_notes field
        self.fields['mood_notes'] = forms.CharField(
            required=False,
            label="Mood notes (optional)",
            widget=forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'Any context about mood or behavior...'
            }),
            help_text="Additional details about mood or behavior"
        )

        # Apply field ordering if specified on the class
        if hasattr(self, 'field_order') and self.field_order:
            self.order_fields(self.field_order)
