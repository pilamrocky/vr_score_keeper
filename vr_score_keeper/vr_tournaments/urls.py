from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("players/", views.players, name="players"),
    path("tournaments/", views.tournaments, name="tournaments"),
    path("tournament/<pk>/", views.tournament_detail, name="tournament_detail"),
    path(
        "tournament/registration/<pk>/",
        views.tournament_registration,
        name="tournament_registration",
    ),
    path("create_tournament/", views.create_tournament, name="create_tournament"),
    path("create_match/<tournament_pk>/", views.create_match, name="create_match"),
    path("create_score/<match_pk>/", views.create_score, name="create_score"),
    path("delete_tournament/<pk>/", views.delete_tournament, name="delete_tournament"),
    path("delete_player/<pk>/", views.delete_player, name="delete_player"),
    path("delete_match/<pk>/", views.delete_match, name="delete_match"),
    path("profile/", views.profile, name="profile"),
    path("profile/edit/", views.profile_edit, name="profile_edit"),
]
