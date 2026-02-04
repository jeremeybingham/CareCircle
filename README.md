# Timeline - Caregiver Communication Hub

A Django application originally designed for maintaining a continuous record of daily information about a mostly non-verbal autistic child, shared among all caregivers.

## Project Purpose

Timeline serves as a central communication hub for parents, teachers, paraprofessionals, therapists, babysitters, and other caregivers. The application addresses limited verbal communication by providing a shared, chronological record of:

- **Essential daily functions**: Toileting, meals, sleep patterns
- **Transition information**: Status updates between home, school, and after-school programs
- **Engagement resources**: Photos and vocabulary for memory reinforcement and conversation
- **Activity tracking**: What the child is doing throughout the day across different settings
- **Mood and behavior**: How they're feeling and responding in different situations

### Primary Use Cases

**For Caregivers Receiving the Child:**
- Quickly check when they last ate and used the bathroom
- See their mood and energy level from earlier in the day
- View recent photos to engage them in conversation
- Know what activities they've been doing
- Access vocabulary words they're currently working on

**For Caregivers Sending the Child:**
- Share overnight information (dinner, sleep, breakfast) before school
- Log school activities for after-school program staff
- Upload weekend photos for Monday discussions at school
- Document new words and phrases the child is using

## Features

- 🕐 **Chronological Timeline**: Shared view of all entries from all caregivers
- 📝 **Multiple Form Types**: Structured data entry for different situations (6 built-in forms)
- 📸 **Photo Uploads**: Visual records for engagement and memory reinforcement
- 👥 **Multi-User Access**: Role-based form access (parents, teachers, therapists, etc.)
- 📱 **Mobile-First Design**: Optimized for mobile browser access
- 🔒 **Secure Authentication**: Each caregiver has their own login
- ⚡ **Quick Status Check**: Immediate access to essential information
- 🎨 **Clean Interface**: Simple, focused design for fast information access
- 📌 **Post Pinning**: Pin important entries to the top of the timeline
- 🗑️ **Post Deletion**: Remove entries with permission-based controls
- 💬 **Vocabulary Tracking**: Track words and phrases the child is using

## Current Form Types

1. **Text Post** (📝) - General notes and observations
2. **Photo** (📸) - Picture uploads with captions for engagement
3. **Overnight** (🌙) - Dinner, sleep, and breakfast tracking (for parents)
4. **School Day** (🎒) - Comprehensive school activity log (for teachers)
5. **My Weekend** (🎉) - Weekend photos and descriptions (for Monday discussions)
6. **Words I'm Using** (💬) - Track new words and phrases the child is using

## Project Status

**Current Stage**: Alpha - Core features and functionality being established

**Primary Focus**: 
- Ensuring reliability and ease of use
- Maintaining flexibility for new forms and situations
- Mobile browser optimization
- Clean, simple interface

**Future Goals**:
- Analytics dashboard (food patterns, sleep quality, mood trends)
- Vocabulary tracking and progress metrics
- Advanced photo tagging and categorization

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd timeline

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env and set SECRET_KEY
```

### 2. Database Setup

```bash
# Run migrations
python manage.py migrate

# Create admin account
python manage.py createsuperuser
```

### 3. Initialize Form Types

```bash
# Load form types into database
python manage.py init_forms
```

### 4. Configure User Access

```bash
# Start development server
python manage.py runserver

# Navigate to admin
open http://localhost:8000/admin/

# Login with superuser credentials
```

In the admin:
1. **Create users** for each caregiver (parents, teachers, therapists, etc.)
2. **Set up profiles** with display names and roles
3. **Grant form access** - assign appropriate forms to each user role
4. Mark forms as **"is_default"** if all new users should have access

### 5. Start Using

Navigate to `http://localhost:8000/` and begin documenting the child's day!

## User Roles

The application is designed for different caregiver roles, each with access to relevant forms:

- **Parents**: Overnight logs, photos, weekend activities, general notes
- **Teachers**: School day logs, photos, vocabulary, activities
- **Paraprofessionals**: Activity tracking, photos, notes
- **Therapists** (ABA, Speech, etc.): Session notes, progress tracking, vocabulary
- **Babysitters/Extended Family**: Photos, meals, activities, notes
- **After-School Program Staff**: Transition info, activities, snacks

## Core Design Principles

### 1. Mobile-First
Most users access via mobile browsers during caregiving, so the interface prioritizes:
- Large touch targets
- Minimal scrolling
- Fast loading
- Simple navigation

### 2. Essential Information First
The timeline prioritizes showing:
- Recent bathroom times
- Last meal and what was eaten
- Current mood/energy level
- Latest photos and activities

### 3. Quick Entry
Forms are designed for rapid data entry:
- Pre-defined choices where possible
- Minimal required fields
- Clear labels and instructions
- Auto-save and confirmation

### 4. Engagement Resources
Photos and vocabulary entries serve dual purposes:
- Information sharing between caregivers
- Tools for engaging the child in conversation and memory activities

## Project Structure

```
timeline/
├── config/                      # Project settings
│   ├── settings.py             # Django configuration
│   ├── urls.py                 # URL routing
│   └── wsgi.py
│
├── timeline/                    # Main app
│   ├── forms/                   # Django Forms
│   │   ├── base.py             # Base form class
│   │   ├── text.py             # General notes
│   │   ├── photo.py            # Photo uploads
│   │   ├── overnight.py        # Sleep/meal tracking
│   │   ├── schoolday.py        # School activities
│   │   ├── weekend.py          # Weekend activities
│   │   ├── words.py            # Vocabulary tracking
│   │   ├── user.py             # User registration
│   │   └── registry.py         # Form registry
│   │
│   ├── templates/timeline/
│   │   ├── timeline.html       # Main timeline view
│   │   ├── entry_form.html     # Form submission
│   │   ├── entry_confirm_delete.html  # Delete confirmation
│   │   ├── entry_confirm_pin.html     # Pin confirmation
│   │   ├── entry_confirm_unpin.html   # Unpin confirmation
│   │   ├── auth/               # Login/signup templates
│   │   └── partials/           # Entry display templates
│   │       ├── entry_meta.html     # Shared timestamp/author display
│   │       ├── entry_text.html     # Text post display
│   │       ├── entry_photo.html    # Photo display
│   │       ├── entry_overnight.html # Overnight display
│   │       ├── entry_schoolday.html # School day display
│   │       ├── entry_weekend.html  # Weekend display
│   │       ├── entry_words.html    # Words display
│   │       └── entry_default.html  # Fallback display
│   │
│   ├── static/timeline/css/
│   │   └── style.css           # Mobile-optimized styles (1000+ lines)
│   │
│   ├── templatetags/
│   │   └── entry_display.py    # Custom template tags
│   │
│   ├── management/commands/
│   │   └── init_forms.py       # Form initialization command
│   │
│   ├── models.py               # Database models
│   ├── views.py                # View logic
│   ├── admin.py                # Admin interface
│   └── urls.py                 # App URL routing
│
├── templates/
│   └── base.html               # Base template
│
├── manage.py
├── requirements.txt
├── README.md
├── CLAUDE.md                   # AI assistant context
├── ADDING_FORMS.md             # Guide for adding new form types
└── TODO.md                     # Development roadmap
```

## Adding Caregivers

### Creating a New User Account

1. Access admin at `/admin/`
2. Navigate to **Users** → **Add User**
3. Set username and password
4. Save and continue editing
5. Fill in profile information:
   - **Display Name**: How they'll appear on posts (e.g., "Ms. Johnson", "Dad", "Speech Therapist Sarah")
   - **Email Address**: For contact and notifications
   - **Position/Role**: Their role in the child's care
   - **First/Last Name**: Legal name
6. Save

### Granting Form Access

1. In admin, go to **User Form Access**
2. Add new access entries for the user
3. Select appropriate forms based on their role:
   - **Teachers**: School Day, Photo, Text
   - **Parents**: Overnight, My Weekend, Photo, Text
   - **Therapists**: Text, Photo, specific therapy forms
4. Save

## Adding New Forms

See `ADDING_FORMS.md` for comprehensive instructions.

**Quick Overview:**
1. Create form class in `timeline/forms/newform.py` inheriting from `BaseEntryForm`
2. Register in `timeline/forms/registry.py`
3. Run `python manage.py init_forms`
4. Create display template: `timeline/templates/timeline/partials/entry_newform.html`
5. Assign to appropriate users in admin

**Example Use Cases for New Forms:**
- Therapy session notes (OT, PT, Speech)
- Behavior incident reports
- Medication tracking
- Sensory activities log
- Social interactions log

## Key Information Display

The timeline is designed to make critical information immediately visible:

### Status at a Glance
Each entry shows:
- **Timestamp**: When the activity occurred
- **Author**: Which caregiver logged it (by display name)
- **Form Type**: What kind of information (icon + label)
- **Key Data**: Most important details prominently displayed

### Recent Activity Tracking
The timeline allows caregivers to quickly scan for:
- Last bathroom time
- Most recent meal and portion eaten
- Current mood indicators
- Latest photos for engagement
- Recent vocabulary words

## Mobile Browser Optimization

### Design Considerations
- **Large touch targets**: Buttons and form inputs sized for thumbs
- **Minimal typing**: Checkboxes and dropdowns preferred over text entry
- **Fast loading**: Optimized images and minimal JavaScript
- **Responsive layout**: Adapts to phone and tablet screens
- **Offline-friendly**: Forms can be completed and submitted when connection returns

### Recommended Usage
- Access via mobile browser (Safari, Chrome, Firefox on iOS/Android)
- Bookmark the site for quick access
- Enable notifications (future feature) for updates

## Development

### For the Developer (Dad)

**Common Development Tasks:**

```bash
# Update form types after registry changes
python manage.py init_forms

# Create new database migration
python manage.py makemigrations
python manage.py migrate

# Collect static files for production
python manage.py collectstatic

# Run tests
python manage.py test timeline
```

**Key Files for Modifications:**
- `timeline/forms/registry.py` - Add new form types
- `timeline/models.py` - Database structure changes
- `timeline/static/timeline/css/style.css` - Visual styling
- `timeline/templates/timeline/partials/` - How entries display

## Deployment

### Target Deployment Environment

**AWS Lightsail Ubuntu** with the following stack:
- **Web Server**: Nginx (reverse proxy)
- **Application Server**: Gunicorn (WSGI)
- **SSL/HTTPS**: Let's Encrypt (certbot)
- **Database**: PostgreSQL
- **Media Storage**: AWS S3 (recommended for photos)

### Production Checklist

- [ ] Set `DEBUG=False` in .env
- [ ] Set strong `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set up PostgreSQL database
- [ ] Configure S3 or file storage for photos
- [ ] Set up SSL/HTTPS with Let's Encrypt
- [ ] Configure Nginx as reverse proxy
- [ ] Set up Gunicorn with systemd service
- [ ] Configure backup system
- [ ] Test on multiple mobile devices

### AWS Lightsail Setup

1. Create Ubuntu instance on AWS Lightsail
2. Install system dependencies: `sudo apt install python3-pip python3-venv nginx postgresql`
3. Set up PostgreSQL database and user
4. Clone repository and create virtual environment
5. Install Python dependencies: `pip install -r requirements.txt gunicorn`
6. Configure Gunicorn systemd service
7. Configure Nginx with proxy_pass to Gunicorn
8. Install certbot and configure Let's Encrypt SSL
9. Set up S3 bucket for media storage (optional but recommended)

### Alternative Hosting
- **App**: Heroku, Railway, or PythonAnywhere
- **Database**: Heroku Postgres or AWS RDS
- **Media Storage**: AWS S3 or Cloudinary
- **Domain**: Custom domain for easy access

## Privacy and Security

### Data Protection
- All data is private to authenticated users only
- No public access to timeline or photos
- User passwords hashed and secured
- Optional: HTTPS encryption for all data transmission

### User Management
- Each caregiver has individual login credentials
- Access can be granted or revoked per user
- Form access is role-based and customizable
- Admin (parent) has full control over all access

## Future Enhancements

### Planned Features
- **Analytics Dashboard**: Track patterns in food, sleep, mood, activities
- **Vocabulary Progress**: Chart word usage and growth over time
- **Photo Tagging**: Categorize photos by activity type, people, locations
- **Push Notifications**: Alert caregivers to new entries
- **Daily Summaries**: Automated end-of-day reports
- **Export/Printing**: Generate reports for doctors, therapists, school meetings
- **Voice Notes**: Audio attachments for non-typing situations

### Long-Term Goals
- Mobile apps (iOS/Android) for better offline support
- Integration with external calendars
- Medication reminder and tracking
- Appointment scheduling and notes
- Behavior pattern recognition
- Customizable reports for IEP meetings

## Support and Contribution

This is a personal project for the care team. If you're part of the care team and have questions or suggestions, contact the administrator directly.

For technical issues or ideas:
- Create an issue in the repository
- Discuss during development meetings
- Email the developer

## License

Private use only. Not for public distribution.

---

## Quick Reference

**Main Goals:**
1. ✅ Quick access to last meal/bathroom/mood
2. ✅ Photo sharing for engagement and memory
3. ✅ Seamless information handoff between caregivers
4. ✅ Vocabulary and activity tracking
5. ✅ Simple, mobile-friendly interface

**Key Commands:**
```bash
python manage.py runserver          # Start server
python manage.py init_forms         # Update forms
python manage.py createsuperuser    # Create admin
```

**Admin Access:** `/admin/`  
**Main Timeline:** `/`  
**User Signup:** `/signup/` (requires admin approval)
