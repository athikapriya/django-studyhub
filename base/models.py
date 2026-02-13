from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from django.core.validators import RegexValidator



# =============== User Model =============== 
class User(AbstractUser):
    name_validator = RegexValidator(
        regex=r'^[a-zA-Z0-9_]+$',
        message='Name can only contain letters, numbers, and underscore.'
    )
    username_validator = RegexValidator(
        regex=r'^[a-zA-Z0-9_]+$',
        message='Username can only contain letters, numbers, and underscore.'
    )
    username = models.CharField( max_length=150, unique=True, validators=[username_validator])
    name = models.CharField(max_length=200, null=True, validators=[name_validator])
    email = models.EmailField(unique=True, null=True)
    bio = models.TextField(null=True)

    avatar = models.ImageField(null=True, blank=True, upload_to="avatar/",  default="profile.svg")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []



# =============== Topic model =============== 
class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name



# =============== Room model =============== 
class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, related_name="rooms")
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    participants = models.ManyToManyField(User, related_name="participants", blank=True)
    slug = models.SlugField(unique=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta :
        ordering = ["-updated", "-created_at"]

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    

# =============== Message model =============== 
class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', '-created_at']

    def __str__(self):
        return self.body[0:50]