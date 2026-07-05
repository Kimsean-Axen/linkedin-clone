from django.contrib import admin
from .models import (Profile, Experience, Education, Skill, Post, Like,
                     Comment, Connection, Job, JobApplication, Message, Notification)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'headline', 'location', 'created_at']
    search_fields = ['user__username', 'user__email', 'headline']

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['author', 'content', 'created_at']
    list_filter = ['created_at']

@admin.register(Connection)
class ConnectionAdmin(admin.ModelAdmin):
    list_display = ['sender', 'receiver', 'status', 'created_at']
    list_filter = ['status']

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'location', 'job_type', 'is_active', 'created_at']
    list_filter = ['job_type', 'experience_level', 'is_active']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'receiver', 'created_at', 'is_read']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'sender', 'notification_type', 'is_read', 'created_at']

admin.site.register(Experience)
admin.site.register(Education)
admin.site.register(Skill)
admin.site.register(Like)
admin.site.register(Comment)
admin.site.register(JobApplication)
