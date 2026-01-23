# Generated migration for timeline app

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FormType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Display name (e.g., "School Day", "Photo")', max_length=100)),
                ('type', models.CharField(help_text="Internal identifier (e.g., 'schoolday', 'photo') - must match form registry", max_length=50, unique=True)),
                ('icon', models.CharField(default='📋', help_text='Emoji icon', max_length=10)),
                ('description', models.TextField(blank=True, help_text='Description shown to users')),
                ('is_active', models.BooleanField(default=True, help_text='If false, form is hidden from all users')),
                ('is_default', models.BooleanField(default=False, help_text='If true, new users automatically get access')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Form Type',
                'verbose_name_plural': 'Form Types',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('data', models.JSONField(help_text='Form data stored as JSON')),
                ('image', models.ImageField(blank=True, null=True, upload_to='uploads/%Y/%m/%d/', validators=[django.core.validators.FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif', 'webp'])])),
                ('form_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='entries', to='timeline.formtype')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='timeline_entries', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Entry',
                'verbose_name_plural': 'Entries',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='UserFormAccess',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('granted_at', models.DateTimeField(auto_now_add=True)),
                ('form_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_access', to='timeline.formtype')),
                ('granted_by', models.ForeignKey(blank=True, help_text='Admin who granted this access', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='granted_form_access', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='form_access', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User Form Access',
                'verbose_name_plural': 'User Form Access',
                'ordering': ['-granted_at'],
            },
        ),
        migrations.AddIndex(
            model_name='entry',
            index=models.Index(fields=['-timestamp'], name='timeline_en_timesta_idx'),
        ),
        migrations.AddIndex(
            model_name='entry',
            index=models.Index(fields=['user', '-timestamp'], name='timeline_en_user_ti_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='userformaccess',
            unique_together={('user', 'form_type')},
        ),
    ]
