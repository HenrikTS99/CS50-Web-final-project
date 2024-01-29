from django.forms import ModelForm, inlineformset_factory
from .models import Item, Transaction, Value, SELL_METHOD_CHOICES
from django import forms
from django.core.exceptions import ValidationError


TRANSACTION_WIDGETS = {
            'transaction_method': forms.Select(attrs={'class': 'transaction-method'}),
            'amount': forms.NumberInput(attrs={'class': 'amount-field'}),
            'currency': forms.TextInput(attrs={'class': 'currency-field'}),
        }

TRANSACTION_METHOD_KEYS = 'keys'
TRANSACTION_METHOD_SCM_FUNDS = 'scm_funds'
TRANSACTION_METHOD_PAYPAL = 'paypal'
TRANSACTION_METHOD_ITEMS = 'items'

class ItemForm(ModelForm):
    quality = forms.ChoiceField(
        choices=Item.QUALITY,
        widget=forms.RadioSelect,
    )
    wear = forms.ChoiceField(
        choices=[('', 'None')] + Item.WEAR_TIERS,
        widget=forms.RadioSelect,
        required=False,
    )
    killstreak = forms.ChoiceField(
        choices=[('', 'None')] + Item.KILLSTREAK_TIERS,
        widget=forms.RadioSelect,
        required=False,
    )
    item_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'item-input-field', 'placeholder': 'Item Name'}),
    )
    texture_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'item-input-field', 'placeholder': 'Texture Name'}),
        required=False,
    )
    particle_effect = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'item-input-field', 'placeholder': 'Particle Effect'}),
        required=False,
    )
    craftable = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'checkbox-input'}),
        required=False, initial=True,
    )
    australium = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'checkbox-input'}),
        required=False,
    )
    image_link = forms.URLField(required=False)

    class Meta:
        model = Item
        fields = ("item_name", "quality", "craftable", "australium", "texture_name",
            "wear", "particle_effect", "description", "killstreak")


class BaseValueForm(forms.ModelForm):
    transaction_method = forms.ChoiceField(
            choices=SELL_METHOD_CHOICES,
            widget=forms.RadioSelect,
            initial=('keys', 'Keys'),
        )

    class Meta:
        model = Value
        fields = ['transaction_method', 'currency', 'amount']
        widgets = TRANSACTION_WIDGETS

    def clean(self):
        cleaned_data = super().clean()
        currency = cleaned_data.get("currency")
        transaction_method = cleaned_data.get("transaction_method")

        if currency and not currency.isupper():
            cleaned_data["currency"] = currency.upper()

        if transaction_method in [TRANSACTION_METHOD_SCM_FUNDS, TRANSACTION_METHOD_PAYPAL] and not currency:
            raise ValidationError({'currency': "Currency is required when transaction method is Steam Wallet Funds or PayPal."})

        return cleaned_data


class ItemValueForm(BaseValueForm):
    # Exclude items from transaction method choices for item value form
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['transaction_method'].choices = [
            choice for choice in self.fields['transaction_method'].choices if choice[0] != TRANSACTION_METHOD_ITEMS
        ]
        
        
class TradeValueForm(BaseValueForm):
    class Meta:
        model = Value
        fields = ['transaction_method', 'currency', 'amount']
        widgets = TRANSACTION_WIDGETS

    def clean(self):
        cleaned_data = super().clean()
        transaction_method = cleaned_data.get("transaction_method")
        currency = cleaned_data.get("currency")
        amount = cleaned_data.get("amount")

        if transaction_method != TRANSACTION_METHOD_ITEMS and not amount:
            raise ValidationError({'amount': "Amount is required. If it's a item's only transaction, please select 'TF2 Items' as the transaction method."})

        return cleaned_data


class TransactionForm(ModelForm):
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'textarea-notes', 'placeholder': 'Notes'}),
        required=False,
    )
    class Meta:
        model = Transaction
        fields = ["transaction_type", "description"]
        widgets = TRANSACTION_WIDGETS


class TradeSaleForm(TransactionForm):
    class Meta(TransactionForm.Meta):
        fields = TransactionForm.Meta.fields + ["items_sold"] + ["items_bought"]
        widgets = TRANSACTION_WIDGETS

    # only items logged-in user owns in items field.
    def __init__(self, *args, **kwargs):
        self.owner = kwargs.pop('owner', None)
        super(TransactionForm, self).__init__(*args, **kwargs)
        if self.owner:
            self.fields['items_sold'].queryset = Item.objects.filter(sold=False, owner=self.owner)
            self.fields['items_bought'].queryset = Item.objects.filter(sold=False, owner=self.owner)
            

class TradeBuyForm(TransactionForm):
    class Meta(TransactionForm.Meta):
        fields = TransactionForm.Meta.fields + ["items_bought"]
    
    # only items logged-in user owns in items field.
    def __init__(self, *args, **kwargs):
        self.owner = kwargs.pop('owner', None)
        super(TransactionForm, self).__init__(*args, **kwargs)
        if self.owner:
            self.fields['items_bought'].queryset = Item.objects.filter(sold=False, owner=self.owner)