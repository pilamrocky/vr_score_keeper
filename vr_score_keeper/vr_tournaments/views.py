import logging
from itertools import groupby
from django.db.models import Sum
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.http import HttpResponseNotAllowed
from django.contrib import messages
from .models import Tournament, Player, Match
from .forms import (
    TournamentForm,
    PlayerForm,
    MatchForm,
    MultiScoreForm,
    UserProfileForm,
)

logger = logging.getLogger(__name__)

# Helper Functions
def is_superuser(user):
    """Checks if the given user has superuser privileges."""
    return user.is_superuser


def is_poweruser(user):
    """Checks if the given user has poweruser privileges."""
    if user.groups.filter(name="powerUser").exists() or user.is_superuser:
        return True
    return False


def calculate_player_scores(tournament):
    """Calculates the total score for each player in the given tournament."""
    player_scores = []
    for player in tournament.players.all():
        total_score = (
            player.scores.filter(match__tournament=tournament).aggregate(
                total=Sum("score")
            )["total"]
            or 0
        )
        player_scores.append((player, total_score))
    return player_scores


@login_required
def profile(request):
    """Displays the user's profile information."""
    return render(request, "profile.html")  # Use app-specific template path


@login_required
def profile_edit(request):
    """Handles editing the user's profile information."""
    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Your profile was successfully updated!"
            )  # Add success message
            return redirect("profile")  # Redirect back to the profile view

        messages.error(request, "Please correct the error below.")  # Add error message

    else:
        form = UserProfileForm(instance=request.user)

    return render(
        request, "profile_edit.html", {"form": form}
    )  # Use app-specific template path


# INDEX #
@login_required
def index(request):
    # Get all current and previous tournaments
    """
    Displays the index page with the latest tournaments and all previous tournaments.

    The latest tournament's player scores are calculated, and the winner is determined
    if the score threshold is met. For each previous tournament, player scores are also
    calculated.

    :param request: The HTTP request object.
    :return: An HTTP response object rendering the index.html template with context
             containing the latest tournament, the latest tournament player scores,
             and previous tournaments with their respective player scores.
    """

    # Get all active tournaments
    active_tournaments = Tournament.objects.filter(winner="").order_by("-date")
    previous_tournaments = Tournament.objects.exclude(winner="").order_by("-date")

    # Calculate scores for active tournaments
    active_tournament_data = []
    for tournament in active_tournaments:
        player_scores = calculate_player_scores(tournament)

        # Determine winner logic (if needed)
        winner = None
        max_score = 0
        for player, score in player_scores:
            if score >= 30 and (winner is None or score > max_score):
                winner = player
                max_score = score
        if winner:
            tournament.winner = winner.name
            tournament.save()

        active_tournament_data.append(
            {
                "tournament": tournament,
                "player_scores": player_scores,
            }
        )

    # Calculate scores for previous tournaments
    previous_tournament_data = []
    for tournament in previous_tournaments:
        player_scores = calculate_player_scores(tournament)
        previous_tournament_data.append(
            {
                "tournament": tournament,
                "player_scores": player_scores,
            }
        )

    return render(
        request,
        "index.html",
        {
            "active_tournaments": active_tournament_data,
            "previous_tournaments": previous_tournament_data,
        },
    )


# PLAYERS #
@login_required
@user_passes_test(is_superuser)
def players(request):
    """
    View to show all players in the database and create a new player if the
    request method is POST.

    The view is only accessible to superusers.

    Template:
        players.html

    Context:
        players: all players in the database
        form: a form to create a new player
    """
    current_players = Player.objects.all()
    form = PlayerForm()
    if request.method == "POST":
        form = PlayerForm(request.POST)
        if form.is_valid():
            player = form.save()
            logger.info(f"User '{request.user.username}' created player '{player.name}'.")
            return render(
                request, "players.html", {"players": current_players, "form": form}
            )

    return render(request, "players.html", {"players": current_players, "form": form})


# TOURNAMENTS #
@login_required
def tournaments(request):
    """
    Displays a list of all tournaments in descending order of date, and allows the user to create a new tournament.

    :param request: The HTTP request object.
    :return: An HTTP response object rendering the tournaments.html template.
    """
    all_tournaments = Tournament.objects.all().order_by("-date")
    form = TournamentForm()
    return render(
        request, "tournaments.html", {"tournaments": all_tournaments, "form": form}
    )


# TOURNAMENT REGISTRATION #
@login_required
@user_passes_test(is_superuser)
def tournament_registration(request, pk):
    """
    Allows a superuser to register players for a tournament. The user is presented
    with a list of all players and a list of players who are currently registered
    for the tournament. The user can add or remove players from the tournament.
    """

    tournament = Tournament.objects.get(pk=pk)
    all_players = Player.objects.all()
    registered_players = []
    if hasattr(tournament, "players"):
        registered_players = tournament.players.all()

    if request.method == "POST":
        player_id = request.POST.get("player_id")
        action = request.POST.get("action")
        player = Player.objects.get(pk=player_id)

        if action == "add":
            player.tournaments.add(tournament)
        elif action == "remove":
            player.tournaments.remove(tournament)

        return redirect("tournament_registration", pk=pk)

    return render(
        request,
        "tournament_registration.html",
        {
            "tournament": tournament,
            "all_players": all_players,
            "registered_players": registered_players,
        },
    )


# TOURNAMENT DETAIL #
@login_required
@user_passes_test(is_poweruser)
def tournament_detail(request, pk):
    """
    Displays the details of a tournament, including the registered players and matches.

    This view pre-fetches related scores to prevent N+1 query issues and prepares
    a list of ordered scores for each match to ensure correct rendering in the template.

    :param request: The HTTP request object.
    :param pk: The primary key of the tournament to be displayed.
    :return: An HTTP response object rendering the tournament detail page.
    """
    tournament = Tournament.objects.get(pk=pk)
    registered_players = tournament.players.all()

    # Get all matches, prefetching scores to prevent N+1 queries.
    matches = tournament.matches.prefetch_related("scores").order_by("-date", "-pk")

    # Augment match objects with a list of scores ordered by registered_players.
    # This fixes the rendering bug in the template and makes it more efficient.
    matches_for_template = []
    for match in matches:
        scores_map = {score.player_id: score.score for score in match.scores.all()}
        match.ordered_scores = [scores_map.get(p.id) for p in registered_players]
        matches_for_template.append(match)

    # Group matches by date.
    grouped_matches = []
    if matches_for_template:
        for date, match_group in groupby(matches_for_template, key=lambda m: m.date):
            grouped_matches.append((date, list(match_group)))

    return render(
        request,
        "tournament_detail.html",
        {
            "tournament": tournament,
            "registered_players": registered_players,
            "grouped_matches": grouped_matches,
        },
    )


@login_required
@user_passes_test(is_poweruser)
def create_tournament(request):
    """
    Creates a new tournament and redirects to the tournament registration page.

    :param request: The HTTP request object.
    :return: An HTTP response object rendering the create tournament page or
             redirecting to the tournament registration page.
    """

    if request.method == "POST":
        form = TournamentForm(request.POST)
        if form.is_valid():
            tournament = form.save()
            logger.info(f"User '{request.user.username}' created tournament '{tournament.name}'.")
            return redirect("tournament_registration", pk=tournament.pk)
    else:
        form = TournamentForm()
    return render(request, "create_tournament.html", {"form": form})


@login_required
@user_passes_test(is_poweruser)
def create_match(request, tournament_pk):
    """
    Creates a new match for a given tournament.

    :param request: The HTTP request object.
    :param tournament_pk: The primary key of the tournament to add the match to.
    :return: An HTTP response object.
    """
    tournament = Tournament.objects.get(pk=tournament_pk)
    if request.method == "POST":
        form = MatchForm(request.POST)
        if form.is_valid():
            match = form.save(commit=False)
            match.tournament = tournament
            match.save()
            logger.info(f"User '{request.user.username}' created match {match.id} for tournament '{tournament.name}'.")
            return redirect("create_score", match_pk=match.pk)
    else:
        form = MatchForm()
    return render(
        request, "create_match.html", {"form": form, "tournament": tournament}
    )


@login_required
@user_passes_test(is_poweruser)
def create_score(request, match_pk):
    """
    Creates scores for a match.

    :param request: The HTTP request object.
    :param match_pk: The primary key of the match to be scored.
    :return: An HTTP response object redirecting to the tournament detail page.
    """
    match = Match.objects.get(pk=match_pk)
    registered_players = match.tournament.players.all()
    if request.method == "POST":
        form = MultiScoreForm(registered_players, match, request.POST)
        if form.is_valid():
            scores = form.save()
            score_details = ", ".join([f"{score.player.name}: {score.score}" for score in scores])
            logger.info(f"User '{request.user.username}' added scores for match {match.id} in tournament '{match.tournament.name}'. Scores: {score_details}.")
            return redirect("index")
    else:
        form = MultiScoreForm(registered_players, match)
    return render(request, "create_score.html", {"form": form, "match": match})


@login_required
@user_passes_test(is_superuser)
def delete_tournament(request, pk):
    """
    Deletes a tournament with the given primary key, and then redirects to the tournament list page.

    :param request: The HTTP request object.
    :param pk: The primary key of the tournament to delete.
    :return: An HTTP response object redirecting to the tournament list page.
    """
    if request.method == "POST":
        tournament = Tournament.objects.get(pk=pk)
        logger.info(f"User '{request.user.username}' deleted tournament '{tournament.name}'.")
        tournament.delete()
        return redirect("tournaments")

    return HttpResponseNotAllowed(["POST"])


@login_required
@user_passes_test(is_superuser)
def delete_player(request, pk):
    """
    Deletes a player with the given primary key, and then redirects to the player list page.

    :param request: The HTTP request object.
    :param pk: The primary key of the player to delete.
    :return: An HTTP response object redirecting to the player list page.
    """
    if request.method == "POST":
        player = Player.objects.get(pk=pk)
        logger.info(f"User '{request.user.username}' deleted player '{player.name}'.")
        player.delete()
        return redirect("players")

    return HttpResponseNotAllowed(["POST"])


@login_required
@user_passes_test(is_poweruser)
def delete_match(request, pk):
    """
    Deletes a match with the given primary key, and then redirects to the tournament
    detail page for the tournament that the match was part of.
    """
    if request.method == "POST":
        match = Match.objects.get(pk=pk)
        scores = Score.objects.filter(match=match)
        score_details = ", ".join([f"{score.player.name}: {score.score}" for score in scores])
        logger.info(f"User '{request.user.username}' deleted match {match.id} from tournament '{match.tournament.name}'. Scores: {score_details}.")
        tournament = match.tournament
        match.delete()
        return redirect("tournament_detail", pk=tournament.pk)

    return HttpResponseNotAllowed(["POST"])
