from django import forms
from django.core.exceptions import ValidationError
from .models import Tournament, Player, Match, Score

class TournamentForm(forms.ModelForm):
    class Meta:
        model = Tournament
        fields = ('date',)

class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ('name',)

    def clean_name(self):
        name = self.cleaned_data['name']
        if Player.objects.filter(name=name).exists():
            raise ValidationError('Player with this name already exists.')
        return name

class MatchForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ('tournament', 'date',)

class ScoreForm(forms.ModelForm):
    class Meta:
        model = Score
        fields = ('match', 'player', 'score',)