from django.shortcuts import render, get_object_or_404

from .models import *



# =============== homepage view =============== 
def homepage(request):
    rooms = Room.objects.all()
    room_count = rooms.count()
    context = {
        "rooms" : rooms,
        "room_count" : room_count
    }
    return render(request, 'base/homepage.html', context)


# =============== room view =============== 
def room(request, slug):
    rooms = get_object_or_404(Room, slug=slug)
    context = {
        "rooms": rooms
    }
    return render(request, 'base/room.html', context)