# third-party imports
from django.forms import ModelForm
from django import forms
from django.core.exceptions import ValidationError

# local app imports 
from .models import Room


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
            "topic" : forms.Select(attrs={
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