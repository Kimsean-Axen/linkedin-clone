from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('linkedin_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='phone_number',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='profile',
            name='contact_email',
            field=models.EmailField(blank=True, help_text='Public contact email, can differ from login email', max_length=254),
        ),
    ]
