I'll outline a comprehensive approach for creating a public demo that's interactive but controlled. Here's my recommendation:

## Recommended Approach: Multi-Tiered Demo System

### **Option 1: Session-Based Anonymous Demo (Most Interactive)**

Create isolated demo experiences where each visitor gets their own temporary view:

```python
# timeline/middleware.py
from django.utils import timezone
from datetime import timedelta
import uuid

class DemoSessionMiddleware:
    """Create isolated demo sessions for anonymous visitors."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if not request.user.is_authenticated and settings.DEMO_MODE:
            # Create or get demo session ID
            if 'demo_session_id' not in request.session:
                request.session['demo_session_id'] = str(uuid.uuid4())
                request.session['demo_created_at'] = timezone.now().isoformat()
                request.session['demo_entry_count'] = 0
            
            # Check session expiry (e.g., 1 hour)
            created_at = timezone.datetime.fromisoformat(
                request.session.get('demo_created_at')
            )
            if timezone.now() - created_at > timedelta(hours=1):
                # Reset session
                self._reset_demo_session(request)
        
        response = self.get_response(request)
        return response
    
    def _reset_demo_session(self, request):
        old_session_id = request.session.get('demo_session_id')
        # Delete entries from this session
        DemoEntry.objects.filter(session_id=old_session_id).delete()
        # Create new session
        request.session['demo_session_id'] = str(uuid.uuid4())
        request.session['demo_created_at'] = timezone.now().isoformat()
        request.session['demo_entry_count'] = 0
```

**Add to settings.py:**
```python
# Demo mode settings
DEMO_MODE = os.getenv('DEMO_MODE', 'False') == 'True'
DEMO_SESSION_TIMEOUT_HOURS = 1
DEMO_MAX_ENTRIES_PER_SESSION = 10
DEMO_ALLOWED_FORM_TYPES = ['text', 'photo', 'overnight']  # Limit forms
```

**Create a Demo-specific Entry model:**
```python
# timeline/models.py

class DemoEntry(models.Model):
    """Temporary entries for demo sessions - auto-deleted after timeout."""
    session_id = models.CharField(max_length=100, db_index=True)
    form_type = models.ForeignKey(FormType, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    data = models.JSONField()
    image = models.ImageField(upload_to='demo_uploads/', blank=True, null=True)
    is_pinned = models.BooleanField(default=False)
    demo_user_persona = models.CharField(
        max_length=50,
        choices=[
            ('parent', 'Parent'),
            ('teacher', 'Teacher'),
            ('therapist', 'Therapist'),
        ],
        default='parent'
    )
    
    class Meta:
        ordering = ['-is_pinned', '-timestamp']
        indexes = [
            models.Index(fields=['session_id', '-timestamp']),
        ]
```

### **Option 2: Pre-defined "Mad Libs" Style Forms (Most Controlled)**

Create demo forms that only allow selection from predefined options:

```python
# timeline/forms/demo.py

class DemoTextForm(BaseEntryForm):
    """Controlled text form for demo - only dropdowns/checkboxes."""
    
    title_template = forms.ChoiceField(
        choices=[
            ('Great day at school!', 'Great day at school!'),
            ('Fun weekend activity', 'Fun weekend activity'),
            ('Bedtime routine went well', 'Bedtime routine went well'),
            ('Tried new food today', 'Tried new food today'),
        ],
        required=True,
        label="Post Title"
    )
    
    activity = forms.MultipleChoiceField(
        choices=[
            ('playground', 'Played at playground'),
            ('reading', 'Read books'),
            ('art', 'Did art project'),
            ('music', 'Music class'),
            ('outside', 'Played outside'),
        ],
        widget=forms.CheckboxSelectMultiple(),
        required=False,
        label="Activities"
    )
    
    mood_rating = forms.ChoiceField(
        choices=[
            ('great', '😊 Great'),
            ('good', '🙂 Good'),
            ('okay', '😐 Okay'),
            ('challenging', '😕 Challenging'),
        ],
        widget=forms.RadioSelect(),
        required=True
    )
    
    additional_note = forms.CharField(
        max_length=200,  # Strict limit
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 2,
            'placeholder': 'Add a brief note (max 200 characters)...'
        })
    )
    
    def clean_additional_note(self):
        """Validate and sanitize text input."""
        note = self.cleaned_data.get('additional_note', '').strip()
        
        # Basic profanity filter (you can use a library like 'better-profanity')
        if note:
            # Simple word filtering
            blocked_words = ['spam', 'test', 'xxx']  # Extend as needed
            note_lower = note.lower()
            if any(word in note_lower for word in blocked_words):
                raise forms.ValidationError(
                    "Please keep comments appropriate for a family app."
                )
        
        return note
```

### **Option 3: Guided Demo Tour (Most User-Friendly)**

Create a step-by-step guided experience:

```python
# timeline/views.py

class DemoTourView(TemplateView):
    """Interactive demo tour with pre-scripted steps."""
    template_name = 'timeline/demo_tour.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Pre-populated demo data
        context['demo_entries'] = self._get_demo_entries()
        context['demo_step'] = self.request.GET.get('step', '1')
        context['demo_personas'] = {
            'parent': {'name': 'Mom', 'color': '#4A90E2'},
            'teacher': {'name': 'Ms. Johnson', 'color': '#F5A623'},
            'therapist': {'name': 'Sarah (Speech)', 'color': '#7ED321'},
        }
        
        return context
    
    def _get_demo_entries(self):
        """Return pre-scripted demo entries."""
        return [
            {
                'persona': 'teacher',
                'type': 'schoolday',
                'data': {
                    'bathroom': '10:30, 1:00',
                    'lunch_from_home': 'Most',
                    'mood': 'happy, focused',
                    'notes_about_day': 'Great participation in circle time!',
                },
                'timestamp': timezone.now() - timedelta(hours=3),
            },
            # ... more demo entries
        ]
```

### **My Recommended Hybrid Approach:**

Combine the best of all three:

1. **Landing Page** - Show pre-populated demo timeline (read-only)
2. **"Try it yourself" Button** - Starts a demo session
3. **Session-based isolation** - Each visitor gets their own sandbox
4. **Controlled forms** - Mix of dropdowns and limited text fields
5. **Auto-cleanup** - Sessions expire after 1 hour
6. **Entry limits** - Max 10 entries per session

**Implementation Plan:**

```python
# config/settings.py additions

MIDDLEWARE = [
    # ... existing middleware ...
    'timeline.middleware.DemoSessionMiddleware',  # Add this
]

# Demo configuration
DEMO_MODE = os.getenv('DEMO_MODE', 'False') == 'True'
DEMO_SESSION_TIMEOUT_HOURS = 1
DEMO_MAX_ENTRIES_PER_SESSION = 10
DEMO_TEXT_MAX_LENGTH = 200
DEMO_ALLOWED_FORMS = ['text', 'photo', 'overnight']
```

```python
# timeline/views.py - Modified views for demo

class DemoTimelineView(ListView):
    """Demo version of timeline that shows session-specific + seed data."""
    template_name = 'timeline/demo_timeline.html'
    
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            session_id = self.request.session.get('demo_session_id')
            
            # Combine seed data + session-specific entries
            seed_entries = DemoEntry.objects.filter(
                session_id='SEED'  # Pre-populated demo data
            )
            session_entries = DemoEntry.objects.filter(
                session_id=session_id
            ) if session_id else DemoEntry.objects.none()
            
            # Combine querysets
            return (seed_entries | session_entries).order_by(
                '-is_pinned', '-timestamp'
            )[:50]  # Limit to recent entries
        
        return super().get_queryset()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_demo'] = not self.request.user.is_authenticated
        context['demo_entries_remaining'] = self._get_entries_remaining()
        return context
    
    def _get_entries_remaining(self):
        if self.request.user.is_authenticated:
            return None
        
        count = self.request.session.get('demo_entry_count', 0)
        return max(0, settings.DEMO_MAX_ENTRIES_PER_SESSION - count)
```

**Management command for cleanup:**

```python
# timeline/management/commands/cleanup_demo.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from timeline.models import DemoEntry

class Command(BaseCommand):
    help = 'Clean up expired demo entries'
    
    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(
            hours=settings.DEMO_SESSION_TIMEOUT_HOURS
        )
        
        # Delete expired entries (except SEED data)
        deleted_count, _ = DemoEntry.objects.filter(
            timestamp__lt=cutoff
        ).exclude(
            session_id='SEED'
        ).delete()
        
        self.stdout.write(
            self.style.SUCCESS(f'Deleted {deleted_count} expired demo entries')
        )
```

**Add to crontab for automatic cleanup:**
```bash
# Run every hour
0 * * * * cd /path/to/timeline && python manage.py cleanup_demo
```

### **Demo-Specific Templates:**

```django
{# timeline/templates/timeline/demo_banner.html #}
<div class="demo-banner">
    <div class="demo-banner-content">
        <span class="demo-icon">🎭</span>
        <div class="demo-text">
            <strong>Demo Mode</strong>
            <p>You're viewing a demonstration. Your entries will expire in 
               {{ demo_time_remaining }} minutes. 
               <strong>{{ demo_entries_remaining }}</strong> entries remaining.</p>
        </div>
        <a href="{% url 'signup' %}" class="demo-cta-btn">Create Real Account</a>
    </div>
</div>
```

### **URL Configuration:**

```python
# config/urls.py

urlpatterns = [
    # ... existing patterns ...
    
    # Demo URLs
    path('demo/', DemoTimelineView.as_view(), name='demo_timeline'),
    path('demo/tour/', DemoTourView.as_view(), name='demo_tour'),
]
```

### **Additional Safety Measures:**

1. **Content filtering library:**
```bash
pip install better-profanity
```

```python
from better_profanity import profanity

def clean_user_text(text):
    """Filter inappropriate content."""
    profanity.load_censor_words()
    return profanity.censor(text)
```

2. **Rate limiting** - Limit requests per IP
3. **Image validation** - Disable or heavily restrict image uploads in demo
4. **reCAPTCHA** - Add to demo form submissions if needed

**Which approach would you prefer?** I can provide more detailed implementation for any of these options, or we can combine elements. The session-based demo with controlled forms is probably the sweet spot for demonstrating functionality while maintaining control.

Great idea! Let's create a sandboxed image picker for demo mode. Here's a comprehensive implementation:

## 1. Demo Photo Assets Structure

First, create a directory for demo photos:

```bash
timeline/static/timeline/demo_photos/
├── school/
│   ├── art_project.jpg
│   ├── playground.jpg
│   ├── circle_time.jpg
│   └── lunch_time.jpg
├── home/
│   ├── breakfast.jpg
│   ├── bedtime_story.jpg
│   ├── playing_blocks.jpg
│   └── outdoor_play.jpg
├── activities/
│   ├── swimming.jpg
│   ├── park_visit.jpg
│   ├── museum.jpg
│   └── family_dinner.jpg
└── therapy/
    ├── speech_session.jpg
    ├── ot_activity.jpg
    └── sensory_play.jpg
```

## 2. Demo Photo Configuration

```python
# timeline/demo_config.py
"""
Configuration for demo mode photos and content.
"""

DEMO_PHOTOS = {
    'school': [
        {
            'filename': 'art_project.jpg',
            'caption': 'Working on an art project',
            'thumbnail': 'art_project_thumb.jpg',
        },
        {
            'filename': 'playground.jpg',
            'caption': 'Playing on the playground',
            'thumbnail': 'playground_thumb.jpg',
        },
        {
            'filename': 'circle_time.jpg',
            'caption': 'Participating in circle time',
            'thumbnail': 'circle_time_thumb.jpg',
        },
        {
            'filename': 'lunch_time.jpg',
            'caption': 'Enjoying lunch with friends',
            'thumbnail': 'lunch_time_thumb.jpg',
        },
    ],
    'home': [
        {
            'filename': 'breakfast.jpg',
            'caption': 'Eating breakfast',
            'thumbnail': 'breakfast_thumb.jpg',
        },
        {
            'filename': 'bedtime_story.jpg',
            'caption': 'Reading a bedtime story',
            'thumbnail': 'bedtime_story_thumb.jpg',
        },
        {
            'filename': 'playing_blocks.jpg',
            'caption': 'Building with blocks',
            'thumbnail': 'playing_blocks_thumb.jpg',
        },
        {
            'filename': 'outdoor_play.jpg',
            'caption': 'Playing outside',
            'thumbnail': 'outdoor_play_thumb.jpg',
        },
    ],
    'activities': [
        {
            'filename': 'swimming.jpg',
            'caption': 'Swimming lesson',
            'thumbnail': 'swimming_thumb.jpg',
        },
        {
            'filename': 'park_visit.jpg',
            'caption': 'Visit to the park',
            'thumbnail': 'park_visit_thumb.jpg',
        },
        {
            'filename': 'museum.jpg',
            'caption': 'Museum trip',
            'thumbnail': 'museum_thumb.jpg',
        },
        {
            'filename': 'family_dinner.jpg',
            'caption': 'Family dinner time',
            'thumbnail': 'family_dinner_thumb.jpg',
        },
    ],
    'therapy': [
        {
            'filename': 'speech_session.jpg',
            'caption': 'Speech therapy session',
            'thumbnail': 'speech_session_thumb.jpg',
        },
        {
            'filename': 'ot_activity.jpg',
            'caption': 'OT activity',
            'thumbnail': 'ot_activity_thumb.jpg',
        },
        {
            'filename': 'sensory_play.jpg',
            'caption': 'Sensory play activity',
            'thumbnail': 'sensory_play_thumb.jpg',
        },
    ],
}

def get_demo_photos_for_form(form_type):
    """Get relevant demo photos based on form type."""
    form_photo_mapping = {
        'photo': ['home', 'activities'],
        'schoolday': ['school'],
        'weekend': ['home', 'activities'],
        'overnight': ['home'],
        'pickup': ['activities'],
    }
    
    categories = form_photo_mapping.get(form_type, ['home', 'activities'])
    photos = []
    for category in categories:
        photos.extend(DEMO_PHOTOS.get(category, []))
    
    return photos
```

## 3. Demo Photo Picker Widget

```python
# timeline/forms/demo_widgets.py
"""
Custom widgets for demo mode.
"""
from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe
from django.templatetags.static import static


class DemoPhotoPickerWidget(forms.Widget):
    """
    Widget that displays a photo picker instead of file upload.
    Shows thumbnails of pre-selected demo photos.
    """
    template_name = 'timeline/widgets/demo_photo_picker.html'
    
    def __init__(self, photos, attrs=None):
        super().__init__(attrs)
        self.photos = photos
    
    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['photos'] = self.photos
        context['widget']['selected_photo'] = value
        return context
    
    def value_from_datadict(self, data, files, name):
        """Get the selected photo path from form data."""
        return data.get(name)
```

```django
{# timeline/templates/timeline/widgets/demo_photo_picker.html #}
<div class="demo-photo-picker">
    <div class="demo-photo-notice">
        <span class="demo-notice-icon">📱</span>
        <p><strong>Demo Mode:</strong> In the real app, clicking here would open your phone or computer's file picker to upload your own photos. For this demo, please select from these sample photos:</p>
    </div>
    
    <div class="demo-photo-grid">
        {% for photo in widget.photos %}
        <label class="demo-photo-option {% if widget.selected_photo == photo.filename %}selected{% endif %}">
            <input type="radio" 
                   name="{{ widget.name }}" 
                   value="{{ photo.filename }}"
                   {% if widget.selected_photo == photo.filename %}checked{% endif %}
                   class="demo-photo-radio">
            <div class="demo-photo-thumbnail">
                <img src="{% static 'timeline/demo_photos/'|add:photo.thumbnail %}" 
                     alt="{{ photo.caption }}"
                     loading="lazy">
                <div class="demo-photo-overlay">
                    <span class="demo-photo-check">✓</span>
                </div>
            </div>
            <span class="demo-photo-caption">{{ photo.caption }}</span>
        </label>
        {% endfor %}
    </div>
    
    <input type="hidden" name="{{ widget.name }}_is_demo" value="true">
</div>
```

## 4. Demo-Specific Form Classes

```python
# timeline/forms/demo_forms.py
"""
Demo versions of forms with photo picker instead of file upload.
"""
from django import forms
from .base import BaseEntryForm
from .mixins import MoodFieldMixin
from .demo_widgets import DemoPhotoPickerWidget
from timeline.demo_config import get_demo_photos_for_form


class DemoPhotoForm(MoodFieldMixin, BaseEntryForm):
    """Demo version of PhotoForm with photo picker."""
    
    image = forms.CharField(  # Changed from ImageField to CharField
        required=True,
        label="Photo",
        widget=DemoPhotoPickerWidget(photos=get_demo_photos_for_form('photo'))
    )
    
    caption = forms.CharField(
        max_length=200,  # Shortened for demo
        required=False,
        label="Caption",
        widget=forms.Textarea(attrs={
            'rows': 2,
            'placeholder': 'Add a brief caption (max 200 characters)...'
        })
    )
    
    field_order = ['image', 'caption', 'mood', 'mood_notes']
    
    def clean_image(self):
        """Validate that selected photo exists."""
        photo = self.cleaned_data.get('image')
        valid_photos = [p['filename'] for p in get_demo_photos_for_form('photo')]
        
        if photo not in valid_photos:
            raise forms.ValidationError("Please select a valid demo photo.")
        
        return photo
    
    def get_demo_photo_url(self):
        """Get the static URL for the selected demo photo."""
        from django.templatetags.static import static
        photo = self.cleaned_data.get('image')
        return static(f'timeline/demo_photos/{photo}')


class DemoWeekendForm(MoodFieldMixin, BaseEntryForm):
    """Demo version of WeekendForm with photo pickers."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        demo_photos = get_demo_photos_for_form('weekend')
        
        # Override photo fields with demo pickers
        self.fields['friday_photo'] = forms.CharField(
            required=False,
            label="Friday Photo",
            widget=DemoPhotoPickerWidget(photos=demo_photos)
        )
        self.fields['saturday_photo'] = forms.CharField(
            required=False,
            label="Saturday Photo",
            widget=DemoPhotoPickerWidget(photos=demo_photos)
        )
        self.fields['sunday_photo'] = forms.CharField(
            required=False,
            label="Sunday Photo",
            widget=DemoPhotoPickerWidget(photos=demo_photos)
        )
    
    friday_text = forms.CharField(
        required=False,
        label="Friday",
        max_length=200,
        widget=forms.TextInput(attrs={
            'placeholder': 'What happened on Friday? (max 200 chars)'
        })
    )
    
    saturday_text = forms.CharField(
        required=False,
        label="Saturday",
        max_length=200,
        widget=forms.TextInput(attrs={
            'placeholder': 'What happened on Saturday? (max 200 chars)'
        })
    )
    
    sunday_text = forms.CharField(
        required=False,
        label="Sunday",
        max_length=200,
        widget=forms.TextInput(attrs={
            'placeholder': 'What happened on Sunday? (max 200 chars)'
        })
    )
    
    notes = forms.CharField(
        required=False,
        label="Weekend Notes",
        widget=forms.Textarea(attrs={
            'rows': 2,
            'placeholder': 'Any other highlights? (max 200 chars)...',
            'maxlength': 200
        })
    )
    
    field_order = [
        'friday_photo', 'friday_text',
        'saturday_photo', 'saturday_text',
        'sunday_photo', 'sunday_text',
        'notes',
        'mood', 'mood_notes',
    ]
    
    def has_multiple_images(self):
        return True
    
    def get_all_images(self):
        """Return dict of selected demo photos."""
        images = {}
        for field_name in ['friday_photo', 'saturday_photo', 'sunday_photo']:
            photo = self.cleaned_data.get(field_name)
            if photo:
                images[field_name] = photo
        return images
```

## 5. Demo Form Registry

```python
# timeline/forms/demo_registry.py
"""
Demo-specific form registry that uses controlled forms.
"""
from .text import TextForm  # Can use regular TextForm
from .demo_forms import DemoPhotoForm, DemoWeekendForm
from .overnight import OvernightForm  # Can use regular OvernightForm
from .schoolday import SchoolDayForm  # Can use regular SchoolDayForm
from .words import WordsForm  # Can use regular WordsForm
from .pickup import PickupForm  # Can use regular PickupForm


DEMO_FORM_REGISTRY = {
    'text': {
        'form_class': TextForm,
        'name': 'Text Post',
        'icon': '📝',
        'description': 'Create a simple text post',
    },
    'photo': {
        'form_class': DemoPhotoForm,  # Demo version
        'name': 'Photo',
        'icon': '📸',
        'description': 'Share a photo with caption',
    },
    'overnight': {
        'form_class': OvernightForm,
        'name': 'Morning Report',
        'icon': '🌅',
        'description': 'Track overnight routine',
    },
    'weekend': {
        'form_class': DemoWeekendForm,  # Demo version
        'name': 'My Weekend',
        'icon': '🎉',
        'description': 'Share weekend photos and highlights',
    },
}


def get_demo_form_class(form_type):
    """Get the demo form class for a given form type."""
    form_config = DEMO_FORM_REGISTRY.get(form_type)
    if form_config:
        return form_config['form_class']
    return None
```

## 6. Modified Views for Demo Mode

```python
# timeline/views.py - Add demo support to EntryCreateView

class EntryCreateView(LoginRequiredMixin, FormView):
    """Generic entry creation view - supports both real and demo mode."""
    template_name = 'timeline/entry_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        """Validate form_type and user access before processing."""
        form_type = kwargs.get('form_type')
        
        # Determine if this is demo mode
        self.is_demo = not request.user.is_authenticated
        
        # Use appropriate registry
        if self.is_demo:
            from timeline.forms.demo_registry import (
                DEMO_FORM_REGISTRY, 
                get_demo_form_class
            )
            registry = DEMO_FORM_REGISTRY
            get_form_func = get_demo_form_class
        else:
            from timeline.forms.registry import (
                FORM_REGISTRY,
                get_form_class as get_form_func
            )
            registry = FORM_REGISTRY
        
        # Check if form type is valid
        if form_type not in registry:
            raise Http404("Form type not found")
        
        # For demo mode, check session limits
        if self.is_demo:
            entry_count = request.session.get('demo_entry_count', 0)
            if entry_count >= settings.DEMO_MAX_ENTRIES_PER_SESSION:
                messages.warning(
                    request,
                    "Demo limit reached! Create a real account to continue."
                )
                return redirect('signup')
        
        # For authenticated users, check access
        if not self.is_demo:
            try:
                self.form_type_obj = FormType.objects.get(
                    type=form_type,
                    is_active=True
                )
            except FormType.DoesNotExist:
                raise Http404("Form type not available")
            
            has_access = UserFormAccess.objects.filter(
                user=request.user,
                form_type=self.form_type_obj
            ).exists()
            
            if not has_access:
                raise Http404("You don't have access to this form")
        
        self.form_type = form_type
        self.get_form_func = get_form_func
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_class(self):
        """Return the appropriate form class."""
        return self.get_form_func(self.form_type)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_type'] = self.form_type
        context['is_demo'] = self.is_demo
        
        if self.is_demo:
            from timeline.forms.demo_registry import DEMO_FORM_REGISTRY
            form_config = DEMO_FORM_REGISTRY[self.form_type]
            context['form_type_obj'] = {
                'name': form_config['name'],
                'icon': form_config['icon'],
                'description': form_config['description'],
                'type': self.form_type,
            }
            context['demo_entries_remaining'] = (
                settings.DEMO_MAX_ENTRIES_PER_SESSION - 
                self.request.session.get('demo_entry_count', 0)
            )
        else:
            context['form_type_obj'] = self.form_type_obj
            context['can_pin'] = user_can_pin_posts(self.request.user)
        
        return context
    
    def form_valid(self, form):
        """Save the entry (demo or real)."""
        if self.is_demo:
            return self._save_demo_entry(form)
        else:
            return self._save_real_entry(form)
    
    def _save_demo_entry(self, form):
        """Save a demo entry."""
        from timeline.models import DemoEntry
        from django.templatetags.static import static
        
        session_id = self.request.session.get('demo_session_id')
        
        # Get or create demo FormType
        demo_form_type, _ = FormType.objects.get_or_create(
            type=self.form_type,
            defaults={
                'name': form.__class__.__name__,
                'icon': '📝',
                'is_active': True,
            }
        )
        
        # Create demo entry
        entry = DemoEntry(
            session_id=session_id,
            form_type=demo_form_type,
            demo_user_persona='parent',  # Default persona
        )
        
        # Get JSON data
        entry.data = form.get_json_data()
        
        # Handle demo photos
        if hasattr(form, 'has_multiple_images') and form.has_multiple_images():
            # Multiple images (Weekend form)
            all_images = form.get_all_images()
            for field_name, photo_filename in all_images.items():
                # Store the static URL in data
                entry.data[f'{field_name}_url'] = static(
                    f'timeline/demo_photos/{photo_filename}'
                )
        elif form.cleaned_data.get('image'):
            # Single image (Photo form)
            photo_filename = form.cleaned_data.get('image')
            entry.data['image_url'] = static(
                f'timeline/demo_photos/{photo_filename}'
            )
        
        entry.save()
        
        # Increment session counter
        self.request.session['demo_entry_count'] = (
            self.request.session.get('demo_entry_count', 0) + 1
        )
        
        messages.success(
            self.request,
            'Demo entry created! In the real app, this would be shared with all caregivers.'
        )
        
        return redirect('demo_timeline')
    
    def _save_real_entry(self, form):
        """Save a real entry (existing logic)."""
        # ... existing form_valid logic ...
        pass
```

## 7. CSS for Photo Picker

```css
/* timeline/static/timeline/css/style.css - Add these styles */

/* Demo Photo Picker */
.demo-photo-picker {
    margin: 20px 0;
}

.demo-photo-notice {
    background: #fff3cd;
    border: 2px solid #ffc107;
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 20px;
    display: flex;
    align-items: flex-start;
    gap: 12px;
}

.demo-notice-icon {
    font-size: 24px;
    flex-shrink: 0;
}

.demo-photo-notice p {
    margin: 0;
    font-size: 14px;
    line-height: 1.5;
}

.demo-photo-notice strong {
    color: #856404;
}

.demo-photo-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 15px;
    margin-top: 15px;
}

@media (max-width: 768px) {
    .demo-photo-grid {
        grid-template-columns: repeat(2, 1fr);
        gap: 10px;
    }
}

.demo-photo-option {
    position: relative;
    cursor: pointer;
    display: flex;
    flex-direction: column;
    border: 3px solid #ddd;
    border-radius: 8px;
    overflow: hidden;
    transition: all 0.3s ease;
    background: white;
}

.demo-photo-option:hover {
    border-color: #007bff;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.demo-photo-option.selected {
    border-color: #28a745;
    box-shadow: 0 0 0 3px rgba(40, 167, 69, 0.2);
}

.demo-photo-radio {
    position: absolute;
    opacity: 0;
    pointer-events: none;
}

.demo-photo-thumbnail {
    position: relative;
    width: 100%;
    padding-top: 75%; /* 4:3 aspect ratio */
    overflow: hidden;
    background: #f5f5f5;
}

.demo-photo-thumbnail img {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.demo-photo-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(40, 167, 69, 0.9);
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0;
    transition: opacity 0.3s ease;
}

.demo-photo-option.selected .demo-photo-overlay {
    opacity: 1;
}

.demo-photo-check {
    color: white;
    font-size: 48px;
    font-weight: bold;
}

.demo-photo-caption {
    padding: 10px;
    font-size: 13px;
    text-align: center;
    background: white;
    color: #333;
    min-height: 45px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.demo-photo-option.selected .demo-photo-caption {
    background: #28a745;
    color: white;
    font-weight: 600;
}

/* Demo Timeline Display */
.demo-entry-badge {
    display: inline-block;
    background: #ffc107;
    color: #856404;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 600;
    margin-left: 10px;
}
```

## 8. Template Updates

```django
{# timeline/templates/timeline/entry_form.html - Update to show demo notice #}
{% extends 'base.html' %}

{% block title %}
    {% if is_demo %}Demo: {% endif %}
    {{ form_type_obj.name }} - Timeline
{% endblock %}

{% block content %}
<div class="form-container">
    {% if is_demo %}
    <div class="demo-form-banner">
        <span class="demo-icon">🎭</span>
        <div>
            <strong>Demo Mode</strong>
            <p>{{ demo_entries_remaining }} demo entries remaining. 
               <a href="{% url 'signup' %}">Create a real account</a> for unlimited entries.</p>
        </div>
    </div>
    {% endif %}
    
    <div class="form-box">
        <h1>{{ form_type_obj.icon }} {{ form_type_obj.name }}</h1>
        {% if form_type_obj.description %}
        <p class="form-description">{{ form_type_obj.description }}</p>
        {% endif %}
        
        <form method="post" enctype="multipart/form-data" class="submission-form">
            {% csrf_token %}
            
            {# ... existing form rendering ... #}
            
        </form>
    </div>
</div>
{% endblock %}
```

## 9. Demo Entry Display Template

```django
{# timeline/templates/timeline/partials/entry_photo.html - Update for demo #}
{% load entry_display %}
{% load static %}

{# Check if this is a demo entry with demo photo URL #}
{% if entry.data.image_url %}
    <img src="{{ entry.data.image_url }}" alt="{{ entry.data.caption|default:'Photo' }}" class="timeline-image">
{% elif entry.image %}
    <img src="{{ entry.image.url }}" alt="{{ entry.data.caption|default:'Photo' }}" class="timeline-image">
{% endif %}

<div class="timeline-content">
    <p class="timeline-caption">{{ entry.data.caption|default:"No caption" }}</p>
    {% include "timeline/partials/_mood_display.html" with moods=entry.data.mood mood_notes=entry.data.mood_notes %}
    {% include "timeline/partials/entry_meta.html" %}
</div>
```

This implementation gives you:

1. ✅ **Sandboxed photos** - Only pre-selected demo images
2. ✅ **Clear explanation** - Users understand this is different from real app
3. ✅ **Touch-friendly UI** - Grid layout works great on mobile
4. ✅ **Visual feedback** - Selected photos show checkmark overlay
5. ✅ **Contextual photos** - Different categories for different form types
6. ✅ **No file upload risk** - Pure selection interface
7. ✅ **Professional demo** - Shows how the feature works without security concerns

Would you like me to also create a script to generate placeholder/sample demo images, or would you prefer to source your own photos for the demo?