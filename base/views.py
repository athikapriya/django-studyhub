# third-party imports
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout


# local app imports
from .models import *
from .forms import RoomForm




# =============== Login view =============== 
def loginPage(request):

    if request.method == "POST":
        email = request.POST.get('email', "").lower()
        password = request.POST.get("password", "")

        if not email or not password:
            messages.error(request, "Both fields are required")
            return render(request, 'base/login_form.html')

        if User.objects.filter(email=email).count() > 1:
            messages.error(request, "Multiple accounts found with this email")
            return render(request, 'base/login_form.html')

        try:
            user = User.objects.get(email=email)
            username = user.username
        except User.DoesNotExist:
            messages.error(request,  "User doesn't exist")
            return render(request, 'base/login_form.html')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("homepage")
        else:
            messages.error(request, "Email or password is incorrect")

    return render(request, 'base/login_form.html')



# =============== homepage view =============== 
def homepage(request):
    q = request.GET.get('q') or ""

    rooms = Room.objects.filter(
       Q(topic__name__icontains= q) |
       Q(name__icontains = q) |
       Q(description__icontains = q)
    )
    room_count = rooms.count()
    room_message = Message.objects.order_by("-created_at")[:5]

    topics = Topic.objects.annotate(
        room_count=Count("rooms")
    )[:9]
    
    topic_count = Topic.objects.count()
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



# =============== browse topics view =============== 
def browseTopics(request):
    q = request.GET.get('q') or ""

    topics = Topic.objects.filter(
        name__icontains= q
    ).annotate(
        room_count = Count("rooms")
    )

    topic_count = topics.count()

    context = {
        "topics": topics,
        "topic_count": topic_count,
    }
    return render(request, "base/browse_topics.html", context)



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
        "form" : form,
        "btn_text" : "Create Room"
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
        "form" : form,
        "btn_text" : "Update Room"
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