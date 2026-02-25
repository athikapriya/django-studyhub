# third-party imports
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count, F
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash


# local app imports
from .models import *
from .forms import RoomForm, CreateUserForm, EditUserForm, CustomPasswordChangeForm


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
    host_username = request.GET.get('host')

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    ).annotate(
        participant_count=Count("participants", distinct=True)
    ).select_related('host').prefetch_related('participants').order_by("-updated")

    if host_username:
        rooms = rooms.filter(host__username=host_username)

    for room in rooms:
        uploaded_participants = [
            p for p in room.participants.exclude(id=room.host.id)
            if p.avatar and p.avatar.public_id != "profile"
        ]
        room.display_participants = uploaded_participants[:7]
        room.extra_participants = len(uploaded_participants) - len(room.display_participants)

    room_count = rooms.count()

    # for activity
    if request.user.is_authenticated:
        user_activity = Message.objects.filter(
            user=request.user
        ).select_related("room").order_by("-created_at")[:3]
    else:
        user_activity = Message.objects.none()

    topics = Topic.objects.annotate(
        room_count=Count("rooms")
    )[:7]
    
    topic_count = Topic.objects.count()

    # top hosts
    top_hosts = User.objects.annotate(
        rooms_count=Count('room', distinct=True)
    ).order_by('-rooms_count')[:5]

    context = {
        "rooms" : rooms,
        "room_count" : room_count,
        "topics" : topics,
        "topic_count" : topic_count,
        "page" : page,
        "user_activity": user_activity,
        "top_hosts": top_hosts
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


# ============================== top hosts view starts ============================== 
def browseHosts(request):

    hosts = User.objects.annotate(
        rooms_count=Count('room')
    ).filter(rooms_count__gt=0).order_by('-rooms_count') 

    context = {
        "hosts": hosts
    }
    return render(request, 'base/browse_hosts.html', context)
# ============================== top hosts view ends ============================== 



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

    if request.user == message.user or request.user == message.room.host:
        message.delete()

    next_url = request.POST.get('next')

    if next_url:
        return redirect(next_url)

    return redirect('homepage')

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

    # activity
    if request.user == user:
        user_activity = Message.objects.filter(
            user=user
        ).select_related("room").order_by("-created_at")[:5]
    else:
        user_activity = None


    topics = Topic.objects.filter(
        rooms__host=user
    ).annotate(
        room_count=Count('rooms')
    ).distinct()

    for room in rooms:
        uploaded_participants = [
            p for p in room.participants.exclude(id=room.host.id)
            if p.avatar and p.avatar.public_id != "profile"
        ]
        room.display_participants = uploaded_participants[:7]
        room.extra_participants = len(uploaded_participants) - len(room.display_participants)

    topic_count = Room.objects.filter(host=user).count()

    context = {
        'profile_user': user,
        'rooms': rooms,
        'topics': topics,
        "topic_count" : topic_count,
        "user_activity": user_activity,
    }
    return render(request, 'base/user_profile.html', context)
# ============================== user profile view ends ============================== 


# ============================== user profile settings view ends here ============================== 
@login_required(login_url="login")
def user_edit(request, username):
    user = get_object_or_404(User, username=username)

    if request.user != user:
        messages.error(request, "You are not allowed to edit this page.")
        return redirect("user-profile", username=user.username)

    if request.method == "POST":
        form = EditUserForm(request.POST, request.FILES, instance=user)

        if form.is_valid():
            remove_avatar = request.POST.get("remove_avatar") == "true"

            old_avatar = None
            if user.avatar and hasattr(user.avatar, 'url'):
                old_avatar = user.avatar

            if remove_avatar:
                user.avatar = None
                user.save()

            form.save()
            return redirect("user-profile", username=user.username)
    else:
        form = EditUserForm(instance=user)

    context = {
        "form": form,
        "user": user
    }
    return render(request, "users/user_edit.html", context)
# ============================== user profile settings view ends here ============================== 


# ============================== activity view starts here ============================== 
@login_required(login_url="login")
def user_activity(request, username):
    user = get_object_or_404(User, username=username)
    
    if request.user != user:
        messages.error(request, "You are not allowed to access this page.")
        return redirect('homepage')  

    user_activity = Message.objects.filter(
        user=user
    ).select_related("room", "user").order_by("-created_at")

    context = {
        "user_activity": user_activity,
        "user": user
    }
    return render(request, "base/user_activity.html", context)
# ============================== activity view starts here ============================== 


# ============================== notofication view starts here ============================== 
@login_required(login_url="login")
def user_notifications(request, username):
    user = get_object_or_404(User, username=username)

    if request.user != user:
        messages.error(request, "You are not allowed to access this page.")
        return redirect('homepage') 
    
    if request.user == user:
        notifications = Message.objects.filter(
            Q(room__host=user) | Q(room__participants=user)
        ).exclude(user=user)  
        notifications = notifications.select_related("room", "user").order_by("-created_at")
    else:
        notifications = Message.objects.none()

    context = {
        "notifications": notifications,
        "user": user
    }

    return render(request, "base/user_notifications.html", context)
# ============================== notofication view ends here ============================== 


# ============================== change password view starts here ============================== 
@login_required(login_url="login")
def change_password(request):

    if request.method == "POST":
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated.')
            return redirect("user-profile", username=request.user.username)
        else:
            messages.error(request, "Please correct the error below.")
    else:
        form = CustomPasswordChangeForm(request.user)

    context = {
        "form": form
    }

    return render(request, 'users/change_password.html', context)
# ============================== change password view starts here ============================== 