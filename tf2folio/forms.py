from django.forms import ModelForm, inlineformset_factory
from .models import Item, Transaction, Value
from django import forms
from django.core.exceptions import ValidationError


TRANSACTION_WIDGETS = {
            'transaction_method': forms.Select(attrs={'class': 'transaction-method'}),
            'amount': forms.NumberInput(attrs={'class': 'amount-field'}),
            'currency': forms.TextInput(attrs={'class': 'currency-field'}),
        }

class ItemForm(ModelForm):
    class Meta:
        model = Item
        fields = ("item_name", "quality", "craftable", "australium", "texture_name",
            "wear", "particle_effect", "description", "killstreak")


class BaseItemValueFormSet(forms.BaseInlineFormSet):
    validate_empty_forms = False
    def __init__(self, *args, **kwargs):
        self.owner = kwargs.pop('owner', None)
        super(BaseItemValueFormSet, self).__init__(*args, **kwargs)

    def add_fields(self, form, index):
        super(BaseItemValueFormSet, self).add_fields(form, index)
        if self.owner:
            form.fields['currency'].initial = self.owner.default_scm_currency

    def clean(self):
        super().clean()

        for form in self.forms:
            if form.is_valid():
                transaction_method = form.cleaned_data.get("transaction_method")
                currency = form.cleaned_data.get("currency")

                if transaction_method in ['scm_funds', 'paypal'] and not currency:
                    raise ValidationError("The 'currency' field is required when transaction method is SCM Funds or PayPal.")
            else:
                print("form is not valid")

    def save(self, commit=True):
        instances = super().save(commit=False)

        for instance in instances:
            if instance.amount is None:
                # should only ever be one form in the formset, therefore only one instance
                print("amount is none")
                return []
            if instance.transaction_method not in ['scm_funds', 'paypal'] and instance.currency:
                instance.currency = None
            if commit:
                instance.save()
        return instances

ItemValueFormset = inlineformset_factory(
    Item, Value, fields=("transaction_method", "currency", "amount"),
    widgets=TRANSACTION_WIDGETS, 
    extra=1, can_delete=False,
    formset=BaseItemValueFormSet)


class ValueForm(forms.ModelForm):
    class Meta:
        model = Value
        fields = ['transaction_method', 'currency', 'amount']
        widgets = TRANSACTION_WIDGETS

    def clean(self):
        cleaned_data = super().clean()
        transaction_method = cleaned_data.get("transaction_method")
        currency = cleaned_data.get("currency")
        amount = cleaned_data.get("amount")

        if transaction_method not in 'items' and not amount:
            raise ValidationError({'amount': "Amount is required."})

        if currency and not currency.isupper():
            cleaned_data["currency"] = currency.upper()

        if transaction_method in ['scm_funds', 'paypal'] and not currency:
            raise ValidationError({'currency': "Currency is required when transaction method is Steam Wallet Funds or PayPal."})

        return cleaned_data


class TransactionForm(ModelForm):
    class Meta:
        model = Transaction
        fields = ["transaction_type", "description"]
        widgets = TRANSACTION_WIDGETS
    
    # def clean(self):
    #     cleaned_data = super().clean()
    #     transaction_method = cleaned_data.get("transaction_method")
    #     currency = cleaned_data.get("currency")
    #     amount = cleaned_data.get("amount")

    #     if transaction_method not in 'items' and not amount:
    #         raise ValidationError({'amount': "Amount is required."})

    #     if currency and not currency.isupper():
    #         cleaned_data["currency"] = currency.upper()

    #     if transaction_method in ['scm_funds', 'paypal'] and not currency:
    #         raise ValidationError({'currency': "Currency is required when transaction method is Steam Wallet Funds or PayPal."})
        
    #     return cleaned_data

TransactionValueFormset = inlineformset_factory(
    Transaction, Value, form=ValueForm,
    widgets=TRANSACTION_WIDGETS, 
    extra=1, can_delete=False)

class TradeSaleForm(TransactionForm):
    class Meta(TransactionForm.Meta):
        fields = TransactionForm.Meta.fields + ["items_sold"] + ["items_bought"]

        widgets = TRANSACTION_WIDGETS

    # only items logged in user owns in items field.
    def __init__(self, *args, **kwargs):
        self.owner = kwargs.pop('owner', None)
        super(TransactionForm, self).__init__(*args, **kwargs)
        if self.owner:
            self.fields['items_sold'].queryset = Item.objects.filter(sold=False, owner=self.owner)
            self.fields['items_bought'].queryset = Item.objects.filter(sold=False, owner=self.owner)
            #self.fields['currency'].initial = self.owner.default_scm_currency

class TradeBuyForm(TransactionForm):
    class Meta(TransactionForm.Meta):
        fields = TransactionForm.Meta.fields + ["items_bought"]
    
    # only items logged in user owns in items field.
    def __init__(self, *args, **kwargs):
        self.owner = kwargs.pop('owner', None)
        super(TransactionForm, self).__init__(*args, **kwargs)
        if self.owner:
            self.fields['items_bought'].queryset = Item.objects.filter(sold=False, owner=self.owner)