# Fix TimeSlot model fields

from django.db import migrations, models


def populate_timeslot_fields(apps, schema_editor):
    """Populate missing fields for existing timeslots"""
    TimeSlot = apps.get_model('timetable_app', 'TimeSlot')
    for i, timeslot in enumerate(TimeSlot.objects.all(), 1):
        timeslot.slot_type = 'lecture'
        timeslot.slot_number = i
        # Determine if it's first half (before 1:00 PM)
        timeslot.is_first_half = timeslot.start_time.hour < 13
        timeslot.save()


def reverse_populate_timeslot_fields(apps, schema_editor):
    """Reverse operation - not needed"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('timetable_app', '0005_fix_subject_fields'),
    ]

    operations = [
        # Add missing fields to TimeSlot
        migrations.AddField(
            model_name='timeslot',
            name='slot_type',
            field=models.CharField(choices=[('lecture', 'Lecture (1 hour)'), ('lab', 'Lab (2 hours)'), ('break', 'Break'), ('project', 'Project Time')], default='lecture', max_length=10),
        ),
        migrations.AddField(
            model_name='timeslot',
            name='slot_number',
            field=models.IntegerField(default=1, help_text='Slot position in day (1-9)'),
        ),
        migrations.AddField(
            model_name='timeslot',
            name='is_first_half',
            field=models.BooleanField(default=True, help_text='Before lunch break'),
        ),
        
        # Populate fields for existing timeslots
        migrations.RunPython(populate_timeslot_fields, reverse_populate_timeslot_fields),
        
        # Add unique constraint
        migrations.AlterUniqueTogether(
            name='timeslot',
            unique_together={('day', 'slot_number')},
        ),
    ]
