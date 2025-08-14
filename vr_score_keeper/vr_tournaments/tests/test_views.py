from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from ..models import Tournament, Player


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
            {"name": "New Tournament", "date": "2024-01-01"},
        )
        self.assertEqual(response.status_code, 302)  # Redirects after creation
        self.assertTrue(Tournament.objects.filter(name="New Tournament").exists())
