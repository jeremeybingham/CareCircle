from django.core.management.base import BaseCommand
from django.db import transaction
from timeline.models import FormType
from timeline.forms import get_registry_info


class Command(BaseCommand):
    help = 'Initialize form types in the database from the form registry'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete all existing form types and recreate them',
        )

    def handle(self, *args, **options):
        reset = options['reset']
        
        if reset:
            self.stdout.write(self.style.WARNING('Resetting all form types...'))
            FormType.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓ All form types deleted'))
        
        # Get all registered forms
        forms_info = get_registry_info()
        
        self.stdout.write(self.style.NOTICE(f'\nFound {len(forms_info)} forms in registry:'))
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        with transaction.atomic():
            for form_info in forms_info:
                form_type, created = FormType.objects.get_or_create(
                    type=form_info['type'],
                    defaults={
                        'name': form_info['name'],
                        'icon': form_info['icon'],
                        'description': form_info['description'],
                        'is_default': False,  # Set manually in admin
                        'is_active': True,
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  ✓ Created: {form_type.icon} {form_type.name} ({form_type.type})'
                        )
                    )
                else:
                    # Update metadata if form already exists
                    updated = False
                    if form_type.name != form_info['name']:
                        form_type.name = form_info['name']
                        updated = True
                    if form_type.icon != form_info['icon']:
                        form_type.icon = form_info['icon']
                        updated = True
                    if form_type.description != form_info['description']:
                        form_type.description = form_info['description']
                        updated = True
                    
                    if updated:
                        form_type.save()
                        updated_count += 1
                        self.stdout.write(
                            self.style.WARNING(
                                f'  ↻ Updated: {form_type.icon} {form_type.name} ({form_type.type})'
                            )
                        )
                    else:
                        skipped_count += 1
                        self.stdout.write(
                            f'  - Skipped: {form_type.icon} {form_type.name} ({form_type.type}) (no changes)'
                        )
        
        # Summary
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS(f'Created: {created_count}'))
        if updated_count > 0:
            self.stdout.write(self.style.WARNING(f'Updated: {updated_count}'))
        if skipped_count > 0:
            self.stdout.write(f'Skipped: {skipped_count}')
        self.stdout.write('=' * 50)
        
        # Instructions
        self.stdout.write('\n' + self.style.NOTICE('Next steps:'))
        self.stdout.write('1. Go to Django admin: /admin/')
        self.stdout.write('2. Navigate to "Form Types"')
        self.stdout.write('3. Mark forms as "default" if they should be auto-granted to new users')
        self.stdout.write('4. Grant access to existing users via "User Form Access"')
        self.stdout.write('')
