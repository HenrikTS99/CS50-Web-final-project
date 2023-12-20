from django.shortcuts import render
from django.template.loader import render_to_string
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.db import IntegrityError
from django.shortcuts import render
from .models import User, Item, Transaction, Value
from .forms import ItemForm, TradeSaleForm, TradeBuyForm, TransactionForm, ItemValueFormset
from . import utils
import datetime
from django.utils import timezone
from django.http import JsonResponse
import json
import requests



def index(request):
    items = request.user.owned_items.all()
    return render(request, "tf2folio/index.html", {
        "items": items
    })

@login_required
def trade_history(request):
    all_trades = Transaction.objects.filter(owner=request.user).order_by('-date')
    return render(request, "tf2folio/trade-history.html", {
        "all_trades": all_trades
    })

def login_view(request):
    if request.method == 'POST':
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "tf2folio/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "tf2folio/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username =request.POST["username"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "tf2folio/register.html", {
                "message": "Passwords must match."
            })

        try: 
            user = User.objects.create_user(username=username, password=password)
            user.save()
        except IntegrityError:
            return render(request, "tf2folio/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "tf2folio/register.html")

@login_required
def new_item(request):
    if request.method == "POST":
        form = ItemForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.date = datetime.date.today()
            obj.item_title = utils.create_title(obj)
            obj.image_url = utils.create_image(obj)
            if obj.particle_effect:
                obj.particle_id = utils.get_particle_id(obj.particle_effect)
            obj.save()
            return HttpResponseRedirect(reverse("index"))
    
    return render(request, "tf2folio/new-item.html", {
        "form": ItemForm()
    })
    
@login_required
def new_trade(request):
    if request.method == "POST":
        pass

    return render(request, "tf2folio/new-trade.html", {
        "sale_form": TradeSaleForm(owner=request.user), "buy_form": TradeBuyForm(owner=request.user), 
        "item_form": ItemForm(), "value_form": ItemValueFormset()
    })

@login_required
def register_item(request):

    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    form = ItemForm(request.POST)
    formset = ItemValueFormset(request.POST, instance=form.instance)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.owner = request.user
        obj.date = datetime.date.today()
        obj.item_title = utils.create_title(obj)
        obj.image_url = utils.create_image(obj)
        if obj.particle_effect:
            obj.particle_id = utils.get_particle_id(obj.particle_effect)
        obj.save()
    if formset.is_valid():
        instances = formset.save(commit=False)
        for instance in instances:
            instance.item = obj
            instance.save()
            obj.estimated_price = instance
            obj.save()

        item_html = render_to_string('tf2folio/item-template.html', {'item': obj })

        response_data = {
            "message": "Data sent successfully.",
            "item_id": obj.id,
            "item_html": item_html
        }
        return JsonResponse(response_data, status=201)
    return JsonResponse({"message": "Invalid form data."}, status=400)


def get_item_html(request, item_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    try:
        item = Item.objects.get(pk=item_id)
    except Item.DoesNotExist:
        return JsonResponse({"error": "Item not found."}, status=404)

    item_html = render_to_string('tf2folio/item-template.html', {'item': item })
    response_data = {
            "message": "Data sent successfully.",
            "item_html": item_html
        }
    return JsonResponse(response_data, status=201)


def register_trade(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # Get the items selected in the form
    item_ids = json.loads(request.POST['itemIds'])
    item_recieved_ids = json.loads(request.POST['itemRecievedIds'])
    item_list, item_recieved_list = [], []
    for item_id in item_ids:
        try:
            item = Item.objects.get(pk=item_id)
            item_list.append(item)
        except Item.DoesNotExist:
            return JsonResponse({"error": "Item not found."}, status=404)
    for item_id in item_recieved_ids:
        try:
            item = Item.objects.get(pk=item_id)
            item_recieved_list.append(item)
        except Item.DoesNotExist:
            return JsonResponse({"error": "Item not found."}, status=404)

    form = TransactionForm(request.POST)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.owner = request.user
        obj.date = timezone.now()

        obj.save() # Save the object to generate an id

        for item in item_list:
            item.sold = True
            if obj.transaction_type == "sale":
                obj.items_sold.add(item)
            elif obj.transaction_type == "buy":
                obj.items_bought.add(item)
        
        if obj.transaction_type == "sale" and item_recieved_list != []:
            for item in item_recieved_list:
                obj.items_bought.add(item)

        obj.save() # Save the changes to the many-to-many fields

        # If one item is sold only for pure, update the item's sale_price/value
        if len(item_list) == 1 and item_recieved_list == []:
            item = item_list[0]
            value = Value.objects.create(item=item, transaction_method=obj.transaction_method, currency=obj.currency, amount=obj.amount)
            item.sale_price = value
            item.save()
            print(f'{item.item_title} sale price: {item.sale_price}')
            # find the original transaction that item came from
            check_parent_item(item)
           

        transaction_html = render_to_string('tf2folio/transaction-template.html', {'transaction': obj })
        response_data = {
            "message": "Data sent successfully.",
            "transaction_id": obj.id,
            "transaction_html": transaction_html,
            "redirect_url": reverse("trade_history")
        }
        return JsonResponse(response_data, status=201)
    print(form.errors)
    return JsonResponse({"message": "Invalid form data."}, status=400)


def check_parent_item(item):
    origin_trade = Transaction.objects.filter(items_bought=item)
    print(f'origin trade:{origin_trade}')
    if origin_trade:
        origin_trade = origin_trade[0]
        if origin_trade.transaction_type != "sale":
            return
        parent_item = origin_trade.items_sold.all()
        if len(parent_item) == 1:
            parent_item = parent_item[0]
            item_sale_price_objects = []
            for item in origin_trade.items_bought.all():
                if not item.sale_price:
                    print(f'{item.item_title} not sold yet.')
                    return 
                item_sale_price_objects.append(item.sale_price)
            
            print(f'item_sale_values: {item_sale_price_objects}')
            # check if cash in trade, if so, create Value object
            if origin_trade.amount:
                item_sale_price_objects.append(Value.objects.create(item=parent_item, transaction_method=origin_trade.transaction_method, currency=origin_trade.currency, amount=origin_trade.amount))
            parent_item.sale_price = calculate_total_sale_price(item_sale_price_objects)
            parent_item.save()
            print(f'{parent_item.item_title} sale price: {parent_item.sale_price}')




def calculate_total_sale_price(value_objects):
    if all(value_object.transaction_method == value_objects[0].transaction_method for value_object in value_objects):
        # all the same transaction method
        print("Same transaction method")
        return Value.objects.create(item=value_objects[0].item, transaction_method=value_objects[0].transaction_method, 
                currency=value_objects[0].currency, amount=sum([value_object.amount for value_object in value_objects]))
        
    else:
        # implement the currency conversion and get key price.
        pass

USD_KEY_PRICES = {
    'scm_funds': 2.2,
    'paypal': 1.7
}

def convert_currency(amount, from_currency, to_currency='USD'):

    url = f'https://api.exchangerate-api.com/v4/latest/{to_currency}'
    response = requests.get(url)
    data = response.json()
    return amount/data['rates'][from_currency]

def get_key_price(currency, transaction_method):
    return currency/USD_KEY_PRICES[transaction_method]
                        

        

    

