from functools import wraps

from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.core.files.storage import default_storage
from django.http import JsonResponse, Http404
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView, CreateView, FormView, DeleteView, DetailView

from .models import FormType, Entry, UserFormAccess, EddieProfile
from .forms import get_form_class, is_valid_form_type
from .forms.user import CustomUserCreationForm


# =============================================================================
# Permission Helpers
# =============================================================================

def get_user_profile_attr(user, attr, default=False):
    """
    Safely get an attribute from a user's profile.

    Args:
        user: The user object
        attr: The profile attribute name (e.g., 'can_pin_posts')
        default: Value to return if profile or attr doesn't exist

    Returns:
        The attribute value or default
    """
    profile = getattr(user, 'profile', None)
    if profile is None:
        return default
    return getattr(profile, attr, default)


def user_can_pin_posts(user):
    """Check if user has permission to pin their own posts."""
    return get_user_profile_attr(user, 'can_pin_posts', False)


def user_can_pin_any_post(user):
    """Check if user has permission to pin any post."""
    return get_user_profile_attr(user, 'can_pin_any_post', False)


def user_can_delete_any_post(user):
    """Check if user has permission to delete any post."""
    return get_user_profile_attr(user, 'can_delete_any_post', False)


# =============================================================================
# API Decorators
# =============================================================================

def api_login_required(view_func):
    """
    Decorator for API views that require authentication.
    Returns JSON error response instead of redirect for unauthenticated users.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        return view_func(request, *args, **kwargs)
    return wrapper


# =============================================================================
# Views
# =============================================================================


class SignupView(CreateView):
    """
    User registration view.
    Creates new user and grants access to default forms.
    """
    form_class = CustomUserCreationForm
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


class AboutEddieView(LoginRequiredMixin, DetailView):
    """
    Displays Eddie's profile information for caregivers.
    Uses singleton pattern - always shows the same profile.
    """
    model = EddieProfile
    template_name = 'timeline/about_eddie.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        """Always return the singleton instance"""
        return EddieProfile.get_instance()

    def get_context_data(self, **kwargs):
        """Add contacts list to context for easier template iteration"""
        context = super().get_context_data(**kwargs)
        profile = self.object

        # Build list of contacts for template
        contacts = []
        for i in range(1, 5):
            name = getattr(profile, f'contact_{i}_name', '')
            if name:
                contacts.append({
                    'name': name,
                    'relationship': getattr(profile, f'contact_{i}_relationship', ''),
                    'phone': getattr(profile, f'contact_{i}_phone', ''),
                    'email': getattr(profile, f'contact_{i}_email', ''),
                })
        context['contacts'] = contacts

        return context


class TimelineListView(LoginRequiredMixin, ListView):
    """
    Main timeline view showing all entries with pagination.
    """
    model = Entry
    template_name = 'timeline/timeline.html'
    context_object_name = 'entries'
    paginate_by = 20
    
    def get_queryset(self):
        """Get all entries"""
        return Entry.objects.all().select_related('form_type', 'user', 'user__profile')
    
    def get_context_data(self, **kwargs):
        """Add available forms to context"""
        context = super().get_context_data(**kwargs)

        # Get forms the user has access to
        available_forms = FormType.objects.filter(
            user_access__user=self.request.user,
            is_active=True
        ).distinct().order_by('name')

        context['forms'] = available_forms

        # Check if user can pin posts
        context['can_pin'] = user_can_pin_posts(self.request.user)

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
        # Check if user can pin posts
        context['can_pin'] = user_can_pin_posts(self.request.user)
        return context

    def form_valid(self, form):
        """Save the entry with JSON data and optional image(s)"""
        # Check if user can pin and wants to pin this post
        can_pin = user_can_pin_posts(self.request.user)
        is_pinned = can_pin and self.request.POST.get('is_pinned') == 'on'

        # Create entry object
        entry = Entry(
            user=self.request.user,
            form_type=self.form_type_obj,
            is_pinned=is_pinned,
        )

        # Get JSON data from form
        entry.data = form.get_json_data()

        # Handle image upload(s)
        if form.has_image_field():
            if form.has_multiple_images():
                # Handle multiple images - save to storage and store URLs in JSON
                all_images = form.get_all_images()
                for field_name, image_file in all_images.items():
                    # Generate unique path for each image
                    now = timezone.now()
                    path = f"uploads/{now.year}/{now.month:02d}/{now.day:02d}/{image_file.name}"
                    # Save to storage
                    saved_path = default_storage.save(path, image_file)
                    # Store URL in JSON data
                    entry.data[f'{field_name}_url'] = default_storage.url(saved_path)
            else:
                # Handle single image using the Entry.image field
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


class EntryDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Delete an entry. Users can delete their own entries, admins can delete any.
    """
    model = Entry
    template_name = 'timeline/entry_confirm_delete.html'
    success_url = reverse_lazy('timeline:timeline')

    def test_func(self):
        """Check if user has permission to delete this entry"""
        entry = self.get_object()
        user = self.request.user
        # Allow if user is the owner, is staff/admin, or has can_delete_any_post permission
        return user == entry.user or user.is_staff or user_can_delete_any_post(user)

    def handle_no_permission(self):
        """Return 403 if user doesn't have permission"""
        raise PermissionDenied("You don't have permission to delete this entry.")


class EntryUnpinView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Unpin an entry. Only users with can_pin_posts permission can unpin.
    Uses DeleteView as base but overrides delete to just update is_pinned.
    """
    model = Entry
    template_name = 'timeline/entry_confirm_unpin.html'
    success_url = reverse_lazy('timeline:timeline')

    def test_func(self):
        """Check if user has permission to unpin posts"""
        return user_can_pin_posts(self.request.user)

    def handle_no_permission(self):
        """Return 403 if user doesn't have permission"""
        raise PermissionDenied("You don't have permission to unpin posts.")

    def form_valid(self, form):
        """Unpin the entry instead of deleting it"""
        self.object = self.get_object()
        self.object.is_pinned = False
        self.object.save()
        return redirect(self.get_success_url())


class EntryPinView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Pin an existing entry. Users can pin their own posts if they have can_pin_posts,
    or pin any post if they have can_pin_any_post.
    Uses DeleteView as base but overrides delete to just update is_pinned.
    """
    model = Entry
    template_name = 'timeline/entry_confirm_pin.html'
    success_url = reverse_lazy('timeline:timeline')

    def test_func(self):
        """Check if user has permission to pin this entry"""
        entry = self.get_object()
        user = self.request.user
        # User can pin any post
        if user_can_pin_any_post(user):
            return True
        # User can pin their own posts if they have can_pin_posts
        if user_can_pin_posts(user) and user == entry.user:
            return True
        return False

    def handle_no_permission(self):
        """Return 403 if user doesn't have permission"""
        raise PermissionDenied("You don't have permission to pin this post.")

    def form_valid(self, form):
        """Pin the entry instead of deleting it"""
        self.object = self.get_object()
        self.object.is_pinned = True
        self.object.save()
        return redirect(self.get_success_url())


# API Views for AJAX/programmatic access

@api_login_required
@require_http_methods(["GET"])
def api_entries(request):
    """
    API endpoint to get entries as JSON.

    Query parameters:
        - form_type: Filter by form type (optional)
        - limit: Number of entries to return (default: 50, max: 100)
    """
    # Get all entries
    entries = Entry.objects.all().select_related('form_type', 'user')

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
            'username': entry.user.username,
        }
        data.append(entry_data)
    
    return JsonResponse(data, safe=False)


@api_login_required
@require_http_methods(["GET"])
def api_forms(request):
    """
    API endpoint to get available forms.

    Returns list of forms the current user has access to.
    """
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
