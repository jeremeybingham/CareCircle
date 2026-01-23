# Timeline - Personal Timeline Application

A clean, flexible Django application for tracking personal events, activities, and information over time.

## Features

- 📝 **Multiple Form Types**: Text posts, photos, overnight logs, school day tracking
- 🔒 **User Authentication**: Secure signup/login system
- 🎨 **Clean UI**: Simple, responsive design
- 🔧 **Admin Control**: Manage forms and user access via Django admin
- 📊 **Timeline View**: Chronological display with filtering
- 🔍 **Flexible Architecture**: Easy to add new form types
- 📱 **Mobile Responsive**: Works on all devices

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd new_timeline

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

# Create superuser for admin access
python manage.py createsuperuser
```

### 3. Initialize Form Types

```bash
# Load form types from registry into database
python manage.py init_forms
```

### 4. Configure Forms (via Admin)

```bash
# Start development server
python manage.py runserver

# Navigate to admin
open http://localhost:8000/admin/

# Login with superuser credentials
```

In the admin:
1. Go to **Form Types**
2. Mark desired forms as **"is_default"** (auto-granted to new users)
3. Go to **User Form Access**
4. Grant form access to your admin user
5. Grant access to other users as needed

### 5. Start Using

Navigate to `http://localhost:8000/` and start creating timeline entries!

## Project Structure

```
new_timeline/
├── config/                      # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── timeline/                    # Main app
│   ├── forms/                   # Django Forms
│   │   ├── base.py             # Base form class
│   │   ├── text.py             # Text post form
│   │   ├── photo.py            # Photo form
│   │   ├── overnight.py        # Overnight form
│   │   ├── schoolday.py        # School day form
│   │   └── registry.py         # Form registry
│   │
│   ├── templates/timeline/
│   │   ├── timeline.html       # Main timeline view
│   │   ├── entry_form.html     # Generic form template
│   │   ├── auth/               # Login/signup
│   │   └── partials/           # Entry display templates
│   │
│   ├── static/timeline/css/
│   │   └── style.css           # Styles
│   │
│   ├── templatetags/
│   │   └── entry_display.py    # Custom template tags
│   │
│   ├── management/commands/
│   │   └── init_forms.py       # Initialize forms
│   │
│   ├── models.py               # Database models
│   ├── views.py                # Views
│   ├── urls.py                 # URL routing
│   └── admin.py                # Admin interface
│
├── templates/
│   └── base.html               # Base template
│
├── manage.py
├── requirements.txt
└── README.md
```

## Available Form Types

1. **Text Post** (📝) - Simple title and content
2. **Photo** (📸) - Image upload with caption
3. **Overnight** (🌙) - Track dinner, sleep, breakfast routine
4. **School Day** (🎒) - Comprehensive school activity tracking

## Adding a New Form Type

See `ADDING_FORMS.md` for detailed instructions.

Quick overview:
1. Create form class in `timeline/forms/newform.py`
2. Add to `timeline/forms/registry.py`
3. Run `python manage.py init_forms`
4. Create display template: `timeline/partials/entry_newform.html`
5. Configure access in admin

## API Endpoints

The application includes JSON API endpoints:

- `GET /api/entries/` - Get user's entries
  - Parameters: `form_type` (filter), `limit` (max results)
- `GET /api/forms/` - Get available forms

## Management Commands

### Initialize Forms
```bash
python manage.py init_forms
```
Loads form types from code into database.

Options:
- `--reset` - Delete all existing form types and recreate

## Configuration

### Environment Variables (.env)

```
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOST=your-domain.com
```

### Settings

Key settings in `config/settings.py`:
- `LOGIN_REDIRECT_URL` - Where to redirect after login
- `MEDIA_ROOT` - Where uploaded images are stored
- `STATIC_ROOT` - Where static files are collected

## Development

### Running Tests

```bash
python manage.py test timeline
```

### Collecting Static Files

```bash
python manage.py collectstatic
```

### Creating Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

## Deployment

### Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Set strong `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set up proper database (PostgreSQL recommended)
- [ ] Configure S3 or file storage
- [ ] Run `collectstatic`
- [ ] Set up SSL/HTTPS
- [ ] Configure email backend
- [ ] Set up backup system

### Database Migration from Old Version

Not applicable - this is a fresh implementation. If you have data from the old version, you'll need to write a custom migration script.

## Architecture

### Models
- **FormType** - Metadata about form types (name, icon, description)
- **UserFormAccess** - Controls which users can use which forms
- **Entry** - Actual timeline entries (stores data as JSON)

### Forms
- Django Forms for validation and rendering
- Registry pattern for form discovery
- Base class for shared functionality

### Views
- Class-based views (ListView, FormView, CreateView)
- Dynamic form loading based on URL parameter
- API views for programmatic access

### Templates
- Template inheritance from base.html
- Custom template tag for entry rendering
- Type-specific display partials

## Customization

### Styling

Edit `timeline/static/timeline/css/style.css` for custom styles.

Key CSS classes:
- `.timeline-item` - Entry container
- `.timeline-{type}` - Type-specific styling
- `.fab` - Floating action buttons

### Form Validation

Add validation in form classes:
```python
def clean_fieldname(self):
    value = self.cleaned_data.get('fieldname')
    # Validate
    return value
```

## Troubleshooting

### Forms not showing up
- Run `python manage.py init_forms`
- Check form is marked `is_active=True` in admin
- Verify user has UserFormAccess for the form

### Images not uploading
- Check `MEDIA_ROOT` and `MEDIA_URL` in settings
- Ensure `media/` directory exists and is writable
- In production, configure S3 or similar

### CSS not loading
- Run `python manage.py collectstatic`
- Check browser console for errors
- Verify `STATIC_URL` in settings

## License

[Your License Here]

## Support

For issues or questions, please [open an issue](your-repo-url/issues).
