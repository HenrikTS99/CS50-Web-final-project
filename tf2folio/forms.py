from django.forms import ModelForm
from .models import Item, Transaction
from django import forms

class ItemForm(ModelForm):
    class Meta:
        model = Item
        fields = ["item_name", "quality", "craftable", "australium", "texture_name",
            "wear", "particle_effect", "description", "killstreak"]


class TradeSaleForm(ModelForm):
    # items_sold = forms.ModelMultipleChoiceField(
    #     queryset=Item.objects.all(),  # Use the queryset for your Item model
    #     widget=forms.SelectMultiple(attrs={'multiple': ''}),  # You can use other widgets like SelectMultiple
    # )
    
    class Meta:
        model = Transaction
        fields = ["transaction_type", "items_sold", "transaction_method", "amount", "description"]


class TradeBuyForm(ModelForm):
    class Meta:
        model = Transaction
        fields = ["transaction_type", "items_bought", "transaction_method", "amount", "description"]