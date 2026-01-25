"""
Form Registry - Maps form type identifiers to form classes

This registry is the central mapping between:
1. FormType.type (database identifier like 'overnight')
2. Form class (like OvernightForm)
3. Display metadata (name, icon)

When adding a new form type:
1. Create the form class in forms/
2. Add it to FORM_REGISTRY below
3. Create FormType in admin with matching 'type' value
4. Create display template in templates/timeline/partials/entry_{type}.html
"""

from .text import TextForm
from .photo import PhotoForm
from .overnight import OvernightForm
from .schoolday import SchoolDayForm
from .weekend import WeekendForm


# Registry mapping: type_identifier -> (FormClass, display_name, icon)
FORM_REGISTRY = {
    'text': {
        'form_class': TextForm,
        'name': 'Text Post',
        'icon': '📝',
        'description': 'Create a simple text post with title and content',
    },
    'photo': {
        'form_class': PhotoForm,
        'name': 'Photo',
        'icon': '📸',
        'description': 'Upload a photo with an optional caption',
    },
    'overnight': {
        'form_class': OvernightForm,
        'name': 'Overnight',
        'icon': '🌙',
        'description': 'Track your overnight routine - dinner, sleep, and breakfast',
    },
    'schoolday': {
        'form_class': SchoolDayForm,
        'name': 'School Day',
        'icon': '🎒',
        'description': 'Track daily school activities, meals, specials, and notes',
    },
    'weekend': {
        'form_class': WeekendForm,
        'name': 'My Weekend',
        'icon': '🎉',
        'description': 'Share photos and highlights from your weekend',
    },
}


def get_form_class(form_type):
    """
    Get the form class for a given form type.
    
    Args:
        form_type (str): Form type identifier (e.g., 'overnight')
    
    Returns:
        Form class or None if not found
    """
    form_config = FORM_REGISTRY.get(form_type)
    if form_config:
        return form_config['form_class']
    return None


def get_form_metadata(form_type):
    """
    Get metadata for a form type.
    
    Args:
        form_type (str): Form type identifier
    
    Returns:
        dict with name, icon, description or None
    """
    return FORM_REGISTRY.get(form_type)


def get_all_form_types():
    """
    Get list of all registered form types.
    
    Returns:
        list of form type identifiers
    """
    return list(FORM_REGISTRY.keys())


def is_valid_form_type(form_type):
    """
    Check if a form type is registered.
    
    Args:
        form_type (str): Form type identifier
    
    Returns:
        bool
    """
    return form_type in FORM_REGISTRY


def get_registry_info():
    """
    Get formatted information about all registered forms.
    Useful for documentation or admin display.
    
    Returns:
        list of dicts with form info
    """
    info = []
    for type_id, config in FORM_REGISTRY.items():
        info.append({
            'type': type_id,
            'name': config['name'],
            'icon': config['icon'],
            'description': config['description'],
            'form_class': config['form_class'].__name__,
        })
    return info
