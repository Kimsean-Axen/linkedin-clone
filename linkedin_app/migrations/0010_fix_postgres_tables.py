from django.db import migrations


def _table_exists(schema_editor, table):
    vendor = schema_editor.connection.vendor
    with schema_editor.connection.cursor() as cur:
        if vendor == 'postgresql':
            cur.execute(
                "SELECT tablename FROM pg_tables WHERE tablename = %s",
                [table],
            )
        else:
            cur.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=%s",
                [table],
            )
        return cur.fetchone() is not None


def create_missing_tables(apps, schema_editor):
    vendor = schema_editor.connection.vendor

    if not _table_exists(schema_editor, 'linkedin_app_profilelink'):
        with schema_editor.connection.cursor() as cur:
            if vendor == 'postgresql':
                cur.execute("""
                    CREATE TABLE linkedin_app_profilelink (
                        id BIGSERIAL PRIMARY KEY,
                        label varchar(100) NOT NULL,
                        url varchar(500) NOT NULL,
                        created_at timestamp with time zone NOT NULL,
                        profile_id bigint NOT NULL REFERENCES linkedin_app_profile(id) DEFERRABLE INITIALLY DEFERRED
                    )
                """)
                cur.execute(
                    "CREATE INDEX linkedin_app_profilelink_profile_id ON linkedin_app_profilelink(profile_id)"
                )

    if not _table_exists(schema_editor, 'linkedin_app_jobcontactlink'):
        with schema_editor.connection.cursor() as cur:
            if vendor == 'postgresql':
                cur.execute("""
                    CREATE TABLE linkedin_app_jobcontactlink (
                        id BIGSERIAL PRIMARY KEY,
                        label varchar(100) NOT NULL,
                        url varchar(500) NOT NULL,
                        created_at timestamp with time zone NOT NULL,
                        job_id bigint NOT NULL REFERENCES linkedin_app_job(id) DEFERRABLE INITIALLY DEFERRED
                    )
                """)
                cur.execute(
                    "CREATE INDEX linkedin_app_jobcontactlink_job_id ON linkedin_app_jobcontactlink(job_id)"
                )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('linkedin_app', '0009_alter_connection_status_alter_job_contact_link_and_more'),
    ]

    operations = [
        migrations.RunPython(create_missing_tables, noop_reverse),
    ]