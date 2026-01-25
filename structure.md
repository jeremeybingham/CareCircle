new_timeline/
├── manage.py ✓
├── requirements.txt ✓
├── .env.example ✓
├── .gitignore ✓
├── README.md ✓
├── ADDING_FORMS.md ✓
│
├── config/
│   ├── __init__.py ✓
│   ├── settings.py ✓
│   ├── urls.py ✓
│   ├── wsgi.py ✓
│   └── asgi.py ✓
│
├── timeline/
│   ├── __init__.py ✓
│   ├── apps.py ✓
│   ├── models.py ✓
│   ├── admin.py ✓
│   ├── views.py ✓
│   ├── urls.py ✓
│   │
│   ├── forms/
│   │   ├── __init__.py ✓
│   │   ├── base.py ✓
│   │   ├── registry.py ✓
│   │   ├── text.py ✓
│   │   ├── photo.py ✓
│   │   ├── overnight.py ✓
│   │   └── schoolday.py ✓
│   │
│   ├── templates/timeline/
│   │   ├── timeline.html ✓
│   │   ├── entry_form.html ✓
│   │   ├── auth/
│   │   │   ├── login.html ✓
│   │   │   └── signup.html ✓
│   │   └── partials/
│   │       ├── entry_text.html ✓
│   │       ├── entry_photo.html ✓
│   │       ├── entry_overnight.html ✓
│   │       ├── entry_schoolday.html ✓
│   │       └── entry_default.html ✓
│   │
│   ├── templatetags/
│   │   ├── __init__.py ✓
│   │   └── entry_display.py ✓
│   │
│   ├── static/timeline/css/
│   │   └── style.css ✓
│   │
│   ├── management/
│   │   ├── __init__.py ✓
│   │   └── commands/
│   │       ├── __init__.py ✓
│   │       └── init_forms.py ✓
│   │
│   └── migrations/
│       ├── __init__.py ✓
│       └── 0001_initial.py ✓
│
├── templates/
│   └── base.html ✓
│
└── static/
    └── .gitkeep ✓