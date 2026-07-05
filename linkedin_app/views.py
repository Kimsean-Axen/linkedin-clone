import logging
import random
import string
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings as django_settings
from django.db import models
from django.db.models import Q
from django.utils import timezone
from .models import (Profile, Post, Like, Comment, Connection, Job,
                     JobApplication, Message, Notification, Experience,
                     Education, Skill, EmailVerification, ProfileLink,
                     JobContactLink)
from .forms import (RegisterForm, LoginForm, ProfileForm, UserUpdateForm,
                    PostForm, CommentForm, JobForm, JobApplicationForm,
                    MessageForm, ExperienceForm, EducationForm, SkillForm,
                    ContactInfoForm, BackgroundForm)

logger = logging.getLogger(__name__)


# ── Helpers ──────────────────────────────────────────────────────────────────

def _generate_code():
    return ''.join(random.choices(string.digits, k=6))


def _send_verification_email(user, code):
    subject = 'Your LinkedIn Clone verification code'
    body = (
        f'Hi {user.first_name},\n\n'
        f'Your email verification code is:\n\n'
        f'    {code}\n\n'
        f'This code expires in 15 minutes.\n\n'
        f'If you did not create an account, you can ignore this email.\n\n'
        f'— LinkedIn Clone'
    )
    logger.info('Attempting to send verification email to %s via %s',
                user.email, django_settings.EMAIL_BACKEND)
    send_mail(
        subject,
        body,
        django_settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )
    logger.info('Verification email sent successfully to %s', user.email)


def _get_connected_ids(user):
    """Return a set of user IDs the given user is connected to (not including self)."""
    rows = Connection.objects.filter(
        Q(sender=user) | Q(receiver=user), status='accepted'
    ).values_list('sender_id', 'receiver_id')
    ids = set()
    for s, r in rows:
        ids.add(s)
        ids.add(r)
    ids.discard(user.id)
    return ids


def _get_pending_sent_ids(user):
    """Return a set of user IDs to whom the user has a pending outgoing request."""
    return set(Connection.objects.filter(sender=user, status='pending').values_list('receiver_id', flat=True))


def _posts_visible_to(viewer, base_qs=None):
    if base_qs is None:
        base_qs = Post.objects.all()
    connected_ids = _get_connected_ids(viewer)
    return base_qs.filter(
        Q(author=viewer) |
        Q(visibility=Post.VISIBILITY_PUBLIC) |
        Q(visibility=Post.VISIBILITY_CONNECTIONS, author__in=connected_ids) |
        Q(visibility=Post.VISIBILITY_SPECIFIC, allowed_viewers=viewer)
    ).distinct()


# ── Auth ─────────────────────────────────────────────────────────────────────

def home(request):
    if request.user.is_authenticated:
        return redirect('feed')
    return render(request, 'home.html')


def register(request):
    if request.user.is_authenticated:
        return redirect('feed')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            code = _generate_code()

            request.session['pending_signup'] = {
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'password': user.password,
                'code': code,
                'created_at': timezone.now().isoformat(),
            }

            try:
                _send_verification_email(user, code)
            except Exception as exc:
                logger.error(
                    'Failed to send verification email to %s: %s',
                    user.email, exc, exc_info=True
                )
                messages.warning(
                    request,
                    'Could not send the verification email — check the server '
                    'terminal for the code and any error details.'
                )

            return redirect('verify_email')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})


def verify_email(request):
    pending = request.session.get('pending_signup')
    if not pending:
        messages.error(request, 'No pending verification. Please register first.')
        return redirect('register')

    email = pending['email']

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'resend':
            code = _generate_code()
            pending['code'] = code
            pending['created_at'] = timezone.now().isoformat()
            request.session['pending_signup'] = pending
            request.session.modified = True

            class _TempUser:
                pass
            temp_user = _TempUser()
            temp_user.email = pending['email']
            temp_user.first_name = pending['first_name']

            try:
                _send_verification_email(temp_user, code)
                messages.success(request, 'A new verification code has been sent.')
            except Exception as exc:
                logger.error('Resend failed for %s: %s', email, exc, exc_info=True)
                messages.warning(request, 'Could not send email — check the server terminal for the code.')
            return redirect('verify_email')

        entered = request.POST.get('code', '').strip()
        created_at = timezone.datetime.fromisoformat(pending['created_at'])
        if timezone.now() > created_at + timezone.timedelta(minutes=15):
            messages.error(
                request,
                'This code has expired (valid for 15 minutes). '
                'Click "Resend code" to get a new one.'
            )
            return redirect('verify_email')

        if entered != pending['code']:
            messages.error(request, 'Incorrect code. Please try again.')
            return redirect('verify_email')

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, 'An account with this email already exists. Please sign in.')
            del request.session['pending_signup']
            return redirect('login')

        user = User.objects.create(
            username=pending['username'],
            email=pending['email'],
            first_name=pending['first_name'],
            last_name=pending['last_name'],
            password=pending['password'],
            is_active=True,
        )
        Profile.objects.get_or_create(user=user)
        del request.session['pending_signup']

        login(request, user)
        messages.success(request, f'Welcome to LinkedIn Clone, {user.first_name}! Your email is verified.')
        request.session['profile_setup_new_user'] = True
        return redirect('profile_setup', step='profile_pic')

    return render(request, 'registration/verify_email.html', {'email': email})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('feed')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                db_user = User.objects.get(email=email)
                if not db_user.is_active:
                    request.session['verify_email'] = email
                    messages.warning(
                        request,
                        'Please verify your email before logging in.'
                    )
                    return redirect('verify_email')
                user = authenticate(request, username=db_user.username, password=password)
                if user:
                    login(request, user)
                    return redirect('feed')
                else:
                    messages.error(request, 'Invalid email or password.')
            except User.DoesNotExist:
                messages.error(request, 'No account found with that email.')
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})


@login_required
def user_logout(request):
    logout(request)
    return redirect('login')


# ── Profile Setup Wizard (simplified to 2 steps) ────────────────────────────

SETUP_STEPS = ['profile_pic', 'cover_photo']
STEP_LABELS = {
    'profile_pic': 'Profile Picture',
    'cover_photo': 'Cover Photo',
}


@login_required
def profile_setup(request, step):
    if not request.session.get('profile_setup_new_user'):
        return redirect('feed')

    if step not in SETUP_STEPS:
        return redirect('profile_setup', step='profile_pic')

    user_profile, _ = Profile.objects.get_or_create(user=request.user)
    step_index = SETUP_STEPS.index(step)
    total = len(SETUP_STEPS)

    def finish():
        if 'profile_setup_new_user' in request.session:
            del request.session['profile_setup_new_user']
        messages.success(request, 'Profile set up! Welcome to LinkedIn Clone.')
        return redirect('feed')

    if step == 'profile_pic':
        if request.method == 'POST':
            if 'skip' in request.POST:
                return redirect('profile_setup', step='cover_photo')
            profile_form = ProfileForm(request.POST, request.FILES, instance=user_profile,
                                       fields_only=['profile_picture'])
            if profile_form.is_valid():
                profile_form.save()
                return redirect('profile_setup', step='cover_photo')
        else:
            profile_form = ProfileForm(instance=user_profile, fields_only=['profile_picture'])
        ctx = {'profile_form': profile_form}

    elif step == 'cover_photo':
        if request.method == 'POST':
            if 'skip' in request.POST or 'finish' in request.POST:
                return finish()
            profile_form = ProfileForm(request.POST, request.FILES, instance=user_profile,
                                       fields_only=['cover_photo'])
            if profile_form.is_valid():
                profile_form.save()
                return finish()
        else:
            profile_form = ProfileForm(instance=user_profile, fields_only=['cover_photo'])
        ctx = {'profile_form': profile_form}
    else:
        ctx = {}

    ctx.update({
        'step': step,
        'step_index': step_index + 1,
        'total_steps': total,
        'step_label': STEP_LABELS[step],
        'steps': SETUP_STEPS,
        'step_labels': STEP_LABELS,
        'is_last_step': step_index == total - 1,
    })
    return render(request, 'profiles/profile_setup.html', ctx)


# ── Feed ────────────────────────────────────────────────────────────────────

@login_required
def feed(request):
    user = request.user
    connected_ids = _get_connected_ids(user)
    pending_sent_ids = _get_pending_sent_ids(user)

    posts = Post.objects.filter(
        author__in=connected_ids
    ).filter(
        Q(visibility=Post.VISIBILITY_PUBLIC) |
        Q(visibility=Post.VISIBILITY_CONNECTIONS) |
        Q(visibility=Post.VISIBILITY_SPECIFIC, allowed_viewers=user)
    ).distinct().select_related(
        'author', 'author__profile'
    ).prefetch_related('likes', 'comments', 'comments__author__profile')

    liked_post_ids = Like.objects.filter(user=user).values_list('post_id', flat=True)
    people_you_may_know = User.objects.exclude(
        id__in=connected_ids
    ).exclude(id=user.id).select_related('profile')[:5]

    return render(request, 'feed/feed.html', {
        'posts': posts,
        'liked_post_ids': list(liked_post_ids),
        'people_you_may_know': people_you_may_know,
        'connected_ids': connected_ids,
        'pending_sent_ids': pending_sent_ids,
    })


def _build_post_form(request, instance=None):
    connected_ids = _get_connected_ids(request.user)
    connections = User.objects.filter(id__in=connected_ids).order_by('first_name', 'last_name')
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=instance)
    else:
        form = PostForm(instance=instance)
    form.fields['allowed_viewers'].queryset = connections
    return form, connections


@login_required
def create_post(request):
    form, connections = _build_post_form(request)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        form.save_m2m()
        if post.visibility != Post.VISIBILITY_SPECIFIC:
            post.allowed_viewers.clear()
        messages.success(request, 'Post created!')
        return redirect('feed')
    return render(request, 'feed/create_post.html', {'form': form, 'connections': connections})


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    form, connections = _build_post_form(request, instance=post)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.save()
        form.save_m2m()
        if post.visibility != Post.VISIBILITY_SPECIFIC:
            post.allowed_viewers.clear()
        messages.success(request, 'Post updated.')
        return redirect('profile', user_id=request.user.id)
    return render(request, 'feed/edit_post.html', {'form': form, 'post': post, 'connections': connections})


@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()
    elif post.author != request.user:
        Notification.objects.create(
            recipient=post.author,
            sender=request.user,
            notification_type='like',
            message=f'{request.user.get_full_name() or request.user.username} liked your post.',
            link=f'/profile/{post.author.id}/?post={post.id}'
        )
    return redirect(request.META.get('HTTP_REFERER', 'feed'))


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            if post.author != request.user:
                Notification.objects.create(
                    recipient=post.author,
                    sender=request.user,
                    notification_type='comment',
                    message=f'{request.user.get_full_name() or request.user.username} commented on your post.',
                    link=f'/profile/{post.author.id}/?post={post.id}'
                )
    return redirect(request.META.get('HTTP_REFERER', 'feed'))


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    post.delete()
    messages.success(request, 'Post deleted.')
    referer = request.META.get('HTTP_REFERER', '')
    if f'/profile/{request.user.id}/' in referer:
        return redirect('profile', user_id=request.user.id)
    return redirect('feed')


# ── Profile ──────────────────────────────────────────────────────────────────

@login_required
def profile(request, user_id):
    profile_user = get_object_or_404(User, id=user_id)
    user_profile, _ = Profile.objects.get_or_create(user=profile_user)

    connection_status = None
    connection_obj = None
    is_owner = (request.user == profile_user)
    has_accepted_connection = False

    if not is_owner:
        try:
            conn = Connection.objects.get(
                Q(sender=request.user, receiver=profile_user) |
                Q(sender=profile_user, receiver=request.user)
            )
            connection_status = conn.status
            connection_obj = conn
            has_accepted_connection = conn.status == 'accepted'
        except Connection.DoesNotExist:
            connection_status = 'none'

    can_view_contact = is_owner or has_accepted_connection

    if is_owner:
        posts = Post.objects.filter(author=profile_user).select_related('author')
    else:
        vis_q = Q(visibility=Post.VISIBILITY_PUBLIC)
        if has_accepted_connection:
            vis_q |= Q(visibility=Post.VISIBILITY_CONNECTIONS)
        vis_q |= Q(visibility=Post.VISIBILITY_SPECIFIC, allowed_viewers=request.user)
        posts = Post.objects.filter(author=profile_user).filter(vis_q).distinct().select_related('author')

    liked_post_ids = Like.objects.filter(user=request.user).values_list('post_id', flat=True)

    exp_form = ExperienceForm()
    edu_form = EducationForm()
    skill_form = SkillForm()
    contact_form = ContactInfoForm(instance=user_profile) if is_owner else None

    return render(request, 'profiles/profile.html', {
        'profile_user': profile_user,
        'user_profile': user_profile,
        'posts': posts,
        'liked_post_ids': list(liked_post_ids),
        'connection_status': connection_status,
        'connection_obj': connection_obj,
        'can_view_contact': can_view_contact,
        'is_owner': is_owner,
        'exp_form': exp_form,
        'edu_form': edu_form,
        'skill_form': skill_form,
        'contact_form': contact_form,
    })


@login_required
def edit_profile(request):
    user_profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=user_profile)

        # Single consolidated save: basic info + optional new experience/education/skill
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()

            # Replace all profile links
            labels = request.POST.getlist('link_label')
            urls = request.POST.getlist('link_url')
            user_profile.links.all().delete()
            for lab, u in zip(labels, urls):
                lab = (lab or '').strip()
                u = (u or '').strip()
                if u:
                    ProfileLink.objects.create(profile=user_profile, label=lab or 'Link', url=u)

            # Optional new experience
            exp_title = (request.POST.get('exp_title') or '').strip()
            exp_company = (request.POST.get('exp_company') or '').strip()
            exp_start = (request.POST.get('exp_start_date') or '').strip()
            if exp_title and exp_company and exp_start:
                try:
                    Experience.objects.create(
                        profile=user_profile,
                        title=exp_title,
                        company=exp_company,
                        location=(request.POST.get('exp_location') or '').strip(),
                        start_date=exp_start,
                        end_date=(request.POST.get('exp_end_date') or None) or None,
                        current=bool(request.POST.get('exp_current')),
                        description=(request.POST.get('exp_description') or '').strip(),
                    )
                except Exception:
                    pass

            # Optional new education
            edu_school = (request.POST.get('edu_school') or '').strip()
            edu_degree = (request.POST.get('edu_degree') or '').strip()
            edu_start_year = (request.POST.get('edu_start_year') or '').strip()
            if edu_school and edu_degree and edu_start_year:
                try:
                    Education.objects.create(
                        profile=user_profile,
                        school=edu_school,
                        degree=edu_degree,
                        field_of_study=(request.POST.get('edu_field_of_study') or '').strip(),
                        start_year=int(edu_start_year),
                        end_year=int(request.POST.get('edu_end_year')) if (request.POST.get('edu_end_year') or '').strip() else None,
                    )
                except Exception:
                    pass

            # Optional new skill(s): comma-separated
            new_skill = (request.POST.get('new_skill') or '').strip()
            if new_skill:
                for name in [s.strip() for s in new_skill.split(',') if s.strip()]:
                    Skill.objects.get_or_create(profile=user_profile, name=name)

            messages.success(request, 'Profile updated!')
            return redirect('profile', user_id=request.user.id)
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileForm(instance=user_profile)

    exp_form = ExperienceForm()
    edu_form = EducationForm()
    skill_form = SkillForm()

    return render(request, 'profiles/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'exp_form': exp_form,
        'edu_form': edu_form,
        'skill_form': skill_form,
        'experiences': user_profile.experiences.all(),
        'educations': user_profile.educations.all(),
        'skills': user_profile.skills.all(),
        'user_profile': user_profile,
        'profile_links': user_profile.links.all(),
    })




@login_required
def profile_add_section(request):
    user_profile, _ = Profile.objects.get_or_create(user=request.user)
    section = request.POST.get('section_type', '')

    if section == 'experience':
        form = ExperienceForm(request.POST)
        if form.is_valid():
            exp = form.save(commit=False)
            exp.profile = user_profile
            exp.save()
            messages.success(request, 'Experience added!')
    elif section == 'education':
        form = EducationForm(request.POST)
        if form.is_valid():
            edu = form.save(commit=False)
            edu.profile = user_profile
            edu.save()
            messages.success(request, 'Education added!')
    elif section == 'skill':
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.profile = user_profile
            skill.save()
            messages.success(request, 'Skill added!')

    return redirect('profile', user_id=request.user.id)


@login_required
def profile_update_contact(request):
    user_profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ContactInfoForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contact info updated!')
    return redirect('profile', user_id=request.user.id)


@login_required
def delete_profile_picture(request):
    if request.method == 'POST':
        prof = request.user.profile
        if prof.profile_picture:
            prof.profile_picture.delete(save=True)
        messages.success(request, 'Profile picture removed.')
    return redirect('edit_profile')


@login_required
def delete_cover_photo(request):
    if request.method == 'POST':
        prof = request.user.profile
        if prof.cover_photo:
            prof.cover_photo.delete(save=True)
        messages.success(request, 'Cover photo removed.')
    return redirect('edit_profile')


@login_required
def delete_experience(request, exp_id):
    exp = get_object_or_404(Experience, id=exp_id, profile__user=request.user)
    exp.delete()
    messages.success(request, 'Experience removed.')
    return redirect('profile', user_id=request.user.id)


@login_required
def delete_education(request, edu_id):
    edu = get_object_or_404(Education, id=edu_id, profile__user=request.user)
    edu.delete()
    messages.success(request, 'Education removed.')
    return redirect('profile', user_id=request.user.id)


@login_required
def delete_skill(request, skill_id):
    skill = get_object_or_404(Skill, id=skill_id, profile__user=request.user)
    skill.delete()
    messages.success(request, 'Skill removed.')
    return redirect('profile', user_id=request.user.id)


# ── Connections ──────────────────────────────────────────────────────────────

@login_required
def connections(request):
    user = request.user
    accepted = Connection.objects.filter(
        Q(sender=user) | Q(receiver=user), status='accepted'
    ).select_related('sender__profile', 'receiver__profile')

    pending_received = Connection.objects.filter(receiver=user, status='pending').select_related('sender__profile')
    pending_sent = Connection.objects.filter(sender=user, status='pending').select_related('receiver__profile')

    connected_ids = set()
    for c in accepted:
        connected_ids.add(c.sender_id)
        connected_ids.add(c.receiver_id)
    connected_ids.discard(user.id)

    pending_ids = set()
    for c in pending_sent:
        pending_ids.add(c.receiver_id)

    suggestions = User.objects.exclude(
        id__in=connected_ids | pending_ids | {user.id}
    ).select_related('profile')[:10]

    return render(request, 'connections/connections.html', {
        'accepted': accepted,
        'pending_received': pending_received,
        'pending_sent': pending_sent,
        'suggestions': suggestions,
    })


@login_required
def send_connection(request, user_id):
    receiver = get_object_or_404(User, id=user_id)
    if receiver != request.user:
        conn, created = Connection.objects.get_or_create(
            sender=request.user, receiver=receiver,
            defaults={'status': 'pending'}
        )
        if created:
            Notification.objects.create(
                recipient=receiver,
                sender=request.user,
                notification_type='connection',
                message=f'{request.user.get_full_name() or request.user.username} sent you a connection request.',
                link='/connections/'
            )
            messages.success(request, f'Connection request sent to {receiver.get_full_name() or receiver.username}.')
        else:
            messages.info(request, 'Connection request already sent.')
    return redirect(request.META.get('HTTP_REFERER', 'connections'))


@login_required
def accept_connection(request, request_id):
    conn = get_object_or_404(Connection, id=request_id, receiver=request.user)
    conn.status = 'accepted'
    conn.save()
    Notification.objects.create(
        recipient=conn.sender,
        sender=request.user,
        notification_type='connection_accepted',
        message=f'{request.user.get_full_name() or request.user.username} accepted your connection request.',
        link=f'/profile/{request.user.id}/'
    )
    messages.success(request, f'Connected with {conn.sender.get_full_name() or conn.sender.username}!')
    return redirect('connections')


@login_required
def decline_connection(request, request_id):
    conn = get_object_or_404(Connection, id=request_id, receiver=request.user)
    conn.status = 'declined'
    conn.save()
    return redirect('connections')


# ── Jobs ─────────────────────────────────────────────────────────────────────

@login_required
def jobs(request):
    job_types = request.GET.getlist('job_type')
    experience_levels = request.GET.getlist('experience_level')
    query = request.GET.get('q', '').strip()

    # Main listing excludes the current user's own jobs.
    job_list = Job.objects.filter(is_active=True).exclude(
        poster=request.user
    ).select_related('poster__profile')

    if query:
        job_list = job_list.filter(
            Q(title__icontains=query) |
            Q(company__icontains=query) |
            Q(location__icontains=query)
        )
    if job_types:
        q_type = Q(job_type__in=job_types)
        for jt in job_types:
            q_type |= Q(job_types__contains=jt)
        job_list = job_list.filter(q_type)
    if experience_levels:
        q_exp = Q(experience_level__in=experience_levels)
        for el in experience_levels:
            q_exp |= Q(experience_levels__contains=el)
        job_list = job_list.filter(q_exp)

    applied_job_ids = JobApplication.objects.filter(applicant=request.user).values_list('job_id', flat=True)
    my_jobs_count = Job.objects.filter(poster=request.user, is_active=True).count()

    return render(request, 'jobs/jobs.html', {
        'jobs': job_list,
        'applied_job_ids': list(applied_job_ids),
        'job_types': job_types,
        'experience_levels': experience_levels,
        'query': query,
        'job_type_choices': Job.JOB_TYPE_CHOICES,
        'experience_choices': Job.EXPERIENCE_CHOICES,
        'current_user': request.user,
        'my_jobs_count': my_jobs_count,
        'keyword_suggestions': [
            'Software Engineer', 'Product Manager', 'Data Scientist',
            'Designer', 'Marketing', 'Remote', 'Sales', 'Finance',
            'Operations', 'Recruiter',
        ],
    })


@login_required
def my_jobs(request):
    """Jobs the current user has posted — separate section."""
    job_list = Job.objects.filter(poster=request.user).select_related('poster__profile')
    return render(request, 'jobs/my_jobs.html', {'jobs': job_list})




@login_required
def create_job(request):
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.poster = request.user
            selected_types = request.POST.getlist('job_types')
            selected_levels = request.POST.getlist('experience_levels')
            job.job_types = ','.join(selected_types)
            job.experience_levels = ','.join(selected_levels)
            job.job_type = selected_types[0] if selected_types else 'full_time'
            job.experience_level = selected_levels[0] if selected_levels else 'mid'
            job.save()
            # Save multiple contact links (label + url pairs)
            labels = request.POST.getlist('contact_link_label')
            urls = request.POST.getlist('contact_link_url')
            for lab, u in zip(labels, urls):
                lab = (lab or '').strip()
                u = (u or '').strip()
                if u:
                    JobContactLink.objects.create(job=job, label=lab or 'Contact', url=u)
            messages.success(request, 'Job posted successfully!')
            return redirect('jobs')
    else:
        form = JobForm()
    return render(request, 'jobs/create_job.html', {
        'form': form,
        'job_type_choices': Job.JOB_TYPE_CHOICES,
        'experience_choices': Job.EXPERIENCE_CHOICES,
    })



@login_required
def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    user_application = JobApplication.objects.filter(job=job, applicant=request.user).first()
    has_applied = user_application is not None
    is_poster = (job.poster == request.user)
    # Job poster sees applicants list (with resumes)
    applicants = job.applications.select_related('applicant__profile').order_by('-applied_at') if is_poster else None
    return render(request, 'jobs/job_detail.html', {
        'job': job,
        'has_applied': has_applied,
        'is_poster': is_poster,
        'user_application': user_application,
        'applicants': applicants,
    })


@login_required
def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    if request.method == 'POST':
        existing = JobApplication.objects.filter(job=job, applicant=request.user).first()
        form = JobApplicationForm(request.POST, request.FILES,
                                  instance=existing if existing else None)
        if form.is_valid():
            app = form.save(commit=False)
            app.job = job
            app.applicant = request.user
            app.save()
            if not existing:
                Notification.objects.create(
                    recipient=job.poster,
                    sender=request.user,
                    notification_type='job_application',
                    message=f'{request.user.get_full_name() or request.user.username} applied to your job: {job.title}.',
                    link=f'/jobs/{job.id}/'
                )
                messages.success(request, 'Application submitted!')
            else:
                messages.success(request, 'Application updated!')
    return redirect('job_detail', job_id=job_id)


@login_required
def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, poster=request.user)
    if request.method == 'POST':
        job.is_active = False
        job.save()
        messages.success(request, 'Job post deleted.')
        return redirect('jobs')
    return redirect('job_detail', job_id=job_id)


# ── Messaging ────────────────────────────────────────────────────────────────

@login_required
def messages_list(request):
    user = request.user
    sent = Message.objects.filter(sender=user).values_list('receiver_id', flat=True)
    received = Message.objects.filter(receiver=user).values_list('sender_id', flat=True)
    conversation_user_ids = set(list(sent) + list(received))
    conversation_users = User.objects.filter(id__in=conversation_user_ids).select_related('profile')

    convos = []
    for other_user in conversation_users:
        last_msg = Message.objects.filter(
            Q(sender=user, receiver=other_user) | Q(sender=other_user, receiver=user)
        ).last()
        unread = Message.objects.filter(sender=other_user, receiver=user, is_read=False).count()
        convos.append({'user': other_user, 'last_message': last_msg, 'unread': unread})

    convos.sort(key=lambda x: x['last_message'].created_at if x['last_message'] else 0, reverse=True)
    unread_msgs = Message.objects.filter(receiver=user, is_read=False).count()

    return render(request, 'messaging/messages_list.html', {
        'convos': convos,
        'unread_msgs': unread_msgs,
    })


@login_required
def new_message(request):
    """Pick a connection and jump into a conversation."""
    connected_ids = _get_connected_ids(request.user)
    connections = User.objects.filter(id__in=connected_ids).select_related('profile').order_by('first_name', 'last_name')
    q = request.GET.get('q', '').strip()
    if q:
        connections = connections.filter(
            Q(first_name__icontains=q) | Q(last_name__icontains=q)
        )
    return render(request, 'messaging/new_message.html', {
        'connections': connections,
        'query': q,
    })




@login_required
def conversation(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    user = request.user
    msgs = Message.objects.filter(
        Q(sender=user, receiver=other_user) | Q(sender=other_user, receiver=user)
    ).order_by('created_at')
    Message.objects.filter(sender=other_user, receiver=user, is_read=False).update(is_read=True)
    msg_form = MessageForm()
    # NOTE: variable is 'chat_messages' not 'messages' — avoids overriding Django's
    # flash-message context processor which also uses the name 'messages'.
    return render(request, 'messaging/conversation.html', {
        'other_user': other_user,
        'chat_messages': msgs,
        'msg_form': msg_form,
    })


@login_required
def send_message(request, user_id):
    # FIX 1: No flash messages added — prevent the stacking banner entirely
    # FIX 2: Duplicate-message guard: check for a recent identical message within 3s
    receiver = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            content = form.cleaned_data.get('content', '').strip()
            attachment = form.cleaned_data.get('attachment')

            # FIX 2: dedup — block exact-same text within a 3-second window
            if content:
                recent_cutoff = timezone.now() - timezone.timedelta(seconds=3)
                duplicate = Message.objects.filter(
                    sender=request.user,
                    receiver=receiver,
                    content=content,
                    created_at__gte=recent_cutoff
                ).exists()
                if duplicate:
                    return redirect('conversation', user_id=user_id)

            msg = Message(sender=request.user, receiver=receiver, content=content)
            # FIX 4: handle attachment
            if attachment:
                msg.attachment = attachment
                mime = attachment.content_type or ''
                if mime.startswith('image/'):
                    msg.attachment_type = 'image'
                elif mime.startswith('video/'):
                    msg.attachment_type = 'video'
                else:
                    msg.attachment_type = 'file'
            msg.save()

            # Only notify receiver once (not sender)
            Notification.objects.create(
                recipient=receiver,
                sender=request.user,
                notification_type='message',
                message=f'New message from {request.user.get_full_name() or request.user.username}.',
                link=f'/messages/{request.user.id}/'
            )
    return redirect('conversation', user_id=user_id)


# ── Search / Notifications ───────────────────────────────────────────────────

@login_required
def search(request):
    query = request.GET.get('q', '')
    users = []
    jobs_results = []
    connection_status_map = {}

    if query:
        # Fix: support full-name searches like "Kim Sean" (case-insensitive)
        q_filter = (
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(profile__headline__icontains=query)
        )
        parts = query.split()
        if len(parts) >= 2:
            q_filter |= Q(first_name__icontains=parts[0], last_name__icontains=parts[1])
            q_filter |= Q(first_name__icontains=parts[1], last_name__icontains=parts[0])

        users = list(User.objects.filter(q_filter).exclude(
            id=request.user.id
        ).distinct().select_related('profile')[:10])

        jobs_results = Job.objects.filter(
            Q(title__icontains=query) | Q(company__icontains=query)
        ).filter(is_active=True)[:10]

        # Build connection status map for button states
        connected_ids = _get_connected_ids(request.user)
        pending_sent_ids = _get_pending_sent_ids(request.user)
        for person in users:
            if person.id in connected_ids:
                connection_status_map[person.id] = 'connected'
            elif person.id in pending_sent_ids:
                connection_status_map[person.id] = 'pending'
            else:
                connection_status_map[person.id] = 'none'

    # Build a list of (person, conn_status) for the template
    users_with_status = []
    for person in users:
        status = connection_status_map.get(person.id, 'none')
        users_with_status.append({'person': person, 'conn_status': status})

    return render(request, 'search.html', {
        'query': query,
        'users_with_status': users_with_status,
        'jobs_results': jobs_results,
    })


@login_required
def notifications(request):
    user = request.user
    notifs = Notification.objects.filter(recipient=user).select_related('sender__profile')
    Notification.objects.filter(recipient=user, is_read=False).update(is_read=True)
    return render(request, 'notifications.html', {'notifs': notifs})


# ── Background & Dark Mode ───────────────────────────────────────────────────

@login_required
def background_edit(request):
    user_profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        if 'remove_bg' in request.POST:
            if user_profile.bg_image:
                user_profile.bg_image.delete(save=True)
            messages.success(request, 'Background image removed.')
            return redirect('background_edit')
        # FIX 5: delete old image file before saving new one to prevent stacking
        old_bg = user_profile.bg_image
        form = BackgroundForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            new_bg = request.FILES.get('bg_image')
            if new_bg and old_bg:
                # Remove old file from storage
                try:
                    if os.path.isfile(old_bg.path):
                        os.remove(old_bg.path)
                except Exception:
                    pass
            form.save()
            messages.success(request, 'Background updated successfully!')
            return redirect('background_edit')
    else:
        form = BackgroundForm(instance=user_profile)
    return render(request, 'background_edit.html', {
        'form': form,
        'user_profile': user_profile,
    })


@login_required
def toggle_dark_mode(request):
    if request.method == 'POST':
        user_profile, _ = Profile.objects.get_or_create(user=request.user)
        user_profile.dark_mode = not user_profile.dark_mode
        user_profile.save()
    return redirect(request.META.get('HTTP_REFERER', '/feed/'))


@login_required
def delete_notification(request, notif_id):
    if request.method == 'POST':
        Notification.objects.filter(id=notif_id, recipient=request.user).delete()
    return redirect(request.META.get('HTTP_REFERER', 'notifications'))
