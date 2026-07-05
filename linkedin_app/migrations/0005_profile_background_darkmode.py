from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('linkedin_app', '0004_post_visibility_allowed_viewers'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='dark_mode',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='bg_image',
            field=models.ImageField(blank=True, null=True, upload_to='page_backgrounds/'),
        ),
        migrations.AddField(
            model_name='profile',
            name='bg_opacity',
            field=models.FloatField(default=0.5),
        ),
        migrations.AddField(
            model_name='profile',
            name='bg_fit',
            field=models.CharField(
                choices=[('cover', 'Cover'), ('contain', 'Contain'), ('stretch', 'Stretch'), ('tile', 'Tile')],
                default='cover',
                max_length=20,
            ),
        ),
    ]
