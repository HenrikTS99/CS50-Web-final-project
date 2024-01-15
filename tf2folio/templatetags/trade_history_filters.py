from django import template

register = template.Library()

transaction_info = {
        'keys': {
            'image': 'https://steamcdn-a.akamaihd.net/apps/440/icons/key.be0a5e2cda3a039132c35b67319829d785e50352.png',
            'label': 'Keys',
            'quality': 'unique',
        },
        'scm_funds': {
            'image': 'https://community.cloudflare.steamstatic.com/public/shared/images/responsive/share_steam_logo.png',
            'label': 'SCM funds',
            'quality': 'normal',
        },
        'paypal': {
            'image': 'https://developer.valvesoftware.com/w/images/thumb/f/f9/Smallcredits.png/300px-Smallcredits.png',
            'label': 'Cash',
            'quality': 'normal',
        },
    }

@register.filter
def get_transaction_info(key):
    return transaction_info.get(key)


@register.filter
def value_display(value):
    currency = value.currency if value.currency else ""
    amount = str(value.amount).rstrip('0').rstrip('.') if '.' in str(value.amount) else value.amount
    return f'{amount} {currency} {value.get_transaction_method_display()}'