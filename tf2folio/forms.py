from django.forms import ModelForm
from .models import Item
from django import forms

class ItemForm(ModelForm):
    class Meta:
        model = Item
        fields = ["item_name", "quality", "craftable", "australium", "texture_name",
            "wear", "particle_effect", "description", "killstreak"]