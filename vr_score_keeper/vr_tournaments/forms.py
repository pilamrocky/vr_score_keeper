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
        self.fields["points_to_win"].initial = 0


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
            self.fields[f"score_{player.pk}"] = forms.IntegerField(
                label=player.name,
                initial=0,
                min_value=0,
            )

    def save(self):
        scores_data = self.cleaned_data
        scores = []
        for player in self.registered_players:
            points = scores_data.get(f"score_{player.pk}", 0)
            score, created = Score.objects.update_or_create(
                match=self.match, player_id=player.pk, defaults={"score": points}
            )
            scores.append(score)
        return scores
