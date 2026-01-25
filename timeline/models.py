from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator, EmailValidator
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """
    Extended user profile information.
    One-to-one relationship with Django's built-in User model.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    display_name = models.CharField(
        max_length=100,
        help_text="Name shown on posts (e.g., 'Ms. Johnson')"
    )
    email_address = models.EmailField(
        unique=True,
        validators=[EmailValidator()],
        help_text="Contact email address"
    )
    position_role = models.CharField(
        max_length=100,
        blank=True,
        help_text="Job title/role (e.g., 'Teacher', 'Parent', 'Administrator')"
    )
    first_name = models.CharField(
        max_length=50,
        help_text="User's first name"
    )
    last_name = models.CharField(
        max_length=50,
        help_text="User's last name"
    )
    can_pin_posts = models.BooleanField(
        default=False,
        help_text="Allow this user to pin posts to the top of the timeline"
    )
    can_delete_any_post = models.BooleanField(
        default=False,
        help_text="Allow this user to delete any post, not just their own"
    )
    can_pin_any_post = models.BooleanField(
        default=False,
        help_text="Allow this user to pin any post, not just their own"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self):
        return f"{self.display_name} ({self.user.username})"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal handler to create UserProfile when a User is created.
    If profile data isn't provided, create a minimal profile.
    """
    if created:
        # Only create if profile doesn't exist (handles cases where profile is created explicitly)
        if not hasattr(instance, 'profile'):
            UserProfile.objects.get_or_create(
                user=instance,
                defaults={
                    'display_name': instance.username,
                    'email_address': instance.email or f'{instance.username}@example.com',
                    'first_name': instance.first_name or '',
                    'last_name': instance.last_name or ''
                }
            )


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Signal handler to save UserProfile when User is saved.
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()


class FormType(models.Model):
    """
    Defines available form types.
    The actual form logic lives in timeline/forms/, not here.
    This model just stores metadata and controls visibility.
    """
    name = models.CharField(
        max_length=100,
        help_text="Display name (e.g., 'School Day', 'Photo')"
    )
    type = models.CharField(
        max_length=50,
        unique=True,
        help_text="Internal identifier (e.g., 'schoolday', 'photo') - must match form registry"
    )
    icon = models.CharField(
        max_length=10,
        default="📋",
        help_text="Emoji icon"
    )
    description = models.TextField(
        blank=True,
        help_text="Description shown to users"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="If false, form is hidden from all users"
    )
    is_default = models.BooleanField(
        default=False,
        help_text="If true, new users automatically get access"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Form Type"
        verbose_name_plural = "Form Types"

    def __str__(self):
        return f"{self.icon} {self.name}"

    def save(self, *args, **kwargs):
        """Auto-grant access to all users if marked as default"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new and self.is_default:
            for user in User.objects.all():
                UserFormAccess.objects.get_or_create(user=user, form_type=self)


class UserFormAccess(models.Model):
    """
    Controls which users have access to which form types.
    Many-to-many relationship between Users and FormTypes.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='form_access'
    )
    form_type = models.ForeignKey(
        FormType,
        on_delete=models.CASCADE,
        related_name='user_access'
    )
    granted_at = models.DateTimeField(auto_now_add=True)
    granted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='granted_form_access',
        help_text="Admin who granted this access"
    )

    class Meta:
        unique_together = ('user', 'form_type')
        ordering = ['-granted_at']
        verbose_name = "User Form Access"
        verbose_name_plural = "User Form Access"

    def __str__(self):
        return f"{self.user.username} → {self.form_type.name}"


class Entry(models.Model):
    """
    Timeline entry submitted by a user.
    Data is stored as JSON for flexibility, but created via Django Forms.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='timeline_entries'
    )
    form_type = models.ForeignKey(
        FormType,
        on_delete=models.PROTECT,
        related_name='entries'
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )
    data = models.JSONField(
        help_text="Form data stored as JSON"
    )
    image = models.ImageField(
        upload_to='uploads/%Y/%m/%d/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif', 'webp'])]
    )
    is_pinned = models.BooleanField(
        default=False,
        help_text="Pin this entry to the top of the timeline"
    )

    class Meta:
        ordering = ['-is_pinned', '-timestamp']
        verbose_name = "Entry"
        verbose_name_plural = "Entries"
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['-is_pinned', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.form_type.name} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

    @property
    def type(self):
        """Convenience property for templates"""
        return self.form_type.type

    def get_display_data(self):
        """Returns data dict with image URL if present"""
        display_data = self.data.copy()
        if self.image:
            display_data['image_url'] = self.image.url
        return display_data
