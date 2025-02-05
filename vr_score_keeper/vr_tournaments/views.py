from django.db.models import Sum
from django.shortcuts import render, redirect
from .models import Tournament, Player, Match, Score
from .forms import TournamentForm, PlayerForm, MatchForm, ScoreForm


def index(request):
    previous_tournaments = Tournament.objects.order_by("-date")[1:]
    latest_tournament = Tournament.objects.order_by("-date").first()
    player_scores = []
    if latest_tournament and hasattr(latest_tournament, "player_set"):
        tournament_players = latest_tournament.player_set.all()
        for player in tournament_players:
            score = player.score_set.filter(tournament=latest_tournament).aggregate(
                total_score=Sum("score")
            )["total_score"]
            player_scores.append((player, score))
    return render(
        request,
        "index.html",
        {
            "tournaments": previous_tournaments,
            "latest_tournament": latest_tournament,
            "player_scores": player_scores,
        },
    )


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


def tournaments(request):
    all_tournaments = Tournament.objects.all().order_by("-date")
    form = TournamentForm()
    return render(
        request, "tournaments.html", {"tournaments": all_tournaments, "form": form}
    )


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


def tournament_detail(request, pk):
    tournament = Tournament.objects.get(pk=pk)
    return render(request, "tournament_detail.html", {"tournament": tournament})


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


def create_match(request):
    if request.method == "POST":
        form = MatchForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("match_list")
    else:
        form = MatchForm()
    return render(request, "create_match.html", {"form": form})


def create_score(request):
    if request.method == "POST":
        form = ScoreForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("score_list")
    else:
        form = ScoreForm()
    return render(request, "create_score.html", {"form": form})


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
    return redirect("player_list")


def delete_match(request, pk):
    match = Match.objects.get(pk=pk)
    match.delete()
    return redirect("match_list")


def delete_score(request, pk):
    score = Score.objects.get(pk=pk)
    score.delete()
    return redirect("score_list")
