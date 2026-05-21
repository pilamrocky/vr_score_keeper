from django import template
from django.contrib.auth.models import Group

register = template.Library()


@register.filter(name="has_group")
def has_group(user, group_name):
    if user.is_superuser:
        return True
    return user.groups.filter(name=group_name).exists()


@register.filter(name="percentage")
def percentage(value, max_value):
    try:
        val = float(value)
        max_val = float(max_value)
        if max_val > 0:
            return min(100.0, max(0.0, (val / max_val) * 100))
        return 0
    except (ValueError, TypeError):
        return 0

