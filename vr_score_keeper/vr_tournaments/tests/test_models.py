from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from ..models import Tournament, Player, Match, Score


class TournamentModelTest(TestCase):
    def test_tournament_creation(self):
        tournament = Tournament.objects.create()
        self.assertIsNotNone(tournament)
        self.assertIn("Tournament", tournament.name)

    def test_tournament_str(self):
        tournament = Tournament.objects.create(name="Test Tournament")
        self.assertEqual(str(tournament), "Test Tournament")


class PlayerModelTest(TestCase):
    def test_player_creation(self):
        player = Player.objects.create(name="Test Player")
        self.assertEqual(player.name, "Test Player")

    def test_player_str(self):
        player = Player.objects.create(name="Test Player")
        self.assertEqual(str(player), "Test Player")


class MatchModelTest(TestCase):
    def setUp(self):
        self.tournament = Tournament.objects.create()

    def test_match_creation(self):
        match = Match.objects.create(tournament=self.tournament)
        self.assertEqual(match.tournament, self.tournament)

    def test_match_str(self):
        match = Match.objects.create(tournament=self.tournament)
        self.assertEqual(str(match), f"Match {match.id} - {self.tournament.name}")


class ScoreModelTest(TestCase):
    def setUp(self):
        self.tournament = Tournament.objects.create()
        self.player = Player.objects.create(name="Player 1")
        self.player2 = Player.objects.create(name="Player 2")
        self.tournament.players.add(self.player, self.player2)
        self.match = Match.objects.create(tournament=self.tournament)

    def test_score_creation(self):
        score = Score.objects.create(player=self.player, match=self.match, score=1)
        self.assertEqual(score.player, self.player)
        self.assertEqual(score.match, self.match)
        self.assertEqual(score.score, 1)

    def test_score_str(self):
        score = Score.objects.create(player=self.player, match=self.match, score=10)
        self.assertEqual(str(score), "Player 1 - 10")

    def test_score_validation(self):
        with self.assertRaises(ValidationError):
            score = Score(player=self.player, match=self.match, score=3)
            score.clean()

        with self.assertRaises(ValidationError):
            score = Score(player=self.player, match=self.match, score=-1)
            score.clean()

        score = Score(player=self.player, match=self.match, score=2)
        score.clean()  # This should not raise an error
