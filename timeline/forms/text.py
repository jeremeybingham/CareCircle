from django import forms

from .base import BaseEntryForm
from .mixins import MoodFieldMixin


class TextForm(MoodFieldMixin, BaseEntryForm):
    """
    Plain text post form.
    Simple title and content fields for text-based entries.
    Includes optional mood tracking.
    """
    title = forms.CharField(
        max_length=200,
        required=True,
        label="Title",
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter a title...'
        })
    )

    content = forms.CharField(
        required=True,
        label="Content",
        widget=forms.Textarea(attrs={
            'rows': 6,
            'placeholder': 'Write your post...'
        })
    )

    # Field ordering: title, content, then mood fields
    field_order = ['title', 'content', 'mood', 'mood_notes']

    def clean_title(self):
        """Ensure title is not empty or just whitespace"""
        title = self.cleaned_data.get('title', '').strip()
        if not title:
            raise forms.ValidationError("Title cannot be empty.")
        return title

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
