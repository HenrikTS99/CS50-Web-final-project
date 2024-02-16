"""
This module contains the models for the TF2Folio app.

The models are used to store data about the users, their items,
transactions and values of items and transactions.
"""

import pycountry
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


TRANSACTION_CHOICES = [
    ('buy', 'Buy'),
    ('sale', 'Sale')
]

SELL_METHOD_CHOICES = [
    ('keys', 'Keys'),
    ('scm_funds', 'Steam Funds'),
    ('paypal', 'PayPal'),
    ('items', 'TF2 Items')
]

CURRENCY_CHOICES = [
    (currency.alpha_3, currency.alpha_3) for currency in pycountry.currencies]

# Create your models here.

class User(AbstractUser):
    """
    Custom User model to store user data.
    Stores the user's items and transactions.
    """
    items = models.ManyToManyField('Item', blank=True, related_name="item_owner")
    transactions = models.ManyToManyField('Transaction', blank=True, related_name="transaction_owner")


class UserMarketSettings(models.Model):
    """
    Model to store user's default currency and key price settings.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='market_settings', null=True)
    default_scm_currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='EUR', null=True, blank=True)
    default_paypal_currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD', null=True, blank=True)
    scm_key_price_dollars = models.DecimalField(max_digits=4, decimal_places=2, default='2.15')
    paypal_key_price_dollars = models.DecimalField(max_digits=4, decimal_places=2, default='1.7')

    def __str__(self):
        return f"{self.user}'s Market Settings"


# Create UserMarketSettings for each user to store market settings.
@receiver(post_save, sender=User)
def create_user_market_settings(sender, instance, created, **_kwargs):
    """
    Signal reciever that creates a UserMarketSettings object for each new user.

    Function is connected to the 'post_save' signal of the User model,
    which is sent at the end of the save() method of the User model.

    Args:
        _sender: The model class that sent the signal.
        instance: The User object that was saved.
        created: A boolean that is True if the User object was created, False if it was updated.
    """
    if created:
        UserMarketSettings.objects.create(user=instance)


class Item(models.Model):
    """
    Model to store data about TF2 items.
    """

    QUALITY = [
        ('unique', 'Unique'),
        ('strange', 'Strange'),
        ('vintage', 'Vintage'),
        ('unusual', 'Unusual'),
        ('genuine', 'Genuine'),
        ('decorated', 'Decorated'),
        ('haunted', 'Haunted'),
        ('collectors', 'Collectors'),
        ('normal', 'Normal')
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

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_items")
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
    purchase_price = models.OneToOneField('Value', on_delete=models.SET_NULL,
                                          related_name="purchase_price_value", default=None, null=True, blank=True)
    sale_price = models.OneToOneField('Value', on_delete=models.SET_NULL,
                                      related_name="sold_item_value", default=None, null=True, blank=True)
    profit_value = models.OneToOneField('Value', on_delete=models.SET_NULL,
                                        related_name="profit_value", default=None, null=True, blank=True)

    @staticmethod
    def create_item(form, user, title, image, particle_id):
        item = form.save(commit=False)
        item.owner = user
        item.item_title = title
        item.image_url = image
        item.particle_id = particle_id
        item.save()
        return item

    def add_sale_price(self, value_object):
        self.sale_price = value_object
        self.save()
    
    def add_profit_value(self, value_object):
        self.profit_value = value_object
        self.save()

    def add_purchase_price(self, value_object):
        self.purchase_price = value_object
        self.save()

    def __str__(self):
        return f"{self.item_title}"


class Value(models.Model):
    """
    Model to store the value of an item or a transaction.

    For items it can store item purchase price, sale price and profit made.

    A Value object can store the value in keys, scm funds or paypal,
    and in diffrent currencies if not in keys.
    """
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="item_value", null=True, blank=True)
    transaction = models.ForeignKey('Transaction', on_delete=models.CASCADE, null=True, blank=True)
    transaction_method = models.CharField(max_length=30, choices=SELL_METHOD_CHOICES, default=('keys', 'Keys'))
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    @staticmethod
    def create_trade_value(form, trade):
        """Create a Value object for a trade."""
        value = form.save(commit=False)
        value.transaction = trade
        value.save()
        return value

    def copy(self):
        """Return a copy of the Value object, without saving it to the database."""
        return Value(item=self.item, transaction=self.transaction, 
                     transaction_method=self.transaction_method, currency=self.currency, amount=self.amount)

    def clean(self):
        """
        Check if the Value object is valid.
        """
        super().clean()
        if self.transaction_method == 'items' and self.item is not None:
            raise ValidationError("The 'items' transaction method is not allowed for Values related to an Item.")

    def __str__(self):
        currency = self.currency if self.currency else ""
        belongs_to = self.item.item_title if self.item else self.transaction.transaction_type
        return f"{belongs_to} - {self.amount} {self.transaction_method} {currency}"


class Transaction(models.Model):
    """
    Model to store data about a trade/transaction between users.
    Keeps track of the items sold and bought, if keys or money was received (transaction_value)
    and the type of transaction (buy/purchase or sale).

    If the trade is a source trade, profit can be calculated if all the items bought/recieved have a sale price.
    """
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name= "user_transactions")
    transaction_value = models.OneToOneField('Value', on_delete=models.SET_NULL, related_name="transaction_value", default=None, null=True, blank=True)
    transaction_type = models.CharField(max_length=4, choices=TRANSACTION_CHOICES)
    items_sold = models.ManyToManyField('Item', blank=True, related_name="sales_transactions")
    items_bought = models.ManyToManyField('Item', blank=True, related_name="buys_transactions")
    description = models.TextField(max_length=400, null=True, blank=True)
    date = models.DateTimeField(null=True, blank=True)
    source_trade = models.BooleanField(default=False) # Means trade is a sale from a item previously bought for pure/cash. Can calculate profit made.

    @staticmethod
    def create_trade(form, user):
        trade = form.save(commit=False)
        trade.owner = user
        trade.date = timezone.now()
        trade.save() # Save the object to generate an id so items can be added to the many-to-many fields
        return trade
    
    def check_if_source_trade(self):
        """
        Check if the trade is a sale of a singular item that was previously bought for pure/cash.
        If so the trade is a source trade and profit can be calculated on the item sold.
        """
        if self.transaction_type == "sale" and self.items_sold.all().count() == 1:
            if self.items_sold.first().purchase_price != None:
                self.source_trade = True
                self.save()

    def add_item(self, item):
        """
        Add an item to the right many-to-many field depending on the transaction type.

        If the transaction is a sale, the item is marked as sold.
        If the transaction is a buy, a Value object is created and added to the item.
        """
        if self.transaction_type == "sale":
            self.items_sold.add(item)
            item.sold = True
            item.save()
        elif self.transaction_type == "buy":
            self.items_bought.add(item)
            value = Value.objects.create(item=item, transaction_method=self.transaction_method, 
                    currency=self.currency, amount=self.amount)
            item.add_purchase_price(value)
            
    def add_items(self, item_list, item_received_list):
        """
        Add all items in the item_list to the transaction,
        and if the transaction is a sale, add the items in the item_received_list to the items_bought field.
        """
        for item in item_list:
            self.add_item(item)
        if self.transaction_type == "sale" and item_received_list:
            for item in item_received_list:
                self.items_bought.add(item)
        self.save()
        self.check_if_source_trade()

    # Properties to get the transaction method, currency and amount from the transaction_value object.
    @property
    def transaction_method(self):
        return self.transaction_value.transaction_method if self.transaction_value else None

    @property
    def currency(self):
        return self.transaction_value.currency if self.transaction_value else None

    @property
    def amount(self):
        return self.transaction_value.amount if self.transaction_value else None

    def __str__(self):
        items_sold_titles = ", ".join([str(item) for item in self.items_sold.all()])
        items_bought_titles = ", ".join([str(item) for item in self.items_bought.all()])
        currency = self.currency if self.currency else ""
        amount = self.amount if self.amount else ""
        if self.transaction_type == "sale":
            return f"{self.owner} sold {items_sold_titles} for {amount} {self.transaction_method} {currency} {items_bought_titles}"
        return f"{self.owner} bought {items_bought_titles} for {amount} {self.transaction_method} {currency}"
