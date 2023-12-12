


def create_title(Item):
    title = ''
    if not Item.craftable:
        title += 'Uncraftable'
    if Item.quality != 'unique':
        title += Item.quality.title() + ' '
    if Item.killstreak:
        if Item.killstreak == 'standard':
            title += 'Killstreak '
        else:
            title += Item.killstreak.title() + ' ' + 'Killstreak '
    if Item.australium:
        title += 'Australium' + ' '
    if Item.texture_name:
        title += Item.texture_name.title() + ' '
    if Item.particle_effect:
        title += Item.particle_effect.title() + ' '

    title += Item.item_name

    if Item.wear:
        title += ' ' + Item.wear.title()
    
    return title