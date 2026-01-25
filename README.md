# Timeline - Eddie's Daily Life Tracker

A Django application for maintaining a continuous record of daily information about Eddie, a mostly non-verbal autistic child, shared among all his caregivers.

## Project Purpose

Timeline serves as a central communication hub for Eddie's parents, teachers, paraprofessionals, therapists, babysitters, and other caregivers. The application addresses Eddie's limited verbal communication by providing a shared, chronological record of:

- **Essential daily functions**: Toileting, meals, sleep patterns
- **Transition information**: Status updates between home, school, and after-school programs
- **Engagement resources**: Photos and vocabulary for memory reinforcement and conversation
- **Activity tracking**: What Eddie is doing throughout his day across different settings
- **Mood and behavior**: How he's feeling and responding in different situations

### Primary Use Cases

**For Caregivers Receiving Eddie:**
- Quickly check when he last ate and used the bathroom
- See his mood and energy level from earlier in the day
- View recent photos to engage him in conversation
- Know what activities he's been doing
- Access vocabulary words he's currently working on

**For Caregivers Sending Eddie:**
- Share overnight information (dinner, sleep, breakfast) before school
- Log school activities for after-school program staff
- Upload weekend photos for Monday discussions at school
- Document new words and phrases Eddie is using

## Features

- 🕐 **Chronological Timeline**: Shared view of all entries from all caregivers
- 📝 **Multiple Form Types**: Structured data entry for different situations
- 📸 **Photo Uploads**: Visual records for engagement and memory reinforcement
- 👥 **Multi-User Access**: Role-based form access (parents, teachers, therapists, etc.)
- 📱 **Mobile-First Design**: Optimized for mobile browser access
- 🔒 **Secure Authentication**: Each caregiver has their own login
- ⚡ **Quick Status Check**: Immediate access to essential information
- 🎨 **Clean Interface**: Simple, focused design for fast information access

## Current Form Types

1. **Text Post** (📝) - General notes and observations
2. **Photo** (📸) - Picture uploads with captions for engagement
3. **Overnight** (🌙) - Dinner, sleep, and breakfast tracking (for parents)
4. **School Day** (🎒) - Comprehensive school activity log (for teachers)
5. **My Weekend** (🎉) - Weekend photos and descriptions (for Monday discussions)

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

Navigate to `http://localhost:8000/` and begin documenting Eddie's day!

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
Most users access via mobile browsers during Eddie's care, so the interface prioritizes:
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
- Tools for engaging Eddie in conversation and memory activities

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
│   │   ├── user.py             # User registration
│   │   └── registry.py         # Form registry
│   │
│   ├── templates/timeline/
│   │   ├── timeline.html       # Main timeline view
│   │   ├── entry_form.html     # Form submission
│   │   ├── auth/               # Login/signup
│   │   └── partials/           # Entry display templates
│   │
│   ├── static/timeline/css/
│   │   └── style.css           # Mobile-optimized styles
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
   - **Position/Role**: Their role in Eddie's care
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

### Production Checklist

- [ ] Set `DEBUG=False` in .env
- [ ] Set strong `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set up PostgreSQL database
- [ ] Configure S3 or file storage for photos
- [ ] Set up SSL/HTTPS
- [ ] Configure backup system
- [ ] Test on multiple mobile devices

### Recommended Hosting
- **App**: Heroku, Railway, or PythonAnywhere
- **Database**: Heroku Postgres or AWS RDS
- **Media Storage**: AWS S3 or Cloudinary
- **Domain**: Custom domain for easy access (e.g., eddies-timeline.com)

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

This is a personal project for Eddie's care team. If you're part of Eddie's care team and have questions or suggestions, contact Dad directly.

For technical issues or ideas:
- Create an issue in the repository
- Discuss during development meetings
- Email the developer

## License

Private use only. Not for public distribution.

---

**For Eddie**: This app exists to help everyone who cares for you communicate better, so we can all work together to support you, understand you, and help you thrive. Every entry here represents someone who loves you and wants the best for you.

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
