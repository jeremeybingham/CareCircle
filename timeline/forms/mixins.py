"""
Form field mixins for Timeline.

Contains reusable field groups that can be added to any form.
"""

from django import forms
from django.utils.safestring import mark_safe

from .constants import MOOD_CHOICES, PORTION_CHOICES
from .widgets import MoodGridWidget


class MealFieldMixin:
    """
    Mixin to add standardized meal tracking fields to any form.

    Each meal gets a portion radio field (using PORTION_CHOICES) and an
    optional "Type of Food" text field, ensuring consistent data capture
    across all forms for reporting and analytics.

    Usage:
        class MyForm(MealFieldMixin, MoodFieldMixin, BaseEntryForm):
            meal_fields = ['dinner', 'breakfast']
            meal_labels = {'dinner': 'Dinner Last Night'}

    The mixin adds these fields for each meal in meal_fields:
        - {meal}_portion: ChoiceField with RadioSelect (PORTION_CHOICES)
        - {meal}_food: CharField for type of food (optional)

    """

    meal_fields = []
    meal_labels = {}

    DEFAULT_MEAL_LABELS = {
        'dinner': 'Dinner',
        'breakfast': 'Breakfast',
        'lunch': 'Lunch',
        'snack': 'Snack',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for meal in self.meal_fields:
            label = self.meal_labels.get(
                meal, self.DEFAULT_MEAL_LABELS.get(meal, meal.title())
            )

            self.fields[f'{meal}_portion'] = forms.ChoiceField(
                choices=PORTION_CHOICES,
                required=False,
                label=label,
                widget=forms.RadioSelect(),
            )

            self.fields[f'{meal}_food'] = forms.CharField(
                required=False,
                label=f"{label} - Notes",
                max_length=200,
                widget=forms.TextInput(attrs={
                    'placeholder': 'Any notes?'
                }),
            )

        # Apply field ordering if specified on the class
        if hasattr(self, 'field_order') and self.field_order:
            self.order_fields(self.field_order)


class MoodFieldMixin:
    """
    Mixin to add standardized mood tracking fields to any form.

    Provides a multi-select mood grid.

    Usage:
        class MyForm(MoodFieldMixin, BaseEntryForm):
            # mood field is automatically included
            other_field = forms.CharField()

    The mixin adds:
        - mood: MultipleChoiceField with MoodGridWidget (optional)

    Note: The mixin injects fields in __init__ to work around Django's
    form metaclass only collecting fields from actual Form subclasses.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add mood field
        self.fields['mood'] = forms.MultipleChoiceField(
            choices=MOOD_CHOICES,
            required=False,
            label=mark_safe(
                'How was their mood?'
                ' <span class="mood-hint">Select all that apply</span>'
            ),
            widget=MoodGridWidget(),
        )

        # Apply field ordering if specified on the class
        if hasattr(self, 'field_order') and self.field_order:
            self.order_fields(self.field_order)
