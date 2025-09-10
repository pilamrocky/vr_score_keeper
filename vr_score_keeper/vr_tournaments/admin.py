from django.contrib import admin
from .models import Tournament, Player, Match, Score

@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'winner')
    search_fields = ('name',)
    list_filter = ('date',)

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_tournaments')
    search_fields = ('name',)

    def get_tournaments(self, obj):
        return ", ".join([t.name for t in obj.tournaments.all()])
    get_tournaments.short_description = 'Tournaments'

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'tournament', 'date')
    list_filter = ('tournament', 'date',)

@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ('player', 'match', 'score')
    list_filter = ('match',)
