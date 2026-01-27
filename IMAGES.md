# Image Optimization Strategy for Timeline App

We need to handle image sizes better to optimize loading speed and performance. 

## 1. **Processing Location Options**

You have three main approaches:

### Option A: Process in Model `save()` method (Recommended)
**Best for**: Centralized logic, works regardless of how image is uploaded

```python
# models.py
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys

class Entry(models.Model):
    # ... existing fields ...
    
    def save(self, *args, **kwargs):
        """Override save to optimize images before storing"""
        if self.image:
            self.image = self.optimize_image(self.image)
        super().save(*args, **kwargs)
    
    def optimize_image(self, image_field):
        """
        Resize and compress uploaded image.
        Returns optimized image file.
        """
        # Open image with Pillow
        img = Image.open(image_field)
        
        # Convert RGBA to RGB (for PNG with transparency)
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # Define maximum dimensions
        MAX_WIDTH = 1920
        MAX_HEIGHT = 1920
        
        # Resize if needed (maintain aspect ratio)
        if img.width > MAX_WIDTH or img.height > MAX_HEIGHT:
            img.thumbnail((MAX_WIDTH, MAX_HEIGHT), Image.Resampling.LANCZOS)
        
        # Save to BytesIO with compression
        output = BytesIO()
        img.save(output, format='JPEG', quality=85, optimize=True)
        output.seek(0)
        
        # Create new file
        optimized_image = InMemoryUploadedFile(
            output,
            'ImageField',
            f"{image_field.name.split('.')[0]}.jpg",
            'image/jpeg',
            sys.getsizeof(output),
            None
        )
        
        return optimized_image
```

### Option B: Process in Form's `clean()` method
**Best for**: Validation-time processing, immediate feedback to user

```python
# forms/photo.py
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys

class PhotoForm(BaseEntryForm):
    # ... existing fields ...
    
    def clean_image(self):
        """Validate and optimize image"""
        image = self.cleaned_data.get('image')
        
        if image:
            # Size validation (keep your existing check)
            if image.size > 10 * 1024 * 1024:
                raise forms.ValidationError("Image file size cannot exceed 10MB.")
            
            # Optimize the image
            image = self._optimize_image(image)
        
        return image
    
    def _optimize_image(self, image_field):
        """Resize and compress image"""
        img = Image.open(image_field)
        
        # Convert to RGB if needed
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'RGBA':
                background.paste(img, mask=img.split()[3])
            else:
                background.paste(img)
            img = background
        
        # Resize maintaining aspect ratio
        MAX_SIZE = (1920, 1920)
        img.thumbnail(MAX_SIZE, Image.Resampling.LANCZOS)
        
        # Compress
        output = BytesIO()
        img.save(output, format='JPEG', quality=85, optimize=True)
        output.seek(0)
        
        return InMemoryUploadedFile(
            output, 'ImageField',
            f"{image_field.name.split('.')[0]}.jpg",
            'image/jpeg',
            sys.getsizeof(output),
            None
        )
```

### Option C: Use Django Signals (Most Flexible)
**Best for**: Separation of concerns, reusable across different upload points

```python
# signals.py (create new file in timeline/)
from django.db.models.signals import pre_save
from django.dispatch import receiver
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys
from .models import Entry

@receiver(pre_save, sender=Entry)
def optimize_entry_image(sender, instance, **kwargs):
    """Optimize image before saving Entry"""
    if instance.image:
        # Check if this is a new image (not already processed)
        try:
            old_instance = Entry.objects.get(pk=instance.pk)
            if old_instance.image == instance.image:
                return  # Image hasn't changed, skip processing
        except Entry.DoesNotExist:
            pass  # New entry, process the image
        
        instance.image = optimize_image(instance.image)

def optimize_image(image_field):
    """Resize and compress image"""
    img = Image.open(image_field)
    
    # Convert RGBA to RGB
    if img.mode in ('RGBA', 'LA', 'P'):
        background = Image.new('RGB', img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
        img = background
    
    # Resize
    MAX_WIDTH = 1920
    MAX_HEIGHT = 1920
    if img.width > MAX_WIDTH or img.height > MAX_HEIGHT:
        img.thumbnail((MAX_WIDTH, MAX_HEIGHT), Image.Resampling.LANCZOS)
    
    # Compress
    output = BytesIO()
    img.save(output, format='JPEG', quality=85, optimize=True)
    output.seek(0)
    
    return InMemoryUploadedFile(
        output,
        'ImageField',
        f"{image_field.name.split('.')[0]}.jpg",
        'image/jpeg',
        sys.getsizeof(output),
        None
    )
```

Then register in `apps.py`:

```python
# timeline/apps.py
from django.apps import AppConfig

class TimelineConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'timeline'
    verbose_name = 'Timeline'
    
    def ready(self):
        import timeline.signals  # Register signals
```

---

## 2. **Configuration Management**

Create a settings configuration for easy adjustment:

```python
# settings.py

# Image optimization settings
IMAGE_OPTIMIZATION = {
    'MAX_WIDTH': 1920,
    'MAX_HEIGHT': 1920,
    'JPEG_QUALITY': 85,  # 1-100, 85 is good balance
    'CONVERT_TO_JPEG': True,  # Convert all images to JPEG
    'OPTIMIZE': True,  # Enable PIL optimize flag
}
```

Then use in your optimization function:

```python
from django.conf import settings

def optimize_image(image_field):
    config = settings.IMAGE_OPTIMIZATION
    
    img = Image.open(image_field)
    
    # ... conversion logic ...
    
    # Resize using config
    max_size = (config['MAX_WIDTH'], config['MAX_HEIGHT'])
    if img.width > max_size[0] or img.height > max_size[1]:
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
    
    # Save with config
    output = BytesIO()
    img.save(
        output,
        format='JPEG',
        quality=config['JPEG_QUALITY'],
        optimize=config['OPTIMIZE']
    )
    output.seek(0)
    
    return InMemoryUploadedFile(...)
```

---

## 3. **Advanced: Multiple Image Sizes**

If you want to generate thumbnails or multiple sizes:

```python
# models.py
class Entry(models.Model):
    # ... existing fields ...
    image = models.ImageField(upload_to='uploads/%Y/%m/%d/', blank=True, null=True)
    image_thumbnail = models.ImageField(upload_to='thumbnails/%Y/%m/%d/', blank=True, null=True)
    image_medium = models.ImageField(upload_to='medium/%Y/%m/%d/', blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if self.image:
            # Generate full size (optimized)
            self.image = self.create_optimized_image(self.image, (1920, 1920), 85)
            
            # Generate medium size
            img = Image.open(self.image)
            self.image_medium = self.create_optimized_image(
                self.image, (800, 800), 80
            )
            
            # Generate thumbnail
            img = Image.open(self.image)
            self.image_thumbnail = self.create_optimized_image(
                self.image, (300, 300), 75
            )
        
        super().save(*args, **kwargs)
    
    def create_optimized_image(self, image_field, max_size, quality):
        """Create optimized image at specified size"""
        img = Image.open(image_field)
        
        # Convert to RGB
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # Resize
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Save
        output = BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)
        output.seek(0)
        
        return InMemoryUploadedFile(
            output,
            'ImageField',
            f"{image_field.name.split('.')[0]}_optimized.jpg",
            'image/jpeg',
            sys.getsizeof(output),
            None
        )
```

Update templates to use appropriate size:

```django
<!-- timeline/partials/entry_photo.html -->
{% if entry.image_thumbnail %}
    <img src="{{ entry.image_thumbnail.url }}" 
         alt="{{ entry.data.caption|default:'Photo' }}" 
         class="timeline-image"
         loading="lazy">
{% elif entry.image %}
    <img src="{{ entry.image.url }}" 
         alt="{{ entry.data.caption|default:'Photo' }}" 
         class="timeline-image"
         loading="lazy">
{% endif %}
```

---

## 4. **Recommended Implementation for Your App**

Given your use case, I recommend **Option A (Model save method)** with this implementation:

```python
# timeline/models.py
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings
import sys

class Entry(models.Model):
    # ... existing fields ...
    
    def save(self, *args, **kwargs):
        """Override save to optimize images"""
        if self.image and self._state.adding:  # Only optimize on creation
            self.image = self._optimize_image(self.image)
        super().save(*args, **kwargs)
    
    @staticmethod
    def _optimize_image(image_field):
        """
        Optimize uploaded image:
        - Convert to JPEG
        - Resize to max 1920x1920
        - Compress to 85% quality
        - Remove EXIF data
        """
        try:
            img = Image.open(image_field)
            
            # Rotate based on EXIF orientation before removing EXIF
            try:
                from PIL import ImageOps
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
            
            # Resize if needed (maintain aspect ratio)
            MAX_SIZE = (1920, 1920)
            if img.width > MAX_SIZE[0] or img.height > MAX_SIZE[1]:
                img.thumbnail(MAX_SIZE, Image.Resampling.LANCZOS)
            
            # Save optimized version
            output = BytesIO()
            img.save(
                output,
                format='JPEG',
                quality=85,
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
```

### Add to settings.py:

```python
# Image optimization (optional - defaults are set in model)
IMAGE_MAX_WIDTH = 1920
IMAGE_MAX_HEIGHT = 1920
IMAGE_JPEG_QUALITY = 85
```

---

## 5. **Benefits of This Approach**

✅ **Replaces original** - Saves storage space  
✅ **Automatic** - Works for all image uploads  
✅ **Consistent format** - All images become JPEG  
✅ **Progressive loading** - Better web performance  
✅ **EXIF rotation** - Handles phone photos correctly  
✅ **Error handling** - Falls back to original if optimization fails  
✅ **One location** - All logic in model, easy to maintain  

---

## 6. **Expected Results**

With these settings:
- **Before**: 3-5 MB phone photo (4000×3000 pixels)
- **After**: 200-400 KB optimized (1920×1440 pixels)
- **Savings**: ~90% reduction in file size
- **Quality**: Virtually indistinguishable for web viewing

---

## 7. **Testing the Implementation**

```python
# Test in Django shell
from timeline.models import Entry
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from io import BytesIO

# Create test image
img = Image.new('RGB', (3000, 2000), color='red')
buffer = BytesIO()
img.save(buffer, format='PNG')
buffer.seek(0)

# Create entry with large image
test_file = SimpleUploadedFile("test.png", buffer.read(), content_type="image/png")
entry = Entry.objects.create(
    user=user,
    form_type=photo_form_type,
    data={'caption': 'Test'},
    image=test_file
)

# Check result
print(f"Original: 3000x2000 PNG")
print(f"Optimized: {entry.image.width}x{entry.image.height}")
print(f"Size: {entry.image.size / 1024:.2f} KB")
```
