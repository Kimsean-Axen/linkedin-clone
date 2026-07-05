from django.db import migrations


def _column_exists(schema_editor, table, column):
    with schema_editor.connection.cursor() as cur:
        cur.execute("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = %s AND column_name = %s
        """, [table, column])
        return cur.fetchone() is not None


def add_video_column(apps, schema_editor):
    if schema_editor.connection.vendor != 'postgresql':
        return
    if not _column_exists(schema_editor, 'linkedin_app_post', 'video'):
        with schema_editor.connection.cursor() as cur:
            cur.execute(
                "ALTER TABLE linkedin_app_post ADD COLUMN video varchar(100) NULL"
            )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('linkedin_app', '0010_fix_postgres_tables'),
    ]

    operations = [
        migrations.RunPython(add_video_column, noop_reverse),
    ]