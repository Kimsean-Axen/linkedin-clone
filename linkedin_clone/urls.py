from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from linkedin_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('verify-email/', views.verify_email, name='verify_email'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    path('profile/setup/<str:step>/', views.profile_setup, name='profile_setup'),

    path('feed/', views.feed, name='feed'),
    path('feed/create/', views.create_post, name='create_post'),

    path('profile/<int:user_id>/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/add-section/', views.profile_add_section, name='profile_add_section'),
    path('profile/update-contact/', views.profile_update_contact, name='profile_update_contact'),
    path('profile/delete-picture/', views.delete_profile_picture, name='delete_profile_picture'),
    path('profile/delete-cover/', views.delete_cover_photo, name='delete_cover_photo'),
    path('profile/experience/<int:exp_id>/delete/', views.delete_experience, name='delete_experience'),
    path('profile/education/<int:edu_id>/delete/', views.delete_education, name='delete_education'),
    path('profile/skill/<int:skill_id>/delete/', views.delete_skill, name='delete_skill'),

    path('post/<int:post_id>/like/', views.like_post, name='like_post'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('post/<int:post_id>/edit/', views.edit_post, name='edit_post'),

    path('connections/', views.connections, name='connections'),
    path('connect/<int:user_id>/', views.send_connection, name='send_connection'),
    path('connection/<int:request_id>/accept/', views.accept_connection, name='accept_connection'),
    path('connection/<int:request_id>/decline/', views.decline_connection, name='decline_connection'),

    path('jobs/', views.jobs, name='jobs'),
    path('jobs/mine/', views.my_jobs, name='my_jobs'),
    path('jobs/create/', views.create_job, name='create_job'),
    path('jobs/<int:job_id>/', views.job_detail, name='job_detail'),
    path('jobs/<int:job_id>/apply/', views.apply_job, name='apply_job'),
    path('jobs/<int:job_id>/delete/', views.delete_job, name='delete_job'),

    path('messages/', views.messages_list, name='messages_list'),
    path('messages/new/', views.new_message, name='new_message'),
    path('messages/<int:user_id>/', views.conversation, name='conversation'),
    path('messages/send/<int:user_id>/', views.send_message, name='send_message'),

    path('search/', views.search, name='search'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:notif_id>/delete/', views.delete_notification, name='delete_notification'),

    path('background/edit/', views.background_edit, name='background_edit'),
    path('toggle-dark-mode/', views.toggle_dark_mode, name='toggle_dark_mode'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
