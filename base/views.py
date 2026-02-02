# third-party imports
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q


# local app imports
from .models import *
from .forms import RoomForm



# =============== homepage view =============== 
def homepage(request):
    q = request.GET.get('q') if request.GET.get("q") != None else ""

    rooms = Room.objects.filter(
       Q(topic__name__icontains= q) |
       Q(name__icontains = q) |
       Q(description__icontains = q)
    )
    room_count = rooms.count()
    room_message = Message.objects.order_by("-created_at")[:5]

    topics = Topic.objects.all()
    topic_count = topics.count()
    context = {
        "rooms" : rooms,
        "room_count" : room_count,
        "room_message" : room_message,
        "topics" : topics,
        "topic_count" : topic_count
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
            room.host = request.user 
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