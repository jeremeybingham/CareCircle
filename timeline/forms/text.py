from django import forms
from .base import BaseEntryForm


class TextForm(BaseEntryForm):
    """
    Plain text post form.
    Simple title and content fields for text-based entries.
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
    
    def clean_title(self):
        """Ensure title is not empty or just whitespace"""
        title = self.cleaned_data.get('title', '').strip()
        if not title:
            raise forms.ValidationError("Title cannot be empty.")
        return title
