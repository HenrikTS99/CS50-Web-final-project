from django.forms import ModelForm, inlineformset_factory
from .models import Item, Transaction, Value
from django import forms

class ItemForm(ModelForm):
    class Meta:
        model = Item
        fields = ("item_name", "quality", "craftable", "australium", "texture_name",
            "wear", "particle_effect", "description", "killstreak")

ItemValueFormset = inlineformset_factory(Item, Value, fields=("transaction_method", "currency", "amount"), extra=1, can_delete=False)


# class ItemValueForm(ModelForm):
#     class Meta:
#         model = Item
#         fields = ["estimated_price", "sale_price"]

class TransactionForm(ModelForm):
    class Meta:
        model = Transaction
        fields = ["transaction_type", "transaction_method", 
            "amount", "currency", "description"]


class TradeSaleForm(TransactionForm):
    class Meta(TransactionForm.Meta):
        fields = TransactionForm.Meta.fields + ["items_sold"] + ["items_bought"]

    # only items logged in user owns in items field.
    def __init__(self, *args, **kwargs):
        self.owner = kwargs.pop('owner', None)
        super(TransactionForm, self).__init__(*args, **kwargs)
        if self.owner:
            self.fields['items_sold'].queryset = Item.objects.filter(sold=False, owner=self.owner)
            self.fields['items_bought'].queryset = Item.objects.filter(sold=False, owner=self.owner)

class TradeBuyForm(TransactionForm):
    class Meta(TransactionForm.Meta):
        fields = TransactionForm.Meta.fields + ["items_bought"]
    
    # only items logged in user owns in items field.
    def __init__(self, *args, **kwargs):
        self.owner = kwargs.pop('owner', None)
        super(TransactionForm, self).__init__(*args, **kwargs)
        if self.owner:
            self.fields['items_bought'].queryset = Item.objects.filter(sold=False, owner=self.owner)