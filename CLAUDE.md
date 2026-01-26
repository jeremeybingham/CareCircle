# CLAUDE.md - AI Assistant Context

This file provides context for AI assistants working on the Timeline project.

## Project Overview

**Timeline** is a Django 5.0+ web application designed to maintain a continuous record of daily information about Eddie, a mostly non-verbal autistic child. The application serves as a central communication hub for all of Eddie's caregivers.

**Purpose**: Enable seamless information sharing between Eddie's parents, teachers, paraprofessionals, therapists, babysitters, and other caregivers. The app addresses Eddie's limited verbal communication by providing a shared chronological record of essential daily functions, activities, mood, photos, and vocabulary.

**Developer**: Solo developer (Dad/Parent)

**Tech Stack**: Django 5.0+, Python 3.x, SQLite/PostgreSQL, Pillow, custom CSS (no JavaScript frameworks)

**Design Focus**: Mobile-first (primary access via mobile browsers during care)

## Core User Needs

### Primary Goals (Priority Order)
1. **Quick status check**: Last meal/bathroom time, current mood
2. **Recent photos**: For engagement and memory reinforcement  
3. **Transition information**: Smooth handoffs between caregivers (home→school→after-school)
4. **Vocabulary tracking**: Words and phrases Eddie is working on
5. **Activity awareness**: What Eddie has been doing throughout the day

### User Roles
- **Parents**: Overnight logs, weekend activities, photos, general notes
- **Teachers**: School day logs, activities, photos, vocabulary
- **Paraprofessionals**: Activity tracking, support notes
- **Therapists** (ABA, Speech, OT): Session notes, progress, vocabulary
- **Babysitters/Extended Family**: Photos, meals, activities
- **After-School Program Staff**: Transition info, activities, snacks

### Key Use Cases

**Receiving Eddie (e.g., teacher at morning drop-off):**
- Check overnight form: Did he eat dinner? How did he sleep? Did he eat breakfast?
- See if parents noted anything unusual (mood, behavior, health)
- View recent photos to engage him in conversation

**Sending Eddie (e.g., teacher at end of school day):**
- Log school day activities, bathroom times, lunch consumption
- Upload photos of activities for after-school staff and parents
- Note new words/phrases used or any incidents

**Engaging Eddie:**
- Show him weekend photos and read descriptions to reinforce memory
- Use vocabulary entries from other caregivers for consistency
- Ask questions about activities shown in recent photos

## Quick Commands

```bash
# Start development server
python manage.py runserver

# Run migrations
python manage.py migrate

# Initialize/update form types from registry
python manage.py init_forms

# Reset all form types
python manage.py init_forms --reset

# Create new user (caregiver)
python manage.py createsuperuser

# Run tests
python manage.py test timeline

# Collect static files
python manage.py collectstatic
```

## Key Architecture Patterns

### Registry Pattern for Forms
Forms are dynamically discovered via a central registry. This allows easy addition of new forms for different caregiver roles and situations.

**To add a new form type:**
1. Create form class in `timeline/forms/newform.py` inheriting from `BaseEntryForm`
2. Register in `timeline/forms/registry.py` (FORM_REGISTRY dict)
3. Export in `timeline/forms/__init__.py`
4. Run `python manage.py init_forms`
5. Create display template: `timeline/templates/timeline/partials/entry_newform.html`
6. Grant access to appropriate user roles in admin

### Template Inheritance
- `templates/base.html` - Root template with navbar, messages, blocks
- `timeline/templates/timeline/*.html` - Page templates
- `timeline/templates/timeline/partials/*.html` - Reusable entry display components
- `timeline/templates/timeline/partials/entry_meta.html` - Shared timestamp/author display

### Custom Template Tags
Located in `timeline/templatetags/entry_display.py`:
- `render_entry` - Renders entry with type-specific template
- `split_commas` - Splits comma-separated strings into lists for tags
- `get_item` - Dictionary access in templates

## Critical Files

| File | Purpose |
|------|---------|
| `timeline/models.py` | 4 models: FormType, UserFormAccess, Entry, UserProfile |
| `timeline/views.py` | TimelineListView, EntryCreateView, EntryDeleteView, EntryPinView, EntryUnpinView, SignupView, API views |
| `timeline/forms/registry.py` | Central form registry (FORM_REGISTRY dict) - add new forms here |
| `timeline/forms/base.py` | BaseEntryForm - all forms inherit from this |
| `timeline/forms/user.py` | Custom user registration with profile fields |
| `timeline/admin.py` | Admin customizations for managing users and form access |
| `config/settings.py` | Django settings, environment variable handling |
| `timeline/static/timeline/css/style.css` | All styling (1000+ lines, mobile-optimized) |

## Models

### Entry
- Stores timeline entries with JSON data field for flexible form data
- Optional image field for photos (essential for engagement)
- Foreign keys to User and FormType
- `is_pinned` - Boolean to pin entry to top of timeline
- Indexed on timestamp, (user, timestamp), and (is_pinned, timestamp) for fast queries
- Ordering: pinned entries first, then by timestamp descending
- Properties: `type`, `get_display_data()`

### FormType
- Defines available form types (name, type, icon, description)
- `is_active` - Whether form can be used
- `is_default` - Auto-granted to new users via signal
- Created/managed via `init_forms` command from registry

### UserFormAccess
- Many-to-many between User and FormType
- Controls which forms each caregiver can access (role-based)
- Tracks who granted access and when
- Unique constraint on (user, form_type)

### UserProfile
- One-to-one with Django User model
- Fields: display_name (shown on posts), email_address, position_role, first_name, last_name
- Permission fields:
  - `can_pin_posts` - Allow user to pin their own posts
  - `can_pin_any_post` - Allow user to pin any post
  - `can_delete_any_post` - Allow user to delete any post (not just their own)
- Auto-created on user signup via signal handler
- `display_name` examples: "Dad", "Ms. Johnson", "Speech Therapist Sarah"

## URL Routes

| URL | View | Purpose |
|-----|------|---------|
| `/` | TimelineListView | Main shared timeline (requires login) |
| `/entry/<form_type>/` | EntryCreateView | Create new entry (dynamic form loading) |
| `/entry/<pk>/delete/` | EntryDeleteView | Delete an entry (owner or admin) |
| `/entry/<pk>/pin/` | EntryPinView | Pin an entry to top of timeline |
| `/entry/<pk>/unpin/` | EntryUnpinView | Unpin an entry |
| `/api/entries/` | api_entries | JSON API for entries (future: mobile app) |
| `/api/forms/` | api_forms | JSON API for available forms |
| `/signup/` | SignupView | User registration with profile |
| `/login/` | LoginView | Authentication |
| `/logout/` | LogoutView | Sign out |
| `/admin/` | Admin site | User/form management |

## Current Form Types

| Type Key | Name | Icon | Primary Users | Purpose |
|----------|------|------|---------------|---------|
| `text` | Text Post | 📝 | All | General notes and observations |
| `photo` | Photo | 📸 | All | Picture uploads for engagement/memory |
| `overnight` | Overnight | 🌙 | Parents | Dinner, sleep, breakfast (morning handoff info) |
| `schoolday` | School Day | 🎒 | Teachers | Comprehensive school activity log |
| `weekend` | My Weekend | 🎉 | Parents | Weekend photos + descriptions (Monday discussions) |
| `words` | Words I'm Using | 💬 | All | Track new words and phrases Eddie is using |

## Adding Features

### Adding a New Form Type
See `ADDING_FORMS.md` for detailed steps. Key files:
- `timeline/forms/newform.py` - Form class inheriting BaseEntryForm
- `timeline/forms/registry.py` - Add to FORM_REGISTRY
- `timeline/templates/timeline/partials/entry_newform.html` - Display template

**Common New Form Ideas:**
- Therapy session notes (OT, PT, Speech)
- Medication tracking
- Behavior incident reports
- Sensory activities log
- Social interactions log

### Modifying Entry Display
- Edit type-specific template in `partials/entry_*.html`
- Shared metadata (timestamp, author) is in `partials/entry_meta.html`
- Styles in `timeline/static/timeline/css/style.css`
- **Key**: Ensure mobile readability (large text, minimal scrolling)

### Adding User (Caregiver)
1. Create user in admin (`/admin/users/`)
2. Set profile fields (display_name, role, email)
3. Grant form access via UserFormAccess
4. Test login and form submission

### Modifying Models
1. Edit model in `timeline/models.py`
2. Run `python manage.py makemigrations`
3. Review migration file
4. Run `python manage.py migrate`
5. Update admin in `timeline/admin.py` if needed
6. Update forms/templates as needed

## Common Gotchas

1. **Forms not showing in FAB**: Run `python manage.py init_forms` after adding to registry
2. **User can't access form**: Grant access via UserFormAccess in admin
3. **New form not rendering**: Check template exists at `partials/entry_<type>.html` with exact name match
4. **Static files not updating**: Run `python manage.py collectstatic` and hard refresh browser
5. **UserProfile missing**: Auto-created on signup; for existing users, create manually in admin
6. **Image not displaying**: Check MEDIA_URL and MEDIA_ROOT settings, ensure media/ directory exists
7. **Mobile layout broken**: Test with actual mobile browser, not just browser dev tools

## Design Principles

### Mobile-First
- **Primary access**: Mobile browsers during caregiving
- **Touch targets**: Minimum 44px for buttons/inputs
- **Font sizes**: 15px+ for body text, 13px+ for labels
- **Forms**: Radio/checkboxes over text input where possible
- **Loading**: Optimize images, minimal JavaScript
- **Layout**: Single column, clear hierarchy, generous spacing

### Essential Information First
Timeline displays prioritize:
1. Timestamp (when it happened)
2. Author (which caregiver logged it)
3. Form type (what kind of info)
4. Key data (bathroom time, meal portion, mood, photo)

### Quick Entry
- Pre-defined choices reduce typing
- Minimal required fields
- Clear labels with context
- Validation with helpful error messages
- Success feedback after submission

### Engagement Resources
Photos serve dual purposes:
- Inform other caregivers of activities
- Provide conversation prompts with Eddie
- Reinforce memory of events
- Build consistent vocabulary across caregivers

## Database Schema

Default: SQLite at `db.sqlite3`  
Production: PostgreSQL recommended

Key tables:
- `timeline_formtype` - Form type definitions
- `timeline_userformaccess` - User-form permissions (role-based access)
- `timeline_entry` - Timeline entries (JSON data field for flexibility)
- `timeline_userprofile` - Extended user info (display names, roles)
- `auth_user` - Django built-in user authentication

## Environment Variables

See `.env.example` for all options. Key vars:
- `SECRET_KEY` - Django secret (required in production)
- `DEBUG` - Set False in production
- `DATABASE_ENGINE` - sqlite3 or postgresql
- `DATABASE_NAME` - Database name/path
- `USE_S3` - Enable S3 storage for photos (recommended for production)
- `AWS_*` - S3 credentials if using

## Testing

```bash
# Run all tests
python manage.py test timeline

# Run with verbose output
python manage.py test timeline -v 2

# Run specific test
python manage.py test timeline.tests.TestClassName

# Test on mobile
# - Use actual devices when possible
# - Test forms, photo uploads, timeline scrolling
# - Check readability and touch target sizes
```

## Current Status

**Stage**: Alpha - Core features being established and tested

### Completed
✅ Multi-user shared timeline with author display names
✅ User registration with profile information (display name, role)
✅ 6 form types (text, photo, overnight, schoolday, weekend, words)
✅ Photo uploads for engagement
✅ Mobile-optimized CSS (1000+ lines)
✅ Role-based form access system
✅ Shared entry_meta.html partial for consistent display
✅ Post pinning (pin important entries to top of timeline)
✅ Post deletion with permission controls
✅ Vocabulary tracking ("Words I'm Using" form)
✅ Permission-based controls (can_pin_posts, can_pin_any_post, can_delete_any_post)

### In Progress
🔨 Testing with actual caregivers
🔨 Refining mobile UX based on real usage
🔨 Adding specialized forms for therapists

### Planned (see TODO.md)
📋 Analytics dashboard (food/sleep/mood patterns)
📋 Vocabulary tracking metrics
📋 Daily summary reports
📋 Push notifications for new entries
📋 Photo tagging and categorization  

### Future Considerations
- Mobile apps (iOS/Android) for better offline support
- Voice notes for situations where typing is difficult
- Integration with external calendars
- Medication reminders
- Appointment tracking
- Behavior pattern recognition
- IEP meeting report generation

## Development Workflow

### Adding a New Caregiver
1. Admin → Users → Add User
2. Set username, password, save
3. Edit user → Fill profile (display_name, role, email)
4. Admin → User Form Access → Grant appropriate forms
5. Send login credentials to caregiver
6. Have them test login and form submission

### Adding a New Form for Specific Role
Example: Speech therapist needs session notes form

1. Create `timeline/forms/speech_session.py`:
```python
from django import forms
from .base import BaseEntryForm

class SpeechSessionForm(BaseEntryForm):
    duration = forms.IntegerField(label="Session Duration (minutes)")
    words_practiced = forms.CharField(widget=forms.Textarea)
    progress_notes = forms.CharField(widget=forms.Textarea)
```

2. Add to `timeline/forms/registry.py`:
```python
from .speech_session import SpeechSessionForm

FORM_REGISTRY = {
    # ... existing forms ...
    'speech_session': {
        'form_class': SpeechSessionForm,
        'name': 'Speech Therapy Session',
        'icon': '🗣️',
        'description': 'Speech therapy session notes and progress',
    },
}
```

3. Add to `timeline/forms/__init__.py`:
```python
from .speech_session import SpeechSessionForm
__all__ = [
    # ... existing forms ...
    'SpeechSessionForm',
]
```

4. Run `python manage.py init_forms`

5. Create `timeline/templates/timeline/partials/entry_speech_session.html`:
```django
<div class="timeline-content">
    <h2 class="timeline-title">
        <span class="timeline-icon">{{ entry.form_type.icon }}</span>
        Speech Therapy Session
    </h2>
    
    <div class="data-list">
        <p><strong>Duration:</strong> {{ entry.data.duration }} minutes</p>
        <p><strong>Words Practiced:</strong> {{ entry.data.words_practiced }}</p>
        <p><strong>Progress Notes:</strong> {{ entry.data.progress_notes }}</p>
    </div>
    
    {% include 'timeline/partials/entry_meta.html' %}
</div>
```

6. Admin → User Form Access → Grant to speech therapist user
7. Test as speech therapist

### Modifying Existing Form
1. Edit form class in `timeline/forms/<formname>.py`
2. Update display template in `timeline/templates/timeline/partials/entry_<formname>.html`
3. Test submission and display
4. Check mobile rendering

### Styling Changes
1. Edit `timeline/static/timeline/css/style.css`
2. Run `python manage.py collectstatic` if in production
3. Hard refresh browser (Cmd+Shift+R or Ctrl+Shift+R)
4. Test on actual mobile device

## Key Context for AI Assistants

### When suggesting changes, consider:
1. **Eddie's needs**: Will this help caregivers better understand and support Eddie?
2. **Mobile usability**: Is it easy to use on a phone during caregiving?
3. **Quick access**: Can caregivers find essential info (bathroom, food, mood) in <10 seconds?
4. **Engagement value**: Does it provide resources to interact with Eddie?
5. **Caregiver burden**: Is data entry quick and simple?
6. **Flexibility**: Can it adapt to new situations/users easily?

### Always prioritize:
1. Essential information visibility (bathroom, food, mood)
2. Mobile browser experience
3. Simple, clean interface
4. Fast loading and submission
5. Photo sharing for engagement
6. Consistency across caregivers

### Avoid:
1. Complex interfaces requiring training
2. Desktop-only features
3. Excessive typing requirements
4. Non-essential fields in forms
5. Anything that slows down data entry
6. Features that don't serve Eddie's needs

## Production Deployment Considerations

### Target Deployment: AWS Lightsail Ubuntu

The target deployment environment is **AWS Lightsail Ubuntu** with the following stack:
- **Web Server**: Nginx (reverse proxy)
- **Application Server**: Gunicorn (WSGI)
- **SSL/HTTPS**: Let's Encrypt (certbot)
- **Database**: PostgreSQL
- **Media Storage**: AWS S3 (recommended for photos)

### AWS Lightsail Setup Steps
1. Create Ubuntu instance on AWS Lightsail
2. Install system dependencies: `sudo apt install python3-pip python3-venv nginx postgresql`
3. Set up PostgreSQL database and user
4. Clone repository and create virtual environment
5. Install Python dependencies: `pip install -r requirements.txt gunicorn`
6. Configure Gunicorn systemd service
7. Configure Nginx with proxy_pass to Gunicorn
8. Install certbot and configure Let's Encrypt SSL
9. Set up S3 bucket for media storage

### Essential for Production
- HTTPS/SSL for all traffic (via Let's Encrypt)
- PostgreSQL database (not SQLite)
- S3 or Cloudinary for photo storage
- Daily database backups
- Environment-based settings (DEBUG=False)
- Strong SECRET_KEY
- Rate limiting for API endpoints
- Error monitoring (Sentry or similar)

### Alternative Hosting
- **App**: Heroku, Railway, or PythonAnywhere
- **Database**: Heroku Postgres or AWS RDS
- **Media**: AWS S3 or Cloudinary
- **Domain**: Short, memorable domain for easy mobile access

### Performance Optimization
- Optimize uploaded photos (resize on upload)
- Database query optimization (select_related, prefetch_related)
- Static file CDN for CSS
- Caching for timeline view
- Pagination for long timelines

## Privacy and Security

**Critical**: This app contains private information about a child with special needs.

- All data is private, authentication required
- No public access to any content
- User passwords properly hashed
- Photos stored securely
- Admin (parent) has full control
- User access can be revoked immediately
- Consider HIPAA compliance for therapy notes

## Notes for AI Assistants

This is a **personal project** for a family supporting their autistic son. The developer is Eddie's dad, working solo to build tools that help Eddie's care team communicate effectively.

**Tone**: Professional but compassionate. This isn't just a coding exercise—it's about helping a child and supporting the people who care for him.

**Success Metrics**: 
- Do caregivers use it regularly?
- Does it improve communication between home and school?
- Does it help Eddie's consistency and progress?
- Is it easy enough for all caregivers to use?

**Remember**: Every feature should serve the goal of helping caregivers better understand, support, and engage with Eddie.
