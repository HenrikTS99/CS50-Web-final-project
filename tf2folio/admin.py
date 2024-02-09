from django.contrib import admin
from .models import User, Item, Transaction, Value, UserMarketSettings
# Register your models here.

admin.site.register(User)
admin.site.register(Item)
admin.site.register(Transaction)
admin.site.register(Value)
admin.site.register(UserMarketSettings)