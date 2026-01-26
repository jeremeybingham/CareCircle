# Timeline - TODO List

## Planned Features and Improvements

### 1. Create "About Eddie" Page

**Goal**: Create a dedicated page with information about Eddie and emergency contact details.

**Content Needed**:
- Basic information about Eddie
- Emergency contact information
- Important medical information
- Daily routine/preferences
- Special notes for caregivers

**Implementation Steps**:
- [ ] Create new view: `AboutEddieView`
- [ ] Create template: `timeline/templates/timeline/about_eddie.html`
- [ ] Add URL route to `timeline/urls.py`
- [ ] Add navigation link in main navbar
- [ ] Create admin-editable model for About page content (or use static content)
- [ ] Style page with clear sections
- [ ] Add security: only authenticated users can view
- [ ] Consider printable version for babysitters

**Files to Create/Modify**:
- `timeline/views.py` - Add AboutEddieView - NEW
- `timeline/templates/timeline/about_eddie.html` - NEW
- `timeline/urls.py` - Add route
- `templates/base.html` - Add nav link
- `timeline/models.py` - Optional: AboutPageContent model
- `timeline/static/timeline/css/style.css` - Style about page

**View Example**:
```python
class AboutEddieView(LoginRequiredMixin, TemplateView):
    template_name = 'timeline/about_eddie.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any dynamic content here
        return context
```

**URL Addition**:
```python
path('about/', views.AboutEddieView.as_view(), name='about_eddie'),
```

**Template Structure**:
```django
{% extends 'base.html' %}

{% block title %}About Eddie{% endblock %}

{% block content %}
<div class="about-container">
    <h1>About Eddie</h1>

    <section class="about-section">
        <h2>Basic Information</h2>
        <!-- Info here -->
    </section>

    <section class="about-section emergency">
        <h2>⚠️ Emergency Contacts</h2>
        <!-- Emergency info here -->
    </section>

    <section class="about-section">
        <h2>Daily Routine</h2>
        <!-- Routine info here -->
    </section>

    <section class="about-section">
        <h2>Important Notes</h2>
        <!-- Notes here -->
    </section>
</div>
{% endblock %}
```

---

### 2. Babysitter & Lunch Form (Friday Pickups)

**Goal**: Create a specialized form for Friday babysitter pickups with lunch details.

**Form Fields**:
- Pickup time
- Who is picking up (name)
- Lunch packed (yes/no)
- Lunch contents (if packed)
- Special instructions
- Contact number

**Implementation Steps**:
- [ ] Create `timeline/forms/friday_pickup.py` with FridayPickupForm
- [ ] Add to form registry
- [ ] Create display template
- [ ] Add validation for required fields
- [ ] Style form to stand out (Friday-specific)
- [ ] Run `python manage.py init_forms`
- [ ] Grant access to relevant users

**Files to Create/Modify**:
- `timeline/forms/friday_pickup.py` - NEW
- `timeline/forms/registry.py` - Add to FORM_REGISTRY
- `timeline/forms/__init__.py` - Add import
- `timeline/templates/timeline/partials/entry_friday_pickup.html` - NEW
- `timeline/static/timeline/css/style.css` - Add styling

**Form Example**:
```python
class FridayPickupForm(BaseEntryForm):
    pickup_time = forms.TimeField(
        required=True,
        label="Pickup Time",
        widget=forms.TimeInput(attrs={'type': 'time'})
    )

    pickup_person = forms.CharField(
        required=True,
        label="Who is picking up?",
        max_length=100
    )

    lunch_packed = forms.ChoiceField(
        choices=[
            ('yes', 'Yes'),
            ('no', 'No'),
        ],
        required=True,
        label="Lunch Packed?",
        widget=forms.RadioSelect()
    )

    lunch_contents = forms.CharField(
        required=False,
        label="Lunch Contents",
        widget=forms.Textarea(attrs={'rows': 3}),
        help_text="What's in the lunchbox?"
    )

    special_instructions = forms.CharField(
        required=False,
        label="Special Instructions",
        widget=forms.Textarea(attrs={'rows': 3})
    )

    contact_number = forms.CharField(
        required=False,
        label="Contact Number",
        max_length=20,
        widget=forms.TextInput(attrs={
            'placeholder': '(555) 123-4567'
        })
    )
```

**Registry Entry**:
```python
'friday_pickup': {
    'form_class': FridayPickupForm,
    'name': 'Friday Pickup',
    'icon': '🚗',
    'description': 'Babysitter and lunch details for Friday pickups',
},
```

---

### 3. Documents & Files Upload System

**Goal**: Create a system for uploading documents/files with descriptions, viewable in timeline and on a dedicated documents page.

**Requirements**:
- Upload any file type (PDF, DOC, XLSX, etc.)
- Add description/title for each document
- Display in timeline as entries
- Separate "Documents" page to view all documents
- Download capability
- Optional: categorization/tags

**Implementation Steps**:
- [ ] Create `timeline/forms/document.py` with DocumentForm
- [ ] Add file upload field and description field
- [ ] Extend Entry model or create separate Document model
- [ ] Add file validation (size limits, allowed types)
- [ ] Create display template for document entries
- [ ] Create DocumentListView for documents-only page
- [ ] Add download link functionality
- [ ] Create documents page template
- [ ] Add navigation link to documents page
- [ ] Style document entries and list page
- [ ] Run migrations
- [ ] Configure file storage (media settings)

**Files to Create/Modify**:
- `timeline/models.py` - Possibly add document field to Entry or create Document model
- `timeline/forms/document.py` - NEW
- `timeline/forms/registry.py` - Add to FORM_REGISTRY
- `timeline/forms/__init__.py` - Add import
- `timeline/views.py` - Add DocumentListView
- `timeline/urls.py` - Add documents page route
- `timeline/templates/timeline/documents.html` - NEW (documents page)
- `timeline/templates/timeline/partials/entry_document.html` - NEW
- `templates/base.html` - Add documents nav link
- `timeline/static/timeline/css/style.css` - Style documents

**Form Example**:
```python
class DocumentForm(BaseEntryForm):
    title = forms.CharField(
        required=True,
        label="Document Title",
        max_length=200
    )

    description = forms.CharField(
        required=False,
        label="Description",
        widget=forms.Textarea(attrs={'rows': 3}),
        help_text="Brief description of this document"
    )

    document = forms.FileField(
        required=True,
        label="File",
        help_text="Upload PDF, DOC, XLSX, or other document"
    )

    def clean_document(self):
        file = self.cleaned_data.get('document')
        if file:
            # Validate file size (e.g., max 10MB)
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError("File size cannot exceed 10MB")
        return file
```

**Model Enhancement**:
```python
class Entry(models.Model):
    # ... existing fields ...
    document = models.FileField(
        upload_to='documents/%Y/%m/%d/',
        blank=True,
        null=True,
        help_text="Uploaded document file"
    )
```

**Documents List View**:
```python
class DocumentListView(LoginRequiredMixin, ListView):
    model = Entry
    template_name = 'timeline/documents.html'
    context_object_name = 'documents'
    paginate_by = 20

    def get_queryset(self):
        """Get only document entries"""
        return Entry.objects.filter(
            user=self.request.user,
            form_type__type='document'
        ).select_related('form_type').order_by('-timestamp')
```

**Display Template Example**:
```django
<div class="timeline-content">
    <h2 class="timeline-title">
        <span class="timeline-icon">📄</span>
        {{ entry.data.title }}
    </h2>

    {% if entry.data.description %}
    <p class="document-description">{{ entry.data.description }}</p>
    {% endif %}

    <div class="document-actions">
        <a href="{{ entry.document.url }}" class="btn-download" download>
            ⬇️ Download
        </a>
        <span class="file-info">
            {{ entry.document.name|basename }}
            ({{ entry.document.size|filesizeformat }})
        </span>
    </div>

    <span class="timeline-timestamp">{{ entry.timestamp|date:"M d, Y g:i A" }}</span>
</div>
```

**Registry Entry**:
```python
'document': {
    'form_class': DocumentForm,
    'name': 'Document',
    'icon': '📄',
    'description': 'Upload and share documents and files',
},
```

---

### 4. Code Quality & Refactoring Improvements

**Goal**: Improve code maintainability, consistency, and adherence to Django best practices without changing functionality.

**Note**: Some items from a January 2026 code review have already been addressed in PR #25 (permission helpers, API decorator, centralized form constants). The items below remain.

#### 4.1 Replace DeleteView for Pin/Unpin Views (Medium Priority)

**Issue**: `EntryPinView` and `EntryUnpinView` inherit from `DeleteView` but override `form_valid()` to update instead of delete. This is semantically confusing.

**Recommendation**: Use `UpdateView` or a generic `View` with `post()` method instead.

**Files to Modify**:
- `timeline/views.py` - Refactor EntryPinView and EntryUnpinView

**Example**:
```python
from django.views.generic import View

class EntryPinView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Pin an entry to the top of the timeline."""

    def post(self, request, pk):
        entry = get_object_or_404(Entry, pk=pk)
        entry.is_pinned = True
        entry.save()
        return redirect('timeline:timeline')

    def test_func(self):
        # ... permission check
```

---

#### 4.2 Add Type Hints (Low Priority)

**Issue**: The codebase doesn't use type hints, which would improve IDE support and catch errors earlier.

**Files to Modify**:
- `timeline/views.py`
- `timeline/models.py`
- `timeline/forms/*.py`
- `timeline/templatetags/entry_display.py`

**Example**:
```python
def get_form_class(form_type: str) -> type[BaseEntryForm] | None:
    """Get the form class for a given form type."""
    form_config = FORM_REGISTRY.get(form_type)
    if form_config:
        return form_config['form_class']
    return None
```

---

#### 4.3 Create Template Inclusion Tag for Tag Sections (Low Priority)

**Issue**: In `entry_schoolday.html`, the same tag-list rendering pattern repeats 4 times for different sections (inclusion specials, small group specials, related services).

**Recommendation**: Create a reusable inclusion tag or template partial.

**Files to Create/Modify**:
- `timeline/templatetags/entry_display.py` - Add new inclusion tag
- `timeline/templates/timeline/partials/_tag_section.html` - NEW partial template
- `timeline/templates/timeline/partials/entry_schoolday.html` - Use new tag

**Example Tag**:
```python
@register.inclusion_tag('timeline/partials/_tag_section.html')
def render_tag_section(title, items, other=None):
    """Render a section with tag badges."""
    return {
        'title': title,
        'items': items.split(', ') if items else [],
        'other': other,
    }
```

**Usage**:
```django
{% render_tag_section "Inclusion Specials" entry.data.inclusion_specials entry.data.inclusion_other %}
```

---

#### 4.4 Standardize Docstring Format (Low Priority)

**Issue**: Docstrings use inconsistent formats - some are detailed with Args/Returns, others are single lines.

**Recommendation**: Adopt Google-style docstrings consistently across the codebase.

**Files to Modify**:
- All Python files with docstrings

**Example** (Google style):
```python
def get_user_profile_attr(user, attr, default=False):
    """Safely get an attribute from a user's profile.

    Args:
        user: The Django user object.
        attr: The profile attribute name (e.g., 'can_pin_posts').
        default: Value to return if profile or attr doesn't exist.

    Returns:
        The attribute value, or default if not found.
    """
```

---

#### 4.5 Split Settings into Environment-Specific Files (Low Priority)

**Issue**: `config/settings.py` handles all environments with conditionals. For larger deployments, split settings are easier to manage.

**Recommendation**: Create separate settings files for different environments.

**Files to Create**:
```
config/
    settings/
        __init__.py      # Imports from appropriate env
        base.py          # Shared settings
        development.py   # Debug=True, SQLite
        production.py    # Debug=False, PostgreSQL, S3
```

**Note**: This is optional and may be overkill for a solo-developer project. Only implement if deployment complexity increases.

---

#### 4.6 Add Custom Model Managers (Low Priority)

**Issue**: Query patterns like `Entry.objects.all().select_related(...)` repeat in views.

**Recommendation**: Add custom managers to encapsulate common query patterns.

**Files to Modify**:
- `timeline/models.py`

**Example**:
```python
class EntryManager(models.Manager):
    def with_relations(self):
        """Return entries with commonly needed related objects."""
        return self.select_related('form_type', 'user', 'user__profile')

    def pinned(self):
        """Return only pinned entries."""
        return self.filter(is_pinned=True)

    def for_timeline(self):
        """Return entries optimized for timeline display."""
        return self.with_relations().order_by('-is_pinned', '-timestamp')

class Entry(models.Model):
    # ... fields ...
    objects = EntryManager()
```

---

## Implementation Priority

**High Priority** (Start with these):
1. About Eddie page - Important for caregivers

**Medium Priority**:
2. Friday pickup form - Specific use case
3. Replace DeleteView for pin/unpin (4.1) - Semantic clarity

**Lower Priority** (More complex or cosmetic):
4. Documents system - Most complex, requires file handling
5. Template inclusion tag for tag sections (4.3)
6. Add type hints (4.2)
7. Standardize docstrings (4.4)
8. Split settings files (4.5) - Only if needed
9. Custom model managers (4.6)

---

## Technical Notes

- All new forms follow the established pattern in `ADDING_FORMS.md`
- Run `python manage.py init_forms` after adding new form types
- Test file uploads thoroughly with various file types and sizes
- Consider storage limits for document uploads in production
- Ensure proper permissions for About Eddie page (authenticated users only)
- Test date dividers with entries spanning multiple months
- Consider mobile responsiveness for all new features

---

## Completed Features

### ✅ Code Quality Improvements (January 2026)
- Added permission helper functions in `views.py` to centralize user profile attribute checking
- Created `@api_login_required` decorator to reduce duplicate authentication code in API views
- Moved `PermissionDenied` import to top of `views.py` (was imported 3 times inside methods)
- Created `timeline/forms/constants.py` with centralized form field choices (PORTION_CHOICES, TIME_CHOICES, activity choices)
- Updated `overnight.py` and `schoolday.py` to use centralized constants
- Removed unnecessary `widget=forms.Select()` declarations where Select is the default
- Reorganized imports in `views.py` to follow Django conventions

### ✅ Pinned Posts Feature
- Added `is_pinned` boolean field to Entry model
- Added `can_pin_posts` permission field to UserProfile
- Pinned posts automatically appear at the top of the timeline
- Visual indicator (📌 Pinned badge) displayed on pinned posts
- Pin checkbox shown in entry form for users with permission
- Admin interface with actions to pin/unpin entries
- Admin can grant/revoke pin permission for users
- Styled pinned posts with amber border and gradient background

### ✅ "Words I'm Using" Form
- Added simple form to track new words/phrases Eddie is using
- Single text input field for comma-separated phrases
- Words display as large, colorful badges with Buzz Lightyear color theme
- Created `timeline/forms/words.py`, display template, and CSS styling

### ✅ Date Dividers in Timeline
- Added automatic date dividers between days in the timeline
- Display format: `------- Monday, January 1 ---------`
- Added template filters: `format_date` and `get_date`
- Added `should_show_date_divider` template tag for date comparison
- Works correctly with pagination

### ✅ Enhanced User Registration Fields
- Added UserProfile model with display_name, email_address, position_role, first_name, last_name
- Updated SignupView with custom registration form
- Added profile fields to admin interface

### ✅ Display User Name on Posts
- User display names now shown on all timeline entries
- Profile information accessible in admin

### ✅ My Weekend Form
- Created weekend form with 3 photos and 3 text descriptions
- Added notes section for weekend highlights

### ✅ Removed Post Filtering
- Simplified timeline view to show all posts
- Removed filter buttons for cleaner interface

### ✅ Overnight Form Enhancements
- Auto-detects day of week from entry timestamp
- Display title shows "[Day] Morning Report" (e.g., "Friday Morning Report")
- Dinner field displays as "Dinner Last Night"

### ✅ Fixed Weekend Form Photo Display
- Weekend photos now display at full size like regular photo posts
- Removed max-height constraint that was cutting off images
- Images maintain aspect ratio and are responsive
