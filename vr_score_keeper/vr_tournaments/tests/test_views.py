from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from ..models import Tournament, Player, Match, Score


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            "user", "user@test.com", "password"
        )
        self.superuser = User.objects.create_superuser(
            "superuser", "superuser@test.com", "password"
        )
        self.tournament = Tournament.objects.create(name="Test Tournament")
        self.player = Player.objects.create(name="Test Player")

    def test_index_view(self):
        self.client.login(username="user", password="password")
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")

    def test_players_view_as_superuser(self):
        self.client.login(username="superuser", password="password")
        response = self.client.get(reverse("players"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "players.html")

    def test_players_view_as_normal_user(self):
        self.client.login(username="user", password="password")
        response = self.client.get(reverse("players"))
        self.assertEqual(response.status_code, 302)  # Redirects

    def test_tournaments_view(self):
        self.client.login(username="user", password="password")
        response = self.client.get(reverse("tournaments"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tournaments.html")

    def test_tournament_detail_view_as_superuser(self):
        self.client.login(username="superuser", password="password")
        response = self.client.get(
            reverse("tournament_detail", args=[self.tournament.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tournament_detail.html")

    def test_create_tournament_view_as_superuser(self):
        self.client.login(username="superuser", password="password")
        response = self.client.post(
            reverse("create_tournament"),
            {"name": "New Tournament", "date": "2024-01-01", "points_to_win": 40},
        )
        self.assertEqual(response.status_code, 302)  # Redirects after creation
        self.assertTrue(Tournament.objects.filter(name="New Tournament").exists())

    def test_tournament_detail_renders_zero_scores(self):
        self.client.login(username="superuser", password="password")
        player_with_score = Player.objects.create(name="Player With Score")
        player_with_zero = Player.objects.create(name="Player With Zero")
        self.tournament.players.add(player_with_score, player_with_zero)
        match = Match.objects.create(tournament=self.tournament)
        Score.objects.create(player=player_with_score, match=match, score=2)
        Score.objects.create(player=player_with_zero, match=match, score=0)

        response = self.client.get(
            reverse("tournament_detail", args=[self.tournament.pk])
        )

        self.assertContains(response, '<td class="has-text-centered">0</td>')

    def test_create_tournament_calculates_points_to_win(self):
        self.client.login(username="superuser", password="password")
        player1 = Player.objects.create(name="Rocky")
        player2 = Player.objects.create(name="Bubba")
        player3 = Player.objects.create(name="Trejo")
        response = self.client.post(
            reverse("create_tournament"),
            {
                "name": "New Tournament",
                "date": "2026-05-21",
                "points_to_win": 0,
                "players": [player1.pk, player2.pk, player3.pk],
            },
        )
        self.assertEqual(response.status_code, 302)
        tournament = Tournament.objects.get(name="New Tournament")
        # 3 players -> (3 - 1) * 10 = 20 points
        self.assertEqual(tournament.points_to_win, 20)

    def test_tournament_registration_updates_points_to_win(self):
        self.client.login(username="superuser", password="password")
        tournament = Tournament.objects.create(name="Register Test")
        player1 = Player.objects.create(name="Player A")
        player2 = Player.objects.create(name="Player B")

        # Add Player A
        self.client.post(
            reverse("tournament_registration", args=[tournament.pk]),
            {"player_id": player1.pk, "action": "add"},
        )
        tournament.refresh_from_db()
        # 1 player -> max(0, (1 - 1) * 10) = 0 points
        self.assertEqual(tournament.points_to_win, 0)

        # Add Player B
        self.client.post(
            reverse("tournament_registration", args=[tournament.pk]),
            {"player_id": player2.pk, "action": "add"},
        )
        tournament.refresh_from_db()
        # 2 players -> max(0, (2 - 1) * 10) = 10 points
        self.assertEqual(tournament.points_to_win, 10)

        # Remove Player A
        self.client.post(
            reverse("tournament_registration", args=[tournament.pk]),
            {"player_id": player1.pk, "action": "remove"},
        )
        tournament.refresh_from_db()
        # 1 player -> max(0, (1 - 1) * 10) = 0 points
        self.assertEqual(tournament.points_to_win, 0)
