from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('linkedin_app', '0003_emailverification'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='visibility',
            field=models.CharField(
                choices=[
                    ('public', 'Public'),
                    ('connections', 'Connections only'),
                    ('only_me', 'Only me'),
                    ('specific', 'Specific people'),
                ],
                default='public',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='post',
            name='allowed_viewers',
            field=models.ManyToManyField(
                blank=True,
                help_text='Only used when visibility is "Specific people"',
                related_name='viewable_posts',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
