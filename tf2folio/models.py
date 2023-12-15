from django.contrib.auth.models import AbstractUser
from django.db import models
import pycountry

# Create your models here.

class User(AbstractUser):
    items = models.ManyToManyField('Item', blank=True, related_name="item_owner")
    transactions = models.ManyToManyField('Transaction', blank=True, related_name="transaction_owner")

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
    # date_arrived = models.DateTimeField(null=True, blank=True)
    # date_sold = models.DateTimeField(null=True, blank=True)
    image_url = models.URLField(max_length=400, null=True, blank=True)

    def __str__(self):
        return f"{self.item_title}"


class Transaction(models.Model):
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
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name= "user_transactions", default=None)
    transaction_type = models.CharField(max_length=4, choices=TRANSACTION_CHOICES)
    transaction_method = models.CharField(max_length=30, choices=SELL_METHOD_CHOICES)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    items_sold = models.ManyToManyField('Item', blank=True, related_name="sales_transactions")
    items_bought = models.ManyToManyField('Item', blank=True, related_name="buys_transactions")
    description = models.TextField(max_length=400, null=True, blank=True)
    date = models.DateTimeField(null=True, blank=True)