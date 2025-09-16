from django.contrib import admin
from django.db.models import Count
from .models import Tournament, Player, Match, Score

@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'winner', 'get_player_count')
    search_fields = ('name',)
    list_filter = ('date',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(player_count=Count('players'))
        return queryset

    def get_player_count(self, obj):
        return obj.player_count
    get_player_count.short_description = 'Player Count'
    get_player_count.admin_order_field = 'player_count'

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_tournaments')
    search_fields = ('name',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.prefetch_related('tournaments')
        return queryset

    def get_tournaments(self, obj):
        return ", ".join([t.name for t in obj.tournaments.all()])
    get_tournaments.short_description = 'Tournaments'

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'tournament', 'date', 'get_players')
    list_filter = ('tournament', 'date',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related(
            'tournament'
        ).prefetch_related('scores__player')
        return queryset

    def get_players(self, obj):
        return ", ".join([score.player.name for score in obj.scores.all()])
    get_players.short_description = 'Players'

@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ('player', 'match', 'score')
    list_filter = ('match__tournament', 'player')
