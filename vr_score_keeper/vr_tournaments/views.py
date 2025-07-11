from django.db.models import Sum
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.http import HttpResponseNotAllowed
from django.contrib import messages
from .models import Tournament, Player, Match, Score
from .forms import (
    TournamentForm,
    PlayerForm,
    MatchForm,
    ScoreForm,
    MultiScoreForm,
    UserProfileForm,
)


def is_superuser(user):
    """Checks if the given user has superuser privileges."""
    return user.is_superuser


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


## INDEX ##
@login_required
def index(request):
    # Get the latest tournament and all previous tournaments
    """
    Displays the index page with the latest tournament and all previous tournaments.

    The latest tournament's player scores are calculated, and the winner is determined
    if the score threshold is met. For each previous tournament, player scores are also
    calculated.

    :param request: The HTTP request object.
    :return: An HTTP response object rendering the index.html template with context
             containing the latest tournament, the latest tournament player scores,
             and previous tournaments with their respective player scores.
    """

    previous_tournaments = Tournament.objects.order_by("-date")[1:]
    latest_tournament = Tournament.objects.order_by("-date").first()

    # Calculate total scores for the latest tournament
    latest_tournament_player_scores = []
    if latest_tournament:
        for player in latest_tournament.players.all():
            total_score = (
                player.scores.filter(match__tournament=latest_tournament).aggregate(
                    total=Sum("score")
                )["total"]
                or 0
            )
            latest_tournament_player_scores.append((player, total_score))

        # Determine the winner if there is one of the latest tournament
        winner = None
        max_score = 0
        for player, score in latest_tournament_player_scores:
            if score >= 30 and (winner is None or score > max_score):
                winner = player
                max_score = score
        if winner:
            latest_tournament.winner = winner.name
            latest_tournament.save()

    # Calculate total scores for previous tournaments
    previous_tournament_player_scores = []
    for tournament in previous_tournaments:
        tournament_player_scores = []
        for player in tournament.players.all():
            total_score = (
                player.scores.filter(match__tournament=tournament).aggregate(
                    total=Sum("score")
                )["total"]
                or 0
            )
            tournament_player_scores.append((player, total_score))
        previous_tournament_player_scores.append((tournament, tournament_player_scores))

    return render(
        request,
        "index.html",
        {
            "latest_tournament": latest_tournament,
            "latest_tournament_player_scores": latest_tournament_player_scores,
            "previous_tournament_player_scores": previous_tournament_player_scores,
        },
    )


## PLAYERS ##
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
            form.save()
            return render(
                request, "players.html", {"players": current_players, "form": form}
            )

    return render(request, "players.html", {"players": current_players, "form": form})


## TOURNAMENTS ##
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


## TOURNAMENT REGISTRATION ##
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


## TOURNAMENT DETAIL ##
@login_required
@user_passes_test(is_superuser)
def tournament_detail(request, pk):
    """
    Displays the details of a tournament, including the registered players and matches.

    :param request: The HTTP request object.
    :param pk: The primary key of the tournament to be displayed.
    :return: An HTTP response object rendering the tournament detail page.
    """

    tournament = Tournament.objects.get(pk=pk)
    tournament_matches = []

    if hasattr(tournament, "matches"):
        tournament_matches = tournament.matches.all().order_by("-date")
    registered_players = []

    if hasattr(tournament, "players"):
        registered_players = tournament.players.all()

    return render(
        request,
        "tournament_detail.html",
        {
            "tournament": tournament,
            "registered_players": registered_players,
            "matches": tournament_matches,
        },
    )


@login_required
@user_passes_test(is_superuser)
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
            form.save()
            return redirect("tournament_registration", pk=form.instance.pk)
    else:
        form = TournamentForm()
    return render(request, "create_tournament.html", {"form": form})


@login_required
@user_passes_test(is_superuser)
def create_player(request):
    """
    Creates a new player.

    :param request: The HTTP request object.
    :return: An HTTP response object redirecting to the player list page.
    """
    if request.method == "POST":
        form = PlayerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("player_list")
    else:
        form = PlayerForm()
    return render(request, "create_player.html", {"form": form})


@login_required
@user_passes_test(is_superuser)
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
            form.save()
            return redirect("create_score", match_pk=form.instance.pk)
    else:
        form = MatchForm()
    return render(
        request, "create_match.html", {"form": form, "tournament": tournament}
    )


@login_required
@user_passes_test(is_superuser)
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
            form.save()
            return redirect("tournament_detail", pk=match.tournament.pk)
    else:
        form = MultiScoreForm(registered_players, match)
    return render(request, "create_score.html", {"form": form, "match": match})


@login_required
@user_passes_test(is_superuser)
def update_tournament(request, pk):
    """
    Updates a tournament with the given primary key, and then redirects to the tournament list page.

    :param request: The HTTP request object.
    :param pk: The primary key of the tournament to be updated.
    :return: An HTTP response object redirecting to the tournament list page.
    """
    tournament = Tournament.objects.get(pk=pk)
    if request.method == "POST":
        form = TournamentForm(request.POST, instance=tournament)
        if form.is_valid():
            form.save()
            return redirect("tournament_list")
    else:
        form = TournamentForm(instance=tournament)
    return render(request, "update_tournament.html", {"form": form})


@login_required
@user_passes_test(is_superuser)
def update_player(request, pk):
    """
    Updates a player with the given primary key, and then redirects to the player list page.

    :param request: The HTTP request object.
    :param pk: The primary key of the player to be updated.
    :return: An HTTP response object redirecting to the player list page.
    """
    player = Player.objects.get(pk=pk)
    if request.method == "POST":
        form = PlayerForm(request.POST, instance=player)
        if form.is_valid():
            form.save()
            return redirect("player_list")
    else:
        form = PlayerForm(instance=player)
    return render(request, "update_player.html", {"form": form})


@login_required
@user_passes_test(is_superuser)
def update_match(request, pk):
    """
    Updates a match with the given primary key, and then redirects to the match list page.

    Args:
        request (HttpRequest): The request object.
        pk (int): The primary key of the match to be updated.

    Returns:
        HttpResponse: The rendered page.
    """
    match = Match.objects.get(pk=pk)
    if request.method == "POST":
        form = MatchForm(request.POST, instance=match)
        if form.is_valid():
            form.save()
            return redirect("match_list")
    else:
        form = MatchForm(instance=match)
    return render(request, "update_match.html", {"form": form})


@login_required
@user_passes_test(is_superuser)
def update_score(request, pk):
    """
    Updates a score with the given primary key, and then redirects to the score list page.

    :param request: The HTTP request object.
    :param pk: The primary key of the score to update.
    :return: An HTTP response object redirecting to the score list page.
    """
    score = Score.objects.get(pk=pk)
    if request.method == "POST":
        form = ScoreForm(request.POST, instance=score)
        if form.is_valid():
            form.save()
            return redirect("score_list")
    else:
        form = ScoreForm(instance=score)
    return render(request, "update_score.html", {"form": form})


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
        player.delete()
        return redirect("players")

    return HttpResponseNotAllowed(["POST"])


@login_required
@user_passes_test(is_superuser)
def delete_match(request, pk):
    """
    Deletes a match with the given primary key, and then redirects to the tournament
    detail page for the tournament that the match was part of.
    """
    if request.method == "POST":
        match = Match.objects.get(pk=pk)
        match.delete()
        tournament = match.tournament
        return redirect("tournament_detail", pk=tournament.pk)

    return HttpResponseNotAllowed(["POST"])
