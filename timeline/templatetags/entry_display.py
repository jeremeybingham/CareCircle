from django import template
from django.template.loader import render_to_string
from django.template import TemplateDoesNotExist
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag(takes_context=True)
def render_entry(context, entry):
    """
    Render an entry using the appropriate template for its type.
    
    Tries to load a type-specific template (e.g., 'entry_overnight.html'),
    falls back to default template if not found.
    
    Usage in templates:
        {% load entry_display %}
        {% render_entry entry %}
    """
    # Try type-specific template first
    template_name = f'timeline/partials/entry_{entry.type}.html'
    
    try:
        html = render_to_string(template_name, {
            'entry': entry,
            'user': context.get('user'),
        })
    except TemplateDoesNotExist:
        # Fall back to default template
        html = render_to_string('timeline/partials/entry_default.html', {
            'entry': entry,
            'user': context.get('user'),
        })
    
    return mark_safe(html)


@register.filter(name='split_commas')
def split_commas(value):
    """
    Split a comma-separated string into a list.
    
    Usage:
        {% for item in my_string|split_commas %}
            {{ item }}
        {% endfor %}
    """
    if not value:
        return []
    return [item.strip() for item in str(value).split(',') if item.strip()]


@register.filter(name='get_item')
def get_item(dictionary, key):
    """
    Get an item from a dictionary by key.

    Usage:
        {{ my_dict|get_item:"key_name" }}
    """
    if not dictionary:
        return None
    return dictionary.get(key)


@register.filter(name='format_date')
def format_date(value):
    """
    Format a date/datetime as 'Monday, January 1'.

    Usage:
        {{ entry.timestamp|format_date }}
    """
    if not value:
        return ''
    return value.strftime('%A, %B %-d')


@register.filter(name='get_date')
def get_date(value):
    """
    Extract just the date from a datetime.

    Usage:
        {{ entry.timestamp|get_date }}
    """
    if not value:
        return None
    if hasattr(value, 'date'):
        return value.date()
    return value


@register.simple_tag
def should_show_date_divider(entries, current_index):
    """
    Determine if a date divider should be shown before the current entry.
    Returns True if this is the first entry or if the date differs from previous.

    Usage:
        {% should_show_date_divider page_obj forloop.counter0 as show_divider %}
    """
    if current_index == 0:
        return True

    current_entry = entries[current_index]
    previous_entry = entries[current_index - 1]

    current_date = current_entry.timestamp.date()
    previous_date = previous_entry.timestamp.date()

    return current_date != previous_date
