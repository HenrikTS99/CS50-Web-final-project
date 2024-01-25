import requests
import json
from .models import Item, Value, Transaction
from django.template.loader import render_to_string
from django.urls import reverse
from decimal import Decimal, ROUND_DOWN
import time
from django.http import JsonResponse
import datetime

PARTICLE_EFFECTS_MAPPING = {
    '4': 'Community Sparkle',
    '5': 'Holy Glow',
    '6': 'Green Confetti',
    '7': 'Purple Confetti',
    '8': 'Haunted Ghosts',
    '9': 'Green Energy',
    '10': 'Purple Energy',
    '11': 'Circling TF Logo',
    '12': 'Massed Flies',
    '13': 'Burning Flames',
    '14': 'Scorching Flames',
    '17': 'Sunbeams',
    '20': 'Map Stamps',
    '29': 'Stormy Storm',
    '33': 'Orbiting Fire',
    '34': 'Bubbling',
    '35': 'Smoking',
    '36': 'Steaming',
    '38': 'Cloudy Moon',
    '56': 'Kill-a-Watt',
    '57': 'Terror-Watt',
    '58': 'Cloud 9',
    '70': 'Time Warp',
    '15': 'Searing Plasma',
    '16': 'Vivid Plasma',
    '18': 'Circling Peace Sign',
    '19': 'Circling Heart',
    '28': 'Genteel Smoke',
    '30': 'Blizzardy Storm',
    '31': 'Nuts n\' Bolts',
    '32': 'Orbiting Planets',
    '37': 'Flaming Lantern',
    '39': 'Cauldron Bubbles',
    '40': 'Eerie Orbiting Fire',
    '43': 'Knifestorm',
    '44': 'Misty Skull',
    '45': 'Harvest Moon',
    '46': 'It\'s A Secret To Everybody',
    '47': 'Stormy 13th Hour',
    '59': 'Aces High',
    '60': 'Dead Presidents',
    '61': 'Miami Nights',
    '62': 'Disco Beat Down',
    '63': 'Phosphorous',
    '64': 'Sulphurous',
    '65': 'Memory Leak',
    '66': 'Overclocked',
    '67': 'Electrostatic',
    '68': 'Power Surge',
    '69': 'Anti-Freeze',
    '71': 'Green Black Hole',
    '72': 'Roboactive',
    '73': 'Arcana',
    '74': 'Spellbound',
    '75': 'Chiroptera Venenata',
    '76': 'Poisoned Shadows',
    '77': 'Something Burning This Way Comes',
    '78': 'Hellfire',
    '79': 'Darkblaze',
    '80': 'Demonflame',
    '3001': 'Showstopper',
    '3003': 'Holy Grail',
    '3004': '\'72',
    '3005': 'Fountain of Delight',
    '3006': 'Screaming Tiger',
    '3007': 'Skill Gotten Gains',
    '3008': 'Midnight Whirlwind',
    '3009': 'Silver Cyclone',
    '3010': 'Mega Strike',
    '81': 'Bonzo The All-Gnawing',
    '82': 'Amaranthine',
    '83': 'Stare From Beyond',
    '84': 'The Ooze',
    '85': 'Ghastly Ghosts Jr',
    '86': 'Haunted Phantasm Jr',
    '3011': 'Haunted Phantasm',
    '3012': 'Ghastly Ghosts',
    '87': 'Frostbite',
    '88': 'Molten Mallard',
    '89': 'Morning Glory',
    '90': 'Death at Dusk',
    '3002': 'Showstopper',
    '701': 'Hot',
    '702': 'Isotope',
    '703': 'Cool',
    '704': 'Energy Orb',
    '91': 'Abduction',
    '92': 'Atomic',
    '93': 'Subatomic',
    '94': 'Electric Hat Protector',
    '95': 'Magnetic Hat Protector',
    '96': 'Voltaic Hat Protector',
    '97': 'Galactic Codex',
    '98': 'Ancient Codex',
    '99': 'Nebula',
    '100': 'Death by Disco',
    '101': 'It\'s a mystery to everyone',
    '102': 'It\'s a puzzle to me',
    '103': 'Ether Trail',
    '104': 'Nether Trail',
    '105': 'Ancient Eldritch',
    '106': 'Eldritch Flame',
    '108': 'Tesla Coil',
    '107': 'Neutron Star',
    '109': 'Starstorm Insomnia',
    '110': 'Starstorm Slumber',
    '3015': 'Infernal Flames',
    '3013': 'Hellish Inferno',
    '3014': 'Spectral Swirl',
    '3016': 'Infernal Smoke',
    '111': 'Brain Drain',
    '112': 'Open Mind',
    '113': 'Head of Steam',
    '114': 'Galactic Gateway',
    '115': 'The Eldritch Opening',
    '116': 'The Dark Doorway',
    '117': 'Ring of Fire',
    '118': 'Vicious Circle',
    '119': 'White Lightning',
    '120': 'Omniscient Orb',
    '121': 'Clairvoyance',
    '3017': 'Acidic Bubbles of Envy',
    '3018': 'Flammable Bubbles of Attraction',
    '3019': 'Poisonous Bubbles of Regret',
    '3020': 'Roaring Rockets',
    '3021': 'Spooky Night',
    '3022': 'Ominous Night',
    '122': 'Fifth Dimension',
    '123': 'Vicious Vortex',
    '124': 'Menacing Miasma',
    '125': 'Abyssal Aura',
    '126': 'Wicked Wood',
    '127': 'Ghastly Grove',
    '128': 'Mystical Medley',
    '129': 'Ethereal Essence',
    '130': 'Twisted Radiance',
    '131': 'Violet Vortex',
    '132': 'Verdant Vortex',
    '133': 'Valiant Vortex',
    '3023': 'Bewitched',
    '3024': 'Accursed',
    '3025': 'Enchanted',
    '3026': 'Static Mist',
    '3027': 'Eerie Lightning',
    '3028': 'Terrifying Thunder',
    '3029': 'Jarate Shock',
    '3030': 'Nether Void',
    '134': 'Sparkling Lights',
    '135': 'Frozen Icefall',
    '136': 'Fragmented Gluons',
    '137': 'Fragmented Quarks',
    '138': 'Fragmented Photons',
    '139': 'Defragmenting Reality',
    '141': 'Fragmenting Reality',
    '142': 'Refragmenting Reality',
    '143': 'Snowfallen',
    '144': 'Snowblinded',
    '145': 'Pyroland Daydream',
    '3031': 'Good-Hearted Goodies',
    '3032': 'Wintery Wisp',
    '3033': 'Arctic Aurora',
    '3034': 'Winter Spirit',
    '3035': 'Festive Spirit',
    '3036': 'Magical Spirit',
    '147': 'Verdatica',
    '148': 'Aromatica',
    '149': 'Chromatica',
    '150': 'Prismatica',
    '151': 'Bee Swarm',
    '152': 'Frisky Fireflies',
    '153': 'Smoldering Spirits',
    '154': 'Wandering Wisps',
    '155': 'Kaleidoscope',
    '156': 'Green Giggler',
    '157': 'Laugh-O-Lantern',
    '158': 'Plum Prankster',
    '159': 'Pyroland Nightmare',
    '160': 'Gravelly Ghoul',
    '161': 'Vexed Volcanics',
    '162': 'Gourdian Angel',
    '163': 'Pumpkin Party',
    '3037': 'Spectral Escort',
    '3038': 'Astral Presence',
    '3039': 'Arcane Assistance',
    '3040': 'Arcane Assistance',
    '3041': 'Emerald Allurement',
    '3042': 'Pyrophoric Personality',
    '3043': 'Spellbound Aspect',
    '3044': 'Static Shock',
    '3045': 'Veno Shock',
    '3046': 'Toxic Terrors',
    '3047': 'Arachnid Assault',
    '3048': 'Creepy Crawlies',
    '164': 'Frozen Fractals',
    '165': 'Lavender Landfall',
    '166': 'Special Snowfall',
    '167': 'Divine Desire',
    '168': 'Distant Dream',
    '169': 'Violent Wintertide',
    '170': 'Blighted Snowstorm',
    '171': 'Pale Nimbus',
    '172': 'Genus Plasmos',
    '173': 'Serenus Lumen',
    '174': 'Ventum Maris',
    '175': 'Mirthful Mistletoe',
    '3049': 'Delightful Star',
    '3050': 'Frosted Star',
    '3051': 'Apotheosis',
    '3052': 'Ascension',
    '3053': 'Reindoonicorn Rancher',
    '3054': 'Reindoonicorn Rancher',
    '3055': 'Twinkling Lights',
    '3056': 'Shimmering Lights',
    '177': 'Resonation',
    '178': 'Aggradation',
    '179': 'Lucidation',
    '180': 'Stunning',
    '181': 'Ardentum Saturnalis',
    '182': 'Fragrancium Elementalis',
    '183': 'Reverium Irregularis',
    '185': 'Perennial Petals',
    '186': 'Flavorsome Sunset',
    '187': 'Raspberry Bloom',
    '188': 'Iridescence',
    '189': 'Tempered Thorns',
    '190': 'Devilish Diablo',
    '191': 'Severed Serration',
    '192': 'Shrieking Shades',
    '193': 'Restless Wraiths',
    '194': 'Restless Wraiths',
    '195': 'Infernal Wraith',
    '196': 'Phantom Crown',
    '197': 'Ancient Specter',
    '198': 'Viridescent Peeper',
    '199': 'Eyes of Molten',
    '200': 'Ominous Stare',
    '201': 'Pumpkin Moon',
    '202': 'Frantic Spooker',
    '203': 'Frightened Poltergeist',
    '204': 'Energetic Haunter',
    '3059': 'Spectral Shackles',
    '3060': 'Cursed Confinement',
    '3061': 'Cavalier de Carte',
    '3062': 'Cavalier de Carte',
    '3063': 'Hollow Flourish',
    '3064': 'Magic Shuffle',
    '3065': 'Vigorous Pulse',
    '3066': 'Thundering Spirit',
    '3067': 'Galvanic Defiance',
    '3068': 'Wispy Halos',
    '3069': 'Nether Wisps',
    '3070': 'Aurora Borealis',
    '3071': 'Aurora Australis',
    '3072': 'Aurora Polaris',
    '205': 'Smissmas Tree',
    '206': 'Hospitable Festivity',
    '207': 'Condescending Embrace',
    '209': 'Sparkling Spruce',
    '210': 'Glittering Juniper',
    '211': 'Prismatic Pine',
    '212': 'Spiraling Lights',
    '213': 'Twisting Lights',
    '214': 'Stardust Pathway',
    '215': 'Flurry Rush',
    '3089': 'Minty Old Man',
    '3096': 'Pumpkin Pile',
    '3101': 'Roaring Rockets',
    '3116': 'Gloved Guest',
    '3122': 'Skull Study',
    '3133': 'Vexed Volcanics',
    '3140': 'Bewitched',
    '3144': 'Haunting',
    '3145': 'Smoldering Spirits',
    '3146': 'Vengeful Spirit',
    '3147': 'Wraithful Spirit',
    '3148': 'Spectral Swirl',
    '3149': 'Twisted Radiance',
    '3150': 'Verdant Vortex',
    '3151': 'Valiant Vortex',
    '3152': 'Fifth Dimension',
    '3153': 'Vicious Vortex',
    '3154': 'Mystical Medley',
    '3155': 'Ethereal Essence',
    '3156': 'Sparkling Lights',
    '3157': 'Frozen Icefall',
    '3158': 'Fragmented Gluons',
    '3159': 'Fragmented Quarks',
    '3160': 'Fragmented Photons',
    '3161': 'Defragmenting Reality',
    '3162': 'Fragmenting Reality',
    '3163': 'Refragmenting Reality',
    '3164': 'Snowfallen',
    '3165': 'Snowblinded',
    '3166': 'Pyroland Daydream',
    '3167': 'Good-Hearted Goodies',
    '3168': 'Wintery Wisp',
    '3169': 'Arctic Aurora',
    '3170': 'Winter Spirit',
    '3171': 'Festive Spirit',
    '3172': 'Magical Spirit',
    '3173': 'Verdatica',
    '3174': 'Aromatica',
    '3175': 'Chromatica',
    '3176': 'Prismatica',
    '3177': 'Bee Swarm',
    '3178': 'Frisky Fireflies',
    '3179': 'Smoldering Spirits',
    '3180': 'Wandering Wisps',
    '3181': 'Kaleidoscope',
    '3182': 'Green Giggler',
    '3183': 'Laugh-O-Lantern',
    '3184': 'Plum Prankster',
    '3185': 'Pyroland Nightmare',
    '3186': 'Gravelly Ghoul',
    '3187': 'Vexed Volcanics',
    '3188': 'Gourdian Angel',
    '3189': 'Pumpkin Party',
    '3190': 'Spectral Escort',
    '3191': 'Astral Presence',
    '3192': 'Arcane Assistance',
    '3193': 'Arcane Assistance',
    '3194': 'Emerald Allurement',
    '3195': 'Pyrophoric Personality',
    '3196': 'Spellbound Aspect',
    '3197': 'Static Shock',
    '3198': 'Veno Shock',
    '3199': 'Toxic Terrors',
    '3200': 'Arachnid Assault',
    '3201': 'Creepy Crawlies',
    '3202': 'Frozen Fractals',
    '3203': 'Lavender Landfall',
    '3204': 'Special Snowfall',
    '3205': 'Divine Desire',
    '3206': 'Distant Dream',
    '3207': 'Violent Wintertide',
    '3208': 'Blighted Snowstorm',
    '3209': 'Pale Nimbus',
    '3210': 'Genus Plasmos',
    '3211': 'Serenus Lumen',
    '3212': 'Ventum Maris',
    '3213': 'Mirthful Mistletoe',
    '3214': 'Delightful Star',
    '3215': 'Frosted Star',
    '3216': 'Apotheosis',
    '3217': 'Ascension',
    '3218': 'Reindoonicorn Rancher',
    '3219': 'Reindoonicorn Rancher',
    '3220': 'Twinkling Lights',
    '3221': 'Shimmering Lights',
    '3222': 'Resonation',
    '3223': 'Aggradation',
    '3224': 'Lucidation',
    '3225': 'Stunning',
    '3226': 'Ardentum Saturnalis',
    '3227': 'Fragrancium Elementalis',
    '3228': 'Reverium Irregularis',
    '3229': 'Perennial Petals',
    '3230': 'Flavorsome Sunset',
    '3231': 'Raspberry Bloom',
    '3232': 'Iridescence',
    '3233': 'Tempered Thorns',
    '3234': 'Devilish Diablo',
    '3235': 'Severed Serration',
    '3236': 'Shrieking Shades',
    '3237': 'Restless Wraiths',
    '3238': 'Restless Wraiths',
    '3239': 'Infernal Wraith',
    '3240': 'Phantom Crown',
    '3241': 'Ancient Specter',
    '3242': 'Viridescent Peeper',
    '3243': 'Eyes of Molten',
    '3244': 'Ominous Stare',
    '3245': 'Pumpkin Moon',
    '3246': 'Frantic Spooker',
    '3247': 'Frightened Poltergeist',
    '3248': 'Energetic Haunter',
    '3249': 'Spectral Shackles',
    '3250': 'Cursed Confinement',
    '3251': 'Cavalier de Carte',
    '3252': 'Cavalier de Carte',
    '3253': 'Hollow Flourish',
    '3254': 'Magic Shuffle',
    '3255': 'Vigorous Pulse',
    '3256': 'Thundering Spirit',
    '3257': 'Galvanic Defiance',
    '3258': 'Wispy Halos',
    '3259': 'Nether Wisps',
    '3260': 'Aurora Borealis',
    '3261': 'Aurora Australis',
    '3262': 'Aurora Polaris',
    '3263': 'Smissmas Tree',
    '3264': 'Hospitable Festivity',
    '3265': 'Condescending Embrace',
    '3266': 'Sparkling Spruce',
    '3267': 'Glittering Juniper',
    '3268': 'Prismatic Pine',
    '3269': 'Spiraling Lights',
    '3270': 'Twisting Lights',
    '3271': 'Stardust Pathway',
    '3272': 'Flurry Rush',
    '3273': 'Spark of Smissmas',
    '3274': 'Polar Forecast',
    '3275': 'Shining Stag',
    '3276': 'Holiday Horns',
    '3277': 'Ardent Antlers',
    '3278': 'Festive Lights',
    '3279': 'Amethyst Winds',
    '3280': 'Golden Gusts',
    '3281': 'Smissmas Swirls',
    '3282': 'Minty Cypress',
    '3283': 'Pristine Pine',
    '3284': 'Sparkly Spruce',
    '3285': 'Festive Fever',
    '3286': 'Golden Glimmer',
    '3287': 'Frosty Silver',
    '3288': 'Glamorous Dazzle',
    '3289': 'Sublime Snowstorm',
    '3290': 'Crustacean Sensation',
    '3291': 'Frosted Decadence',
    '3292': 'Sprinkled Delights',
    '3293': 'Terrestrial Favor',
    '3294': 'Tropical Thrill',
    '3295': 'Flourishing Passion',
    '3296': 'Dazzling Fireworks',
    '3297': 'Blazing Fireworks',
    '3298': 'Twinkling Fireworks',
    '3299': 'Sparkling Fireworks',
    '3300': 'Glowing Fireworks',
    '3301': 'Flying Lights',
    '3302': 'Limelight',
    '3303': 'Shining Star',
    '3304': 'Cold Cosmos',
    '3305': 'Refracting Fractals',
    '3306': 'Startrance',
    '3307': 'Starlush',
    '3308': 'Starfire',
    '3309': 'Stardust',
    '3310': 'Contagious Eruption',
    '3311': 'Daydream Eruption',
    '3312': 'Volcanic Eruption',
    '3313': 'Divine Sunlight',
    '3314': 'Audiophile',
    '3315': 'Soundwave',
    '3316': 'Synesthesia',
    '3317': 'Haunted Kraken',
    '3318': 'Eerie Kraken',
    '3319': 'Soulful Slice',
    '3320': 'Horsemann\'s Hack',
    '3321': 'Haunted Forever!',
    '3323': 'Forever And Forever!',
    '3324': 'Cursed Forever!',
    '3325': 'Moth Plague',
    '3326': 'Malevolent Monoculi',
    '3327': 'Haunted Wick',
    '3329': 'Wicked Wick',
    '3330': 'Spectral Wick',
    '3331': 'Marigold Ritual',
    '3333': 'Pungent Poison',
    '3334': 'Blazed Brew',
    '3335': 'Mysterious Mixture',
    '3336': 'Linguistic Deviation',
    '3337': 'Aurelian Seal',
    '3338': 'Runic Imprisonment',
    '3340': 'Prismatic Haze',
    '3341': 'Rising Ritual',
    '3342': 'Bloody Grip',
    '3344': 'Toxic Grip',
    '3345': 'Infernal Grip',
    '3346': 'Death Grip',
    '3347': 'Musical Maelstrom',
    '3348': 'Verdant Virtuoso',
    '3349': 'Silver Serenade',
    '3350': 'Cosmic Constellations',
    '3352': 'Dazzling Constellations',
    '3353': 'Tainted Frost',
}

REVERSE_PARTICLE_MAPPING = {v: k for k, v in PARTICLE_EFFECTS_MAPPING.items()}

USD_KEY_PRICES = {
    'scm_funds': 2.2,
    'paypal': 1.7
}

conversion_rates_cache = {}


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
    return 'https://scrap.tf/img/items/warpaint/Grenade%20Launcher_407_5_0.png' # 'https://wiki.teamfortress.com/w/images/thumb/c/c4/Unknownweapon.png/256px-Unknownweapon.png'


def get_particle_id(particle_effect):
    if particle_effect:
        print(particle_effect)
        particle_id = REVERSE_PARTICLE_MAPPING.get(particle_effect)
        if particle_id:
            print("particle img sucsess")
            return particle_id
        elif particle_effect != particle_effect.title():
            print("Particle ID lookup failed, trying again with capitalized title.")
            get_particle_id(particle_effect.title())

    return None


# New trade functions
def create_item_lists(item_ids):
    item_list = []
    for item_id in item_ids:
        try:
            item = Item.objects.get(pk=item_id)
            item_list.append(item)
        except Item.DoesNotExist:
            return JsonResponse({"error": "Item not found."}, status=404)
    return item_list


def process_items(request):
    item_ids = json.loads(request.POST['itemIds'])
    item_recieved_ids = json.loads(request.POST['itemRecievedIds'])

    item_list = create_item_lists(item_ids)
    if item_list == []:
        return None, None, JsonResponse({"error": "No items selected."}, status=404)

    item_recieved_list = create_item_lists(item_recieved_ids)
    # item trades need items recieved
    if item_recieved_list == [] and request.POST['transaction_method'] == "items":
        return None, None, JsonResponse({"error": "No items recieved in item trade."}, status=404)
    
    return item_list, item_recieved_list, None


def validate_forms(form, valueForm):
    if not form.is_valid():
        print(form.errors)
        return JsonResponse({"errors": form.errors}, status=400)
    if not valueForm.is_valid():
        print(valueForm.errors)
        return JsonResponse({"errors": valueForm.errors}, status=400)
    return None


def create_trade_response_data(trade):
    # TODO: transaction_html might not be used, consider removing from here, templates and new-trade.js in future
    transaction_html = render_to_string('tf2folio/transaction-template.html', {'transaction': trade })
    return {
        "message": "Data sent successfully.",
        "transaction_id": trade.id,
        "transaction_html": transaction_html,
        "redirect_url": reverse("trade_history")
    }


# Functions for handling  pure sales
def process_pure_sale(item, trade):
    print(item)
    tradeValue = trade.transaction_value
    value = Value.objects.create(item=item, transaction_method=tradeValue.transaction_method, 
                    currency=tradeValue.currency, amount=tradeValue.amount)
    item.add_sale_price(value)
    print(f'{item.item_title} sale price: {item.sale_price}')
    # find the original transaction and item that item came from
    parent_item, origin_trade = get_parent_item_and_origin_trade(item)
    if parent_item and origin_trade:
        process_parent_item(parent_item, origin_trade)


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
        return None, None
    parent_item = origin_trade.items_sold.all()
    if len(parent_item) == 1:
        return parent_item[0], origin_trade
    return None, None


def process_parent_item(parent_item, origin_trade):
    item_sale_price_objects = []
    for item in origin_trade.items_bought.all():
        if not item.sale_price:
            print(f'{item.item_title} not sold yet.')
            return 
        item_sale_price_objects.append(item.sale_price)

    # check if cash/keys in trade, if so, create Value object
    if origin_trade.transaction_value:
        item_sale_price_objects.append(origin_trade.transaction_value)

    sale_value = get_total_sale_value_object(item_sale_price_objects, parent_item)
    parent_item.add_sale_price(sale_value)
    # check if parent item has a parent item recursively
    get_parent_item_and_origin_trade(parent_item)
    

def get_total_sale_value_object(value_objects, item):
    # check if all transaction methods are the same, if so add the sums of the amounts and return Value object
    if all(value_object.transaction_method == value_objects[0].transaction_method for value_object in value_objects):
        print("Same transaction method:", value_objects[0].transaction_method)
        return Value.objects.create(item=item, transaction_method=value_objects[0].transaction_method, 
                currency=value_objects[0].currency, amount=sum([value_object.amount for value_object in value_objects]))
    else:
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
                key_amount += get_key_price(value_object.amount, value_object.transaction_method)
        return Value.objects.create(item=item, transaction_method='keys', amount=key_amount)


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


def get_key_price(amount_usd, transaction_method):
    key_price = Decimal(amount_usd)/Decimal(USD_KEY_PRICES[transaction_method])
    key_price =  key_price.quantize(Decimal('.00'), rounding=ROUND_DOWN)
    #print(f'key_price: {key_price} from {amount_usd} USD')
    return key_price


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
        key_price = get_key_price(value.amount, value.transaction_method)
        value.amount = key_price
        value.transaction_method = 'keys'
        value.currency = None
    return value