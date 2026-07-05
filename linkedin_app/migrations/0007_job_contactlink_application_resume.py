from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('linkedin_app', '0006_all_fixes'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='contact_link',
            field=models.CharField(
                blank=True, max_length=500, default='',
                help_text='Any URL or contact link (Telegram, WhatsApp, website…)'
            ),
        ),
        migrations.AddField(
            model_name='jobapplication',
            name='resume',
            field=models.FileField(
                blank=True, null=True,
                upload_to='application_resumes/'
            ),
        ),
    ]
