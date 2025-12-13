# Fix Subject model fields

from django.db import migrations, models


def populate_subject_codes(apps, schema_editor):
    """Populate unique codes for existing subjects"""
    Subject = apps.get_model('timetable_app', 'Subject')
    for i, subject in enumerate(Subject.objects.all(), 1):
        subject.code = f"SUBJ-{i:03d}"
        subject.save()


def reverse_populate_subject_codes(apps, schema_editor):
    """Reverse operation - not needed"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('timetable_app', '0004_enhanced_models'),
    ]

    operations = [
        # Add missing code field to Subject (non-unique first)
        migrations.AddField(
            model_name='subject',
            name='code',
            field=models.CharField(max_length=20, null=True, blank=True),
        ),
        
        # Populate codes for existing subjects
        migrations.RunPython(populate_subject_codes, reverse_populate_subject_codes),
        
        # Make code field unique and non-null
        migrations.AlterField(
            model_name='subject',
            name='code',
            field=models.CharField(max_length=20, unique=True),
        ),
        
        # Rename is_lab to requires_lab
        migrations.RenameField(
            model_name='subject',
            old_name='is_lab',
            new_name='requires_lab',
        ),
        
        # Add missing lab_type field to Lab
        migrations.AddField(
            model_name='lab',
            name='lab_type',
            field=models.CharField(blank=True, max_length=50),
        ),
        
        # Add missing room_type field to Room
        migrations.AddField(
            model_name='room',
            name='room_type',
            field=models.CharField(default='classroom', max_length=20),
        ),
    ]
