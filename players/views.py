from django.template.response import TemplateResponse
from players.models import Player


def stats(request, pk):
    player = Player.objects.get(id=pk)
    context = {
        'player': player,
    }

    return TemplateResponse(request,
        'players/player_stats.html', context)
