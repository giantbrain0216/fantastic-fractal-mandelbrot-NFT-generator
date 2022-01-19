import json


def getValue(key, attrs):
    for attr in attrs:
        if(attr['trait_type'] == key):
            return attr['value']


def getRare(key, value, all_traits):
    whole = len(all_traits)
    count = 0
    for trait in all_traits:
        for attr in trait['attributes']:
            if(attr['trait_type'] == key and attr['value'] == value):
                count = count + 1
    return round(whole/count)


def genRarity(traits):
    rarities = []
    for tr in traits:
        trait = {
            "name": tr['name'],
            "totalRarityScore": getRare('Stripe', getValue('Stripe', tr['attributes']), traits) + getRare('Cycle', getValue('Cycle', tr['attributes']), traits) + getRare('Step', getValue('Step', tr['attributes']), traits) + getRare('Color', getValue('Color', tr['attributes']), traits) + getRare('Point', getValue('Point', tr['attributes']), traits) + getRare('Location', getValue('Location', tr['attributes']), traits) + getRare('Complexity', getValue('Complexity', tr['attributes']), traits) + getRare('Splendor', getValue('Splendor', tr['attributes']), traits) + getRare('Energy', getValue('Energy', tr['attributes']), traits),
            "rarities": {
                "Stripe": {
                    "value": getValue('Stripe', tr['attributes']),
                    "rarity": getRare('Stripe', getValue('Stripe', tr['attributes']), traits)
                },
                "Cycle": {
                    "value": getValue('Cycle', tr['attributes']),
                    "rarity": getRare('Cycle', getValue('Cycle', tr['attributes']), traits)
                },
                "Step": {
                    "value": getValue('Step', tr['attributes']),
                    "rarity": getRare('Step', getValue('Step', tr['attributes']), traits)
                },
                "Color": {
                    "value": getValue('Color', tr['attributes']),
                    "rarity": getRare('Color', getValue('Color', tr['attributes']), traits)
                },
                "Point": {
                    "value": getValue('Point', tr['attributes']),
                    "rarity": getRare('Point', getValue('Point', tr['attributes']), traits)
                },
                "Location": {
                    "value": getValue('Location', tr['attributes']),
                    "rarity": getRare('Location', getValue('Location', tr['attributes']), traits)
                },
                "Complexiity": {
                    "value": getValue('Complexity', tr['attributes']),
                    "rarity": getRare('Complexity', getValue('Complexity', tr['attributes']), traits)
                },
                "Splendor": {
                    "value": getValue('Splendor', tr['attributes']),
                    "rarity": getRare('Splendor', getValue('Splendor', tr['attributes']), traits)
                },
                "Energy": {
                    "value": getValue('Energy', tr['attributes']),
                    "rarity": getRare('Energy', getValue('Energy', tr['attributes']), traits)
                }
            }
        }
        rarities.append(trait)
    return rarities


all_traits = []


with open('./metadata/all-traits.json', 'r') as f:
    text = f.read()
    all_traits = json.loads(text)


rarities = genRarity(all_traits)
with open('rarities.json', 'w') as rarity:
    json.dump(rarities, rarity, indent=4)
