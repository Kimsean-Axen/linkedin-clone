from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Profile(models.Model):
    BG_FIT_CHOICES = [
        ('cover', 'Cover'),
        ('contain', 'Contain'),
        ('stretch', 'Stretch'),
        ('tile', 'Tile'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    headline = models.CharField(max_length=220, blank=True)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    contact_email = models.EmailField(blank=True, help_text="Public contact email, can differ from login email")
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    cover_photo = models.ImageField(upload_to='cover_photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Dark mode & background customization
    dark_mode = models.BooleanField(default=False)
    bg_image = models.ImageField(upload_to='page_backgrounds/', blank=True, null=True)
    bg_opacity = models.FloatField(default=0.5)
    bg_fit = models.CharField(max_length=20, choices=BG_FIT_CHOICES, default='cover')
    # FIX 6: Manual background positioning controls
    bg_position_x = models.FloatField(default=50)   # 0–100 %
    bg_position_y = models.FloatField(default=50)   # 0–100 %
    bg_zoom = models.FloatField(default=100)         # 50–300 %

    def __str__(self):
        return f'{self.user.username} Profile'

    def get_connection_count(self):
        return Connection.objects.filter(
            (models.Q(sender=self.user) | models.Q(receiver=self.user)),
            status='accepted'
        ).count()


class EmailVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='email_verification')
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=15)

    def __str__(self):
        return f'Verification for {self.user.email}'


class Experience(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='experiences')
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=100, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    current = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f'{self.title} at {self.company}'


class Education(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='educations')
    school = models.CharField(max_length=200)
    degree = models.CharField(max_length=200)
    field_of_study = models.CharField(max_length=200, blank=True)
    start_year = models.IntegerField()
    end_year = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['-start_year']

    def __str__(self):
        return f'{self.degree} at {self.school}'


class Skill(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Post(models.Model):
    VISIBILITY_PUBLIC = 'public'
    VISIBILITY_CONNECTIONS = 'connections'
    VISIBILITY_ONLY_ME = 'only_me'
    VISIBILITY_SPECIFIC = 'specific'

    VISIBILITY_CHOICES = [
        (VISIBILITY_PUBLIC, 'Public'),
        (VISIBILITY_CONNECTIONS, 'Connections only'),
        (VISIBILITY_ONLY_ME, 'Only me'),
        (VISIBILITY_SPECIFIC, 'Specific people'),
    ]

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    video = models.FileField(upload_to='post_videos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default=VISIBILITY_PUBLIC)
    allowed_viewers = models.ManyToManyField(User, blank=True, related_name='allowed_posts')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Post by {self.author.username}'


class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Comment by {self.author.username}'


class Connection(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_connections')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_connections')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('sender', 'receiver')

    def __str__(self):
        return f'{self.sender.username} → {self.receiver.username} ({self.status})'


class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ('full_time', 'Full-time'),
        ('part_time', 'Part-time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('remote', 'Remote'),
    ]
    EXPERIENCE_CHOICES = [
        ('entry', 'Entry Level'),
        ('mid', 'Mid Level'),
        ('senior', 'Senior Level'),
        ('executive', 'Executive'),
    ]
    poster = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_jobs')
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    # Legacy single-value fields kept for read compatibility
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='full_time')
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, default='mid')
    # FIX 7: Multi-select — stored as comma-separated values
    job_types = models.CharField(max_length=200, blank=True, default='',
                                 help_text='Comma-separated job type values')
    experience_levels = models.CharField(max_length=200, blank=True, default='',
                                         help_text='Comma-separated experience level values')
    description = models.TextField()
    requirements = models.TextField(blank=True)
    # Clickable contact / apply link (Telegram, WhatsApp, website, etc.)
    contact_link = models.CharField(max_length=500, blank=True,
                                    help_text='Any URL or contact link (Telegram, WhatsApp, website…)')
    salary_min = models.IntegerField(null=True, blank=True)
    salary_max = models.IntegerField(null=True, blank=True)
    salary_negotiable = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def get_job_types_list(self):
        if self.job_types:
            return [t.strip() for t in self.job_types.split(',') if t.strip()]
        if self.job_type:
            return [self.job_type]
        return []

    def get_experience_levels_list(self):
        if self.experience_levels:
            return [l.strip() for l in self.experience_levels.split(',') if l.strip()]
        if self.experience_level:
            return [self.experience_level]
        return []

    def get_job_type_labels(self):
        type_map = dict(self.JOB_TYPE_CHOICES)
        return [type_map.get(t, t) for t in self.get_job_types_list()]

    def get_experience_level_labels(self):
        exp_map = dict(self.EXPERIENCE_CHOICES)
        return [exp_map.get(l, l) for l in self.get_experience_levels_list()]

    @property
    def applicant_count(self):
        return self.applications.count()

    def __str__(self):
        return self.title


class JobApplication(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    cover_letter = models.TextField(blank=True)
    resume = models.FileField(upload_to='application_resumes/', blank=True, null=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='applied')

    class Meta:
        unique_together = ('job', 'applicant')

    def __str__(self):
        return f'{self.applicant.username} applied to {self.job.title}'


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField(blank=True)
    # FIX 4: Media attachments
    attachment = models.FileField(upload_to='message_attachments/', blank=True, null=True)
    attachment_type = models.CharField(max_length=20, blank=True,
                                       help_text='image, video, or file')
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Message from {self.sender.username} to {self.receiver.username}'


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('connection', 'Connection Request'),
        ('connection_accepted', 'Connection Accepted'),
        ('job_application', 'Job Application'),
        ('message', 'New Message'),
    ]
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    link = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Notification for {self.recipient.username}: {self.notification_type}'


class ProfileLink(models.Model):
    """User-defined extra links on a profile (label + URL). Clickable."""
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='links')
    label = models.CharField(max_length=100)
    url = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.label} — {self.url}'


class JobContactLink(models.Model):
    """Extra contact links on a job posting (phone, WhatsApp, Telegram, etc.)."""
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='contact_links')
    label = models.CharField(max_length=100)
    url = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.label} — {self.url}'
