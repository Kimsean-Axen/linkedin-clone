# LinkedIn Clone - Django

A full-featured LinkedIn clone built with Django.

## Features

- **User Authentication** — Register, login, logout with email-based auth + email verification
- **Profiles** — Full profile with headline, bio, experience, education, skills, profile picture, cover photo
- **News Feed** — Create posts with images, like posts, comment on posts
- **Network** — Send/accept/decline connection requests, people you may know suggestions
- **Jobs** — Browse, filter, and apply for jobs; post your own jobs
- **Messaging** — Direct messages between connected users
- **Notifications** — Real-time notifications for likes, comments, connections, messages
- **Search** — Search people and jobs

## Tech Stack

- **Backend**: Django 4.2
- **Database**: SQLite (easily swap to PostgreSQL/MySQL)
- **Frontend**: Bootstrap 5 + Bootstrap Icons
- **Image handling**: Pillow

## Quick Start

> Note: if any command below with `python` gives a "command not found" error,
> use `python3` and `pip3` instead (common on macOS/Linux).

### 0. Go to the project folder

Unzip the project first, then move into the folder that contains `manage.py`:

```bash
cd linkedin_clone_work
```

All commands below must be run from inside this folder.

### 1. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate            # macOS/Linux
venv\Scripts\activate               # Windows (Command Prompt)
venv\Scripts\Activate.ps1           # Windows (PowerShell)
```

> **PowerShell error "running scripts is disabled on this system"?**
> This is a default Windows security setting, not a bug. Fix it by running
> this once in PowerShell (as the same user, not admin needed):
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```
> Then try `venv\Scripts\Activate.ps1` again.

Once activated, your terminal prompt should show `(venv)` at the start of the
line. If it doesn't, the activation didn't work — re-run the command above.

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create your .env file

The app automatically loads settings (like the secret key and email config)
from a `.env` file in this folder. Create it by copying the example:

```bash
cp .env.example .env        # macOS/Linux
copy .env.example .env      # Windows
```

You can leave the defaults for now — the app will still run and print
verification codes to the terminal instead of emailing them. See
**Email Setup** below if you want real emails sent later.

### 4. Set up the database

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create a superuser (admin)

```bash
python manage.py createsuperuser
```

Follow the prompts (username, email, password) — this account lets you log
into `/admin/`.

### 6. Configure email (optional — so verification codes are actually sent)

See the **Email Setup** section below. Without this step, codes are only printed
to the terminal — users will not receive them in their inbox.

### 7. Run the development server

```bash
python manage.py runserver
```

Visit **http://127.0.0.1:8000** in your browser.

---

## Email Setup — How to Make Verification Codes Actually Send

By default the app uses Django's **console** email backend, which prints the
verification code to your terminal instead of emailing it. To send real emails
you need to set a few environment variables before starting the server.

### Option A — Gmail (recommended, free)

1. Sign in to your Google Account.
2. Go to **Security → 2-Step Verification** and make sure it is **turned ON**.
3. Go to **Security → App Passwords** (search "App Passwords" in your Google
   account settings if you can't find it).
4. Create a new App Password — choose **Mail** and your device, then copy the
   16-character password shown (e.g. `abcd efgh ijkl mnop`).
5. Set the following environment variables in your terminal **before** running
   the server:

**macOS / Linux:**
```bash
export EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
export EMAIL_HOST=smtp.gmail.com
export EMAIL_PORT=587
export EMAIL_USE_TLS=True
export EMAIL_HOST_USER=your_gmail_address@gmail.com
export EMAIL_HOST_PASSWORD=abcdefghijklmnop   # 16-char App Password (no spaces)
export DEFAULT_FROM_EMAIL="LinkedIn Clone <your_gmail_address@gmail.com>"

python manage.py runserver
```

**Windows (Command Prompt):**
```cmd
set EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
set EMAIL_HOST=smtp.gmail.com
set EMAIL_PORT=587
set EMAIL_USE_TLS=True
set EMAIL_HOST_USER=your_gmail_address@gmail.com
set EMAIL_HOST_PASSWORD=abcdefghijklmnop
set DEFAULT_FROM_EMAIL=LinkedIn Clone <your_gmail_address@gmail.com>

python manage.py runserver
```

**Windows (PowerShell):**
```powershell
$env:EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend"
$env:EMAIL_HOST="smtp.gmail.com"
$env:EMAIL_PORT="587"
$env:EMAIL_USE_TLS="True"
$env:EMAIL_HOST_USER="your_gmail_address@gmail.com"
$env:EMAIL_HOST_PASSWORD="abcdefghijklmnop"
$env:DEFAULT_FROM_EMAIL="LinkedIn Clone <your_gmail_address@gmail.com>"

python manage.py runserver
```

### Option B — Outlook / Hotmail

```bash
export EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
export EMAIL_HOST=smtp.office365.com
export EMAIL_PORT=587
export EMAIL_USE_TLS=True
export EMAIL_HOST_USER=your_email@outlook.com
export EMAIL_HOST_PASSWORD=your_outlook_password
export DEFAULT_FROM_EMAIL="LinkedIn Clone <your_email@outlook.com>"
```

### Development fallback (no email configured)

If you do not set the `EMAIL_BACKEND` environment variable, verification codes
are printed to the **terminal window** where you ran `python manage.py runserver`.
Look for a block that starts with `Subject: Your LinkedIn Clone verification code`
— the 6-digit code is inside that block. You can copy it manually to verify
accounts during testing.

---

## Admin Panel

Visit **http://127.0.0.1:8000/admin/** to manage all data.

## Project Structure

```
linkedin_clone/
├── manage.py
├── requirements.txt
├── README.md
├── linkedin_clone/          # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── linkedin_app/            # Main app
│   ├── models.py            # All data models
│   ├── views.py             # All view logic
│   ├── forms.py             # Django forms
│   ├── admin.py             # Admin configuration
│   └── migrations/
├── templates/               # HTML templates
│   ├── base.html            # Base layout with navbar
│   ├── home.html            # Landing page
│   ├── registration/        # Login & Register
│   ├── feed/                # News feed
│   ├── profiles/            # User profiles
│   ├── connections/         # Network management
│   ├── jobs/                # Jobs board
│   ├── messaging/           # Direct messages
│   ├── search.html
│   └── notifications.html
└── static/
    └── css/
        └── style.css        # Custom LinkedIn-style CSS
```

## Models

- **Profile** — Extended user profile (headline, bio, location, pictures)
- **Experience** — Work experience entries
- **Education** — Education history
- **Skill** — Skills list
- **Post** — User posts with optional images
- **Like** — Post likes (unique per user+post)
- **Comment** — Post comments
- **Connection** — Friend connections (pending/accepted/declined)
- **Job** — Job postings with type, level, salary
- **JobApplication** — Job applications with cover letter
- **Message** — Direct messages between users
- **Notification** — Activity notifications

## Deploying to Production

1. Change `SECRET_KEY` in `settings.py` (use environment variable)
2. Set `DEBUG = False`
3. Update `ALLOWED_HOSTS` with your domain
4. Switch to PostgreSQL by updating `DATABASES`
5. Configure email environment variables (see Email Setup above)
6. Run `python manage.py collectstatic`
7. Use gunicorn + nginx for serving
