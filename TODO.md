# Timeline - TODO List

## Planned Features and Improvements
 
- [ ] **User guide**: Create how-to guide for new users, accessible from user profile page
- [ ] **Clickable links in posts**: Auto-detect and convert URLs in text posts to clickable links
- [ ] **Time Menu Ennhancements**: Make time entry menus easier
- [ ] **Disclaimer on Signup**: Add a note and checkbox about privacy and not sharing the app or info from it with unauthorized parties.
- [ ] **General CSS Overhaul** Once app is stable add more decorative CSS elements
- [ ] **Questions Prompts** Add self-generated posts according to day of week (or list from School of dated questions provided) see QUESTIONS.md file in root dir
- [ ] **Child Name as Param** Remove all instances of "Eddie" in template HTML and use a settable field/paramater in the admin / "About Eddie" form info
- [ ] **ABA/Afterschool form** Create a new form for ABA and/or afterschool program (probably separate but similar in parts)

## Planned Features with more detail

### Caregiver Directory (User List with Contact Info)
 
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
        <a href="mailto:{{ user.profile.email_address }}">ðŸ“§ {{ user.profile.email_address }}</a>
        {% endif %}
        {% if user.profile.phone_number %}
        <a href="tel:{{ user.profile.phone_number }}">ðŸ“ž {{ user.profile.phone_number }}</a>
        {% endif %}
    </div>
    {% endfor %}
</section>
{% endfor %}
```
 
---
 
### Documents & Files Upload System
 
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
        <span class="timeline-icon">ðŸ“„</span>
        {{ entry.data.title }}
    </h2>
 
    {% if entry.data.description %}
    <p class="document-description">{{ entry.data.description }}</p>
    {% endif %}
 
    <div class="document-actions">
        <a href="{{ entry.document.url }}" class="btn-download" download>
            â¬‡ï¸ Download
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
    'icon': 'ðŸ“„',
    'description': 'Upload and share documents and files',
},
```

---
 
## Code Quality & Refactoring Improvements
 
**Goal**: Improve code maintainability, consistency, and adherence to Django best practices without changing functionality.
 
#### Replace DeleteView for Pin/Unpin Views (Medium Priority)
 
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
 
#### Add Type Hints (Low Priority)
 
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
 
#### Create Template Inclusion Tag for Tag Sections (Low Priority)
 
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
 
#### Standardize Docstring Format (Low Priority)
 
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
 
#### Split Settings into Environment-Specific Files (Low Priority)
 
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
 
#### Add Custom Model Managers (Low Priority)
 
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
 
### Future: Analytics & Reporting Dashboard
 
**Goal**: Leverage standardized data (Section 5) to provide insights on patterns and trends.
 
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
 
## Technical Notes
 
- All new forms follow the established pattern in `ADDING_FORMS.md`
- Run `python manage.py init_forms` after adding new form types
- Test file uploads thoroughly with various file types and sizes
- Consider storage limits for document uploads in production
- Test date dividers with entries spanning multiple months
- Consider mobile responsiveness for all new features
 
---
 
## Completed Features
 
### About Eddie Page
- Created dedicated page with information about Eddie and emergency contacts
- Added `AboutEddieView` at `/about/` route
- Page includes: basic information, emergency contacts, daily routine, preferences
- Navigation link added to main navbar
- Accessible only to authenticated users
- Mobile-responsive design
 
### Code Quality Improvements (January 2026)
- Added permission helper functions in `views.py` to centralize user profile attribute checking
- Created `@api_login_required` decorator to reduce duplicate authentication code in API views
- Moved `PermissionDenied` import to top of `views.py` (was imported 3 times inside methods)
- Created `timeline/forms/constants.py` with centralized form field choices (PORTION_CHOICES, TIME_CHOICES, activity choices)
- Updated `overnight.py` and `schoolday.py` to use centralized constants
- Removed unnecessary `widget=forms.Select()` declarations where Select is the default
- Reorganized imports in `views.py` to follow Django conventions
 
### Pinned Posts Feature
- Added `is_pinned` boolean field to Entry model
- Added `can_pin_posts` permission field to UserProfile
- Pinned posts automatically appear at the top of the timeline
- Visual indicator (ðŸ“Œ Pinned badge) displayed on pinned posts
- Pin checkbox shown in entry form for users with permission
- Admin interface with actions to pin/unpin entries
- Admin can grant/revoke pin permission for users
- Styled pinned posts with amber border and gradient background
 
### "Words I'm Using" Form
- Added simple form to track new words/phrases Eddie is using
- Single text input field for comma-separated phrases
- Words display as large, colorful badges with Buzz Lightyear color theme
- Created `timeline/forms/words.py`, display template, and CSS styling
 
### Date Dividers in Timeline
- Added automatic date dividers between days in the timeline
- Display format: `------- Monday, January 1 ---------`
- Added template filters: `format_date` and `get_date`
- Added `should_show_date_divider` template tag for date comparison
- Works correctly with pagination
 
### Enhanced User Registration Fields
- Added UserProfile model with display_name, email_address, position_role, first_name, last_name
- Updated SignupView with custom registration form
- Added profile fields to admin interface
 
### Display User Name on Posts
- User display names now shown on all timeline entries
- Profile information accessible in admin
 
### My Weekend Form
- Created weekend form with 3 photos and 3 text descriptions
- Added notes section for weekend highlights
 
### Removed Post Filtering
- Simplified timeline view to show all posts
- Removed filter buttons for cleaner interface
 
### Overnight Form Enhancements
- Auto-detects day of week from entry timestamp
- Display title shows "[Day] Morning Report" (e.g., "Friday Morning Report")
- Dinner field displays as "Dinner Last Night"
 
### Fixed Weekend Form Photo Display
- Weekend photos now display at full size like regular photo posts
- Removed max-height constraint that was cutting off images
- Images maintain aspect ratio and are responsive
 
### User Profile Self-Service Page
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
 
### Standardized Mood Tracking Grid
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

### Visual & Display Improvements
- **Morning Report icon**: Change icon from moon 🌙 to sunrise 🌅
- **Mood display spacing**: Remove "MOOD" text above mood display section (redundant, improves spacing)
- **Navigation branding**: Replace "Eddie's Timeline" text with "About Eddie" link (keep rocket emoji)
- **Page title fix**: Change main tab/page title from "My Timeline" to correct title (check base.html)
- **Timeline header**: Show Display Name instead of username at top of timeline page
- **About Eddie photo**: Make profile picture 60% width of container and crop to square (currently too small)
- **Weekend notes styling**: Change background from yellow to light blue or green

### Form & Entry Display Improvements
- **Morning Report date format**: Auto-format previous day's dinner based on day of week
  - Example: "Mon Dinner" (on Tuesday), "Fri Dinner" (on Saturday)
-  **School Day form updates**:
  - Display bathroom times as badges (improve spacing)
  - Add emoji icons to sections: Food Log 🍎, Specials 🏃‍♂️
  -  Remove "Additional Notes/Reminders" field from form and display
  - Remove "Other" option for Inclusion Specials and Small Group Specials
  - Keep "Other" option for Related Services only
- **Weekend form mood grid**: Add optional mood grid to Weekend form input
- **Photo post mood grid**: Add optional mood grid to Photo form input

### **Babysitter & Lunch Form**: Create a specialized form for babysitter pickups with optional lunch details.
 
### Easy Fixes
- **Login Page Text**: "Welcome Back | Login to your timeline" change to: "Eddie's Timeline | Login to View"
- **Mood Grid Placement**: ensure Mood Grid is at bottom of forms it's included in, and doesn't render in between fields for the forms it's included in; see "overnight.py" "pickup.py" and "schoolday.py" for examples of it pushing other form fields down.
- **Remove Mood Grid Notes**: Not needed, remove
- **About Eddie Visual** Add some colored background to the section headers like the "Emergency Contact" section is purple - use other Buzz Lightyear colors in CSS
- **User Profile page Visual** Add some colored background to the section headers
- **User Signup page** Move Last Name below first name to avoid overflow on mobile
- **EST Time Zone** Post times seem to be correctly in NY time zone but the post dividers with the date IN BETWEEN the posts seem to be using UTC(?) and appear earlier than they should by 6-7 hours
- **Standardized Data Fields for Food Reporting**: Coordinate field types and data storage across forms so that identical data for food is captured consistently, enabling future analytics and reporting. See FOOD.md file in root dir for examples.
