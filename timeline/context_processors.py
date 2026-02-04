"""
Context processors for Timeline app.

These functions add variables to the template context for all requests.
"""

from .models import ChildProfile


def child_profile(request):
    """
    Add child profile information to all template contexts.

    This allows templates to access the child's name and other profile
    data without each view needing to explicitly pass it.

    Returns:
        dict with:
            - child_name: The child's name (or "Timeline" if not set)
            - child_name_possessive: Possessive form (e.g., "Eddie's" or "Timeline")
    """
    try:
        profile = ChildProfile.get_instance()
        name = profile.child_name if profile.child_name else "Timeline"
        # Create possessive form
        if name and name != "Timeline":
            possessive = f"{name}'s"
        else:
            possessive = name
    except Exception:
        # Fallback if database isn't ready or other issues
        name = "Timeline"
        possessive = "Timeline"

    return {
        'child_name': name,
        'child_name_possessive': possessive,
    }
