# third-party imports
from django.shortcuts import render, get_object_or_404, redirect


# local app imports
from .models import *
from .forms import RoomForm



# =============== homepage view =============== 
def homepage(request):
    rooms = Room.objects.all()
    room_count = rooms.count()
    room_message = Message.objects.all()[0:5]
    context = {
        "rooms" : rooms,
        "room_count" : room_count,
        "room_message" : room_message
    }
    return render(request, 'base/homepage.html', context)


# =============== room view =============== 
def room(request, slug):
    room = get_object_or_404(Room, slug=slug)
    context = {
        "room": room
    }
    return render(request, 'base/room.html', context)



# =============== Room create view =============== 
def createRoom(request):
    if request.method == "POST":
        print(request.POST)
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            request.host = request.user 
            room.save()
            return redirect("homepage")
    else:
        form = RoomForm()

    context = {
        "form" : form
    }
    return render(request, 'base/room_form.html', context)



# =============== Room update view =============== 
def updateRoom(request, pk):
    room = get_object_or_404(Room, id=pk)
    form = RoomForm(instance=room)

    if request.method == "POST":
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect("room", slug=room.slug)
    context = {
        "room" : room,
        "form" : form
    }
    return render(request, 'base/room_form.html', context)



# =============== Room delete view =============== 
def deleteRoom(request, pk):
    room = get_object_or_404(Room, id=pk)

    if request.method == "POST":
        room.delete()
        return redirect("homepage")
    context = {
        "room" : room
    }
    return render(request, "base/delete_room.html", context)