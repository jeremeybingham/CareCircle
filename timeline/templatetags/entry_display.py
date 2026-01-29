import ast

from django import template
from django.template.loader import render_to_string
from django.template import TemplateDoesNotExist
from django.utils import timezone as tz
from django.utils.safestring import mark_safe

from timeline.forms.constants import MOOD_EMOJI_MAP

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
    Also handles Python list representations (e.g., "['Happy', 'Energetic']").

    For space-separated values, only splits if content looks like time entries
    (contains ':'), to preserve multi-word phrases like "hello world".

    Usage:
        {% for item in my_string|split_commas %}
            {{ item }}
        {% endfor %}
    """
    if not value:
        return []

    # Handle actual Python lists
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]

    value_str = str(value)

    # Handle Python list string representation (e.g., "['Happy', 'Energetic']")
    if value_str.startswith('[') and value_str.endswith(']'):
        try:
            parsed = ast.literal_eval(value_str)
            if isinstance(parsed, list):
                return [str(item).strip() for item in parsed if str(item).strip()]
        except (ValueError, SyntaxError):
            pass

    # Split by comma first (primary delimiter for phrases)
    if ',' in value_str:
        return [item.strip() for item in value_str.split(',') if item.strip()]

    # Split by space only if it looks like time entries (contains ':')
    # This preserves multi-word phrases like "hello world" as single items
    if ':' in value_str:
        return [item.strip() for item in value_str.split() if item.strip()]

    # No commas and not time entries - return as single item
    return [value_str.strip()] if value_str.strip() else []


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
    Converts to local timezone before formatting.

    Usage:
        {{ entry.timestamp|format_date }}
    """
    if not value:
        return ''
    if hasattr(value, 'tzinfo') and value.tzinfo is not None:
        value = tz.localtime(value)
    return value.strftime('%A, %B %-d')


@register.filter(name='get_date')
def get_date(value):
    """
    Extract just the date from a datetime.
    Converts to local timezone before extracting.

    Usage:
        {{ entry.timestamp|get_date }}
    """
    if not value:
        return None
    if hasattr(value, 'date'):
        if hasattr(value, 'tzinfo') and value.tzinfo is not None:
            value = tz.localtime(value)
        return value.date()
    return value


@register.simple_tag
def should_show_date_divider(entries, current_index):
    """
    Determine if a date divider should be shown before the current entry.
    Returns True if this is the first non-pinned entry or if the date differs from previous.
    Pinned entries never show date dividers (their dates can be confusing when old).

    Usage:
        {% should_show_date_divider page_obj forloop.counter0 as show_divider %}
    """
    current_entry = entries[current_index]

    # Never show date divider for pinned entries
    if current_entry.is_pinned:
        return False

    # Show divider for first entry or first non-pinned entry after pinned section
    if current_index == 0:
        return True

    previous_entry = entries[current_index - 1]

    # Show divider when transitioning from pinned to non-pinned
    if previous_entry.is_pinned:
        return True

    current_date = tz.localtime(current_entry.timestamp).date()
    previous_date = tz.localtime(previous_entry.timestamp).date()

    return current_date != previous_date


@register.filter(name='mood_emoji')
def mood_emoji(mood_key):
    """
    Get the emoji for a mood key.

    Usage:
        {{ "happy"|mood_emoji }}  -> 😊
        {{ mood|mood_emoji }}
    """
    if not mood_key:
        return ''
    return MOOD_EMOJI_MAP.get(mood_key.strip().lower(), '')


@register.filter(name='previous_day_abbrev')
def previous_day_abbrev(value):
    """
    Get the abbreviated name of the previous day.
    Converts to local timezone before extracting the date.

    For a morning report on Tuesday, returns "Mon" (for Monday's dinner).
    For a morning report on Saturday, returns "Fri" (for Friday's dinner).

    Usage:
        {{ entry.timestamp|previous_day_abbrev }} Dinner
        -> "Mon Dinner" (if entry is on Tuesday)
    """
    from datetime import timedelta
    if not value:
        return ''
    if hasattr(value, 'date'):
        if hasattr(value, 'tzinfo') and value.tzinfo is not None:
            value = tz.localtime(value)
        date = value.date()
    else:
        date = value
    previous_day = date - timedelta(days=1)
    return previous_day.strftime('%a')
