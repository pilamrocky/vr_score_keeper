from django.db.models import Sum
from django.shortcuts import render, redirect
from .models import Tournament, Player, Match, Score
from .forms import TournamentForm, PlayerForm, MatchForm, ScoreForm, MultiScoreForm


## INDEX ##
def index(request):
    # Get the latest tournament and all previous tournaments
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
def players(request):
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
def tournaments(request):
    all_tournaments = Tournament.objects.all().order_by("-date")
    form = TournamentForm()
    return render(
        request, "tournaments.html", {"tournaments": all_tournaments, "form": form}
    )


## TOURNAMENT REGISTRATION ##
def tournament_registration(request, pk):
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
def tournament_detail(request, pk):
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


def create_tournament(request):
    if request.method == "POST":
        form = TournamentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("tournament_registration", pk=form.instance.pk)
    else:
        form = TournamentForm()
    return render(request, "create_tournament.html", {"form": form})


def create_player(request):
    if request.method == "POST":
        form = PlayerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("player_list")
    else:
        form = PlayerForm()
    return render(request, "create_player.html", {"form": form})


def create_match(request, tournament_pk):
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


def create_score(request, match_pk):
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


def update_tournament(request, pk):
    tournament = Tournament.objects.get(pk=pk)
    if request.method == "POST":
        form = TournamentForm(request.POST, instance=tournament)
        if form.is_valid():
            form.save()
            return redirect("tournament_list")
    else:
        form = TournamentForm(instance=tournament)
    return render(request, "update_tournament.html", {"form": form})


def update_player(request, pk):
    player = Player.objects.get(pk=pk)
    if request.method == "POST":
        form = PlayerForm(request.POST, instance=player)
        if form.is_valid():
            form.save()
            return redirect("player_list")
    else:
        form = PlayerForm(instance=player)
    return render(request, "update_player.html", {"form": form})


def update_match(request, pk):
    match = Match.objects.get(pk=pk)
    if request.method == "POST":
        form = MatchForm(request.POST, instance=match)
        if form.is_valid():
            form.save()
            return redirect("match_list")
    else:
        form = MatchForm(instance=match)
    return render(request, "update_match.html", {"form": form})


def update_score(request, pk):
    score = Score.objects.get(pk=pk)
    if request.method == "POST":
        form = ScoreForm(request.POST, instance=score)
        if form.is_valid():
            form.save()
            return redirect("score_list")
    else:
        form = ScoreForm(instance=score)
    return render(request, "update_score.html", {"form": form})


def delete_tournament(request, pk):
    tournament = Tournament.objects.get(pk=pk)
    tournament.delete()
    return redirect("tournaments")


def delete_player(request, pk):
    player = Player.objects.get(pk=pk)
    player.delete()
    return redirect("players")


def delete_match(request, pk):
    match = Match.objects.get(pk=pk)
    match.delete()
    tournament = match.tournament
    return redirect("tournament_detail", pk=tournament.pk)
