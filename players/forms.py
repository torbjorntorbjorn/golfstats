from django.forms import ModelForm

from players.models import Player


class PlayerForm(ModelForm):
    class Meta:
        model = Player
        fields = ("name", "pdga_number")
