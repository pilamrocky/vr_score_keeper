from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Tournament, Player, Match, Score
from .forms import TournamentForm, PlayerForm, MatchForm, ScoreForm


def index(request):
    tournaments = Tournament.objects.all()
    latest_tournament = Tournament.objects.order_by("-date").first()
    if latest_tournament:
        players = latest_tournament.player_set.all()
        player_scores = []
        for player in players:
            score = player.score_set.filter(tournament=latest_tournament).aggregate(
                total_score=Sum("score")
            )["total_score"]
            player_scores.append((player, score))
    else:
        player_scores = []
    return render(
        request,
        "index.html",
        {
            "tournaments": tournaments,
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


def tournament_list(request):
    tournaments = Tournament.objects.all()
    form = TournamentForm()
    return render(
        request, "tournament_list.html", {"tournaments": tournaments, "form": form}
    )


def tournament_detail(request, pk):
    tournament = Tournament.objects.get(pk=pk)
    return render(request, "tournament_detail.html", {"tournament": tournament})


def player_list(request):
    players = Player.objects.all()
    return render(request, "player_list.html", {"players": players})


def player_detail(request, pk):
    player = Player.objects.get(pk=pk)
    return render(request, "player_detail.html", {"player": player})


def match_list(request):
    matches = Match.objects.all()
    return render(request, "match_list.html", {"matches": matches})


def match_detail(request, pk):
    match = Match.objects.get(pk=pk)
    return render(request, "match_detail.html", {"match": match})


def score_list(request):
    scores = Score.objects.all()
    return render(request, "score_list.html", {"scores": scores})


def score_detail(request, pk):
    score = Score.objects.get(pk=pk)
    return render(request, "score_detail.html", {"score": score})


def create_tournament(request):
    if request.method == "POST":
        form = TournamentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("tournament_list")
        else:
            return render(request, "tournament_list.html", {"form": form})
    form = TournamentForm()
    return render(request, "tournament_list.html", {"form": form})


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
    return redirect("tournament_list")


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
