from django import forms
from .base import BaseEntryForm
from .mixins import MoodFieldMixin


class WeekendForm(MoodFieldMixin, BaseEntryForm):
    """
    Weekend summary form with photos and descriptions for Friday, Saturday, Sunday.
    Allows users to share photos and highlights from their weekend.
    """

    # Field ordering to put mood at the end
    field_order = [
        'friday_photo', 'friday_text',
        'saturday_photo', 'saturday_text',
        'sunday_photo', 'sunday_text',
        'notes',
        'mood', 'mood_notes',
    ]

    # Friday
    friday_photo = forms.ImageField(
        required=False,
        label="Friday Photo",
        help_text="Upload a photo from Friday",
        widget=forms.FileInput(attrs={
            'accept': 'image/*'
        })
    )
    friday_text = forms.CharField(
        required=False,
        label="Friday",
        max_length=500,
        widget=forms.TextInput(attrs={
            'placeholder': 'What happened on Friday?'
        })
    )

    # Saturday
    saturday_photo = forms.ImageField(
        required=False,
        label="Saturday Photo",
        help_text="Upload a photo from Saturday",
        widget=forms.FileInput(attrs={
            'accept': 'image/*'
        })
    )
    saturday_text = forms.CharField(
        required=False,
        label="Saturday",
        max_length=500,
        widget=forms.TextInput(attrs={
            'placeholder': 'What happened on Saturday?'
        })
    )

    # Sunday
    sunday_photo = forms.ImageField(
        required=False,
        label="Sunday Photo",
        help_text="Upload a photo from Sunday",
        widget=forms.FileInput(attrs={
            'accept': 'image/*'
        })
    )
    sunday_text = forms.CharField(
        required=False,
        label="Sunday",
        max_length=500,
        widget=forms.TextInput(attrs={
            'placeholder': 'What happened on Sunday?'
        })
    )

    # Notes
    notes = forms.CharField(
        required=False,
        label="Weekend Notes",
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': 'Any other highlights or notes from the weekend...'
        })
    )

    def clean(self):
        """Validate that at least some content is provided"""
        cleaned_data = super().clean()

        # Check if at least one field has content
        has_content = any([
            cleaned_data.get('friday_photo'),
            cleaned_data.get('friday_text'),
            cleaned_data.get('saturday_photo'),
            cleaned_data.get('saturday_text'),
            cleaned_data.get('sunday_photo'),
            cleaned_data.get('sunday_text'),
            cleaned_data.get('notes'),
            cleaned_data.get('mood'),
        ])

        if not has_content:
            raise forms.ValidationError(
                "Please add at least one photo, description, or note."
            )

        return cleaned_data

    def clean_friday_photo(self):
        """Validate Friday photo"""
        return self._validate_image(self.cleaned_data.get('friday_photo'))

    def clean_saturday_photo(self):
        """Validate Saturday photo"""
        return self._validate_image(self.cleaned_data.get('saturday_photo'))

    def clean_sunday_photo(self):
        """Validate Sunday photo"""
        return self._validate_image(self.cleaned_data.get('sunday_photo'))

    def _validate_image(self, image):
        """Common image validation"""
        if image:
            # Check file size (limit to 10MB)
            if image.size > 10 * 1024 * 1024:
                raise forms.ValidationError("Image file size cannot exceed 10MB.")

            # Check file extension
            valid_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp']
            ext = image.name.split('.')[-1].lower()
            if ext not in valid_extensions:
                raise forms.ValidationError(
                    f"Invalid file type. Allowed types: {', '.join(valid_extensions)}"
                )

        return image

    def get_all_images(self):
        """
        Get all image fields with their data.
        Returns dict of {field_name: image_file}
        """
        images = {}
        for field_name in ['friday_photo', 'saturday_photo', 'sunday_photo']:
            image = self.cleaned_data.get(field_name)
            if image:
                images[field_name] = image
        return images

    def has_multiple_images(self):
        """Check if this form has multiple image fields"""
        return True
