"""
Custom form widgets for Timeline.

Contains specialized widgets for enhanced form input experiences.
"""

from django import forms

from .constants import MOOD_EMOJI_MAP


class MoodGridWidget(forms.CheckboxSelectMultiple):
    """
    Custom widget for mood multi-select grid display.

    Displays mood options in a grid layout with emojis and text labels.
    Touch-friendly design optimized for mobile use.
    """
    template_name = 'timeline/widgets/mood_grid.html'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs['class'] = 'mood-grid'

    def get_context(self, name, value, attrs):
        """Add emoji mapping to the widget context."""
        context = super().get_context(name, value, attrs)
        context['emoji_map'] = MOOD_EMOJI_MAP
        return context
