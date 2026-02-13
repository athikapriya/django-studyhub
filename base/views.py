# third-party imports
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count, F
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


# local app imports
from .models import *
from .forms import RoomForm, CreateUserForm


# ============================== AUTH views starts here ============================== 
# =============== Login view starts =============== 
def loginPage(request):

    if request.user.is_authenticated:
        return redirect("homepage")

    if request.method == "POST":
        email = request.POST.get('email', "").lower()
        password = request.POST.get("password", "")

        if not email or not password:
            messages.error(request, "Both fields are required", extra_tags="auth")
            return render(request, 'base/authentication/login_form.html')

        if User.objects.filter(email=email).count() > 1:
            messages.error(request, "Multiple accounts found with this email", extra_tags="auth")
            return render(request, 'base/authentication/login_form.html')

        try:
            user = User.objects.get(email=email)
            username = user.username
        except User.DoesNotExist:
            messages.error(request,  "User doesn't exist", extra_tags="auth")
            return render(request, 'base/authentication/login_form.html')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect("homepage")
        else:
            messages.error(request, "Email or password is incorrect", extra_tags="auth")

    context = {
       
    }
    return render(request, 'base/authentication/login_form.html', context)
# =============== Login view ends =============== 



# =============== logout view starts =============== 
def logoutUser(request):
    logout(request)
    return redirect("login")
# =============== logout view ends =============== 


# =============== register view starts =============== 
def registerUser(request):
    form = CreateUserForm()

    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()

            messages.success(request, "Account created successfully. Please log in.", extra_tags="auth")
            return redirect('login')  

    context = {
        "form": form
    }
    return render(request, 'base/authentication/register_form.html', context)
# =============== register view ends =============== 
# ============================== AUTH views ends here ============================== 



# ============================== homepage view starts here ============================== 
def homepage(request):
    page= "homepage"

    q = request.GET.get('q') or ""

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    ).annotate(
        participant_count=Count("participants", distinct=True)
    ).select_related('host').prefetch_related('participants').order_by("-updated")

    for room in rooms:
        uploaded_participants = [p for p in room.participants.exclude(id=room.host.id)  if p.avatar and p.avatar.name != "profile.svg"]
        room.display_participants = uploaded_participants[:7]
        room.extra_participants = len(uploaded_participants) - len(room.display_participants)

    room_count = rooms.count()
    if request.user.is_authenticated:
        room_message = Message.objects.filter(
            room__host=request.user  
        ).select_related("room", "user").order_by("-created_at")
    else:
        room_message = Message.objects.none()

    topics = Topic.objects.annotate(
        room_count=Count("rooms")
    )[:7]
    
    topic_count = Topic.objects.count()
    context = {
        "rooms" : rooms,
        "room_count" : room_count,
        "room_message" : room_message,
        "topics" : topics,
        "topic_count" : topic_count,
        "page" : page
    }
    return render(request, 'base/homepage.html', context)
# ============================== homepage view ends here ============================== 


# ============================== room view starts here ============================== 
def room(request, slug):
    room = get_object_or_404(Room, slug=slug)
    room_messages = room.message_set.all()
    participants = room.participants.exclude(id=room.host.id)
    total_participant = participants.count()

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect("login")
    
        body = request.POST.get("body")

        if body:
            Message.objects.create(
                user = request.user,
                room = room,
                body = body
            )
            room.participants.add(request.user)

        return redirect("room", slug=slug)
    
    context = {
        "room": room,
        "room_messages" : room_messages,
        "participants" : participants,
        "total_participant" : total_participant
    }
    return render(request, 'base/room.html', context)
# ============================== room view ends here ============================== 


# ============================== Room CURD starts here ============================== 
# =============== Room create view starts =============== 
@login_required(login_url='login')
def createRoom(request):
    topics = Topic.objects.all()

    if request.method == "POST":
        topic_name = request.POST.get("topic")
        topic, created = Topic.objects.get_or_create(name=topic_name)

        room = Room(
            host = request.user,
            topic = topic,
            name = request.POST.get("name"),
            description = request.POST.get("description")
        )
        room.save()
        return redirect("homepage")
    
    else:
        form = RoomForm()

    context = {
        "form" : form,
        "btn_text" : "Create Room",
        "topics" : topics
    }
    return render(request, 'base/room_form.html', context)
# =============== Room update view ends =============== 



# =============== Room update view starts =============== 
@login_required(login_url='login')
def updateRoom(request, pk):
    room = get_object_or_404(Room, id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host:
        messages.error(request, "Sorry! You are not allowed to update this room.")
        return redirect("room", slug=room.slug)

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect("room", slug=room.slug)
    
    context = {
        "room" : room,
        "form" : form,
        "btn_text" : "Update Room",
        "topics" : topics
    }
    return render(request, 'base/room_form.html', context)
# =============== Room update view ends =============== 



# =============== Room delete view starts =============== 
@login_required(login_url='login')
def deleteRoom(request, pk):
    room = get_object_or_404(Room, id=pk)

    if request.user != room.host:
        messages.error(request, "Sorry! You are not allowed to delete this room.")
        return redirect("room", slug=room.slug)

    if request.method == "POST":
        room.delete()
        return redirect("homepage")
    context = {
        "room" : room
    }
    return render(request, "base/delete_room.html", context)
# =============== Room delete view ends =============== 
# ============================== Room CURD ends here ============================== 



# ==============================browse topics view starts ============================== 
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
# ============================== browse topics view ends ============================== 



# ============================== Message views starts here ============================== 
# =============== update message view strts =============== 
@login_required(login_url='login')
def updateMessage(request, pk):
    message = get_object_or_404(Message, id=pk)

    if request.user != message.user:
        messages.error(request, "You can't edit this message.")
        return redirect("room", slug=message.room.slug)

    if request.method == "POST":
        body = request.POST.get("body")
        if body:
            message.body = body
            message.save()

    return redirect("room", slug=message.room.slug)
# =============== update message view ends =============== 


# =============== delete message view starts =============== 
@login_required(login_url='login')
def deleteMessage(request, pk):
    message = get_object_or_404(Message, id=pk)

    if request.method == "POST":
        message.delete()
    
    return redirect("room", slug=message.room.slug)
# =============== delete message view ends =============== 
# ============================== Message views ends here ============================== 



# ==============================User profile view starts ============================== 
@login_required(login_url="login")
def userProfile(request, username):
    user = get_object_or_404(User, username=username)

    rooms = Room.objects.filter(host=user).annotate(
        participant_count=Count(
            'participants',
            filter=~Q(participants=F('host')),
            distinct=True
        )
    )   
    room_messages = Message.objects.filter(user=user)

    topics = Topic.objects.filter(
        rooms__host=user
    ).annotate(
        room_count=Count('rooms')
    ).distinct()

    for room in rooms:
        uploaded_participants = [p for p in room.participants.exclude(id=room.host.id) if p.avatar and p.avatar.name != "profile.svg"]
        room.display_participants = uploaded_participants[:7]
        room.extra_participants = len(uploaded_participants) - len(room.display_participants)

    topic_count = Room.objects.filter(host=user).count()

    context = {
        'user': user,
        'rooms': rooms,
        'room_messages': room_messages,
        'topics': topics,
        "topic_count" : topic_count
    }
    return render(request, 'base/user_profile.html', context)
# ============================== user profile view ends ============================== 