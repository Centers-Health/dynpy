from django import template
from django.contrib.auth.models import AbstractUser
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def get_toasts_delay_time(message):
    """
    Returns the amount of time the toast stays open.
    Calculated by multiplying the number of words by 1/2 a second
    Minimum time of delay is 3 seconds.
    """
    message_str = str(message)
    word_count = len(message_str.split())
    delay = word_count * 500
    return delay if delay > 3000 else 3000


@register.filter
def user_display(user):
    if not isinstance(user, AbstractUser):
        return user
    return render_to_string(
        "dynpy_ui/includes/user_card.html",
        {"user": user, "placeholder": mark_safe('<i class="fa fa-user"></i>')},
    )
