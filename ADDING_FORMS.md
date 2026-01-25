# Adding New Forms to Timeline

This guide shows you how to add a new form type to the Timeline application.

## Overview

Adding a new form requires:
1. Creating a Django Form class
2. Registering it in the form registry
3. Running the init command
4. Creating a display template
5. Granting user access (via admin)

## Step-by-Step Guide

### Step 1: Create the Form Class

Create a new file in `timeline/forms/` (e.g., `mood.py`):

```python
from django import forms
from .base import BaseEntryForm


class MoodForm(BaseEntryForm):
    """Track daily mood and energy levels"""
    
    mood = forms.ChoiceField(
        choices=[
            ('happy', 'Happy'),
            ('okay', 'Okay'),
            ('sad', 'Sad'),
            ('stressed', 'Stressed'),
        ],
        required=True,
        label="How are you feeling?",
    )
    
    energy = forms.IntegerField(
        min_value=1,
        max_value=10,
        required=True,
        label="Energy Level (1-10)",
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3}),
        label="Notes",
    )
```

### Step 2: Register the Form

Edit `timeline/forms/registry.py`:

```python
# Add import at top
from .mood import MoodForm

# Add to FORM_REGISTRY dictionary
FORM_REGISTRY = {
    # ... existing forms ...
    'mood': {
        'form_class': MoodForm,
        'name': 'Mood Check',
        'icon': '😊',
        'description': 'Track your daily mood and energy',
    },
}
```

### Step 3: Update Forms __init__.py

Edit `timeline/forms/__init__.py`:

```python
# Add import
from .mood import MoodForm

# Add to __all__
__all__ = [
    # ... existing forms ...
    'MoodForm',
]
```

### Step 4: Initialize in Database

Run the management command:

```bash
python manage.py init_forms
```

This creates a FormType record in the database.

### Step 5: Create Display Template

Create `timeline/templates/timeline/partials/entry_mood.html`:

```django
<div class="timeline-content">
    <h2 class="timeline-title">
        <span class="timeline-icon">{{ entry.form_type.icon }}</span>
        Mood Check
    </h2>
    
    <div class="data-list">
        <p><strong>Feeling:</strong> {{ entry.data.mood|title }}</p>
        <p><strong>Energy:</strong> {{ entry.data.energy }}/10</p>
        {% if entry.data.notes %}
        <p><strong>Notes:</strong> {{ entry.data.notes }}</p>
        {% endif %}
    </div>
    
    <span class="timeline-timestamp">{{ entry.timestamp|date:"M d, Y g:i A" }}</span>
</div>
```

### Step 6: Grant Access (Admin)

1. Go to `/admin/`
2. Navigate to **Form Types**
3. Find your new form (Mood Check)
4. Optionally mark as **"is_default"** for auto-access
5. Go to **User Form Access**
6. Grant access to users

Done! The new form will now appear in the FAB menu.

## Form Field Types

Common Django form fields:

```python
# Text input
title = forms.CharField(max_length=200, required=True)

# Long text
content = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}))

# Number
rating = forms.IntegerField(min_value=1, max_value=5)

# Dropdown
category = forms.ChoiceField(choices=[...])

# Multiple checkboxes
activities = forms.MultipleChoiceField(
    choices=[...],
    widget=forms.CheckboxSelectMultiple()
)

# Radio buttons
priority = forms.ChoiceField(
    choices=[...],
    widget=forms.RadioSelect()
)

# Image upload
photo = forms.ImageField(required=False)

# Date
date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
```

## Display Template Patterns

### Simple Data List
```django
<div class="data-list">
    <p><strong>Field 1:</strong> {{ entry.data.field1 }}</p>
    <p><strong>Field 2:</strong> {{ entry.data.field2 }}</p>
</div>
```

### Grid Layout
```django
<div class="data-grid">
    <div class="data-item">
        <span class="data-label">Label</span>
        <span class="data-value">{{ entry.data.value }}</span>
    </div>
</div>
```

### Tags
```django
<div class="tag-list">
    {% for item in entry.data.items|split_commas %}
    <span class="tag">{{ item }}</span>
    {% endfor %}
</div>
```

### With Image
```django
{% if entry.image %}
<img src="{{ entry.image.url }}" alt="Image" class="timeline-image">
{% endif %}
```

## Custom Validation

Add validation in your form class:

```python
def clean_energy(self):
    energy = self.cleaned_data.get('energy')
    if energy and energy > 10:
        raise forms.ValidationError("Energy cannot exceed 10")
    return energy

def clean(self):
    """Cross-field validation"""
    cleaned_data = super().clean()
    mood = cleaned_data.get('mood')
    energy = cleaned_data.get('energy')
    
    if mood == 'happy' and energy < 5:
        raise forms.ValidationError(
            "If you're happy, energy should be at least 5"
        )
    
    return cleaned_data
```

## Custom Data Serialization

Override `get_json_data()` in your form:

```python
def get_json_data(self):
    """Convert checkbox lists to comma-separated strings"""
    data = {}
    for field_name, value in self.cleaned_data.items():
        if isinstance(value, list):
            data[field_name] = ', '.join(value)
        elif value is not None:
            data[field_name] = value
    return data
```

## Testing Your Form

```python
# In Django shell
from timeline.forms import MoodForm

# Test valid data
form = MoodForm(data={
    'mood': 'happy',
    'energy': 8,
    'notes': 'Great day!'
})

print(form.is_valid())  # Should be True
print(form.cleaned_data)
print(form.get_json_data())

# Test invalid data
form = MoodForm(data={
    'mood': 'invalid',
    'energy': 15,
})

print(form.is_valid())  # Should be False
print(form.errors)
```

## Styling

Add custom CSS in `timeline/static/timeline/css/style.css`:

```css
/* Mood form styling */
.timeline-mood {
    border-left: 3px solid #3b82f6;
}

.timeline-mood .data-list p {
    padding: 10px;
}
```

## Troubleshooting

**Form not appearing:**
- Check `python manage.py init_forms` was run
- Verify FormType exists in admin and `is_active=True`
- Check user has UserFormAccess

**Form validation errors:**
- Check required fields are provided
- Verify field types match (CharField, IntegerField, etc.)
- Look at form.errors in Django shell

**Display not working:**
- Check template filename matches form type exactly
- Verify template is in `timeline/partials/` directory
- Check for template syntax errors in server logs

## Quick Reference

**File checklist:**
- [ ] `timeline/forms/newform.py` - Form class
- [ ] `timeline/forms/registry.py` - Add to FORM_REGISTRY
- [ ] `timeline/forms/__init__.py` - Add to imports and __all__
- [ ] `timeline/partials/entry_newform.html` - Display template
- [ ] Run `python manage.py init_forms`
- [ ] Grant access in admin

**Registry entry format:**
```python
'formtype': {
    'form_class': FormClass,
    'name': 'Display Name',
    'icon': '🎯',
    'description': 'What this form does',
}
```

That's it! The system handles the rest automatically.
