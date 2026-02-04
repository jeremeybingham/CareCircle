from django.urls import path
from . import views

app_name = 'timeline'

urlpatterns = [
    # Main timeline view
    path('', views.TimelineListView.as_view(), name='timeline'),

    # About page (child profile)
    path('about/', views.AboutChildView.as_view(), name='about'),

    # User Profile pages
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile/edit/', views.UserProfileEditView.as_view(), name='profile_edit'),
    path('profile/password/', views.UserPasswordChangeView.as_view(), name='password_change'),

    # Entry creation
    path('entry/<str:form_type>/', views.EntryCreateView.as_view(), name='entry_create'),

    # Entry deletion
    path('entry/<int:pk>/delete/', views.EntryDeleteView.as_view(), name='entry_delete'),

    # Entry unpin
    path('entry/<int:pk>/unpin/', views.EntryUnpinView.as_view(), name='entry_unpin'),

    # Entry pin
    path('entry/<int:pk>/pin/', views.EntryPinView.as_view(), name='entry_pin'),

    # API endpoints
    path('api/entries/', views.api_entries, name='api_entries'),
    path('api/forms/', views.api_forms, name='api_forms'),

    # Webhook endpoints (token-authenticated, no login required)
    path('webhooks/<str:token>/not_named_place/', views.webhook_not_named_place, name='webhook_not_named_place'),
    path('webhooks/<str:token>/arrived_at/<str:location>/', views.webhook_arrived_at, name='webhook_arrived_at'),
    path('webhooks/<str:token>/left_at/<str:location>/<str:time>/', views.webhook_left_at, name='webhook_left_at'),
]
