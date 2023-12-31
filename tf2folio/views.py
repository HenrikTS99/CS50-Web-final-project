from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.db import IntegrityError
from .models import User, Item, Transaction, Value
from .forms import ItemForm, TradeSaleForm, TradeBuyForm, TransactionForm, ItemValueFormset, ValueForm
from . import utils
import datetime
from django.utils import timezone
from django.http import JsonResponse
import json
import requests
from django.template.loader import render_to_string

@login_required
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
    if request.method != "GET":
        pass

    return render(request, "tf2folio/new-trade.html", {
        "sale_form": TradeSaleForm(owner=request.user), "buy_form": TradeBuyForm(owner=request.user), 
        "item_form": ItemForm(), "item_value_form": ItemValueFormset(owner=request.user),
        "value_form": ValueForm(),
        "user": request.user
    })


@require_POST
@login_required
def register_item(request):
    form = ItemForm(request.POST)
    formset = ItemValueFormset(request.POST, instance=form.instance)

    if form.is_valid():
        item = utils.save_item(form, request.user)
        if formset.is_valid():
            utils.add_estimated_price_to_item(formset, item)
        else:
            print(formset.errors)
        item_html = render_to_string('tf2folio/item-template.html', {'item': item })
        response_data = {
            "message": "Data sent successfully.",
            "item_id": item.id,
            "item_html": item_html
        }
        return JsonResponse(response_data, status=201)
    return JsonResponse({"message": "Invalid form data."}, status=400)

@require_POST
def get_item_html(request, item_id):
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
    print(request.POST)
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # Get the items selected in the form
    item_list, item_recieved_list, response, = utils.process_items(request)
    # Error handling
    if response:
        return response
    
    form = TransactionForm(request.POST)
    valueForm = ValueForm(request.POST)
    if form.is_valid():
        trade = form.save(commit=False)
        trade.owner = request.user
        trade.date = timezone.now()
        
        trade.save() # Save the object to generate an id so items can be added to the many-to-many fields
        if valueForm.is_valid():
            value = valueForm.save(commit=False)
            value.transaction = trade
            value.save()
            trade.transaction_value = value
            trade.save()
            #utils.add_estimated_price_to_item(valueForm, trade)
        #trade.transaction_value = Value.objects.create(transaction=trade, transaction_method=trade.transaction_method, 
         #       currency=trade.currency, amount=trade.amount)
        #trade.save()
        trade.add_items(item_list, item_recieved_list) # Add the items to the many-to-many fields

        # If one item is sold only for pure, update the item's sale_price/value
        print(item_recieved_list)
        if len(item_list) == 1 and not item_recieved_list and request.POST.get('transaction_type') == 'sale':
            print("logging pure sale")
            utils.process_pure_sale(item_list[0], trade)
        
        response_data = utils.create_trade_response_data(trade)
        return JsonResponse(response_data, status=201)
    # Form is not valid
    print(form.errors)
    return JsonResponse({"errors": form.errors}, status=400)


                        

        

    

