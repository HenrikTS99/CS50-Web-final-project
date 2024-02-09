import requests
import json
from .models import Item, Value, Transaction
from django.template.loader import render_to_string
from django.urls import reverse
from decimal import Decimal, ROUND_DOWN
import time
from django.http import JsonResponse
import datetime
from django.core.paginator import Paginator
from .forms import TransactionForm, TradeValueForm

PARTICLE_EFFECTS_MAPPING = {
    "4": "Community Sparkle",
    "5": "Holy Glow",
    "6": "Green Confetti",
    "7": "Purple Confetti",
    "8": "Haunted Ghosts",
    "9": "Green Energy",
    "10": "Purple Energy",
    "11": "Circling TF Logo",
    "12": "Massed Flies",
    "13": "Burning Flames",
    "14": "Scorching Flames",
    "17": "Sunbeams",
    "20": "Map Stamps",
    "29": "Stormy Storm",
    "33": "Orbiting Fire",
    "34": "Bubbling",
    "35": "Smoking",
    "36": "Steaming",
    "38": "Cloudy Moon",
    "56": "Kill-a-Watt",
    "57": "Terror-Watt",
    "58": "Cloud 9",
    "70": "Time Warp",
    "15": "Searing Plasma",
    "16": "Vivid Plasma",
    "18": "Circling Peace Sign",
    "19": "Circling Heart",
    "28": "Genteel Smoke",
    "30": "Blizzardy Storm",
    "31": "Nuts n' Bolts",
    "32": "Orbiting Planets",
    "37": "Flaming Lantern",
    "39": "Cauldron Bubbles",
    "40": "Eerie Orbiting Fire",
    "43": "Knifestorm",
    "44": "Misty Skull",
    "45": "Harvest Moon",
    "46": "It's A Secret To Everybody",
    "47": "Stormy 13th Hour",
    "59": "Aces High",
    "60": "Dead Presidents",
    "61": "Miami Nights",
    "62": "Disco Beat Down",
    "63": "Phosphorous",
    "64": "Sulphurous",
    "65": "Memory Leak",
    "66": "Overclocked",
    "67": "Electrostatic",
    "68": "Power Surge",
    "69": "Anti-Freeze",
    "71": "Green Black Hole",
    "72": "Roboactive",
    "73": "Arcana",
    "74": "Spellbound",
    "75": "Chiroptera Venenata",
    "76": "Poisoned Shadows",
    "77": "Something Burning This Way Comes",
    "78": "Hellfire",
    "79": "Darkblaze",
    "80": "Demonflame",
    "3001": "Showstopper",
    "3003": "Holy Grail",
    "3004": "'72",
    "3005": "Fountain of Delight",
    "3006": "Screaming Tiger",
    "3007": "Skill Gotten Gains",
    "3008": "Midnight Whirlwind",
    "3009": "Silver Cyclone",
    "3010": "Mega Strike",
    "81": "Bonzo The All-Gnawing",
    "82": "Amaranthine",
    "83": "Stare From Beyond",
    "84": "The Ooze",
    "85": "Ghastly Ghosts Jr",
    "86": "Haunted Phantasm Jr",
    "3011": "Haunted Phantasm",
    "3012": "Ghastly Ghosts",
    "87": "Frostbite",
    "88": "Molten Mallard",
    "89": "Morning Glory",
    "90": "Death at Dusk",
    "3002": "Showstopper",
    "701": "Hot",
    "702": "Isotope",
    "703": "Cool",
    "704": "Energy Orb",
    "91": "Abduction",
    "92": "Atomic",
    "93": "Subatomic",
    "94": "Electric Hat Protector",
    "95": "Magnetic Hat Protector",
    "96": "Voltaic Hat Protector",
    "97": "Galactic Codex",
    "98": "Ancient Codex",
    "99": "Nebula",
    "100": "Death by Disco",
    "101": "It's a mystery to everyone",
    "102": "It's a puzzle to me",
    "103": "Ether Trail",
    "104": "Nether Trail",
    "105": "Ancient Eldritch",
    "106": "Eldritch Flame",
    "108": "Tesla Coil",
    "107": "Neutron Star",
    "109": "Starstorm Insomnia",
    "110": "Starstorm Slumber",
    "3015": "Infernal Flames",
    "3013": "Hellish Inferno",
    "3014": "Spectral Swirl",
    "3016": "Infernal Smoke",
    "111": "Brain Drain",
    "112": "Open Mind",
    "113": "Head of Steam",
    "114": "Galactic Gateway",
    "115": "The Eldritch Opening",
    "116": "The Dark Doorway",
    "117": "Ring of Fire",
    "118": "Vicious Circle",
    "119": "White Lightning",
    "120": "Omniscient Orb",
    "121": "Clairvoyance",
    "3017": "Acidic Bubbles of Envy",
    "3018": "Flammable Bubbles of Attraction",
    "3019": "Poisonous Bubbles of Regret",
    "3020": "Roaring Rockets",
    "3021": "Spooky Night",
    "3022": "Ominous Night",
    "122": "Fifth Dimension",
    "123": "Vicious Vortex",
    "124": "Menacing Miasma",
    "125": "Abyssal Aura",
    "126": "Wicked Wood",
    "127": "Ghastly Grove",
    "128": "Mystical Medley",
    "129": "Ethereal Essence",
    "130": "Twisted Radiance",
    "131": "Violet Vortex",
    "132": "Verdant Vortex",
    "133": "Valiant Vortex",
    "3023": "Bewitched",
    "3024": "Accursed",
    "3025": "Enchanted",
    "3026": "Static Mist",
    "3027": "Eerie Lightning",
    "3028": "Terrifying Thunder",
    "3029": "Jarate Shock",
    "3030": "Nether Void",
    "134": "Sparkling Lights",
    "135": "Frozen Icefall",
    "136": "Fragmented Gluons",
    "137": "Fragmented Quarks",
    "138": "Fragmented Photons",
    "139": "Defragmenting Reality",
    "141": "Fragmenting Reality",
    "142": "Refragmenting Reality",
    "143": "Snowfallen",
    "144": "Snowblinded",
    "145": "Pyroland Daydream",
    "3031": "Good-Hearted Goodies",
    "3032": "Wintery Wisp",
    "3033": "Arctic Aurora",
    "3034": "Winter Spirit",
    "3035": "Festive Spirit",
    "3036": "Magical Spirit",
    "147": "Verdatica",
    "148": "Aromatica",
    "149": "Chromatica",
    "150": "Prismatica",
    "151": "Bee Swarm",
    "152": "Frisky Fireflies",
    "153": "Smoldering Spirits",
    "154": "Wandering Wisps",
    "155": "Kaleidoscope",
    "156": "Green Giggler",
    "157": "Laugh-O-Lantern",
    "158": "Plum Prankster",
    "159": "Pyroland Nightmare",
    "160": "Gravelly Ghoul",
    "161": "Vexed Volcanics",
    "162": "Gourdian Angel",
    "163": "Pumpkin Party",
    "3037": "Spectral Escort",
    "3038": "Astral Presence",
    "3039": "Arcane Assistance",
    "3040": "Arcane Assistance",
    "3041": "Emerald Allurement",
    "3042": "Pyrophoric Personality",
    "3043": "Spellbound Aspect",
    "3044": "Static Shock",
    "3045": "Veno Shock",
    "3046": "Toxic Terrors",
    "3047": "Arachnid Assault",
    "3048": "Creepy Crawlies",
    "164": "Frozen Fractals",
    "165": "Lavender Landfall",
    "166": "Special Snowfall",
    "167": "Divine Desire",
    "168": "Distant Dream",
    "169": "Violent Wintertide",
    "170": "Blighted Snowstorm",
    "171": "Pale Nimbus",
    "172": "Genus Plasmos",
    "173": "Serenus Lumen",
    "174": "Ventum Maris",
    "175": "Mirthful Mistletoe",
    "3049": "Delightful Star",
    "3050": "Frosted Star",
    "3051": "Apotheosis",
    "3052": "Ascension",
    "3053": "Reindoonicorn Rancher",
    "3054": "Reindoonicorn Rancher",
    "3055": "Twinkling Lights",
    "3056": "Shimmering Lights",
    "177": "Resonation",
    "178": "Aggradation",
    "179": "Lucidation",
    "180": "Stunning",
    "181": "Ardentum Saturnalis",
    "182": "Fragrancium Elementalis",
    "183": "Reverium Irregularis",
    "185": "Perennial Petals",
    "186": "Flavorsome Sunset",
    "187": "Raspberry Bloom",
    "188": "Iridescence",
    "189": "Tempered Thorns",
    "190": "Devilish Diablo",
    "191": "Severed Serration",
    "192": "Shrieking Shades",
    "193": "Restless Wraiths",
    "194": "Restless Wraiths",
    "195": "Infernal Wraith",
    "196": "Phantom Crown",
    "197": "Ancient Specter",
    "198": "Viridescent Peeper",
    "199": "Eyes of Molten",
    "200": "Ominous Stare",
    "201": "Pumpkin Moon",
    "202": "Frantic Spooker",
    "203": "Frightened Poltergeist",
    "204": "Energetic Haunter",
    "3059": "Spectral Shackles",
    "3060": "Cursed Confinement",
    "3061": "Cavalier de Carte",
    "3062": "Cavalier de Carte",
    "3063": "Hollow Flourish",
    "3064": "Magic Shuffle",
    "3065": "Vigorous Pulse",
    "3066": "Thundering Spirit",
    "3067": "Galvanic Defiance",
    "3068": "Wispy Halos",
    "3069": "Nether Wisps",
    "3070": "Aurora Borealis",
    "3071": "Aurora Australis",
    "3072": "Aurora Polaris",
    "205": "Smissmas Tree",
    "206": "Hospitable Festivity",
    "207": "Condescending Embrace",
    "209": "Sparkling Spruce",
    "210": "Glittering Juniper",
    "211": "Prismatic Pine",
    "212": "Spiraling Lights",
    "213": "Twisting Lights",
    "214": "Stardust Pathway",
    "215": "Flurry Rush",
    "216": "Spark of Smissmas",
    "218": "Polar Forecast",
    "219": "Shining Stag",
    "220": "Holiday Horns",
    "221": "Ardent Antlers",
    "223": "Festive Lights",
    "3073": "Amethyst Winds",
    "3074": "Golden Gusts",
    "3075": "Smissmas Swirls",
    "3077": "Minty Cypress",
    "3078": "Pristine Pine",
    "3079": "Sparkly Spruce",
    "3081": "Festive Fever",
    "3083": "Golden Glimmer",
    "3084": "Frosty Silver",
    "3085": "Glamorous Dazzle",
    "3087": "Sublime Snowstorm",
    "224": "Crustacean Sensation",
    "226": "Frosted Decadence",
    "228": "Sprinkled Delights",
    "229": "Terrestrial Favor",
    "230": "Tropical Thrill",
    "231": "Flourishing Passion",
    "232": "Dazzling Fireworks",
    "233": "Blazing Fireworks",
    "235": "Twinkling Fireworks",
    "236": "Sparkling Fireworks",
    "237": "Glowing Fireworks",
    "239": "Flying Lights",
    "241": "Limelight",
    "242": "Shining Star",
    "243": "Cold Cosmos",
    "244": "Refracting Fractals",
    "245": "Startrance",
    "247": "Starlush",
    "248": "Starfire",
    "249": "Stardust",
    "250": "Contagious Eruption",
    "251": "Daydream Eruption",
    "252": "Volcanic Eruption",
    "253": "Divine Sunlight",
    "254": "Audiophile",
    "255": "Soundwave",
    "256": "Synesthesia",
    "257": "Haunted Kraken",
    "258": "Eerie Kraken",
    "259": "Soulful Slice",
    "260": "Horsemann's Hack",
    "261": "Haunted Forever!",
    "263": "Forever And Forever!",
    "264": "Cursed Forever!",
    "265": "Moth Plague",
    "266": "Malevolent Monoculi",
    "267": "Haunted Wick",
    "269": "Wicked Wick",
    "270": "Spectral Wick",
    "3088": "Marigold Ritual",
    "3090": "Pungent Poison",
    "3091": "Blazed Brew",
    "3092": "Mysterious Mixture",
    "3093": "Linguistic Deviation",
    "3094": "Aurelian Seal",
    "3095": "Runic Imprisonment",
    "3097": "Prismatic Haze",
    "3098": "Rising Ritual",
    "3100": "Bloody Grip",
    "3102": "Toxic Grip",
    "3103": "Infernal Grip",
    "3104": "Death Grip",
    "271": "Musical Maelstrom",
    "272": "Verdant Virtuoso",
    "273": "Silver Serenade",
    "274": "Cosmic Constellations",
    "276": "Dazzling Constellations",
    "277": "Tainted Frost",
    "278": "Starlight Haze",
    "3105": "Charged Arcane",
    "3106": "Thunderous Rage",
    "3107": "Convulsive Fiery",
    "3108": "Festivized Formation",
    "3110": "Twirling Spirits",
    "3111": "Squash n' Twist",
    "3112": "Midnight Sparklers",
    "3113": "Boundless Blizzard",
    "279": "Hard Carry",
    "281": "Jellyfish Field",
    "283": "Jellyfish Hunter",
    "284": "Jellyfish Jam",
    "285": "Global Clusters",
    "286": "Celestial Starburst",
    "287": "Sylicone Succiduous",
    "288": "Sakura Smoke Bomb",
    "289": "Treasure Trove",
    "290": "Bubble Breeze",
    "291": "Fireflies",
    "292": "Mountain Halo",
    "3114": "Solar Scorched",
    "3115": "Deepsea Rave",
    "3117": "Blooming Beacon",
    "3118": "Beaming Beacon",
    "3119": "Blazing Beacon",
    "3120": "Floppin' Frenzy",
    "3121": "Pastel Trance",
    "3123": "Wildflower Meadows",
    "293": "Celestial Summit",
    "294": "Stellar Ascent",
    "295": "Sapped",
    "297": "Hellspawned Horns",
    "299": "Demonic Impaler",
    "300": "Revenant's Rack",
    "301": "Sixth Sense",
    "303": "Amygdala",
    "304": "The Bone Zone",
    "305": "Arachne's Web",
    "306": "Acidic Climate",
    "307": "Otherworldly Weather",
    "308": "Nightmarish Storm",
    "3124": "Deep-sea Devourer",
    "3125": "Eldritch Horror",
    "3126": "Autumn Leaves",
    "3127": "Dead Man's Party",
    "3128": "Potion Explosion",
    "3129": "Haunted Cremation",
    "3130": "Cremation",
    "309": "Icestruck",
    "311": "Goldstruck",
    "312": "Radiant Rivalry",
    "314": "Radiant Legacy",
    "315": "Frosty Flavours",
    "317": "Mint Frost",
    "318": "North Star",
    "320": "Prettiest Star",
    "321": "Festive Falling Star",
    "322": "Lunar Lights",
    "324": "Fairy Lights",
    "325": "Natural Lights",
    "3131": "Snowfall",
    "3132": "Galactic Connection",
    "3134": "Dark Twilight",
    "3135": "Eldritch Rift",
    "3136": "Selfless Sensation",
    "3137": "Distant Desire",
    "3138": "Glamorous Glance",
    "3139": "Permafrost Essence",
    "3141": "Arctic Delight",
    "3142": "Winning Spirit",
    "3143": "Petal Prance",
}

REVERSE_PARTICLE_MAPPING_LOWER = {v.lower(): k for k, v in PARTICLE_EFFECTS_MAPPING.items()}


WAR_PAINTS = [
    "Park Pigmented", "Sax Waxed", "Yeti Coated", "Croc Dusted", "Macaw Masked", 
    "Piña Polished", "Anodized Aloha", "Bamboo Brushed", "Leopard Printed", 
    "Mannana Peeled", "Tiger Buffed", "Fire Glazed", "Bonk Varnished", 
    "Dream Piped", "Freedom Wrapped", "Bank Rolled", "Clover Camo'd", 
    "Kill Covered", "Pizza Polished", "Bloom Buffed", "Cardboard Boxed", 
    "Merc Stained", "Quack Canvassed", "Star Crossed", "Carpet Bomber Mk.II", 
    "Woodland Warrior Mk.II", "Wrapped Reviver Mk.II", "Forest Fire Mk.II", 
    "Night Owl Mk.II", "Woodsy Widowmaker Mk.II", "Autumn Mk.II", 
    "Plaid Potshotter Mk.II", "Civil Servant Mk.II", "Civic Duty Mk.II", 
    "Bovine Blazemaker Mk.II", "Dead Reckoner Mk.II", "Backwoods Boomstick Mk.II", 
    "Masked Mender Mk.II", "Iron Wood Mk.II", "Macabre Web Mk.II", 
    "Nutcracker Mk.II", "Smalltown Bringdown Mk.II", "Dragon Slayer", 
    "Smissmas Sweater", "Miami Element", "Jazzy", "Mosaic", 
    "Cosmic Calamity", "Hana", "Neo Tokyo", "Uranium", 
    "Alien Tech", "Bomber Soul", "Cabin Fevered", "Damascus and Mahogany", 
    "Dovetailed", "Geometrical Teams", "Hazard Warning", "Polar Surprise", 
    "Electroshocked", "Ghost Town", "Tumor Toasted", "Calavera Canvas", 
    "Spectral Shimmered", "Skull Study", "Haunted Ghosts", "Horror Holiday", 
    "Spirit of Halloween", "Totally Boned", "Winterland Wrapped", "Smissmas Camo", 
    "Smissmas Village", "Frost Ornamented", "Sleighin' Style", "Snow Covered", 
    "Alpine", "Gift Wrapped", "Igloo", "Seriously Snowed", 
    "Spectrum Splattered", "Pumpkin Pied", "Mummified Mimic", "Helldriver", 
    "Sweet Toothed", "Crawlspace Critters", "Raving Dead", "Spider's Cluster", 
    "Candy Coated", "Portal Plastered", "Death Deluxe", "Eyestalker", 
    "Gourdy Green", "Spider Season", "Organ-ically Hellraised", 
    "Starlight Serenity", "Saccharine Striped", "Frosty Delivery", "Cookie Fortress", 
    "Frozen Aurora", "Elfin Enamel", "Smissmas Spycrabs", "Gingerbread Winner", 
    "Peppermint Swirl", "Gifting Mann's Wrapping Paper", "Glacial Glazed", 
    "Snow Globalization", "Snowflake Swirled", "Misfortunate", "Broken Bones", 
    "Party Phantoms", "Necromanced", "Neon-ween", "Polter-Guised", 
    "Swashbuckled", "Kiln and Conquer", "Potent Poison", "Sarsaparilla Sprayed", 
    "Searing Souls", "Simple Spirits", "Skull Cracked", "Sacred Slayer", "Bonzo Gnawed", 
    "Ghoul Blaster", "Metalized Soul", "Pumpkin Plastered", "Chilly Autumn", 
    "Sunriser", "Health and Hell", "Hypergon", 
    "Cream Corned", "Sky Stallion", "Business Class", "Deadly Dragon", 
    "Mechanized Monster", "Steel Brushed", "Warborn", "Bomb Carrier", 
    "Pacific Peacemaker", "Secretly Serviced", "Team Serviced"
]

WEAPON_SKINS_LIST = [
    "Airwolf", "Spruce Deuce", "American Pastoral", "Antique Annihilator", "Aqua Marine", "Autumn", "Backcountry Blaster", "Backwoods Boomstick",
    "Balloonicorn", "Barn Burner", "Black Dahlia", "Blue Mew", "Bogtrotter", "Boneyard", "Bovine Blazemaker",
    "Brain Candy", "Brick House", "Butcher Bird", "Carpet Bomber", "Civic Duty", "Civil Servant", "Citizen Pain",
    "Coffin Nail", "Corsair", "Country Crusher", "Current Event", "Dead Reckoner", "Dressed to Kill", "Earth, Sky and Fire",
    "Flash Fryer", "Flower Power", "Forest Fire", "Hickory Hole-Puncher", "High Roller's", "Homemade Heater", "Iron Wood",
    "King of the Jungle", "Killer Bee", "Lumber From Down Under", "Low Profile", "Macabre Web", "Masked Mender", "Mister Cuddles",
    "Night Owl", "Night Terror", "Nutcracker", "Old Country", "Plaid Potshotter", "Psychedelic Slugger",
    "Purple Range", "Rainbow", "Red Bear", "Red Rock Roscoe", "Reclaimed Reanimator", "Rooftop Wrangler", "Rustic Ruiner",
    "Sand Cannon", "Sandstone Special", "Sudden Flurry", "Sweet Dream", "Tartan Torpedo", "Team Sprayer", "Thunderbolt",
    "Top Shelf", "Torqued to Hell", "Treadplate Tormenter", "Turbocharged", "War Room", "Warhawk", "Wildwood", "Woodland Warrior",
    "Woodsy Widowmaker", "Liquid Asset", "Shell Shocker", "Pink Elephant", "Spark of Life", "Lightning Rod", "Local Hero", "Mayor Revolver", "Smalltown Bringdown", 
    "Shot in the Dark", "Blasted Bombardier", "Wrapped Reviver", "Pumpkin Patch", "Stabbed to Hell", "Shot to Hell", "Blitzkrieg"
]

TEXTURE_NAMES = WAR_PAINTS + WEAPON_SKINS_LIST

USD_KEY_PRICES = {
    'scm_funds': 2.2,
    'paypal': 1.7
}

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
        print(particle_effect)
        particle_id = REVERSE_PARTICLE_MAPPING_LOWER.get(particle_effect.lower())
        if particle_id:
            print("particle img sucsess: ", particle_id)
            return particle_id
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
    forms = []
    forms.append(TransactionForm(request.POST))
    forms.append(TradeValueForm(request.POST))

    for form in forms:
        errorResponse = validate_form(form)
        if errorResponse:
            return None, None, errorResponse
    return forms[0], forms[1], None


def get_trade_history_redirect_response():
    return {
        "message": "Data sent successfully.",
        "redirect_url": reverse("trade_history")
    }


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


def get_current_key_sell_order():
    try:
        url = 'https://steamcommunity.com/market/itemordershistogram?country=US&language=english&currency=1&item_nameid=1'
        response = requests.get(url)
        data = response.json()
        print(data)
        print(data['sell_order_graph'])
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
    print(item.purchase_price, 'purchase price')
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