# third-party imports
from django.forms import ModelForm

# local app imports 
from .models import Room


class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = "__all__"
        exclude = ["slug"]