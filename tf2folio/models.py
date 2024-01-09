from django.contrib.auth.models import AbstractUser
from django.db import models
import pycountry

TRANSACTION_CHOICES = [
    ('buy', 'Buy'),
    ('sale', 'Sale')
]

SELL_METHOD_CHOICES = [
    ('keys', 'Keys'),
    ('scm_funds', 'Steam Wallet Funds'),
    ('paypal', 'PayPal'),
    ('items', 'TF2 Items')
]

CURRENCY_CHOICES = [
    (currency.alpha_3, currency.alpha_3) for currency in pycountry.currencies]

# Create your models here.

class User(AbstractUser):
    items = models.ManyToManyField('Item', blank=True, related_name="item_owner")
    transactions = models.ManyToManyField('Transaction', blank=True, related_name="transaction_owner")
    default_scm_currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='NOK', null=True, blank=True)
    default_paypal_currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD', null=True, blank=True)

class Item(models.Model):

    QUALITY = [
        ('unique', 'Unique'),
        ('strange', 'Strange'),
        ('vintage', 'Vintage'),
        ('unusual', 'Unusual'),
        ('genuine', 'Genuine'),
        ('decorated', 'Decorated'),
        ('haunted', 'Haunted'),
        ('collectors', 'Collectors'),
        ('normal', 'Normal'),
    ]

    WEAR_TIERS = [
        ('factory_new', 'Factory New'),
        ('minimal_wear','Minimal Wear'),
        ('field_tested','Field-Tested'),
        ('well_worn','Well-Worn'),
        ('battle_scarred','Battle Scarred')
    ]

    KILLSTREAK_TIERS = [
        ('standard', 'Standard'),
        ('specialized', 'Specialized'),
        ('professional', 'Professional')
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_items", default=None)
    item_name = models.CharField(max_length=150)
    item_title = models.CharField(max_length=250, blank=True)
    quality = models.CharField(max_length=20, choices=QUALITY)
    craftable = models.BooleanField(default=True)
    australium = models.BooleanField(default=False)
    texture_name = models.CharField(max_length=64, null=True, blank=True)
    wear = models.CharField(max_length=20, choices=WEAR_TIERS, blank=True)
    particle_effect = models.CharField(max_length=64, blank=True)
    particle_id = models.CharField(max_length=4, blank=True, null=True)
    description = models.TextField(max_length=400, null=True, blank=True)
    killstreak = models.CharField(max_length=20, choices=KILLSTREAK_TIERS, null=True, blank=True)
    sold = models.BooleanField(default=False)
    image_url = models.URLField(max_length=400, null=True, blank=True)
    estimated_price = models.OneToOneField('Value', on_delete=models.SET_NULL, related_name="estimated_item_value", default=None, null=True, blank=True)
    purchase_price = models.OneToOneField('Value', on_delete=models.SET_NULL, related_name="purchase_price_value", default=None, null=True, blank=True)
    sale_price = models.OneToOneField('Value', on_delete=models.SET_NULL, related_name="sold_item_value", default=None, null=True, blank=True)

        
    def add_sale_price(self, value_object):
        self.sale_price = value_object
        self.save()

    def add_purchase_price(self, value_object):
        self.purchase_price = value_object
        self.save()

    def profit(self):
        if self.purchase_price and self.sale_price:
            profit = self.sale_price.amount - self.purchase_price.amount
            profit = str(profit).rstrip('0').rstrip('.') if '.' in str(profit) else profit
            currency = self.purchase_price.currency if self.purchase_price.currency else ""
            return f'{profit} {currency} {self.purchase_price.get_transaction_method_display()}'
        return None

    def __str__(self):
        return f"{self.item_title}"


class Value(models.Model):

    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="item_value", null=True, blank=True)
    transaction = models.ForeignKey('Transaction', on_delete=models.CASCADE, null=True, blank=True)
    transaction_method = models.CharField(max_length=30, choices=SELL_METHOD_CHOICES, default=('keys', 'Keys'))
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    @classmethod
    def create_for_item(cls, item, transaction_method, currency, amount):
        return cls.objects.create(item=item, transaction_method=transaction_method, currency=currency, amount=amount)

    def clean(self):
        # Call the superclass's clean method to perform default validation
        super().clean()

        # Check if the transaction_method is 'items' and the Value is related to an Item
        if self.transaction_method == 'items' and self.item is not None:
            raise ValidationError("The 'items' transaction method is not allowed for Values related to an Item.")

    def __str__(self):
        currency = self.currency if self.currency else ""
        belongs_to = self.item.item_title if self.item else self.transaction.transaction_type
        return f"{belongs_to} - {self.amount} {self.transaction_method} {currency}"


class Transaction(models.Model):
    TRANSACTION_METHOD_CHOICES = SELL_METHOD_CHOICES + [('items', 'TF2 Items')]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name= "user_transactions", default=None)
    transaction_value = models.OneToOneField('Value', on_delete=models.SET_NULL, related_name="transaction_value", default=None, null=True, blank=True)
    transaction_type = models.CharField(max_length=4, choices=TRANSACTION_CHOICES)
    # transaction_method = models.CharField(max_length=30, choices=TRANSACTION_METHOD_CHOICES, default=('keys', 'Keys'))
    # currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, null=True, blank=True)
    # amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    items_sold = models.ManyToManyField('Item', blank=True, related_name="sales_transactions")
    items_bought = models.ManyToManyField('Item', blank=True, related_name="buys_transactions")
    description = models.TextField(max_length=400, null=True, blank=True)
    date = models.DateTimeField(null=True, blank=True)

    @property
    def transaction_method(self):
        return self.transaction_value.transaction_method if self.transaction_value else None

    @property
    def currency(self):
        return self.transaction_value.currency if self.transaction_value else None

    @property
    def amount(self):
        return self.transaction_value.amount if self.transaction_value else None

    def add_item(self, item):
        if self.transaction_type == "sale":
            self.items_sold.add(item)
            item.sold = True
            item.save()
        elif self.transaction_type == "buy":
            self.items_bought.add(item)
            value = Value.create_for_item(item=item, transaction_method=self.transaction_method, 
                    currency=self.currency, amount=self.amount)
            item.add_purchase_price(value)
            

    def add_items(self, item_list, item_recieved_list):
        for item in item_list:
            self.add_item(item)
        if self.transaction_type == "sale" and item_recieved_list:
            for item in item_recieved_list:
                self.items_bought.add(item)
        self.save()
    
    def total_pure_recieved(self):
        pass

    def __str__(self):
        items_sold_titles = ", ".join([str(item) for item in self.items_sold.all()])
        items_bought_titles = ", ".join([str(item) for item in self.items_bought.all()])
        currency = self.currency if self.currency else ""
        amount = self.amount if self.amount else ""
        if self.transaction_type == "sale":
            return f"{self.owner} sold {items_sold_titles} for {amount} {self.transaction_method} {currency} {items_bought_titles} on {self.date}"
        return f"{self.owner} bought {items_bought_titles} for {amount} {self.transaction_method} {currency} on {self.date}"

