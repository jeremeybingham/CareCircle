"""
Management command to optimize existing images in the database.

This applies the same optimization as new uploads:
- Convert to JPEG
- Resize to max dimensions (default 1920x1920)
- Compress to quality setting (default 85%)
- Handle EXIF rotation
- Remove EXIF data
"""

import os
import sys
from io import BytesIO

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from PIL import Image, ImageOps

from timeline.models import Entry


class Command(BaseCommand):
    help = 'Optimize existing images in the database to reduce file sizes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be optimized without making changes',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Re-optimize images even if they are already JPEG',
        )
        parser.add_argument(
            '--min-size',
            type=int,
            default=100,
            help='Minimum file size in KB to consider for optimization (default: 100)',
        )
        parser.add_argument(
            '--entry-id',
            type=int,
            help='Optimize only a specific entry by ID',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']
        min_size_kb = options['min_size']
        entry_id = options['entry_id']

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No changes will be made\n'))

        # Get image optimization settings
        max_width = getattr(settings, 'IMAGE_MAX_WIDTH', 1920)
        max_height = getattr(settings, 'IMAGE_MAX_HEIGHT', 1920)
        jpeg_quality = getattr(settings, 'IMAGE_JPEG_QUALITY', 85)

        self.stdout.write(f'Image settings: max {max_width}x{max_height}, JPEG quality {jpeg_quality}%\n')

        # Build queryset
        queryset = Entry.objects.exclude(image='').exclude(image__isnull=True)
        if entry_id:
            queryset = queryset.filter(pk=entry_id)

        total_entries = queryset.count()
        if total_entries == 0:
            self.stdout.write(self.style.WARNING('No entries with images found.'))
            return

        self.stdout.write(f'Found {total_entries} entries with images\n')

        # Track statistics
        optimized_count = 0
        skipped_count = 0
        error_count = 0
        total_saved_bytes = 0

        for entry in queryset:
            result = self._process_entry(
                entry,
                dry_run=dry_run,
                force=force,
                min_size_kb=min_size_kb,
                max_width=max_width,
                max_height=max_height,
                jpeg_quality=jpeg_quality,
            )

            if result['status'] == 'optimized':
                optimized_count += 1
                total_saved_bytes += result.get('saved_bytes', 0)
            elif result['status'] == 'skipped':
                skipped_count += 1
            elif result['status'] == 'error':
                error_count += 1

        # Summary
        self.stdout.write('\n' + '=' * 60)
        action = 'Would optimize' if dry_run else 'Optimized'
        self.stdout.write(self.style.SUCCESS(f'{action}: {optimized_count}'))
        self.stdout.write(f'Skipped: {skipped_count}')
        if error_count:
            self.stdout.write(self.style.ERROR(f'Errors: {error_count}'))

        if total_saved_bytes > 0:
            saved_mb = total_saved_bytes / (1024 * 1024)
            saved_label = 'Would save' if dry_run else 'Saved'
            self.stdout.write(self.style.SUCCESS(f'{saved_label}: {saved_mb:.2f} MB'))

        self.stdout.write('=' * 60)

        if dry_run and optimized_count > 0:
            self.stdout.write(
                self.style.NOTICE('\nRun without --dry-run to apply optimizations')
            )

    def _process_entry(self, entry, dry_run, force, min_size_kb, max_width, max_height, jpeg_quality):
        """Process a single entry's image."""
        try:
            # Check if image file exists
            if not entry.image:
                return {'status': 'skipped', 'reason': 'no image'}

            try:
                image_path = entry.image.path
                original_size = os.path.getsize(image_path)
            except (ValueError, FileNotFoundError):
                # S3 or missing file - try to get size from storage
                try:
                    original_size = entry.image.size
                except Exception:
                    self.stdout.write(
                        self.style.WARNING(f'  Entry {entry.pk}: Cannot access image file')
                    )
                    return {'status': 'error', 'reason': 'file not accessible'}

            original_size_kb = original_size / 1024

            # Skip small files unless forced
            if original_size_kb < min_size_kb and not force:
                return {'status': 'skipped', 'reason': 'below size threshold'}

            # Check if already a small JPEG
            filename = entry.image.name.lower()
            is_jpeg = filename.endswith(('.jpg', '.jpeg'))

            # Open and analyze the image
            entry.image.seek(0)
            img = Image.open(entry.image)

            needs_resize = img.width > max_width or img.height > max_height
            needs_convert = img.mode not in ('RGB',) or not is_jpeg

            if not needs_resize and not needs_convert and not force:
                return {'status': 'skipped', 'reason': 'already optimized'}

            # Perform optimization
            optimized_data = self._optimize_image(
                entry.image,
                max_width,
                max_height,
                jpeg_quality,
            )

            if optimized_data is None:
                return {'status': 'error', 'reason': 'optimization failed'}

            new_size = len(optimized_data)
            saved_bytes = original_size - new_size

            # Only save if we actually reduced size (or forced)
            if saved_bytes <= 0 and not force:
                self.stdout.write(
                    f'  Entry {entry.pk}: Skipped (no size reduction)'
                )
                return {'status': 'skipped', 'reason': 'no size reduction'}

            # Generate new filename
            original_name = entry.image.name
            name_without_ext = original_name.rsplit('.', 1)[0]
            new_filename = f"{name_without_ext}.jpg"

            # Report
            saved_kb = saved_bytes / 1024
            percent_saved = (saved_bytes / original_size * 100) if original_size > 0 else 0
            action = 'Would optimize' if dry_run else 'Optimized'

            self.stdout.write(
                self.style.SUCCESS(
                    f'  {action} Entry {entry.pk}: '
                    f'{original_size_kb:.1f}KB → {new_size/1024:.1f}KB '
                    f'(saved {saved_kb:.1f}KB, {percent_saved:.0f}%)'
                )
            )

            if not dry_run:
                # Delete old file
                old_name = entry.image.name
                entry.image.delete(save=False)

                # Save new optimized image
                entry.image.save(new_filename, ContentFile(optimized_data), save=True)

            return {
                'status': 'optimized',
                'saved_bytes': saved_bytes,
            }

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'  Entry {entry.pk}: Error - {str(e)}')
            )
            return {'status': 'error', 'reason': str(e)}

    def _optimize_image(self, image_field, max_width, max_height, jpeg_quality):
        """
        Optimize an image file.

        Returns the optimized image bytes, or None if optimization fails.
        """
        try:
            image_field.seek(0)
            img = Image.open(image_field)

            # Rotate based on EXIF orientation before removing EXIF
            try:
                img = ImageOps.exif_transpose(img)
            except Exception:
                pass

            # Convert to RGB (handles PNG transparency, etc.)
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                if img.mode == 'RGBA':
                    background.paste(img, mask=img.split()[3])
                else:
                    background.paste(img)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')

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
                progressive=True,
            )

            return output.getvalue()

        except Exception as e:
            self.stderr.write(f'Optimization error: {e}')
            return None
