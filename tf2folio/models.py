from django.contrib.auth.models import AbstractUser
from django.db import models
import pycountry
from django.utils import timezone
import datetime
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
    items = models.ManyToManyField('Item', blank=True, related_name="item_owner")
    transactions = models.ManyToManyField('Transaction', blank=True, related_name="transaction_owner")
    

class UserMarketSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='market_settings', null=True)
    default_scm_currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='EUR', null=True, blank=True)
    default_paypal_currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD', null=True, blank=True)
    scm_key_price_dollars = models.DecimalField(max_digits=4, decimal_places=2, default='2.2')
    paypal_key_price_dollars = models.DecimalField(max_digits=4, decimal_places=2, default='1.7')

    def __str__(self):
        return f"{self.user} Market Settings"


# Create UserMarketSettings for each user to store market settings. post_save signal is when the a save event occurs for the User.
@receiver(post_save, sender=User)
def create_user_market_settings(sender, instance, created, **kwargs):
    if created:
        UserMarketSettings.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_market_settings(sender, instance, **kwargs):
    instance.market_settings.save()


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
    purchase_price = models.OneToOneField('Value', on_delete=models.SET_NULL, related_name="purchase_price_value", default=None, null=True, blank=True)
    sale_price = models.OneToOneField('Value', on_delete=models.SET_NULL, related_name="sold_item_value", default=None, null=True, blank=True)
    profit_value = models.OneToOneField('Value', on_delete=models.SET_NULL, related_name="profit_value", default=None, null=True, blank=True)

    @classmethod
    def create_item(cls, form, user, title, image, particle_id):
        item = form.save(commit=False)
        item.owner = user
        item.date = datetime.date.today()
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

    def get_and_add_profit_value(self):
        if self.purchase_price:
            from .utils import get_item_profit_value #Import here to avoid circular import
            profit_value = get_item_profit_value(self)
            if profit_value:
                self.profit_value = profit_value
                self.save()

    def add_purchase_price(self, value_object):
        self.purchase_price = value_object
        self.save()

    def __str__(self):
        return f"{self.item_title}"


class Value(models.Model):

    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="item_value", null=True, blank=True)
    transaction = models.ForeignKey('Transaction', on_delete=models.CASCADE, null=True, blank=True)
    transaction_method = models.CharField(max_length=30, choices=SELL_METHOD_CHOICES, default=('keys', 'Keys'))
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    @classmethod
    def create_trade_value(cls, form, trade):
        value = form.save(commit=False)
        value.transaction = trade
        value.save()
        return value

    def copy(self):
        return Value(item=self.item, transaction_method=self.transaction_method, currency=self.currency, amount=self.amount)

    def clean(self):
        super().clean()

        if self.transaction_method == 'items' and self.item is not None:
            raise ValidationError("The 'items' transaction method is not allowed for Values related to an Item.")

    def __str__(self):
        currency = self.currency if self.currency else ""
        belongs_to = self.item.item_title if self.item else self.transaction.transaction_type
        return f"{belongs_to} - {self.amount} {self.transaction_method} {currency}"


class Transaction(models.Model):

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name= "user_transactions", default=None)
    transaction_value = models.OneToOneField('Value', on_delete=models.SET_NULL, related_name="transaction_value", default=None, null=True, blank=True)
    transaction_type = models.CharField(max_length=4, choices=TRANSACTION_CHOICES)
    items_sold = models.ManyToManyField('Item', blank=True, related_name="sales_transactions")
    items_bought = models.ManyToManyField('Item', blank=True, related_name="buys_transactions")
    description = models.TextField(max_length=400, null=True, blank=True)
    date = models.DateTimeField(null=True, blank=True)
    source_trade = models.BooleanField(default=False) # Means trade is a sale from a item previously bought for pure/cash. Can calculate profit made.
    #subsequent_trades = models.ManyToManyField('Transaction', blank=True, related_name="subsequent_trades")
    #origin_trade = models.ForeginKey('Transaction', on_delete=models.SET_NULL, null=True, blank=True, related_name='child_trades')

    @classmethod
    def create_trade(cls, form, user, item_list, item_received_list):
        trade = form.save(commit=False)
        trade.owner = user
        trade.date = timezone.now()
        trade.save() # Save the object to generate an id so items can be added to the many-to-many fields
        return trade
    
    def check_if_source_trade(self):
        if self.transaction_type == "sale" and self.items_sold.all().count() == 1:
            if self.items_sold.first().purchase_price != None:
                self.source_trade = True
                self.save()

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
            value = Value.objects.create(item=item, transaction_method=self.transaction_method, 
                    currency=self.currency, amount=self.amount)
            item.add_purchase_price(value)
            
    def add_items(self, item_list, item_received_list):
        for item in item_list:
            self.add_item(item)
        if self.transaction_type == "sale" and item_received_list:
            for item in item_received_list:
                self.items_bought.add(item)
        self.save()
        self.check_if_source_trade()
    
    def total_pure_received(self):
        pass

    def __str__(self):
        items_sold_titles = ", ".join([str(item) for item in self.items_sold.all()])
        items_bought_titles = ", ".join([str(item) for item in self.items_bought.all()])
        currency = self.currency if self.currency else ""
        amount = self.amount if self.amount else ""
        if self.transaction_type == "sale":
            return f"{self.owner} sold {items_sold_titles} for {amount} {self.transaction_method} {currency} {items_bought_titles}"
        return f"{self.owner} bought {items_bought_titles} for {amount} {self.transaction_method} {currency}"

