from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('linkedin_app', '0005_profile_background_darkmode'),
    ]

    operations = [
        # FIX 6: Background positioning controls
        migrations.AddField(
            model_name='profile',
            name='bg_position_x',
            field=models.FloatField(default=50),
        ),
        migrations.AddField(
            model_name='profile',
            name='bg_position_y',
            field=models.FloatField(default=50),
        ),
        migrations.AddField(
            model_name='profile',
            name='bg_zoom',
            field=models.FloatField(default=100),
        ),
        # FIX 7: Multi-select job types & experience levels
        migrations.AddField(
            model_name='job',
            name='job_types',
            field=models.CharField(
                blank=True, default='', max_length=200,
                help_text='Comma-separated job type values'
            ),
        ),
        migrations.AddField(
            model_name='job',
            name='experience_levels',
            field=models.CharField(
                blank=True, default='', max_length=200,
                help_text='Comma-separated experience level values'
            ),
        ),
        migrations.AddField(
            model_name='job',
            name='salary_negotiable',
            field=models.BooleanField(default=False),
        ),
        # FIX 4: Message attachments
        migrations.AlterField(
            model_name='message',
            name='content',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='message',
            name='attachment',
            field=models.FileField(blank=True, null=True, upload_to='message_attachments/'),
        ),
        migrations.AddField(
            model_name='message',
            name='attachment_type',
            field=models.CharField(blank=True, max_length=20),
        ),
    ]
