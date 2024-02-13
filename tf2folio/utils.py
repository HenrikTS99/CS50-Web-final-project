import requests
import os
import json
from cachetools import cached, TTLCache
from .models import Item, Value, Transaction
from django.template.loader import render_to_string
from django.urls import reverse
from decimal import Decimal, ROUND_DOWN
import time
from django.http import JsonResponse
from django.core.paginator import Paginator
from .forms import TransactionForm, TradeValueForm

# Load particle effects and warpaints dicts and lists from JSON files
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_json(filename):
    file_path = os.path.join(BASE_DIR, 'tf2folio', 'data', filename)
    with open(file_path, 'r') as f:
        return json.load(f)

PARTICLE_EFFECTS_MAPPING = load_json('particle_effects_mapping.json')
REVERSE_PARTICLE_MAPPING_LOWER = {v.lower(): k for k, v in PARTICLE_EFFECTS_MAPPING.items()}

WAR_PAINTS = load_json('war_paints.json')
WEAPON_SKINS_LIST = load_json('weapon_skins.json')

TEXTURE_NAMES = WAR_PAINTS + WEAPON_SKINS_LIST

# Create a cache that expires after 1 hour
cache = TTLCache(maxsize=10, ttl=3600)

conversion_rates_cache = {}

def paginate(posts, request, page):
    p = Paginator(posts, 10)
    return p.get_page(page)

    
def create_item_data(form):
    item = form.save(commit=False)
    title = create_title(item)
    image_url = create_image(item)
    particle_id = get_particle_id(item.particle_effect)
    return title, image_url, particle_id


def create_title(Item):
    title_parts = []
    if not Item.craftable:
        title_parts.append('Uncraftable')
    if Item.quality != 'unique':
        title_parts.append(Item.quality.title())
    if Item.killstreak:
        killstreak_title = ('Killstreak' if Item.killstreak == 'standard' 
                            else f"{Item.killstreak.title()} Killstreak")
        title_parts.append(killstreak_title)
    if Item.australium:
        title_parts.append('Australium')
    if Item.texture_name:
        title_parts.append(Item.texture_name.title())
    if Item.particle_effect:
        title_parts.append(Item.particle_effect.title())

    title_parts.append(Item.item_name)

    if Item.texture_name:
        if not Item.wear:
            Item.wear = 'Factory New'
        title_parts.append(f"({Item.get_wear_display().title()})")
    return ' '.join(title_parts)


def create_image(Item):
    search_name = ''
    # Warpaints
    if Item.texture_name:
        if Item.quality == 'decorated':
            search_name = f'{Item.texture_name} {Item.item_name} ({Item.get_wear_display().title()})'
        else:
            search_name = f'{Item.quality} {Item.texture_name} {Item.item_name} ({Item.get_wear_display().title()})'

    # Australium
    elif Item.australium:
        search_name = f'Strange Australium {Item.item_name}'

    elif Item.quality == 'unique':
        search_name = Item.item_name
    else:
        search_name = f'{Item.quality.title()} {Item.item_name}'
    
    for i in range(2):
        print(search_name)
        api_url = f"https://api.steamapis.com/image/item/440/{search_name}"
        try:
            response = requests.get(api_url, timeout=5)
        except requests.exceptions.Timeout:
            print("Request timed out")
            break
        if response.status_code == 200:
            print("item img sucsess")
            return response.url
        else:
            print('Failed to fetch the image', 404, search_name)
            print("Testing capitalized title.")
            search_name = search_name.title()
    return None # 'https://wiki.teamfortress.com/w/images/thumb/c/c4/Unknownweapon.png/256px-Unknownweapon.png'

# TODO: add function for finding images for warpaints


def get_particle_id(particle_effect):
    if particle_effect:
        print(particle_effect.lower())
        particle_id = REVERSE_PARTICLE_MAPPING_LOWER.get(particle_effect.lower())
        if particle_id:
            print("particle img sucsess: ", particle_id)
            return particle_id
    return None


# Register trade view functions 

def process_trade_request(request):
    """
    Processes the trade request by extractiong the transaction method, getting the item lists,
    and getting and validating the forms. 
    Returns these values along with any potential error JSON response.
    """
    transaction_method = request.POST.get('transaction_method')
    item_list, item_received_list, error_response = process_items(request)
    if error_response:
        return transaction_method, item_list, item_received_list, None, None, error_response
    error_response = validate_items(request, item_list, item_received_list)
    if error_response:
        return transaction_method, item_list, item_received_list, None, None, error_response
    form, value_form, error_response = get_and_validate_forms(request)
    return transaction_method, item_list, item_received_list, form, value_form, error_response

def create_item_lists(item_ids):
    item_list = []
    for item_id in item_ids:
        try:
            item = Item.objects.get(pk=item_id)
            item_list.append(item)
        except Item.DoesNotExist:
            return JsonResponse({"error": "Item not found."}, status=404)
    return item_list

# First two return values are the item lists, third return value is the error response
def process_items(request):
    item_ids = json.loads(request.POST['itemIds'])
    item_received_ids = json.loads(request.POST['itemReceivedIds'])

    item_list = create_item_lists(item_ids)
    if item_list == []:
        return None, None, JsonResponse({"error": "No items selected."}, status=404)

    item_received_list = create_item_lists(item_received_ids)
    # item transaction trades need items received
    if item_received_list == [] and request.POST['transaction_method'] == "items":
        return None, None, JsonResponse({"error": "No items received in item trade."}, status=404)
    
    return item_list, item_received_list, None

# Make sure items arent already in another trade
def validate_items(response, item_list, item_received_list):
    transaction_type = response.POST['transaction_type']

    for item in item_list:
        if transaction_type == "buy":
            trade_with_item_recieved = Transaction.objects.filter(items_bought=item)
            if trade_with_item_recieved:
                return JsonResponse({"error": f"You have already bought this item in another trade: {item}"}, status=400)

        if transaction_type == "buy" and item.purchase_price:
            return JsonResponse({"error": f"You have already bought this item: {item}"}, status=400)
    
    for item in item_received_list:
        trade_with_item_recieved = Transaction.objects.filter(items_bought=item)
        if trade_with_item_recieved:
            return JsonResponse({"error": f"You have already recieved this item in another trade: {item}"}, status=400)


def validate_form(form):
    if not form.is_valid():
        print(form.errors)
        return JsonResponse({"errors": form.errors}, status=400)
    return None

def get_and_validate_forms(request):
    forms = [TransactionForm(request.POST), TradeValueForm(request.POST)]

    for form in forms:
        error_response = validate_form(form)
        if error_response:
            return None, None, error_response
    return forms[0], forms[1], None


def create_trade(form, value_form, transaction_method, user, item_list, item_received_list):
    """
    Creates the trade object and the trade value object if possible. 
    Adds all the items to the trade object many-to-many fields.

    Returns:
        trade object
    """
    trade = Transaction.create_trade(form, user, item_list, item_received_list)
    form_amount = value_form.cleaned_data.get('amount')
    if form_amount is not None and transaction_method != 'items':
        value = Value.create_trade_value(value_form, trade)
        trade.transaction_value = value
        trade.save()
    trade.add_items(item_list, item_received_list)
    return trade


def check_if_pure_sale(item_list, item_received_list, trade):
    """
    If one item is sold only for pure, update the item's sale_price/value
    """
    # TODO: handle if more than 1 item is sold for pure
    if len(item_list) == 1 and not item_received_list and trade.transaction_type == 'sale':
        print("logging pure sale")
        process_pure_sale(item_list[0], trade)


# Function for handling  pure sales, add sale price to item and find parent item
def process_pure_sale(item, trade):
    print(item)
    tradeValue = trade.transaction_value
    value = Value.objects.create(item=item, transaction_method=tradeValue.transaction_method, 
                    currency=tradeValue.currency, amount=tradeValue.amount)
    add_sale_price_and_check_profit(item, value)
    print(f'{item.item_title} sale price: {item.sale_price}')
    # find the original transaction and item that item came from
    get_parent_item_and_origin_trade(item)
    

def get_parent_item_and_origin_trade(item):
    origin_trade = None
    try:
        origin_trade = Transaction.objects.get(items_bought=item)
        print(f'origin trade:{origin_trade}')
    except Transaction.DoesNotExist:
        print(f"No origin trade found for {item}.")
    except Transaction.MultipleObjectsReturned:
        print("Multiple origin trades found for this item, but there should only be one.")

    if not origin_trade or origin_trade.transaction_type != "sale":
        # Purchase transactions can't have a parent item
        return
    
    parent_item = origin_trade.items_sold.all()
    if len(parent_item) == 1:
        process_parent_item(parent_item[0], origin_trade)


def process_parent_item(parent_item, origin_trade):
    item_sale_price_values = get_item_sale_price_values(origin_trade)
    if not item_sale_price_values:
        return
    # check if cash/keys in trade, if so, create Value object
    if origin_trade.transaction_value:
        item_sale_price_values.append(origin_trade.transaction_value)
    sale_value = get_total_sale_value_object(item_sale_price_values, parent_item)
    add_sale_price_and_check_profit(parent_item, sale_value)
    # check if parent item has a parent item recursively
    get_parent_item_and_origin_trade(parent_item)

def get_item_sale_price_values(origin_trade):
    item_sale_price_values = []
    for item in origin_trade.items_bought.all():
        if not item.sale_price:
            print(f'{item.item_title} not sold yet.')
            return None
        item_sale_price_values.append(item.sale_price)
    return item_sale_price_values


def get_total_sale_value_object(value_objects, item):
    # check if all transaction methods are the same, if so add the sums of the amounts and return Value object
    if all(value_object.transaction_method == value_objects[0].transaction_method for value_object in value_objects):
        print("Same transaction method:", value_objects[0].transaction_method)
        return Value.objects.create(item=item, transaction_method=value_objects[0].transaction_method, 
                currency=value_objects[0].currency, amount=sum([value_object.amount for value_object in value_objects]))
    else:
        key_amount = convert_sale_values_to_keys(value_objects)
        return Value.objects.create(item=item, transaction_method='keys', amount=key_amount)


def convert_sale_values_to_keys(value_objects):
    key_amount = 0
    for value_object in value_objects:
        print(f'value_object: {value_object}')
        if value_object.transaction_method == "keys":
            key_amount += value_object.amount
        # Convert currency if needed and get key price. Add to key_amount
        elif value_object.transaction_method in ["paypal", "scm_funds"]:
            if value_object.currency != 'USD':
                converted_amount = convert_currency(value_object.amount, value_object.currency)
                if converted_amount is None:
                    print ('Error converting currency, skipping this value object')
                    continue
                value_object.amount = converted_amount
            key_amount += get_key_price(value_object)
    return key_amount


def convert_currency(amount, from_currency, to_currency='USD'):
    if from_currency in conversion_rates_cache and to_currency in conversion_rates_cache[from_currency] and time.time() - conversion_rates_cache[from_currency][to_currency]['time'] < 3600:
        print(f'Using cached conversion rate for {from_currency} to {to_currency}')
        return Decimal(amount/Decimal(conversion_rates_cache[from_currency][to_currency]['rate']))
    try:
        url = f'https://api.exchangerate-api.com/v4/latest/{to_currency}'
        response = requests.get(url)
        data = response.json()
        if from_currency not in conversion_rates_cache:
            conversion_rates_cache[from_currency] = {}
        conversion_rates_cache[from_currency][to_currency] = {'rate': data['rates'][from_currency], 'time': time.time()}
        print(conversion_rates_cache)
        return Decimal(amount/Decimal(data['rates'][from_currency]))
    except requests.exceptions.RequestException as error:
        print('Error:', error)
    except KeyError:
        print(f'KeyError: {from_currency} not found in response data')
    return None


@cached(cache)
def get_current_key_sell_order():
    """
    Gets the current cheapest sell order for Keys on Steam Community Market in USD
    Return value is cached to avoid being rate limited

    Returns:
        Key price or None if error
    """
    try:
        url = 'https://steamcommunity.com/market/itemordershistogram?country=US&language=english&currency=1&item_nameid=1'
        response = requests.get(url)
        data = response.json()
        return data['sell_order_graph'][0][0]
    except requests.exceptions.RequestException as error:
        print('Error:', error)
    return None


def get_key_price(value):

    amount_usd = value.amount
    transaction_method = value.transaction_method
    user = find_user_from_value(value)
    key_price = Decimal(amount_usd)/Decimal(get_usd_key_prices(transaction_method, user))
    key_price =  key_price.quantize(Decimal('.00'), rounding=ROUND_DOWN)
    #print(f'key_price: {key_price} from {amount_usd} USD')
    return key_price

def find_user_from_value(value):
    if value.transaction:
        return value.transaction.owner
    elif value.item:
        return value.item.owner

def get_usd_key_prices(transaction_method, user):
    if transaction_method == 'scm_funds':
        return user.market_settings.scm_key_price_dollars
    elif transaction_method == 'paypal':
        return user.market_settings.paypal_key_price_dollars


def add_sale_price_and_check_profit(item, value):
    item.add_sale_price(value)
    profit_value = get_item_profit_value(item)
    if profit_value:
        item.add_profit_value(profit_value)
        print(f'{item.item_title} profit: {item.profit_value}')

# Functions for getting item profit value
def get_item_profit_value(item):
    if item.purchase_price and item.sale_price:
        purchase_price, sale_price = normalize_transaction_values(item.purchase_price, item.sale_price)

        profit = sale_price.amount - purchase_price.amount
        currency = purchase_price.currency if purchase_price.currency else None
        profit_value = Value.objects.create(item=item, transaction_method=purchase_price.transaction_method,
                currency=currency, amount=profit)
        return profit_value
    return None

# If values are in different currencies or transaction methods, convert to be in same currency and transaction method
def normalize_transaction_values(purchase_value, sale_value):
    if purchase_value.transaction_method != sale_value.transaction_method:
        purchase_price = convert_value_method_to_keys(purchase_value)
        sale_price = convert_value_method_to_keys(sale_value)
            
    elif purchase_value.currency != sale_value.currency:
        purchase_price, sale_price = convert_to_same_currency(purchase_value, sale_value)

    else:
        purchase_price = purchase_value
        sale_price = sale_value
    return purchase_price, sale_price


def convert_to_same_currency(value1, value2):
    value2 = value2.copy() # copy to avoid changing original value object
    conversion_currency = value1.currency
    converted_amount = round(convert_currency(value2.amount, value2.currency, conversion_currency), 2)

    if converted_amount is None:
        print ('Error converting currency, skipping this value object')
        return None
    value2.amount = converted_amount
    value2.currency = conversion_currency
    return value1, value2


def convert_value_method_to_keys(value):
    value = value.copy() # copy to avoid changing original value object
    if value.transaction_method == 'keys':
        return value
    if value.transaction_method in ['paypal', 'scm_funds']:
        if value.currency != 'USD':
            converted_amount = convert_currency(value.amount, value.currency)
            if converted_amount is None:
                print ('Error converting currency, skipping this value object')
                return None
            value.amount = converted_amount
        key_price = get_key_price(value)
        value.amount = key_price
        value.transaction_method = 'keys'
        value.currency = None
    return value