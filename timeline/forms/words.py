from django import forms
from .base import BaseEntryForm


class WordsForm(BaseEntryForm):
    """
    Form for tracking new words and phrases.
    Allows entering comma-separated words/phrases that display as colorful badges.
    """
    words = forms.CharField(
        required=True,
        label="Words and Phrases",
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter words/phrases separated by commas',
            'class': 'form-control'
        }),
        help_text="Separate each word or phrase with a comma (e.g., 'hello, bye bye, more please')"
    )

    def clean_words(self):
        """Ensure words field is not empty or just whitespace"""
        words = self.cleaned_data.get('words', '').strip()
        if not words:
            raise forms.ValidationError("Please enter at least one word or phrase.")
        return words
