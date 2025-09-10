import logging
from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.dispatch import receiver

logger = logging.getLogger(__name__)

@receiver(user_logged_in)
def log_user_logged_in(sender, request, user, **kwargs):
    """
    Logs successful user logins.
    """
    logger.info(f"User '{user.username}' logged in successfully.")

@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    """
    Logs failed user login attempts.
    """
    logger.warning(f"Failed login attempt for username: '{credentials.get('username')}'.")
