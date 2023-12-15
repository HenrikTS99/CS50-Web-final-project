from django.forms import ModelForm
from .models import Item, Transaction
from django import forms

class ItemForm(ModelForm):
    class Meta:
        model = Item
        fields = ["item_name", "quality", "craftable", "australium", "texture_name",
            "wear", "particle_effect", "description", "killstreak"]


class TransactionForm(ModelForm):
    class Meta:
        model = Transaction
        fields = ["transaction_type", "transaction_method", 
            "amount", "currency", "description"]

class TradeSaleForm(TransactionForm):
    class Meta(TransactionForm.Meta):
        fields = TransactionForm.Meta.fields + ["items_sold"]

class TradeBuyForm(TransactionForm):
    class Meta(TransactionForm.Meta):
        fields = TransactionForm.Meta.fields + ["items_bought"]