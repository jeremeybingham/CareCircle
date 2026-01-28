from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator, EmailValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image, ImageOps
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings
import sys


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

    def save(self, *args, **kwargs):
        """Override save to optimize images before storing"""
        if self.image and self._state.adding:  # Only optimize on creation
            self.image = self._optimize_image(self.image)
        super().save(*args, **kwargs)

    @staticmethod
    def _optimize_image(image_field):
        """
        Optimize uploaded image:
        - Convert to JPEG
        - Resize to max dimensions (default 1920x1920)
        - Compress to quality setting (default 85%)
        - Handle EXIF rotation
        - Remove EXIF data

        Returns optimized image file, or original if optimization fails.
        """
        try:
            img = Image.open(image_field)

            # Rotate based on EXIF orientation before removing EXIF
            try:
                img = ImageOps.exif_transpose(img)
            except Exception:
                pass

            # Convert to RGB (handles PNG transparency, etc.)
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'RGBA':
                    background.paste(img, mask=img.split()[3])
                else:
                    background.paste(img)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')

            # Get settings with defaults
            max_width = getattr(settings, 'IMAGE_MAX_WIDTH', 1920)
            max_height = getattr(settings, 'IMAGE_MAX_HEIGHT', 1920)
            jpeg_quality = getattr(settings, 'IMAGE_JPEG_QUALITY', 85)

            # Resize if needed (maintain aspect ratio)
            if img.width > max_width or img.height > max_height:
                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

            # Save optimized version
            output = BytesIO()
            img.save(
                output,
                format='JPEG',
                quality=jpeg_quality,
                optimize=True,
                progressive=True  # Progressive JPEG for better web loading
            )
            output.seek(0)

            # Generate new filename with .jpg extension
            original_name = image_field.name
            name_without_ext = original_name.rsplit('.', 1)[0]
            new_filename = f"{name_without_ext}.jpg"

            return InMemoryUploadedFile(
                output,
                'ImageField',
                new_filename,
                'image/jpeg',
                sys.getsizeof(output),
                None
            )

        except Exception as e:
            # If optimization fails, return original
            print(f"Image optimization failed: {e}")
            return image_field


class EddieProfile(models.Model):
    """
    Singleton model storing Eddie's profile information for the "About Eddie" page.
    This information is shared with all caregivers to help them understand and support Eddie.
    """
    # Profile Photo
    photo = models.ImageField(
        upload_to='eddie_profile/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif', 'webp'])],
        help_text="Current photo of Eddie for caregivers"
    )

    # Bio Section
    bio = models.TextField(
        help_text="General information about Eddie (age, family, personality)"
    )

    # Tips and Tricks
    tips_and_tricks = models.TextField(
        help_text="Calming strategies, what helps when overwhelmed"
    )

    # Favorites
    favorites = models.TextField(
        help_text="Eddie's favorite activities, foods, games, etc."
    )

    # Fun Facts
    fun_facts = models.TextField(
        help_text="Fun and interesting things about Eddie"
    )

    # Goals for This Year
    goals = models.TextField(
        help_text="Current developmental and educational goals"
    )

    # Meals
    meals_info = models.TextField(
        help_text="Eating habits, food preferences, dietary notes"
    )

    # Potty
    potty_info = models.TextField(
        help_text="Bathroom routine, assistance needed"
    )

    # Safety
    safety_info = models.TextField(
        help_text="Safety considerations, supervision needs"
    )

    # Communication
    communication_info = models.TextField(
        help_text="How Eddie communicates, AAC usage, verbal abilities"
    )

    # Physical Description
    height = models.CharField(
        max_length=20,
        blank=True,
        help_text="Height (e.g., '3 ft 8 in')"
    )
    weight = models.CharField(
        max_length=20,
        blank=True,
        help_text="Weight (e.g., '45 lbs')"
    )
    hair_color = models.CharField(
        max_length=50,
        blank=True,
        help_text="Hair color"
    )
    eye_color = models.CharField(
        max_length=50,
        blank=True,
        help_text="Eye color"
    )
    distinguishing_marks = models.TextField(
        blank=True,
        help_text="Any distinguishing marks or features"
    )

    # Emergency Contacts
    contact_1_name = models.CharField(
        max_length=100,
        help_text="Contact 1 name (e.g., 'Mom')"
    )
    contact_1_relationship = models.CharField(
        max_length=50,
        help_text="Relationship to Eddie"
    )
    contact_1_phone = models.CharField(
        max_length=20,
        help_text="Phone number"
    )
    contact_1_email = models.EmailField(
        blank=True,
        help_text="Email address (optional)"
    )

    contact_2_name = models.CharField(
        max_length=100,
        help_text="Contact 2 name (e.g., 'Dad')"
    )
    contact_2_relationship = models.CharField(
        max_length=50,
        help_text="Relationship to Eddie"
    )
    contact_2_phone = models.CharField(
        max_length=20,
        help_text="Phone number"
    )
    contact_2_email = models.EmailField(
        blank=True,
        help_text="Email address (optional)"
    )

    contact_3_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Contact 3 name (optional)"
    )
    contact_3_relationship = models.CharField(
        max_length=50,
        blank=True,
        help_text="Relationship to Eddie"
    )
    contact_3_phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Phone number"
    )
    contact_3_email = models.EmailField(
        blank=True,
        help_text="Email address (optional)"
    )

    contact_4_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Contact 4 name (optional)"
    )
    contact_4_relationship = models.CharField(
        max_length=50,
        blank=True,
        help_text="Relationship to Eddie"
    )
    contact_4_phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Phone number"
    )
    contact_4_email = models.EmailField(
        blank=True,
        help_text="Email address (optional)"
    )

    # Metadata
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User who last updated this profile"
    )

    class Meta:
        verbose_name = "Eddie's Profile"
        verbose_name_plural = "Eddie's Profile"

    def __str__(self):
        return "Eddie's Profile"

    def save(self, *args, **kwargs):
        """Ensure only one instance exists (singleton pattern)"""
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_instance(cls):
        """Get or create the singleton instance"""
        obj, created = cls.objects.get_or_create(
            pk=1,
            defaults={
                'bio': '',
                'tips_and_tricks': '',
                'favorites': '',
                'fun_facts': '',
                'goals': '',
                'meals_info': '',
                'potty_info': '',
                'safety_info': '',
                'communication_info': '',
                'contact_1_name': 'Mom',
                'contact_1_relationship': 'Mother',
                'contact_1_phone': '',
                'contact_2_name': 'Dad',
                'contact_2_relationship': 'Father',
                'contact_2_phone': '',
            }
        )
        return obj
