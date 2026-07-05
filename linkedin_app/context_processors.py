from .models import Connection, Message, Notification, Profile


def nav_badges(request):
    if not request.user.is_authenticated:
        return {}
    user = request.user
    pending_requests = Connection.objects.filter(receiver=user, status='pending').count()
    unread_messages = Message.objects.filter(receiver=user, is_read=False).count()
    unread_notifications = Notification.objects.filter(recipient=user, is_read=False).count()


    try:
        prof = user.profile
        dark_mode = prof.dark_mode
        bg_image = prof.bg_image
        bg_opacity = prof.bg_opacity
        bg_fit = prof.bg_fit
        bg_position_x = prof.bg_position_x
        bg_position_y = prof.bg_position_y
        bg_zoom = prof.bg_zoom
    except Profile.DoesNotExist:
        dark_mode = False
        bg_image = None
        bg_opacity = 0.5
        bg_fit = 'cover'
        bg_position_x = 50
        bg_position_y = 50
        bg_zoom = 100

    return {
        'pending_requests': pending_requests,
        'unread_messages': unread_messages,
        'unread_notifications': unread_notifications,
        'user_dark_mode': dark_mode,
        'user_bg_image': bg_image,
        'user_bg_opacity': bg_opacity,
        'user_bg_fit': bg_fit,
        'user_bg_position_x': bg_position_x,
        'user_bg_position_y': bg_position_y,
        'user_bg_zoom': bg_zoom,
    }
