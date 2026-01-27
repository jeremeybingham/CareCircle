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

### 5. User Profile Self-Service Page

**Goal**: Allow users to view and edit their own profile information without requiring admin intervention.

**Current Limitation**: Users can only have their profile information updated by an admin through the Django admin interface. There is no self-service option.

**Features Needed**:
- View own profile information
- Edit display name, email, first name, last name, position/role
- Change password functionality (since there's no email sending capability, password reset must be done while logged in)
- Display current permissions (read-only, for transparency)

**Password Change Considerations**:
- No email sending capability means no "forgot password" flow
- Password change must require current password verification
- Admin can reset passwords via Django admin for locked-out users
- Consider adding password requirements/validation

**Implementation Steps**:
- [x] Create `UserProfileView` for viewing profile
- [x] Create `UserProfileEditView` for editing profile
- [x] Create `PasswordChangeView` (or use Django's built-in with custom template)
- [x] Create templates for profile view and edit
- [x] Add URL routes for profile pages
- [x] Add navigation link to profile in navbar/menu
- [x] Style forms to match existing mobile-first design
- [x] Add success messages for profile updates
- [x] Handle validation errors gracefully

**Files to Create/Modify**:
- `timeline/views.py` - Add UserProfileView, UserProfileEditView
- `timeline/forms/user.py` - Add UserProfileEditForm
- `timeline/templates/timeline/profile.html` - NEW (view profile)
- `timeline/templates/timeline/profile_edit.html` - NEW (edit profile)
- `timeline/templates/registration/password_change_form.html` - Custom styled password change
- `timeline/urls.py` - Add profile routes
- `templates/base.html` - Add profile nav link
- `timeline/static/timeline/css/style.css` - Style profile pages

**URL Structure**:
```python
path('profile/', views.UserProfileView.as_view(), name='profile'),
path('profile/edit/', views.UserProfileEditView.as_view(), name='profile_edit'),
path('profile/password/', auth_views.PasswordChangeView.as_view(
    template_name='registration/password_change_form.html',
    success_url=reverse_lazy('timeline:profile')
), name='password_change'),
```

---

### 6. Caregiver Directory (User List with Contact Info)

**Goal**: Create a page listing all caregivers with their contact information for easy reference during handoffs or emergencies.

**Use Case**: When a caregiver needs to reach another team member (e.g., teacher needs to call parent, babysitter needs to reach after-school program), they should be able to quickly find contact information.

**Features Needed**:
- List all active users with their profiles
- Display: name, display name, position/role, email, phone (if added)
- Group by role (Parents, Teachers, Therapists, etc.)
- Mobile-friendly list/card layout
- Search/filter functionality (optional)
- Privacy consideration: only visible to authenticated users

**Profile Model Enhancement** (optional):
- Add phone number field to UserProfile
- Add availability/schedule notes field

**Implementation Steps**:
- [ ] Create `CaregiverDirectoryView`
- [ ] Create directory template with grouped listings
- [ ] Add phone field to UserProfile model (migration required)
- [ ] Update profile edit form to include phone
- [ ] Add URL route
- [ ] Add navigation link
- [ ] Style for mobile readability (large touch targets for phone links)
- [ ] Consider tel: links for phone numbers

**Files to Create/Modify**:
- `timeline/models.py` - Add phone_number field to UserProfile
- `timeline/views.py` - Add CaregiverDirectoryView
- `timeline/forms/user.py` - Add phone to profile forms
- `timeline/templates/timeline/caregiver_directory.html` - NEW
- `timeline/urls.py` - Add route
- `templates/base.html` - Add nav link
- `timeline/static/timeline/css/style.css` - Style directory page

**Template Structure**:
```django
{% for role, users in grouped_users.items %}
<section class="role-section">
    <h2>{{ role }}</h2>
    {% for user in users %}
    <div class="caregiver-card">
        <h3>{{ user.profile.display_name }}</h3>
        <p>{{ user.profile.position_role }}</p>
        {% if user.profile.email_address %}
        <a href="mailto:{{ user.profile.email_address }}">📧 {{ user.profile.email_address }}</a>
        {% endif %}
        {% if user.profile.phone_number %}
        <a href="tel:{{ user.profile.phone_number }}">📞 {{ user.profile.phone_number }}</a>
        {% endif %}
    </div>
    {% endfor %}
</section>
{% endfor %}
```

---

### 7. User Post History Export

**Goal**: Allow users to download their post history in portable formats for record-keeping, IEP meetings, or personal archives.

**Use Cases**:
- Parents preparing for IEP meetings need documentation
- Therapists want records of session notes
- Caregivers leaving want to hand off their contribution history
- Creating a backup of observations and photos

**Export Formats**:

#### 7.1 Plaintext Export (Simpler, Lower Resource Usage)
- Generate a text file with all user's posts
- Include timestamps, form types, and all form data
- Include URLs/links to photos (not embedded)
- Easy to implement, minimal server resources
- Good for quick reference and searching

#### 7.2 PDF Export with Embedded Photos (Resource Intensive)
- Generate a formatted PDF document
- Embed photos directly in the document
- Professional appearance for meetings/records
- **Server Resource Concerns**:
  - Photo processing requires significant memory
  - Large photo collections could timeout or crash
  - May need pagination/chunking for large histories
  - Consider using Celery for background processing
  - Alternative: Generate incrementally (month-by-month exports)

**Implementation Considerations**:
- Start with plaintext export (lower complexity)
- Add PDF export as optional enhancement
- Implement date range filtering to limit export size
- Show warning for large exports
- Consider email delivery for large PDFs (requires email setup)

**Implementation Steps**:
- [ ] Create `ExportPostHistoryView` with format selection
- [ ] Implement plaintext export generator
- [ ] Add date range filter to limit export scope
- [ ] Create download response with proper headers
- [ ] (Optional) Implement PDF export using WeasyPrint or ReportLab
- [ ] (Optional) Add background task processing for large exports
- [ ] Add export button to user profile page
- [ ] Handle empty post history gracefully

**Files to Create/Modify**:
- `timeline/views.py` - Add export views
- `timeline/templates/timeline/export_history.html` - NEW (format/date selection)
- `timeline/utils/export.py` - NEW (export generation logic)
- `timeline/urls.py` - Add export routes
- `requirements.txt` - Add PDF library if implementing PDF export

**Plaintext Export Example**:
```
Timeline Post History Export
User: Ms. Johnson (Teacher)
Exported: January 27, 2026
Date Range: January 1, 2026 - January 27, 2026
---

[2026-01-27 08:30 AM] School Day Entry
- Breakfast: Most of it eaten
- Mood: Happy, energetic
- Activities: Circle time, art project
- Photo: https://timeline.example.com/media/photos/2026/01/27/morning.jpg

[2026-01-26 03:15 PM] Words I'm Using
- Words: "more please", "all done", "help"
...
```

---

### 8. Standardized Data Fields for Reporting

**Goal**: Coordinate field types and data storage across forms so that identical data (food intake, mood, activities, etc.) is captured consistently, enabling future analytics and reporting.

**Why This Matters**:
- Currently, different forms may capture similar data in different formats
- Example: "dinner" in overnight form vs "lunch" in schoolday form use similar portion options but may have inconsistent field names or choices
- Standardization enables: trend analysis, pattern recognition, IEP progress reports, health tracking

**Areas Needing Standardization**:

#### 8.1 Food/Meal Intake
- **Current**: `PORTION_CHOICES` in `constants.py` (All of it, Most of it, Half, Some, None)
- **Ensure**: All meal-related fields across all forms use identical choices
- **Field naming**: Use consistent names like `breakfast_portion`, `lunch_portion`, `dinner_portion`, `snack_portion`
- **Additional data**: Consider adding `meal_type` (breakfast/lunch/dinner/snack) and `meal_notes` fields

#### 8.2 Mood (See Section 9)
- Standardized mood grid with consistent options across all forms
- Enable mood tracking over time

#### 8.3 Sleep
- **Fields**: `sleep_quality`, `sleep_duration`, `wake_ups`, `bedtime`, `wake_time`
- **Choices**: Consistent quality scale (Great, Good, Fair, Poor, Terrible)

#### 8.4 Bathroom/Toileting
- **Fields**: `bathroom_time`, `bathroom_type`, `bathroom_success`
- **Ensure**: Timestamp format consistency for trend analysis

#### 8.5 Activities
- **Current**: Activity choices exist but may vary between forms
- **Solution**: Central `ACTIVITY_CHOICES` in constants.py used everywhere

**Implementation Steps**:
- [ ] Audit all existing forms for overlapping data fields
- [ ] Document current field names and choice values
- [ ] Design standardized field schema for each data category
- [ ] Update `timeline/forms/constants.py` with all standardized choices
- [ ] Create standardized form field mixins or base classes
- [ ] Migrate existing forms to use standardized fields
- [ ] Update display templates to handle standardized data
- [ ] Consider data migration for existing entries (optional, complex)
- [ ] Document field standards for future form development

**Files to Create/Modify**:
- `timeline/forms/constants.py` - Expand with all standardized choices
- `timeline/forms/mixins.py` - NEW (reusable form field groups)
- `timeline/forms/*.py` - Update all forms to use standardized fields
- `docs/DATA_STANDARDS.md` - NEW (document field conventions)

**Example Standardized Constants**:
```python
# timeline/forms/constants.py

# Food/Meal Intake
PORTION_CHOICES = [
    ('all', 'All of it'),
    ('most', 'Most of it'),
    ('half', 'About half'),
    ('some', 'Some of it'),
    ('none', 'None'),
    ('na', 'N/A'),
]

# Mood Options (multi-select compatible)
MOOD_CHOICES = [
    ('happy', 'Happy 😊'),
    ('calm', 'Calm 😌'),
    ('energetic', 'Energetic ⚡'),
    ('tired', 'Tired 😴'),
    ('sad', 'Sad 😢'),
    ('anxious', 'Anxious 😰'),
    ('frustrated', 'Frustrated 😤'),
    ('silly', 'Silly 🤪'),
]

# Sleep Quality
SLEEP_QUALITY_CHOICES = [
    ('great', 'Great'),
    ('good', 'Good'),
    ('fair', 'Fair'),
    ('poor', 'Poor'),
    ('terrible', 'Terrible'),
]
```

---

### 9. Standardized Mood Tracking Grid

**Goal**: Create a reusable, multi-select mood tracking component that can be added to any form, with consistent data storage for reporting and trend analysis.

**Design Requirements**:
- Multi-select grid (Eddie may exhibit multiple moods)
- Visual, touch-friendly design for mobile
- Optional notes field for context
- Consistent across all forms that track mood
- Data stored in standardized format for analytics

**Mood Options** (initial set, expandable):
- 😊 Happy
- 😌 Calm
- ⚡ Energetic
- 😴 Tired
- 😢 Sad
- 😰 Anxious
- 😤 Frustrated
- 🤪 Silly
- 😠 Upset/Angry
- 🤒 Not feeling well
- 🤔 Focused
- 😶 Quiet/Withdrawn

**Visual Design**:
- Grid layout (3-4 columns on mobile, more on desktop)
- Large touch targets (minimum 48px)
- Toggle-style selection with clear visual feedback
- Selected moods highlighted with color
- Emoji + text label for each option

**Implementation Steps**:
- [x] Add `MOOD_CHOICES` to `timeline/forms/constants.py`
- [x] Create `MoodGridWidget` custom widget for multi-select display
- [x] Create `MoodFieldMixin` for easy addition to any form
- [x] Create CSS for mood grid layout and selection states
- [x] Add mood grid to existing forms: overnight, schoolday, text post
- [x] Create display template partial for mood data
- [x] Update entry display templates to show mood badges
- [x] Ensure data is stored in consistent format (list of mood keys)

**Files to Create/Modify**:
- `timeline/forms/constants.py` - Add MOOD_CHOICES
- `timeline/forms/widgets.py` - NEW (custom MoodGridWidget)
- `timeline/forms/mixins.py` - Add MoodFieldMixin
- `timeline/forms/overnight.py` - Add mood field
- `timeline/forms/schoolday.py` - Add mood field
- `timeline/forms/text.py` - Add mood field
- `timeline/templates/timeline/partials/_mood_display.html` - NEW
- `timeline/templates/timeline/partials/entry_*.html` - Include mood display
- `timeline/static/timeline/css/style.css` - Mood grid styles

**Widget Example**:
```python
class MoodGridWidget(forms.CheckboxSelectMultiple):
    """Custom widget for mood multi-select grid display."""
    template_name = 'timeline/widgets/mood_grid.html'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs['class'] = 'mood-grid'
```

**Form Mixin Example**:
```python
class MoodFieldMixin:
    """Mixin to add standardized mood tracking to any form."""

    mood = forms.MultipleChoiceField(
        choices=MOOD_CHOICES,
        required=False,
        label="How was Eddie's mood?",
        widget=MoodGridWidget(),
    )

    mood_notes = forms.CharField(
        required=False,
        label="Mood notes (optional)",
        widget=forms.Textarea(attrs={'rows': 2}),
        help_text="Any context about mood or behavior"
    )
```

**CSS Example**:
```css
.mood-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
    margin: 10px 0;
}

.mood-grid label {
    display: flex;
    align-items: center;
    padding: 12px;
    border: 2px solid #ddd;
    border-radius: 8px;
    cursor: pointer;
    font-size: 14px;
}

.mood-grid input:checked + label,
.mood-grid label.selected {
    background-color: #e8f4fd;
    border-color: #3498db;
}

.mood-emoji {
    font-size: 24px;
    margin-right: 8px;
}
```

**Display Template** (`_mood_display.html`):
```django
{% if moods %}
<div class="mood-display">
    <strong>Mood:</strong>
    <div class="mood-badges">
        {% for mood in moods %}
        <span class="mood-badge mood-{{ mood }}">
            {{ mood|mood_emoji }} {{ mood|title }}
        </span>
        {% endfor %}
    </div>
    {% if mood_notes %}
    <p class="mood-notes">{{ mood_notes }}</p>
    {% endif %}
</div>
{% endif %}
```

---

### 10. Future: Analytics & Reporting Dashboard

**Goal**: Leverage standardized data (Sections 8-9) to provide insights on patterns and trends.

**Note**: This is a long-term goal that depends on first implementing standardized data fields.

**Potential Reports**:
- Meal intake trends (what meals are eaten well/poorly)
- Sleep pattern analysis
- Mood trends over time
- Activity frequency
- Vocabulary growth tracking
- Bathroom/toileting patterns

**Visualization Options**:
- Simple charts (Chart.js or similar)
- Weekly/monthly summaries
- Comparison reports for IEP meetings
- PDF export for documentation

**Implementation**: To be planned after data standardization is complete.

---

## Implementation Priority

**High Priority** (Start with these):
1. About Eddie page - Important for caregivers
2. User Profile Self-Service (5) - Enables users to manage their own info

**Medium Priority**:
3. Friday pickup form - Specific use case
4. Replace DeleteView for pin/unpin (4.1) - Semantic clarity
5. Caregiver Directory (6) - Useful for team communication
6. Standardized Data Fields (8) - Foundation for reporting
7. Mood Tracking Grid (9) - Depends on #6, enhances data collection

**Lower Priority** (More complex or optional):
8. Documents system - Most complex, requires file handling
9. User Post History Export (7) - Start with plaintext
10. Template inclusion tag for tag sections (4.3)
11. Add type hints (4.2)
12. Standardize docstrings (4.4)
13. Split settings files (4.5) - Only if needed
14. Custom model managers (4.6)

**Long-term**:
15. Analytics & Reporting Dashboard (10) - After data standardization

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

### ✅ User Profile Self-Service Page
- Created profile view page (`/profile/`) showing user information
- Created profile edit page (`/profile/edit/`) for updating profile fields
- Created password change page (`/profile/password/`) using Django's built-in with custom template
- Added `UserProfileEditForm` with email uniqueness validation
- Added `StyledPasswordChangeForm` with styled widgets
- Display name, email, first name, last name, and position/role are editable
- Permissions displayed as read-only (admin-controlled)
- Form access list shows which forms the user can use
- Username link in navbar goes to profile page
- Mobile-responsive design with CSS styling
- Success messages for profile updates and password changes

### ✅ Standardized Mood Tracking Grid
- Created reusable `MoodFieldMixin` for adding mood tracking to any form
- Created `MoodGridWidget` custom widget with touch-friendly grid layout
- Added 12 mood options with emojis: Happy, Calm, Energetic, Tired, Sad, Anxious, Frustrated, Silly, Upset/Angry, Not feeling well, Focused, Quiet/Withdrawn
- Added `MOOD_CHOICES` and `MOOD_EMOJI_MAP` to `timeline/forms/constants.py`
- Created mood grid widget template at `timeline/templates/timeline/widgets/mood_grid.html`
- Created mood display partial at `timeline/templates/timeline/partials/_mood_display.html`
- Added `mood_emoji` template filter for displaying mood emojis
- Integrated mood tracking into Text Post, Overnight, and School Day forms
- Added optional mood_notes field for additional context
- Data stored as comma-separated string for consistent JSON storage
- Mobile-responsive CSS with 3-column grid (2 on small screens)
- Color-coded mood badges in entry display (Buzz Lightyear theme)
