from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Experience, Education, Skill, Post, Comment, Job, JobApplication, Message


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'placeholder': 'First name'}))
    last_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'placeholder': 'Last name'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email address'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email__iexact=email).exists() or User.objects.filter(username__iexact=email).exists():
            raise forms.ValidationError(
                'An account with this email address already exists. '
                'Please sign in or use a different email.'
            )
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email address'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))


class ProfileForm(forms.ModelForm):
    """
    Pass fields_only=['field1', 'field2'] to restrict which fields are rendered.
    Used by the profile setup wizard to show only relevant fields per step.
    """
    def __init__(self, *args, fields_only=None, **kwargs):
        super().__init__(*args, **kwargs)
        if fields_only is not None:
            allowed = set(fields_only)
            for field_name in list(self.fields.keys()):
                if field_name not in allowed:
                    del self.fields[field_name]

    class Meta:
        model = Profile
        fields = ['headline', 'bio', 'location', 'website', 'phone_number', 'contact_email',
                  'profile_picture', 'cover_photo']
        widgets = {
            'headline': forms.TextInput(attrs={'placeholder': 'e.g. Software Engineer at Google'}),
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell us about yourself...'}),
            'location': forms.TextInput(attrs={'placeholder': 'e.g. San Francisco, CA'}),
            'website': forms.URLInput(attrs={'placeholder': 'https://yourwebsite.com'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'e.g. +1 (555) 000-0000'}),
            'contact_email': forms.EmailInput(attrs={'placeholder': 'e.g. contact@yourname.com'}),
        }


class ContactInfoForm(forms.ModelForm):
    """Focused form for editing only the contact fields, used in the profile page modal."""
    class Meta:
        model = Profile
        fields = ['contact_email', 'phone_number', 'website', 'location']
        widgets = {
            'contact_email': forms.EmailInput(attrs={'placeholder': 'Public contact email'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'e.g. +1 (555) 000-0000'}),
            'website': forms.URLInput(attrs={'placeholder': 'https://yourwebsite.com'}),
            'location': forms.TextInput(attrs={'placeholder': 'e.g. San Francisco, CA'}),
        }


class UserUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']



class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = ['title', 'company', 'location', 'start_date', 'end_date', 'current', 'description']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ['school', 'degree', 'field_of_study', 'start_year', 'end_year', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['name']


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'image', 'video', 'visibility', 'allowed_viewers']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Share an update, article, or idea…',
                'class': 'post-textarea',
            }),
            'allowed_viewers': forms.CheckboxSelectMultiple(),
        }



class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.TextInput(attrs={'placeholder': 'Add a comment…', 'class': 'comment-input'}),
        }


class JobForm(forms.ModelForm):
    """Custom form: job_types and experience_levels handled as multi-checkbox in the template."""
    class Meta:
        model = Job
        fields = ['title', 'company', 'location', 'description', 'requirements',
                  'contact_link', 'salary_min', 'salary_max', 'salary_negotiable']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 7, 'placeholder': 'Describe the role, responsibilities, and company culture…'}),
            'requirements': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Skills, qualifications, and experience required…'}),
            'contact_link': forms.TextInput(attrs={'placeholder': 'e.g. https://t.me/yourhandle or https://wa.me/1234567890'}),
        }


class JobApplicationForm(forms.ModelForm):
    resume = forms.FileField(
        required=False,
        label='Resume / CV (optional)',
        widget=forms.FileInput(attrs={'accept': '.pdf,.doc,.docx,.txt'}),
        help_text='PDF, DOC, DOCX or TXT · max 5 MB'
    )

    class Meta:
        model = JobApplication
        # Cover letter removed from the flow — resume-only application.
        fields = ['resume']



class MessageForm(forms.ModelForm):
    # FIX 4: support optional file attachment
    attachment = forms.FileField(required=False, widget=forms.FileInput(attrs={
        'accept': 'image/*,video/*,.pdf,.doc,.docx,.txt,.zip',
        'style': 'display:none;',
        'id': 'msg-attachment-input',
    }))

    class Meta:
        model = Message
        fields = ['content', 'attachment']
        widgets = {
            'content': forms.TextInput(attrs={'placeholder': 'Write a message…', 'autocomplete': 'off'}),
        }

    def clean(self):
        cleaned = super().clean()
        content = cleaned.get('content', '').strip()
        attachment = cleaned.get('attachment')
        if not content and not attachment:
            raise forms.ValidationError('Please enter a message or attach a file.')
        return cleaned


class BackgroundForm(forms.ModelForm):
    bg_opacity = forms.FloatField(
        min_value=0.0,
        max_value=1.0,
        widget=forms.NumberInput(attrs={
            'type': 'range',
            'min': '0',
            'max': '1',
            'step': '0.05',
            'class': 'form-range',
            'id': 'bg-opacity-slider',
        }),
        label='Background opacity',
        initial=0.5,
    )
    # FIX 6: position + zoom controls
    bg_position_x = forms.FloatField(
        min_value=0, max_value=100,
        widget=forms.NumberInput(attrs={
            'type': 'range', 'min': '0', 'max': '100', 'step': '1',
            'class': 'form-range', 'id': 'bg-pos-x-slider',
        }),
        label='Horizontal position',
        initial=50,
    )
    bg_position_y = forms.FloatField(
        min_value=0, max_value=100,
        widget=forms.NumberInput(attrs={
            'type': 'range', 'min': '0', 'max': '100', 'step': '1',
            'class': 'form-range', 'id': 'bg-pos-y-slider',
        }),
        label='Vertical position',
        initial=50,
    )
    bg_zoom = forms.FloatField(
        min_value=50, max_value=300,
        widget=forms.NumberInput(attrs={
            'type': 'range', 'min': '50', 'max': '300', 'step': '5',
            'class': 'form-range', 'id': 'bg-zoom-slider',
        }),
        label='Zoom / size',
        initial=100,
    )

    class Meta:
        model = Profile
        fields = ['bg_image', 'bg_opacity', 'bg_fit', 'bg_position_x', 'bg_position_y', 'bg_zoom']
        widgets = {
            'bg_fit': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'bg_image': 'Background image',
            'bg_fit': 'Image fit / position',
        }
