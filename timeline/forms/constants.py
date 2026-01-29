"""
Common form field choices used across multiple forms.

Centralizing these choices ensures consistency and makes it easier
to update options across the application.
"""

# =============================================================================
# Portion/Consumption Choices (Standardized)
# =============================================================================

# Standardized portion choices for all meal-related fields (radio buttons).
# Used across all forms: overnight, schoolday, pickup, etc.
# Always paired with an optional text field for "Type of Food".
# See FOOD.md for the standardization specification.
PORTION_CHOICES = [
    ('', 'Not specified'),
    ('None', 'None'),
    ('Some', 'Some'),
    ('Most', 'Most'),
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


# =============================================================================
# Mood Choices (Standardized for all forms)
# =============================================================================

# Mood options with emoji for visual display
# Format: (value, display_label)
# The emoji is stored separately in MOOD_EMOJI_MAP for flexibility
MOOD_CHOICES = [
    ('happy', 'Happy'),
    ('calm', 'Calm'),
    ('energetic', 'Energetic'),
    ('tired', 'Tired'),
    ('sad', 'Sad'),
    ('anxious', 'Anxious'),
    ('frustrated', 'Frustrated'),
    ('silly', 'Silly'),
    ('upset', 'Upset/Angry'),
    ('unwell', 'Not feeling well'),
    ('focused', 'Focused'),
    ('withdrawn', 'Quiet/Withdrawn'),
]

# Emoji mapping for mood display
MOOD_EMOJI_MAP = {
    'happy': '😊',
    'calm': '😌',
    'energetic': '⚡',
    'tired': '😴',
    'sad': '😢',
    'anxious': '😰',
    'frustrated': '😤',
    'silly': '🤪',
    'upset': '😠',
    'unwell': '🤒',
    'focused': '🤔',
    'withdrawn': '😶',
}
