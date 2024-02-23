"""
This module contains the views for the application. It includes import statements for Django shortcuts, 
decorators, authentication, HTTP responses, URL reversing, database models, forms, and utility functions.
"""

from django.shortcuts import render
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db import IntegrityError
from django.db.models import Q
from django.http import JsonResponse
from django.template.loader import render_to_string
from .models import User, Item, Transaction
from .forms import ItemForm, TradeSaleForm, TradeBuyForm, TradeValueForm, CurrencySettingsForm
from . import utils

@login_required
def index(request):
    """
    Function for getting the inventory page and also serves as the default Index page.
    Displays all items in the users inventory, and all items the user has sold.
    """
    items = Item.objects.filter(Q(sold=False) & Q(owner=request.user))
    sold_items = Item.objects.filter(Q(sold=True) & Q(owner=request.user))

    return render(request, "tf2folio/inventory.html", {
        "items": items, 'sold_items': sold_items
    })


@login_required
def trade_history(request, page=1):
    """
    Fetches and displays all of a users trades. Uses pagination to create pages.
    If the user has selected to 'show only source trades' on the HTML page, it instead fetches and 
    diplays all the source trades instead of all trades.
    
    A 'source trade' refers to a transaction that allows for profit calculation, 
    since the trade is a sale from a item previously bought for pure/cash.
    """
    source_trades = request.GET.get('source_trades', False)

    if source_trades:
        trades = Transaction.objects.filter(Q(owner=request.user) 
                                            & Q(source_trade=True)).order_by('-date')
    else:
        trades = Transaction.objects.filter(owner=request.user).order_by('-date')

    all_trades = utils.paginate(trades, page)
    return render(request, "tf2folio/trade-history.html", {
        "all_trades": all_trades
    })


@login_required
def item_trade_history(request, item_id):
    """
    Fetches and returns all the trades involving a specific item

    Q-objects info: https://docs.djangoproject.com/en/5.0/topics/db/queries/#complex-lookups-with-q-objects

    Returns:
        trade-history template with all the trades the specific item is in
    """
    item_trades = Transaction.objects.filter(
        Q(owner=request.user) & (Q(items_sold__id=item_id) | Q(items_bought__id=item_id))
    ).order_by('-date')
    return render(request, "tf2folio/trade-history.html", {
        "all_trades": item_trades,
    })


@login_required
def currency_settings(request):
    """
    Displays and handles the currency settings form. If the form is valid, 
    the settings are saved and the user is redirected to the index page.
    If the form is invalid, the form errors are displayed on the HTML page.

    The current key price in USD from the SCM is retrieved and displayed on the page.
    """
    scm_key_price_usd = utils.get_current_key_sell_order()
    form = CurrencySettingsForm(request.POST or None, instance=request.user.market_settings)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("index"))

    return render(request, "tf2folio/currency-settings.html", {
        "settings_form": form, "scm_key_price_usd": scm_key_price_usd
    })


def login_view(request):
    """
    Handles the login form. If the form is valid, the user is logged in and redirected to the index page.
    If the form is invalid, the user recieves a error message.
    """
    if request.method == 'POST':
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user:
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
    return HttpResponseRedirect(reverse("login"))


def register(request):
    """
    Handles user registration. If the form is valid, the user is registered and logged in.
    If the form is invalid, the user recieves a error message.
    """
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
    
    return render(request, "tf2folio/register.html")


@require_GET
@login_required
def new_trade(request):
    """
    Displays the new trade form. Retrives all necessary forms and data for the HTML page.
    
    User is used to get the user's default currency settings in the form.
    'particle effects' and 'texture names' are used to autocomplete
    the input fields on the HTML page for registering new items.
    """
    user_market_settings = request.user.market_settings
    return render(request, "tf2folio/new-trade.html", {
        "sale_form": TradeSaleForm(owner=request.user), "buy_form": TradeBuyForm(owner=request.user), 
        "item_form": ItemForm(),
        "value_form": TradeValueForm(),
        "user_market_settings": user_market_settings,
        "particle_effects": list(utils.PARTICLE_EFFECTS_MAPPING.values()),
        "texture_names": utils.TEXTURE_NAMES,
    })


@require_POST
@login_required
def register_item(request):
    """
    Handles the registration of new items. If the form is valid, the necessary item data is generated.
    Creates and saves the item object to the database. Returns a JSON response with the item's HTML template
    for displaying the item and the item ID.
    """
    form = ItemForm(request.POST)
    error_response = utils.validate_form(form)
    if error_response:
        return error_response

    item_title, item_image, item_particle_id = utils.create_item_data(form)

    # If user has entered an image link, use that instead of generated image
    item_image_link = form.cleaned_data.get("image_link")
    if item_image_link:
        item_image = item_image_link

    item = Item.create_item(form, request.user, item_title, item_image, item_particle_id)

    item_html = render_to_string('tf2folio/item-template.html', 
                                {'item': item, 'link_enabled': 'False'}) # Django template boolean values are strings
    response_data = {
        "message": "Data sent successfully.",
        "item_id": item.id,
        "item_html": item_html
    }
    return JsonResponse(response_data, status=201)


@require_POST
@login_required
def get_item_data(request):
    """
    Gets the item data from the form and returns a JSON response with the item's image URL, particle ID, and title.
    For creating the item preview in item register form.
    """
    form = ItemForm(request.POST)
    error_response = utils.validate_form(form)
    if error_response:
        return error_response

    item_title, item_image, item_particle_id = utils.create_item_data(form)

    if not item_image:
        return JsonResponse({"error": "Image could not be generated."}, status=404)

    response_data = {
        "message": "image generated successfully.",
        "image_url": item_image,
        "particle_id": item_particle_id,
        "item_title": item_title
    }
    return JsonResponse(response_data, status=201)


@require_POST
@login_required
def get_item_html(request, item_id):
    """
    Fetches the item object from the database and returns the item's HTML template for displaying the item.
    """
    try:
        item = Item.objects.get(pk=item_id)
    except Item.DoesNotExist:
        return JsonResponse({"error": "Item not found."}, status=404)
    item_html = render_to_string('tf2folio/item-template.html',
                {'item': item, 'link_enabled': 'False' })
    
    response_data = {
            "message": "Data sent successfully.",
            "item_html": item_html
        }
    return JsonResponse(response_data, status=201)


@require_POST
@login_required
def register_trade(request):
    """
    Registers a new trade.

    This function handles the registration of new trades. If the forms are valid and there is no errors,
    the necessary trade data is generated, and the trade object is created and saved to the database.

    If any of the functions in 'process_trade_request' return an error response, 
    this error is returned as a JSON response.

    Returns:
        A JSON response. If the trade registration is successful, this response contains the trade history redirect URL. 
        If there is an error, the response contains the error message.
    """
    (
        transaction_method,
        item_list,
        item_received_list,
        form,
        value_form,
        error_response
    ) = utils.process_trade_request(request)
    
    if error_response:
        return error_response
    trade = utils.create_trade_and_add_items(form, value_form, transaction_method,
                               request.user, item_list, item_received_list)
    utils.check_if_pure_sale(item_list, item_received_list, trade)

    response_data = {
            "message": "Trade registered successfully.",
            "redirect_url": reverse("trade_history"),
        }
    return JsonResponse(response_data, status=201)
