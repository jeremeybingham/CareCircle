from django.urls import path
from . import views

app_name = 'timeline'

urlpatterns = [
    # Main timeline view
    path('', views.TimelineListView.as_view(), name='timeline'),

    # Entry creation
    path('entry/<str:form_type>/', views.EntryCreateView.as_view(), name='entry_create'),

    # API endpoints
    path('api/entries/', views.api_entries, name='api_entries'),
    path('api/forms/', views.api_forms, name='api_forms'),
]
