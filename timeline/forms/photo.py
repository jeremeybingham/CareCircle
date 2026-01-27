from django import forms
from .base import BaseEntryForm
from .mixins import MoodFieldMixin


class PhotoForm(MoodFieldMixin, BaseEntryForm):
    """
    Photo with caption form.
    Allows users to upload an image with an optional caption and mood tracking.
    """

    # Field ordering
    field_order = ['image', 'caption', 'mood', 'mood_notes']

    image = forms.ImageField(
        required=True,
        label="Photo",
        help_text="Upload a photo (JPG, PNG, GIF, or WebP)",
        widget=forms.FileInput(attrs={
            'accept': 'image/*'
        })
    )
    
    caption = forms.CharField(
        max_length=500,
        required=False,
        label="Caption",
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Add a caption (optional)...'
        })
    )
    
    def clean_image(self):
        """Validate image file"""
        image = self.cleaned_data.get('image')
        
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
