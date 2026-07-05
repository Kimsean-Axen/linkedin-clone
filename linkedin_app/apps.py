from django.apps import AppConfig


class LinkedinAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'linkedin_app'

    def ready(self):
        from django.conf import settings as s
        line = '=' * 62
        print(line)
        print('EMAIL SETTINGS (startup diagnostics):')
        print(f'  EMAIL_BACKEND   = {s.EMAIL_BACKEND}')
        print(f'  EMAIL_HOST      = {s.EMAIL_HOST}')
        print(f'  EMAIL_PORT      = {s.EMAIL_PORT}')
        print(f'  EMAIL_USE_TLS   = {s.EMAIL_USE_TLS}')
        print(f'  EMAIL_HOST_USER = {s.EMAIL_HOST_USER or "(not set)"}')
        if s.EMAIL_HOST_PASSWORD:
            print(f'  EMAIL_HOST_PASS = (set — {len(s.EMAIL_HOST_PASSWORD)} chars)')
        else:
            print('  EMAIL_HOST_PASS = (not set)')
        print(f'  DEFAULT_FROM    = {s.DEFAULT_FROM_EMAIL}')
        if 'console' in s.EMAIL_BACKEND:
            print()
            print('  ⚠  Console backend is active.')
            print('     Verification codes will PRINT HERE in the terminal.')
            print('     To send real emails, set these env vars before starting:')
            print('       EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend')
            print('       EMAIL_HOST=smtp.gmail.com')
            print('       EMAIL_PORT=587')
            print('       EMAIL_USE_TLS=True')
            print('       EMAIL_HOST_USER=your@gmail.com')
            print('       EMAIL_HOST_PASSWORD=your_16_char_app_password')
        print(line)
