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

## Implementation Priority

**High Priority** (Start with these):
1. About Eddie page - Important for caregivers

**Medium Priority**:
2. Friday pickup form - Specific use case

**Lower Priority** (More complex):
3. Documents system - Most complex, requires file handling

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
