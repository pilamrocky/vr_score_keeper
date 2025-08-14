from django.test import TestCase
from ..forms import TournamentForm, PlayerForm, MatchForm
from ..models import Tournament


class FormTests(TestCase):
    def test_tournament_form(self):
        form_data = {"name": "Test Tournament", "date": "2024-01-01"}
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
