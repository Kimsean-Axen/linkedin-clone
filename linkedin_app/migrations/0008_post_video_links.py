from django.db import migrations, models
import django.db.models.deletion


def _table_columns(schema_editor, table):
    with schema_editor.connection.cursor() as cur:
        cur.execute(f"PRAGMA table_info({table})")
        return {row[1] for row in cur.fetchall()}


def _table_exists(schema_editor, table):
    with schema_editor.connection.cursor() as cur:
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=%s",
            [table],
        )
        return cur.fetchone() is not None


def add_missing_schema(apps, schema_editor):
    """Idempotently add new columns / tables that some shipped DBs may already have."""
    if schema_editor.connection.vendor != 'sqlite':
        # Fallback: rely on Django's regular AddField/CreateModel for non-sqlite.
        return

    if 'video' not in _table_columns(schema_editor, 'linkedin_app_post'):
        with schema_editor.connection.cursor() as cur:
            cur.execute(
                "ALTER TABLE linkedin_app_post ADD COLUMN video varchar(100) NULL"
            )

    if not _table_exists(schema_editor, 'linkedin_app_profilelink'):
        with schema_editor.connection.cursor() as cur:
            cur.execute("""
                CREATE TABLE linkedin_app_profilelink (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    label varchar(100) NOT NULL,
                    url varchar(500) NOT NULL,
                    created_at datetime NOT NULL,
                    profile_id bigint NOT NULL REFERENCES linkedin_app_profile(id) DEFERRABLE INITIALLY DEFERRED
                )
            """)
            cur.execute(
                "CREATE INDEX linkedin_app_profilelink_profile_id ON linkedin_app_profilelink(profile_id)"
            )

    if not _table_exists(schema_editor, 'linkedin_app_jobcontactlink'):
        with schema_editor.connection.cursor() as cur:
            cur.execute("""
                CREATE TABLE linkedin_app_jobcontactlink (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    label varchar(100) NOT NULL,
                    url varchar(500) NOT NULL,
                    created_at datetime NOT NULL,
                    job_id bigint NOT NULL REFERENCES linkedin_app_job(id) DEFERRABLE INITIALLY DEFERRED
                )
            """)
            cur.execute(
                "CREATE INDEX linkedin_app_jobcontactlink_job_id ON linkedin_app_jobcontactlink(job_id)"
            )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    """Idempotent schema sync + Django state registration.

    Some shipped SQLite databases already carry a ``video`` column on Post from
    an earlier iteration. Running a plain AddField would crash on those with
    ``duplicate column name: video``. This migration therefore updates
    Django's model state unconditionally (state_operations) and applies the
    schema change only when the column/table is actually missing
    (database_operations via RunPython).
    """

    dependencies = [
        ('linkedin_app', '0007_job_contactlink_application_resume'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddField(
                    model_name='post',
                    name='video',
                    field=models.FileField(blank=True, null=True, upload_to='post_videos/'),
                ),
                migrations.CreateModel(
                    name='ProfileLink',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('label', models.CharField(max_length=100)),
                        ('url', models.CharField(max_length=500)),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='links', to='linkedin_app.profile')),
                    ],
                    options={'ordering': ['created_at']},
                ),
                migrations.CreateModel(
                    name='JobContactLink',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('label', models.CharField(max_length=100)),
                        ('url', models.CharField(max_length=500)),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contact_links', to='linkedin_app.job')),
                    ],
                    options={'ordering': ['created_at']},
                ),
            ],
            database_operations=[
                migrations.RunPython(add_missing_schema, noop_reverse),
            ],
        ),
    ]
