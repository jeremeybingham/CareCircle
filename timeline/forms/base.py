from django import forms
from django.core.exceptions import ValidationError


class BaseEntryForm(forms.Form):
    """
    Base class for all timeline entry forms.
    
    All form fields should be defined in subclasses.
    This base class provides common functionality and cleaned_data handling.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes to all form fields for consistent styling
        for field_name, field in self.fields.items():
            # Add form-control class for styling
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            elif isinstance(field.widget, forms.RadioSelect):
                field.widget.attrs['class'] = 'form-radio'
            else:
                field.widget.attrs['class'] = 'form-control'
            
            # Add placeholder if not set
            if hasattr(field.widget, 'attrs') and 'placeholder' not in field.widget.attrs:
                if field.label:
                    field.widget.attrs['placeholder'] = field.label
    
    def clean(self):
        """
        Base validation. Subclasses can override to add custom validation.
        """
        cleaned_data = super().clean()
        return cleaned_data
    
    def get_json_data(self):
        """
        Convert cleaned_data to JSON-serializable dict for storage.
        Subclasses can override to customize data structure.
        """
        data = {}
        for field_name, value in self.cleaned_data.items():
            # Skip image fields - those are handled separately
            if isinstance(self.fields[field_name], forms.ImageField):
                continue
            
            # Convert to JSON-serializable format
            if value is not None:
                data[field_name] = value
        
        return data
    
    def has_image_field(self):
        """Check if this form has an image field"""
        for field in self.fields.values():
            if isinstance(field, forms.ImageField):
                return True
        return False

    def get_image_data(self):
        """Get the first image file if present (for single-image forms)"""
        for field_name, field in self.fields.items():
            if isinstance(field, forms.ImageField):
                return self.cleaned_data.get(field_name)
        return None

    def has_multiple_images(self):
        """Check if this form has multiple image fields. Override in subclass if needed."""
        return False

    def get_all_images(self):
        """
        Get all image fields with their data.
        Returns dict of {field_name: image_file}
        Override in subclass for custom behavior.
        """
        images = {}
        for field_name, field in self.fields.items():
            if isinstance(field, forms.ImageField):
                image = self.cleaned_data.get(field_name)
                if image:
                    images[field_name] = image
        return images
