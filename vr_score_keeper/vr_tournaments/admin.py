from django.contrib import admin
from django.db.models import Count
from .models import Tournament, Player, Match, Score


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for the Tournament model.
    Displays tournament name, date, winner, and player count.
    """

    list_display = ("name", "date", "winner", "get_player_count")
    search_fields = ("name",)
    list_filter = ("date",)

    def get_queryset(self, request):
        """
        Annotates the queryset with the player count for each tournament.
        """
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(player_count=Count("players"))
        return queryset

    def get_player_count(self, obj):
        """
        Returns the number of players in the tournament.
        """
        return obj.player_count

    get_player_count.short_description = "Player Count"
    get_player_count.admin_order_field = "player_count"


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for the Player model.
    Displays player name and the tournaments they are part of.
    """

    list_display = ("name", "get_tournaments")
    search_fields = ("name",)

    def get_queryset(self, request):
        """
        Prefetches related tournaments for each player.
        """
        queryset = super().get_queryset(request)
        queryset = queryset.prefetch_related("tournaments")
        return queryset

    def get_tournaments(self, obj):
        """
        Returns a comma-separated string of tournament names the player is part of.
        """
        return ", ".join([t.name for t in obj.tournaments.all()])

    get_tournaments.short_description = "Tournaments"


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for the Match model.
    Displays match string, tournament, date, and participating players.
    """

    list_display = ("id", "tournament", "date", "get_players")
    list_filter = (
        "tournament",
        "date",
    )

    def get_queryset(self, request):
        """
        Selects related tournament and prefetches related scores and players for each match.
        """
        queryset = super().get_queryset(request)
        queryset = queryset.select_related("tournament").prefetch_related(
            "scores__player"
        )
        return queryset

    def get_players(self, obj):
        """
        Returns a comma-separated string of player names who participated in the match.
        """
        return ", ".join([score.player.name for score in obj.scores.all()])

    get_players.short_description = "Players"


@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for the Score model.
    Displays player, match, and score.
    """

    list_display = ("player", "match", "score")
    list_filter = ("match__tournament", "player")

    def get_queryset(self, request):
        """
        Selects related player and tournament for each score.
        """
        queryset = super().get_queryset(request)
        queryset = queryset.select_related("player", "match__tournament")
        return queryset
