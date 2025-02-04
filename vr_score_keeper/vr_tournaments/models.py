from datetime import datetime
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import models


class Tournament(models.Model):
    """
    Represents a single tournament with a date and an optional name.

    The name is automatically set to a string like "Tournament 1" if not set.
    """

    date = models.DateField(default=timezone.localdate)
    name = models.CharField(max_length=255, blank=True)

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = f"Tournament {Tournament.objects.count() + 1}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-date"]


class Player(models.Model):
    """
    Represents a single player.

    The player has a unique name and can be part of multiple tournaments.
    """

    name = models.CharField(max_length=255, unique=True)
    tournaments = models.ManyToManyField(Tournament, related_name="players")
    # Add any other relevant fields for the player

    def __str__(self):
        return str(self.name)


class Match(models.Model):
    """
    Represents a match in a tournament.

    The match has a reference to the tournament, a date, and any other relevant
    fields for the match.
    """

    tournament = models.ForeignKey(
        Tournament, on_delete=models.CASCADE, related_name="matches"
    )
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Match {self.id} - {self.tournament.name}"

    def clean(self):
        if self.date > datetime.now():
            raise ValidationError("Match date cannot be in the future")

    class Meta:
        ordering = ["-date"]


class Score(models.Model):
    """
    Represents a score for a player in a match.

    Each score is associated with a player and a match, and has a validation
    to ensure it is within the acceptable range based on the number of players
    in the tournament.
    """

    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="scores")
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="scores")
    score = models.IntegerField()

    def __str__(self):
        return f"{self.player.name} - {self.score}"

    def clean(self):
        max_score = self.match.tournament.players.count()
        if self.score < 0 or self.score > max_score:
            raise ValidationError(f"Score must be between 0 and {max_score}")
