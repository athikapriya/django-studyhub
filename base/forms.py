# third-party imports
from django.forms import ModelForm
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, SetPasswordForm


# local app imports 
from .models import Room, User



# =============== user form =============== 
class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["name", "username", "email", 'password1', "password2"]


        widgets = {
            "name" : forms.TextInput(attrs={
                "class" : "form-control form-control-sm form-input-custom",
                "placeholder" : "Enter your full name"
            }),
            "username" : forms.TextInput(attrs={
                "class" : "form-control form-control-sm form-input-custom",
                "placeholder" : "e.g. john_doe"
            }),
            "email" : forms.EmailInput(attrs={
                "class" : "form-control form-control-sm form-input-custom",
                "placeholder" : "e.g. john@example.com"
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["password1"].widget.attrs.update({
            "class": "form-control form-control-sm form-input-custom",
            "placeholder": "••••••••",
        })

        self.fields["password2"].widget.attrs.update({
            "class": "form-control form-control-sm form-input-custom",
            "placeholder": "••••••••",
        })

    def clean_email(self):
        email = self.cleaned_data.get("email").lower()

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "An account with this email already exists."
            )

        return email
    



# =============== Edit User Form =============== 
class EditUserForm(ModelForm):
    class Meta:
        model = User
        fields = ["name", "username", 'bio', 'avatar', "is_online"]

        widgets = {
            "name" : forms.TextInput(attrs={
                "class" : "form-control form-control-sm form-input-custom"
            }),
            "username": forms.TextInput(attrs={
                "class": "form-control form-control-sm form-input-custom",
            }),
            "bio": forms.Textarea(attrs={
                "class": "form-control form-control-sm form-input-custom",
                "rows": 3,
                "style": "resize:none;"
            }),
            'avatar': forms.FileInput(attrs=
                {'style': 'display:none;'
            }),
            "is_online" : forms.CheckboxInput(attrs={
                "class" : "form-check-input"
            }),
        }

    def clean_username(self):
        username = self.cleaned_data.get("username").lower()

        if User.objects.exclude(pk=self.instance.pk).filter(username=username).exists():
            raise ValidationError("This username is already taken.")

        return username



# =============== room form =============== 
class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = ["name", "topic", "description"]

        labels = {
            "name" : "Room Name",
            "topic" : "Topic",
            "description" : "About"
        }

        widgets = {
            "name" : forms.TextInput(attrs={
                "class" : "form-control form-control-sm form-input-custom",
                "placeholder" : "Ex: Mastering Python+Django"
            }),
            "topic" : forms.TextInput(attrs={
                "class" : "form-control form-control-sm form-select-custom"
            }),
            "description" : forms.Textarea(attrs={
                "class" : "form-control form-control-sm form-input-custom",
                "placeholder" : "What is the room about...",
                "rows" : 4,
                "style": "resize: none;"
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["topic"].empty_label = "Select a topic"

    def clean_description(self):
        description = self.cleaned_data.get("description", "")
        if description and len(description.split()) > 200:
            raise ValidationError("Try summarizing your thoughts — 200 words max, please.")
        return description
    


# =============== Change password form =============== 
class CustomPasswordChangeForm(PasswordChangeForm):
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)

        self.fields['old_password'].label = "Current Password"
        self.fields['new_password1'].label = "New Password"
        self.fields['new_password2'].label = "Confirm New Password"

        self.fields['old_password'].widget.attrs.update({
            "class": "form-control form-control-sm form-input-custom",
            "placeholder": "Enter current password"
        })

        self.fields['new_password1'].widget.attrs.update({
            "class": "form-control form-control-sm form-input-custom",
            "placeholder": "Enter new password"
        })

        self.fields['new_password2'].widget.attrs.update({
            "class": "form-control form-control-sm form-input-custom",
            "placeholder": "Confirm new password"
        })



# =============== for ResetPasswordform =============== 
class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control form-input-custom",
            "placeholder": "Enter new password"
        })
    )

    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control form-input-custom",
            "placeholder": "Confirm new password"
        })
    )