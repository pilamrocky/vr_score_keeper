from django import forms
from django.contrib.auth.forms import PasswordChangeForm  # Keep existing forms
from django.contrib.auth.models import User  # Import User model
from django.core.exceptions import ValidationError
from .models import Tournament, Player, Match, Score


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TournamentForm(forms.ModelForm):
    class Meta:
        model = Tournament
        fields = (
            "name",
            "date",
            "points_to_win",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].initial = f"Tournament {Tournament.objects.count() + 1}"
        self.fields["points_to_win"].initial = 40


class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ("name",)

    def clean_name(self):
        name = self.cleaned_data["name"]
        if Player.objects.filter(name=name).exists():
            raise ValidationError("Player with this name already exists.")
        return name


class MatchForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = (
            "tournament",
            "date",
        )


class MultiScoreForm(forms.Form):
    def __init__(self, registered_players, match, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.registered_players = registered_players
        self.match = match
        for player in registered_players:
            self.fields[f"rank_{player.pk}"] = forms.IntegerField(label=player.name, initial=1)

    def save(self):
        ranks_data = self.cleaned_data
        
        player_ranks = []
        for player in self.registered_players:
            rank = ranks_data.get(f"rank_{player.pk}", 1)
            player_ranks.append((player.pk, rank))
            
        N = len(self.registered_players)
        scores = []
        
        for player_pk, rank in player_ranks:
            # Count how many players had a strictly better (lower) rank
            beat_me = sum(1 for p_pk, r in player_ranks if r < rank)
            points = max(0, N - beat_me)
            
            score, created = Score.objects.update_or_create(
                match=self.match, player_id=player_pk, defaults={"score": points}
            )
            scores.append(score)
            
        return scores
