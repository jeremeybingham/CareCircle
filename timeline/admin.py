from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import FormType, UserFormAccess, Entry, UserProfile


# Customize User Admin to show form access and profile
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'
    fields = ['display_name', 'email_address', 'first_name', 'last_name', 'position_role', 'can_pin_posts', 'can_delete_any_post']


class UserFormAccessInline(admin.TabularInline):
    model = UserFormAccess
    extra = 1
    fk_name = 'user'
    autocomplete_fields = ['form_type']
    readonly_fields = ['granted_at']


class CustomUserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline, UserFormAccessInline]
    list_display = ['username', 'email', 'first_name', 'last_name', 'display_name_info', 'is_staff', 'entry_count', 'date_joined']

    def display_name_info(self, obj):
        """Show display name from profile"""
        if hasattr(obj, 'profile'):
            return obj.profile.display_name
        return '-'
    display_name_info.short_description = 'Display Name'

    def entry_count(self, obj):
        count = obj.timeline_entries.count()
        url = reverse('admin:timeline_entry_changelist') + f'?user__id__exact={obj.id}'
        return format_html('<a href="{}">{} entries</a>', url, count)
    entry_count.short_description = 'Entries'


# Unregister default User admin and register custom
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(FormType)
class FormTypeAdmin(admin.ModelAdmin):
    list_display = ['icon_display', 'name', 'type', 'is_default', 'is_active', 'user_count', 'entry_count', 'created_at']
    list_filter = ['is_default', 'is_active', 'created_at']
    search_fields = ['name', 'type', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'type', 'icon', 'description')
        }),
        ('Settings', {
            'fields': ('is_default', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def icon_display(self, obj):
        return obj.icon
    icon_display.short_description = ''
    
    def user_count(self, obj):
        count = obj.user_access.count()
        url = reverse('admin:timeline_userformaccess_changelist') + f'?form_type__id__exact={obj.id}'
        return format_html('<a href="{}">{} users</a>', url, count)
    user_count.short_description = 'Users with Access'
    
    def entry_count(self, obj):
        count = obj.entries.count()
        url = reverse('admin:timeline_entry_changelist') + f'?form_type__id__exact={obj.id}'
        return format_html('<a href="{}">{} entries</a>', url, count)
    entry_count.short_description = 'Entries'
    
    actions = ['make_default', 'remove_default', 'activate', 'deactivate']
    
    def make_default(self, request, queryset):
        queryset.update(is_default=True)
        self.message_user(request, f"{queryset.count()} forms marked as default")
    make_default.short_description = "Mark as default (auto-grant to new users)"
    
    def remove_default(self, request, queryset):
        queryset.update(is_default=False)
        self.message_user(request, f"{queryset.count()} forms unmarked as default")
    remove_default.short_description = "Remove default status"
    
    def activate(self, request, queryset):
        queryset.update(is_active=True)
    activate.short_description = "Activate selected forms"
    
    def deactivate(self, request, queryset):
        queryset.update(is_active=False)
    deactivate.short_description = "Deactivate selected forms"


@admin.register(UserFormAccess)
class UserFormAccessAdmin(admin.ModelAdmin):
    list_display = ['user_display', 'form_display', 'granted_at', 'granted_by']
    list_filter = ['form_type', 'granted_at']
    search_fields = ['user__username', 'user__email', 'form_type__name']
    autocomplete_fields = ['user', 'form_type']
    readonly_fields = ['granted_at']
    
    def user_display(self, obj):
        return obj.user.username
    user_display.short_description = 'User'
    user_display.admin_order_field = 'user__username'
    
    def form_display(self, obj):
        return f"{obj.form_type.icon} {obj.form_type.name}"
    form_display.short_description = 'Form'
    form_display.admin_order_field = 'form_type__name'
    
    actions = ['grant_default_forms']
    
    def grant_default_forms(self, request, queryset):
        """Grant all default forms to selected users"""
        users = queryset.values_list('user', flat=True).distinct()
        default_forms = FormType.objects.filter(is_default=True)
        
        created_count = 0
        for user_id in users:
            for form_type in default_forms:
                _, created = UserFormAccess.objects.get_or_create(
                    user_id=user_id,
                    form_type=form_type,
                    defaults={'granted_by': request.user}
                )
                if created:
                    created_count += 1
        
        self.message_user(request, f"Granted {created_count} form accesses")
    grant_default_forms.short_description = "Grant all default forms to selected users"


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_display', 'form_display', 'timestamp', 'preview', 'has_image', 'is_pinned_display']
    list_filter = ['is_pinned', 'form_type__type', 'form_type', 'timestamp']
    search_fields = ['user__username', 'user__email', 'data']
    readonly_fields = ['timestamp', 'data_display', 'image_preview']
    autocomplete_fields = ['user', 'form_type']
    date_hierarchy = 'timestamp'

    fieldsets = (
        ('Entry Information', {
            'fields': ('user', 'form_type', 'timestamp', 'is_pinned')
        }),
        ('Content', {
            'fields': ('data_display', 'image', 'image_preview')
        }),
    )
    
    def user_display(self, obj):
        return obj.user.username
    user_display.short_description = 'User'
    user_display.admin_order_field = 'user__username'
    
    def form_display(self, obj):
        return f"{obj.form_type.icon} {obj.form_type.name}"
    form_display.short_description = 'Form'
    form_display.admin_order_field = 'form_type__name'
    
    def preview(self, obj):
        """Show a preview of the entry data"""
        data = obj.data
        if isinstance(data, dict):
            # Try common field names for preview
            for key in ['title', 'caption', 'content', 'text', 'notes_about_day']:
                if key in data and data[key]:
                    text = str(data[key])
                    return text[:60] + ('...' if len(text) > 60 else '')
        return str(data)[:60]
    preview.short_description = 'Preview'
    
    def has_image(self, obj):
        return '✓' if obj.image else ''
    has_image.short_description = 'Image'

    def is_pinned_display(self, obj):
        return '📌' if obj.is_pinned else ''
    is_pinned_display.short_description = 'Pinned'

    def data_display(self, obj):
        """Pretty-print JSON data"""
        import json
        return format_html('<pre>{}</pre>', json.dumps(obj.data, indent=2))
    data_display.short_description = 'Data (JSON)'
    
    def image_preview(self, obj):
        """Show image thumbnail"""
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="max-width: 300px; max-height: 300px;" />')
        return "No image"
    image_preview.short_description = 'Image Preview'

    actions = ['pin_entries', 'unpin_entries']

    def pin_entries(self, request, queryset):
        count = queryset.update(is_pinned=True)
        self.message_user(request, f"{count} entries pinned to top of timeline")
    pin_entries.short_description = "📌 Pin selected entries to top"

    def unpin_entries(self, request, queryset):
        count = queryset.update(is_pinned=False)
        self.message_user(request, f"{count} entries unpinned")
    unpin_entries.short_description = "Unpin selected entries"


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'display_name', 'email_address', 'position_role', 'can_pin_posts', 'can_delete_any_post', 'created_at']
    list_filter = ['position_role', 'can_pin_posts', 'can_delete_any_post', 'created_at']
    search_fields = ['user__username', 'display_name', 'email_address', 'first_name', 'last_name']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['user']

    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Profile Information', {
            'fields': ('display_name', 'first_name', 'last_name', 'email_address', 'position_role')
        }),
        ('Permissions', {
            'fields': ('can_pin_posts', 'can_delete_any_post')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['grant_pin_permission', 'revoke_pin_permission', 'grant_delete_any_permission', 'revoke_delete_any_permission']

    def grant_pin_permission(self, request, queryset):
        count = queryset.update(can_pin_posts=True)
        self.message_user(request, f"Granted pin permission to {count} users")
    grant_pin_permission.short_description = "📌 Grant pin posts permission"

    def revoke_pin_permission(self, request, queryset):
        count = queryset.update(can_pin_posts=False)
        self.message_user(request, f"Revoked pin permission from {count} users")
    revoke_pin_permission.short_description = "Revoke pin posts permission"

    def grant_delete_any_permission(self, request, queryset):
        count = queryset.update(can_delete_any_post=True)
        self.message_user(request, f"Granted delete any post permission to {count} users")
    grant_delete_any_permission.short_description = "🗑️ Grant delete any post permission"

    def revoke_delete_any_permission(self, request, queryset):
        count = queryset.update(can_delete_any_post=False)
        self.message_user(request, f"Revoked delete any post permission from {count} users")
    revoke_delete_any_permission.short_description = "Revoke delete any post permission"


# Customize admin site header
admin.site.site_header = "Timeline Administration"
admin.site.site_title = "Timeline Admin"
admin.site.index_title = "Welcome to Timeline Admin"
