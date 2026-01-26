"""
Common form field choices used across multiple forms.

Centralizing these choices ensures consistency and makes it easier
to update options across the application.
"""

# =============================================================================
# Portion/Consumption Choices
# =============================================================================

# Full portion choices with blank option (for dropdown/select fields)
PORTION_CHOICES_WITH_BLANK = [
    ('', '-- Select --'),
    ('None', 'None'),
    ('Some', 'Some'),
    ('Most', 'Most'),
    ('All', 'All'),
]

# Simple portion choices without "Most" (for radio buttons)
PORTION_CHOICES_SIMPLE = [
    ('None', 'None'),
    ('Some', 'Some'),
    ('All', 'All'),
]

# Portion choices with "Not specified" blank (for optional radio buttons)
PORTION_CHOICES_RADIO = [
    ('', 'Not specified'),
    ('None', 'None'),
    ('Some', 'Some'),
    ('All', 'All'),
]


# =============================================================================
# Time Choices
# =============================================================================

TIME_CHOICES = [
    ('', '-- Select --'),
    ('Early', 'Early'),
    ('Normal', 'Normal'),
    ('Late', 'Late'),
]


# =============================================================================
# School Activity Choices
# =============================================================================

INCLUSION_SPECIALS_CHOICES = [
    ('Art', 'Art'),
    ('Music', 'Music'),
    ('Gym', 'Gym'),
    ('Library', 'Library'),
]

SMALL_GROUP_SPECIALS_CHOICES = [
    ('Art', 'Art'),
    ('Music', 'Music'),
    ('Library', 'Library'),
]

RELATED_SERVICES_CHOICES = [
    ('Speech', 'Speech'),
    ('OT', 'OT'),
]
