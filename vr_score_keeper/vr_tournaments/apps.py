from django.apps import AppConfig


class VrTournamentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'vr_tournaments'

    def ready(self):
        import vr_tournaments.receivers
