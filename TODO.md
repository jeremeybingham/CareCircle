# Timeline - TODO List

## Planned Features and Improvements

### 1. Create "My Weekend" Form Type

**Goal**: Add a new form type for tracking weekend activities with photos and descriptions.

**Form Structure**:
- 3 photo upload fields (one for Friday, Saturday, Sunday)
- 3 short answer text boxes (one for Friday, Saturday, Sunday)
- 1 notes section (textarea for general notes/highlights)

**Implementation Steps**:
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
    'name': 'My Weekend',
    'icon': '🎉',  # or '📅' or '🌞'
    'description': 'Share photos and highlights from your weekend',
},
```

**Form Field Example**:
```python
class WeekendForm(BaseEntryForm):
    # Friday
    friday_photo = forms.ImageField(required=False, label="Friday Photo")
    friday_text = forms.CharField(required=False, label="Friday", max_length=500)

    # Saturday
    saturday_photo = forms.ImageField(required=False, label="Saturday Photo")
    saturday_text = forms.CharField(required=False, label="Saturday", max_length=500)

    # Sunday
    sunday_photo = forms.ImageField(required=False, label="Sunday Photo")
    sunday_text = forms.CharField(required=False, label="Sunday", max_length=500)

    # Notes
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 4}),
        label="Weekend Notes"
    )
```

---

### 2. Remove Post Filtering Buttons

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

## Completed Features

### ✅ Display User Name on Posts
- Added shared `entry_meta.html` partial template for timestamp and author display
- Updated all entry type templates to use the shared partial
- Timeline displays author's display_name next to timestamps
- Format: "Posted by [Display Name] on [Date/Time]"
- Optimized query with `select_related` for user profile data

### ✅ Enhanced User Registration Fields
- Added UserProfile model with display_name, email_address, position_role, first_name, last_name
- Updated SignupView with custom registration form
- Added profile fields to admin interface
- Users can now set display names shown on their posts

### ✅ Shared Timeline View
- All authenticated users see all entries from all users
- Each entry shows author attribution via display name
- Maintains filtering by form type for organization

---

## Notes

- All changes should maintain backward compatibility where possible
- Run migrations after model changes
- Test all forms after changes
- Update documentation in README.md as features are implemented
- Consider user feedback during implementation
