# CLAUDE.md - AI Assistant Context

This file provides context for AI assistants working on the Timeline project.

## Project Overview

**Timeline** is a Django 5.0+ web application for tracking a child's personal events, activities, and information. It features a shared timeline where all authenticated users can see all entries with author attribution.

**Tech Stack**: Django 5.0+, Python 3.x, SQLite/PostgreSQL, Pillow, custom CSS (no JS frameworks)

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

# Run tests
python manage.py test timeline

# Collect static files
python manage.py collectstatic
```

## Key Architecture Patterns

### Registry Pattern for Forms
Forms are dynamically discovered via a central registry. To add a new form type:
1. Create form class in `timeline/forms/newform.py`
2. Register in `timeline/forms/registry.py` (FORM_REGISTRY dict)
3. Export in `timeline/forms/__init__.py`
4. Run `python manage.py init_forms`
5. Create display template: `timeline/templates/timeline/partials/entry_newform.html`

### Template Inheritance
- `templates/base.html` - Root template with navbar, messages, blocks
- `timeline/templates/timeline/*.html` - Page templates
- `timeline/templates/timeline/partials/*.html` - Reusable components
- `timeline/templates/timeline/partials/entry_meta.html` - Shared timestamp/author display

### Custom Template Tags
Located in `timeline/templatetags/entry_display.py`:
- `render_entry` - Renders entry with type-specific template
- `split_commas` - Splits comma-separated strings into lists
- `get_item` - Dictionary access in templates

## Critical Files

| File | Purpose |
|------|---------|
| `timeline/models.py` | 4 models: FormType, UserFormAccess, Entry, UserProfile |
| `timeline/views.py` | TimelineListView, EntryCreateView, SignupView, API views |
| `timeline/forms/registry.py` | Central form registry (FORM_REGISTRY dict) |
| `timeline/forms/base.py` | BaseEntryForm - all forms inherit from this |
| `timeline/admin.py` | Admin customizations with actions |
| `config/settings.py` | Django settings, env var handling |
| `timeline/static/timeline/css/style.css` | All styling (700+ lines) |

## Models

### Entry
- Stores timeline entries with JSON data field for flexible form data
- Optional image field for photos
- Foreign keys to User and FormType
- Indexed on timestamp and (user, timestamp)

### FormType
- Defines available form types (name, type, icon, description)
- `is_active` - Whether form can be used
- `is_default` - Auto-granted to new users via signal

### UserFormAccess
- Many-to-many between User and FormType
- Controls which forms each user can access
- Tracks who granted access and when

### UserProfile
- One-to-one with Django User
- Fields: display_name, email_address, position_role, first_name, last_name
- Auto-created on user signup via signal handler

## URL Routes

| URL | View | Purpose |
|-----|------|---------|
| `/` | TimelineListView | Main timeline (requires login) |
| `/entry/<form_type>/` | EntryCreateView | Create new entry |
| `/api/entries/` | api_entries | JSON API for entries |
| `/api/forms/` | api_forms | JSON API for available forms |
| `/signup/` | SignupView | User registration |
| `/login/` | LoginView | Authentication |
| `/admin/` | Admin site | Django admin |

## Form Types

| Type Key | Name | Icon | Description |
|----------|------|------|-------------|
| `text` | Text Post | 📝 | Simple title and content |
| `photo` | Photo | 📸 | Image upload with caption |
| `overnight` | Overnight | 🌙 | Dinner, sleep, breakfast tracking |
| `schoolday` | School Day | 🎒 | Comprehensive school activity log |

## Adding Features

### Adding a New Form Type
See `ADDING_FORMS.md` for detailed steps. Key files:
- `timeline/forms/newform.py` - Form class inheriting BaseEntryForm
- `timeline/forms/registry.py` - Add to FORM_REGISTRY
- `timeline/templates/timeline/partials/entry_newform.html` - Display template

### Modifying Entry Display
- Edit type-specific template in `partials/entry_*.html`
- Shared metadata is in `partials/entry_meta.html`
- Styles in `timeline/static/timeline/css/style.css`

### Adding Model Fields
1. Modify model in `timeline/models.py`
2. Run `python manage.py makemigrations`
3. Run `python manage.py migrate`
4. Update admin in `timeline/admin.py` if needed

## Common Gotchas

1. **Forms not showing**: Run `python manage.py init_forms` after adding to registry
2. **User can't access form**: Grant via UserFormAccess in admin
3. **New form not rendering**: Check template exists at `partials/entry_<type>.html`
4. **Static files not updating**: Run `python manage.py collectstatic`
5. **UserProfile missing**: Auto-created on signup; for existing users, create manually

## Testing

```bash
# Run all tests
python manage.py test timeline

# Run with verbose output
python manage.py test timeline -v 2

# Run specific test
python manage.py test timeline.tests.TestClassName
```

## Database

Default: SQLite at `db.sqlite3`
Optional: PostgreSQL (set DATABASE_ENGINE in .env)

Schema overview:
- `timeline_formtype` - Form type definitions
- `timeline_userformaccess` - User-form permissions
- `timeline_entry` - Timeline entries (JSON data field)
- `timeline_userprofile` - Extended user info

## Environment Variables

See `.env.example` for all options. Key vars:
- `SECRET_KEY` - Django secret (required in production)
- `DEBUG` - Set False in production
- `DATABASE_ENGINE` - sqlite3 or postgresql
- `USE_S3` - Enable S3 storage for media

## Current Status

### Completed
- Multi-user shared timeline with author display names
- User registration with profile information
- 4 form types (text, photo, overnight, schoolday)
- Shared entry_meta.html partial for consistent display

### Pending (see TODO.md)
1. "My Weekend" form type (3 photos + 3 texts + notes)
2. Remove post filtering buttons
