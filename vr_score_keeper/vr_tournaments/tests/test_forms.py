from django.test import TestCase
from ..forms import TournamentForm, PlayerForm, MatchForm, MultiScoreForm
from ..models import Tournament, Player, Match, Score


class FormTests(TestCase):
    def test_tournament_form(self):
        form_data = {"name": "Test Tournament", "date": "2024-01-01", "points_to_win": 40}
        form = TournamentForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_player_form(self):
        form_data = {"name": "Test Player"}
        form = PlayerForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_match_form(self):
        tournament = Tournament.objects.create()
        form_data_with_date = {"tournament": tournament.pk, "date": "2024-01-01"}
        form = MatchForm(data=form_data_with_date)
        self.assertTrue(form.is_valid())

    def test_multi_score_form_scores_ties_by_leaderboard_rank(self):
        tournament = Tournament.objects.create()
        players = [
            Player.objects.create(name="Rocky"),
            Player.objects.create(name="Bubba"),
            Player.objects.create(name="Trejo"),
            Player.objects.create(name="Tweeter"),
        ]
        tournament.players.add(*players)
        match = Match.objects.create(tournament=tournament)
        form = MultiScoreForm(
            players,
            match,
            data={
                f"rank_{players[0].pk}": 1,
                f"rank_{players[1].pk}": 1,
                f"rank_{players[2].pk}": 3,
                f"rank_{players[3].pk}": 4,
            },
        )

        self.assertTrue(form.is_valid())
        form.save()

        scores = {
            score.player.name: score.score
            for score in Score.objects.filter(match=match).select_related("player")
        }
        self.assertEqual(scores["Rocky"], 4)
        self.assertEqual(scores["Bubba"], 4)
        self.assertEqual(scores["Trejo"], 2)
        self.assertEqual(scores["Tweeter"], 1)

    def test_multi_score_form_scores_na_as_zero_and_reduces_points_pool(self):
        tournament = Tournament.objects.create()
        players = [
            Player.objects.create(name="Rocky"),
            Player.objects.create(name="Bubba"),
            Player.objects.create(name="Trejo"),
            Player.objects.create(name="Tweeter"),
        ]
        tournament.players.add(*players)
        match = Match.objects.create(tournament=tournament)
        form = MultiScoreForm(
            players,
            match,
            data={
                f"rank_{players[0].pk}": 1,
                f"rank_{players[1].pk}": 2,
                f"rank_{players[2].pk}": 3,
                f"rank_{players[3].pk}": 0,
            },
        )

        self.assertTrue(form.is_valid())
        form.save()

        scores = {
            score.player.name: score.score
            for score in Score.objects.filter(match=match).select_related("player")
        }
        self.assertEqual(scores["Rocky"], 3)
        self.assertEqual(scores["Bubba"], 2)
        self.assertEqual(scores["Trejo"], 1)
        self.assertEqual(scores["Tweeter"], 0)

    def test_multi_score_form_rejects_rank_past_player_count(self):
        tournament = Tournament.objects.create()
        players = [
            Player.objects.create(name="Rocky"),
            Player.objects.create(name="Bubba"),
        ]
        tournament.players.add(*players)
        match = Match.objects.create(tournament=tournament)
        form = MultiScoreForm(
            players,
            match,
            data={
                f"rank_{players[0].pk}": 1,
                f"rank_{players[1].pk}": 3,
            },
        )

        self.assertFalse(form.is_valid())
