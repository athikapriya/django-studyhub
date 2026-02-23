# third party imports
from rest_framework.serializers import ModelSerializer

# local app imports
from base.models import Room


class RoomSerializer(ModelSerializer):
    class Meta:
        model = Room
        fields = "__all__"