# Timeline - TODO List

## Planned Features and Improvements

### 1. Enhanced User Registration Fields

**Goal**: Extend user registration to capture additional profile information.

**New Fields to Add**:
- `display_name` - Name shown on posts (e.g., "Ms. Johnson")
- `email_address` - Contact email
- `position_role` - Job title/role (e.g., "Teacher", "Parent", "Administrator")
- `first_name` - User's first name
- `last_name` - User's last name

**Implementation Steps**:
- [ ] Create a `UserProfile` model with these fields (or extend User model)
- [ ] Update `SignupView` to include custom registration form
- [ ] Create custom registration form class extending `UserCreationForm`
- [ ] Update signup template to display new fields
- [ ] Add validation for email uniqueness and format
- [ ] Update admin interface to show/edit profile fields

**Files to Modify**:
- `timeline/models.py` - Add UserProfile model
- `timeline/forms/` - Create user registration form
- `timeline/views.py` - Update SignupView
- `timeline/templates/timeline/auth/signup.html` - Update form
- `timeline/admin.py` - Add UserProfile admin

---

### 2. Display User Name on Posts

**Goal**: Show the author's display name on each timeline entry.

**Changes**:
- Display `display_name` next to or below the timestamp on each post
- Format: "Posted by [Display Name] on [Date/Time]"
- Alternative format: "[Date/Time]" on one line, "by [Display Name]" below

**Implementation Steps**:
- [ ] Update entry display templates to include user display name
- [ ] Modify timeline query to select related user profile
- [ ] Add CSS styling for author attribution
- [ ] Ensure display name shows in all entry type templates

**Files to Modify**:
- `timeline/templates/timeline/partials/entry_default.html`
- `timeline/templates/timeline/partials/entry_text.html`
- `timeline/templates/timeline/partials/entry_photo.html`
- `timeline/templates/timeline/partials/entry_overnight.html`
- `timeline/templates/timeline/partials/entry_schoolday.html`
- `timeline/views.py` - Update query in TimelineListView
- `timeline/static/timeline/css/style.css` - Add author styling

**Example Template Change**:
```django
<span class="timeline-timestamp">
    {{ entry.timestamp|date:"M d, Y g:i A" }}
</span>
<span class="timeline-author">
    by {{ entry.user.profile.display_name }}
</span>
```

---

### 3. Create "Weekend" Form Type

**Goal**: Add a new form type for tracking weekend activities.

**Status**: Content/fields to be determined

**Potential Fields** (placeholder ideas):
- Weekend activities/events
- Meals
- Sleep schedule
- Highlights/notes
- Photos

**Implementation Steps**:
- [ ] Define form fields and structure
- [ ] Create `timeline/forms/weekend.py` with WeekendForm class
- [ ] Add to `timeline/forms/registry.py`
- [ ] Update `timeline/forms/__init__.py`
- [ ] Create display template: `timeline/templates/timeline/partials/entry_weekend.html`
- [ ] Run `python manage.py init_forms`
- [ ] Test form submission and display
- [ ] Add CSS styling for weekend entries

**Files to Create/Modify**:
- `timeline/forms/weekend.py` - NEW
- `timeline/forms/registry.py` - Add weekend to FORM_REGISTRY
- `timeline/forms/__init__.py` - Add WeekendForm import
- `timeline/templates/timeline/partials/entry_weekend.html` - NEW
- `timeline/static/timeline/css/style.css` - Add .timeline-weekend styles

**Registry Entry**:
```python
'weekend': {
    'form_class': WeekendForm,
    'name': 'Weekend',
    'icon': '🎉',  # or '📅' or '🌞'
    'description': 'Track weekend activities and highlights',
},
```

---

### 4. Remove Post Filtering Buttons

**Goal**: Simplify timeline view by removing form type filter buttons. Show all posts by default.

**Changes**:
- Remove filter button UI from top of timeline
- Remove query parameter handling for form filtering
- Display all entries for the user in chronological order

**Implementation Steps**:
- [ ] Remove filter buttons from `timeline/templates/timeline/timeline.html`
- [ ] Remove `current_filter` context variable from TimelineListView
- [ ] Simplify `get_queryset()` to not check for form filter parameter
- [ ] Update pagination links to remove filter parameter
- [ ] Remove filter-related CSS if no longer needed

**Files to Modify**:
- `timeline/templates/timeline/timeline.html` - Remove filter buttons section
- `timeline/views.py` - Simplify TimelineListView.get_queryset()
- `timeline/views.py` - Remove current_filter from get_context_data()
- `timeline/static/timeline/css/style.css` - Clean up filter button styles (optional)

**Template Changes**:
Remove this section from timeline.html:
```django
<div class="filter-buttons">
    <a href="{% url 'timeline:timeline' %}" class="filter-btn {% if not current_filter %}active{% endif %}">All</a>
    {% for form in forms %}
    <a href="?form={{ form.type }}" class="filter-btn {% if current_filter == form.type %}active{% endif %}">
        {{ form.icon }} {{ form.name }}
    </a>
    {% endfor %}
</div>
```

**View Changes**:
```python
def get_queryset(self):
    """Get all entries for current user"""
    return Entry.objects.filter(user=self.request.user).select_related('form_type')

def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['forms'] = FormType.objects.filter(
        user_access__user=self.request.user,
        is_active=True
    ).distinct().order_by('name')
    # Remove: context['current_filter'] = ...
    return context
```

---

## Future Considerations

### Possible Future Enhancements:
- [ ] Entry editing capability
- [ ] Entry deletion with soft delete
- [ ] Date range filtering
- [ ] Mobile app version
- [ ] Email notifications
- [ ] Multi-user timeline sharing
- [ ] Calendar view of entries

---

## Notes

- All changes should maintain backward compatibility where possible
- Run migrations after model changes
- Test all forms after changes
- Update documentation in README.md as features are implemented
- Consider user feedback during implementation
