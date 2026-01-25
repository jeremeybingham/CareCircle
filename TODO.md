# Timeline - TODO List

## Planned Features and Improvements

### 1. Create "Words I'm Using" Form

**Goal**: Add a simple form to track new words/phrases Eddie is using.

**Form Structure**:
- Single text input field (comma-separated phrases)
- Display words as large, colorful text in timeline

**Implementation Steps**:
- [ ] Create `timeline/forms/words.py` with WordsForm class
- [ ] Add single CharField for comma-separated input
- [ ] Add to `timeline/forms/registry.py`
- [ ] Update `timeline/forms/__init__.py`
- [ ] Create display template: `timeline/templates/timeline/partials/entry_words.html`
- [ ] Style words with larger font size and varied colors
- [ ] Run `python manage.py init_forms`
- [ ] Test form submission and display

**Files to Create/Modify**:
- `timeline/forms/words.py` - NEW
- `timeline/forms/registry.py` - Add to FORM_REGISTRY
- `timeline/forms/__init__.py` - Add import
- `timeline/templates/timeline/partials/entry_words.html` - NEW
- `timeline/static/timeline/css/style.css` - Add word styling

**Form Example**:
```python
class WordsForm(BaseEntryForm):
    words = forms.CharField(
        required=True,
        label="Words and Phrases",
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter words/phrases separated by commas'
        }),
        help_text="Separate each word or phrase with a comma"
    )
```

**Registry Entry**:
```python
'words': {
    'form_class': WordsForm,
    'name': "Words I'm Using",
    'icon': '💬',
    'description': "Track new words and phrases Eddie is using",
},
```

**Display Template Example**:
```django
<div class="timeline-content">
    <h2 class="timeline-title">
        <span class="timeline-icon">{{ entry.form_type.icon }}</span>
        Words I'm Using
    </h2>
    <div class="words-display">
        {% for word in entry.data.words|split_commas %}
        <span class="word-badge">{{ word }}</span>
        {% endfor %}
    </div>
    <span class="timeline-timestamp">{{ entry.timestamp|date:"M d, Y g:i A" }}</span>
</div>
```

**CSS Example**:
```css
.words-display {
    display: flex;
    flex-wrap: wrap;
    gap: 15px;
    margin: 20px 0;
}

.word-badge {
    font-size: 24px;
    font-weight: bold;
    padding: 10px 20px;
    border-radius: 8px;
    display: inline-block;
}

.word-badge:nth-child(5n+1) { background-color: #fef3c7; color: #92400e; }
.word-badge:nth-child(5n+2) { background-color: #dbeafe; color: #1e40af; }
.word-badge:nth-child(5n+3) { background-color: #dcfce7; color: #166534; }
.word-badge:nth-child(5n+4) { background-color: #fce7f3; color: #9f1239; }
.word-badge:nth-child(5n+5) { background-color: #f3e8ff; color: #6b21a8; }
```

---

### 2. Add Date Dividers in Timeline

**Goal**: Automatically insert subtle date dividers between days in the timeline for better organization.

**Display Format**: `------- Monday, January 1 ---------`

**Implementation Steps**:
- [ ] Modify `TimelineListView` to group entries by date
- [ ] Create template filter or tag to detect date changes
- [ ] Update `timeline.html` to insert dividers between different dates
- [ ] Style dividers with subtle line and centered date text
- [ ] Ensure dividers work correctly with pagination

**Files to Modify**:
- `timeline/views.py` - Add date grouping logic
- `timeline/templates/timeline/timeline.html` - Add divider rendering
- `timeline/templatetags/entry_display.py` - Add date comparison filter
- `timeline/static/timeline/css/style.css` - Style dividers

**Template Filter Example**:
```python
@register.filter(name='format_date')
def format_date(value):
    """Format date as 'Monday, January 1'"""
    if not value:
        return ''
    return value.strftime('%A, %B %-d')

@register.filter(name='get_date')
def get_date(timestamp):
    """Extract just the date from a timestamp"""
    return timestamp.date()
```

**Template Implementation**:
```django
{% for entry in page_obj %}
    {% if forloop.first or entry.timestamp|get_date != page_obj|lookup:forloop.counter0|add:"-1"|get_date %}
    <div class="date-divider">
        <span class="divider-line"></span>
        <span class="divider-text">{{ entry.timestamp|format_date }}</span>
        <span class="divider-line"></span>
    </div>
    {% endif %}
    
    <div class="timeline-item timeline-{{ entry.type }}">
        {% render_entry entry %}
    </div>
{% endfor %}
```

**CSS Example**:
```css
.date-divider {
    display: flex;
    align-items: center;
    margin: 30px 0 20px 0;
    opacity: 0.6;
}

.divider-line {
    flex: 1;
    height: 1px;
    background: linear-gradient(to right, transparent, #d1d5db, transparent);
}

.divider-text {
    padding: 0 20px;
    font-size: 14px;
    color: #6b7280;
    font-weight: 500;
    white-space: nowrap;
}
```

---

### 3. Pinned Posts Feature

**Goal**: Allow designated users to create posts that stay pinned at the top of the timeline.

**Requirements**:
- Only certain users can create pinned posts
- Pinned posts always appear at top of timeline
- Visual indicator showing post is pinned
- Admin control over who can pin posts

**Implementation Steps**:
- [ ] Add `is_pinned` boolean field to Entry model
- [ ] Add `can_pin_posts` permission to User model or UserProfile
- [ ] Create database migration for new fields
- [ ] Update `TimelineListView` queryset to sort pinned posts first
- [ ] Add "Pin this post" checkbox to entry forms (conditional on permission)
- [ ] Add visual indicator (📌 icon) to pinned posts
- [ ] Add admin interface to manage pinned status
- [ ] Test pinning/unpinning functionality

**Files to Modify**:
- `timeline/models.py` - Add is_pinned field to Entry
- `timeline/views.py` - Update queryset ordering
- `timeline/forms/base.py` - Add optional pin checkbox
- `timeline/templates/timeline/entry_form.html` - Show pin option
- `timeline/templates/timeline/partials/*.html` - Add pin indicator
- `timeline/admin.py` - Add pinned filtering
- `timeline/static/timeline/css/style.css` - Style pinned posts

**Model Changes**:
```python
class Entry(models.Model):
    # ... existing fields ...
    is_pinned = models.BooleanField(
        default=False,
        help_text="Pin this entry to the top of the timeline"
    )
    
    class Meta:
        ordering = ['-is_pinned', '-timestamp']  # Pinned first, then by date
```

**View Changes**:
```python
def get_queryset(self):
    """Get all entries with pinned posts first"""
    return Entry.objects.filter(
        user=self.request.user
    ).select_related('form_type').order_by('-is_pinned', '-timestamp')
```

**Display Indicator**:
```django
{% if entry.is_pinned %}
<span class="pinned-indicator">📌 Pinned</span>
{% endif %}
```

---

### 4. Create "About Eddie" Page

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

### 5. Babysitter & Lunch Form (Friday Pickups)

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

### 6. Documents & Files Upload System

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
2. Words I'm Using form - Simple, high value

**Medium Priority**:
3. Date dividers in timeline - Improves readability
4. Friday pickup form - Specific use case

**Lower Priority** (More complex):
5. Pinned posts - Requires model changes and permissions
6. Documents system - Most complex, requires file handling

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
