from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import ListView, CreateView, FormView
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, Http404
from django.urls import reverse_lazy, reverse
from django.core.paginator import Paginator
from django.db.models import Q

from .models import FormType, Entry, UserFormAccess
from .forms import get_form_class, is_valid_form_type


class SignupView(CreateView):
    """
    User registration view.
    Creates new user and grants access to default forms.
    """
    form_class = UserCreationForm
    template_name = 'timeline/auth/signup.html'
    success_url = reverse_lazy('timeline:timeline')
    
    def form_valid(self, form):
        """Save user and grant default form access"""
        response = super().form_valid(form)
        user = self.object
        
        # Grant access to all default forms
        default_forms = FormType.objects.filter(is_default=True, is_active=True)
        for form_type in default_forms:
            UserFormAccess.objects.create(user=user, form_type=form_type)
        
        # Log the user in
        login(self.request, user)
        
        return response


class TimelineListView(LoginRequiredMixin, ListView):
    """
    Main timeline view showing user's entries.
    Supports filtering by form type and pagination.
    """
    model = Entry
    template_name = 'timeline/timeline.html'
    context_object_name = 'entries'
    paginate_by = 20
    
    def get_queryset(self):
        """Get entries for current user, optionally filtered by form type"""
        queryset = Entry.objects.filter(user=self.request.user).select_related('form_type')
        
        # Optional: Filter by form type
        form_filter = self.request.GET.get('form')
        if form_filter:
            queryset = queryset.filter(form_type__type=form_filter)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """Add available forms and current filter to context"""
        context = super().get_context_data(**kwargs)
        
        # Get forms the user has access to
        available_forms = FormType.objects.filter(
            user_access__user=self.request.user,
            is_active=True
        ).distinct().order_by('name')
        
        context['forms'] = available_forms
        context['current_filter'] = self.request.GET.get('form', '')
        
        return context


class EntryCreateView(LoginRequiredMixin, FormView):
    """
    Generic entry creation view.
    Dynamically loads the appropriate form based on form_type parameter.
    """
    template_name = 'timeline/entry_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        """Validate form_type and user access before processing"""
        form_type = kwargs.get('form_type')
        
        # Check if form type is valid
        if not is_valid_form_type(form_type):
            raise Http404("Form type not found")
        
        # Get the FormType object
        try:
            self.form_type_obj = FormType.objects.get(
                type=form_type,
                is_active=True
            )
        except FormType.DoesNotExist:
            raise Http404("Form type not available")
        
        # Check if user has access to this form
        has_access = UserFormAccess.objects.filter(
            user=request.user,
            form_type=self.form_type_obj
        ).exists()
        
        if not has_access:
            raise Http404("You don't have access to this form")
        
        # Store form type for later use
        self.form_type = form_type
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_class(self):
        """Return the appropriate form class for this form type"""
        return get_form_class(self.form_type)
    
    def get_context_data(self, **kwargs):
        """Add form type metadata to context"""
        context = super().get_context_data(**kwargs)
        context['form_type_obj'] = self.form_type_obj
        context['form_type'] = self.form_type
        return context
    
    def form_valid(self, form):
        """Save the entry with JSON data and optional image"""
        # Create entry object
        entry = Entry(
            user=self.request.user,
            form_type=self.form_type_obj,
        )
        
        # Get JSON data from form
        entry.data = form.get_json_data()
        
        # Handle image upload if present
        if form.has_image_field():
            image = form.get_image_data()
            if image:
                entry.image = image
        
        entry.save()
        
        # Handle AJAX requests
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'entry_id': entry.id,
                'redirect_url': reverse('timeline:timeline')
            })
        
        return redirect('timeline:timeline')
    
    def form_invalid(self, form):
        """Handle invalid form submission"""
        # Handle AJAX requests
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
        
        return super().form_invalid(form)
    
    def get_success_url(self):
        """Redirect to timeline after successful submission"""
        return reverse('timeline:timeline')


# API Views for AJAX/programmatic access

@require_http_methods(["GET"])
def api_entries(request):
    """
    API endpoint to get entries as JSON.
    
    Query parameters:
        - form_type: Filter by form type (optional)
        - limit: Number of entries to return (default: 50, max: 100)
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    # Get entries for current user
    entries = Entry.objects.filter(user=request.user).select_related('form_type')
    
    # Optional filtering by form type
    form_type = request.GET.get('form_type')
    if form_type:
        entries = entries.filter(form_type__type=form_type)
    
    # Limit results
    limit = min(int(request.GET.get('limit', 50)), 100)
    entries = entries[:limit]
    
    # Serialize entries
    data = []
    for entry in entries:
        entry_data = {
            'id': entry.id,
            'type': entry.form_type.type,
            'form_name': entry.form_type.name,
            'form_icon': entry.form_type.icon,
            'timestamp': entry.timestamp.isoformat(),
            'data': entry.get_display_data(),
        }
        data.append(entry_data)
    
    return JsonResponse(data, safe=False)


@require_http_methods(["GET"])
def api_forms(request):
    """
    API endpoint to get available forms.
    
    Returns list of forms the current user has access to.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    # Get forms user has access to
    forms = FormType.objects.filter(
        user_access__user=request.user,
        is_active=True
    ).distinct()
    
    # Serialize forms
    data = []
    for form in forms:
        data.append({
            'id': form.id,
            'name': form.name,
            'type': form.type,
            'icon': form.icon,
            'description': form.description,
        })
    
    return JsonResponse(data, safe=False)
