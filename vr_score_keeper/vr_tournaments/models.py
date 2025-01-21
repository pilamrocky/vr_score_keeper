from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import models
from datetime import datetime

class Tournament(models.Model):
    date = models.DateField(default=timezone.localdate)
    # Add any other relevant fields for the tournament

    @property
    def name(self):
        return f"Tournament {self.id}"

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-date']

class Player(models.Model):
    name = models.CharField(max_length=255, unique=True)
    tournaments = models.ManyToManyField(Tournament, related_name='players')
    # Add any other relevant fields for the player

    def __str__(self):
        return self.name

class Match(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='matches')
    date = models.DateTimeField(default=timezone.now)
    # Add any other relevant fields for the match

    def __str__(self):
        return f"Match {self.id} - {self.tournament.name}"

    def clean(self):
        if self.date > datetime.now():
            raise ValidationError("Match date cannot be in the future")

    class Meta:
        ordering = ['-date']

class Score(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='scores')
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='scores')
    score = models.IntegerField()
    # Add any other relevant fields for the score

    def __str__(self):
        return f"{self.player.name} - {self.match.name} - {self.score}"

    def clean(self):
        max_score = self.match.tournament.players.count()
        if self.score < 0 or self.score > max_score:
            raise ValidationError(f"Score must be between 0 and {max_score}")