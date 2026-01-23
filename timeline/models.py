from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator


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

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Entry"
        verbose_name_plural = "Entries"
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['user', '-timestamp']),
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
