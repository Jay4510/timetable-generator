# Generated manually to avoid interactive prompts

from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('timetable_app', '0003_auto_20251001_0206'),
    ]

    operations = [
        # Add new fields to Teacher model
        migrations.AddField(
            model_name='teacher',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='teacher',
            name='department',
            field=models.CharField(default='Information Technology', max_length=100),
        ),
        migrations.AddField(
            model_name='teacher',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('resigned', 'Resigned'), ('on_leave', 'On Leave'), ('temporary', 'Temporary')], default='active', max_length=20),
        ),
        migrations.AddField(
            model_name='teacher',
            name='time_preference',
            field=models.CharField(choices=[('first_half', 'Prefer First Half (Before Lunch)'), ('second_half', 'Prefer Second Half (After Lunch)'), ('no_preference', 'No Preference'), ('mixed', 'Mixed (Both Halves)')], default='no_preference', max_length=20),
        ),
        migrations.AddField(
            model_name='teacher',
            name='can_teach_labs',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='teacher',
            name='can_teach_projects',
            field=models.BooleanField(default=True),
        ),
        
        # Add new fields to TimetableVersion model
        migrations.AddField(
            model_name='timetableversion',
            name='algorithm_used',
            field=models.CharField(default='enhanced_genetic', max_length=50),
        ),
        migrations.AddField(
            model_name='timetableversion',
            name='fitness_score',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='timetableversion',
            name='generation_time',
            field=models.FloatField(blank=True, help_text='Time taken to generate in seconds', null=True),
        ),
        
        # Create new models
        migrations.CreateModel(
            name='SubjectProficiency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('knowledge_rating', models.IntegerField(help_text='Knowledge level (1-10)', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)])),
                ('willingness_rating', models.IntegerField(help_text='Willingness to teach (1-10)', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timetable_app.subject')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timetable_app.teacher')),
            ],
            options={
                'ordering': ['-knowledge_rating', '-willingness_rating'],
            },
        ),
        migrations.CreateModel(
            name='ProjectTimeAllocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_type', models.CharField(choices=[('mini', 'Mini Project'), ('major', 'Major Project'), ('internship', 'Internship'), ('research', 'Research Work')], max_length=20)),
                ('duration_hours', models.IntegerField(default=4, help_text='Duration in hours')),
                ('is_active', models.BooleanField(default=True)),
                ('division', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timetable_app.division')),
                ('guide', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='guided_projects', to='timetable_app.teacher')),
                ('timeslot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timetable_app.timeslot')),
                ('year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timetable_app.year')),
            ],
        ),
        migrations.CreateModel(
            name='TeacherReplacement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.CharField(help_text='Reason for replacement', max_length=200)),
                ('effective_date', models.DateField()),
                ('is_completed', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('original_teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='replacements_from', to='timetable_app.teacher')),
                ('replacement_teacher', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='replacements_to', to='timetable_app.teacher')),
                ('subjects_transferred', models.ManyToManyField(blank=True, to='timetable_app.subject')),
            ],
        ),
        
        # Add unique constraints
        migrations.AlterUniqueTogether(
            name='subjectproficiency',
            unique_together={('teacher', 'subject')},
        ),
        migrations.AlterUniqueTogether(
            name='projecttimeallocation',
            unique_together={('year', 'division', 'timeslot')},
        ),
    ]
