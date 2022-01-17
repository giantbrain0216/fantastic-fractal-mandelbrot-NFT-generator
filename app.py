import eel
import os
import json
import random
import shutil
from mandelbrot import Mandelbrot
import joblib
from joblib import Parallel, delayed
from colorthief import ColorThief
from scipy.spatial import KDTree
from webcolors import (
    CSS3_HEX_TO_NAMES,
    hex_to_rgb,
)
from PIL import Image
import math
import timeit

number_of_cpu = joblib.cpu_count()

eel.init('web')


@eel.expose
def generateFractal(data):

    all_traits = []

    if(os.path.isdir('results') != True):
        os.makedirs('results')
    else:
        shutil.rmtree('results')
        os.makedirs('results')

    if(os.path.isdir('metadata') != True):
        os.makedirs('metadata')
    else:
        shutil.rmtree('metadata')
        os.makedirs('metadata')

    datums = json.loads(data)
    Parallel(n_jobs=number_of_cpu)(delayed(drawFractal)(i, datums)
                                   for i in range(int(datums['repeatNum'])))

    for filename in os.listdir("metadata"):
        with open(os.path.join("metadata", filename), 'r') as f:
            text = f.read()
            all_traits.append(json.loads(text))
    METADATA_FILE_NAME = 'all-traits.json'
    with open('./metadata/' + METADATA_FILE_NAME, 'w') as outfile:
        json.dump(all_traits, outfile, indent=4)
    # for i in range(int(datums['repeatNum'])):
    #     drawFractal(i, datums)
    return 'success'


def drawFractal(value, datums):
    xmin = -2
    xmax = 1
    ymin = -1
    ymax = 1

    pointNames = [
        {'name': "Poseidon", 'value': (0.25, 9)},
        {'name': "Hera", 'value': (0.04, 0.25)},
        {'name': "Zeus", 'value': (-0.3, 0.04)},
        {'name': "Demeter", 'value': (-0.453, -0.3)},
        {'name': "Athena", 'value': (-0.637, -0.453)},
        {'name': "Apollo", 'value': (-0.735, -0.637)},
        {'name': "Aphrodite", 'value': (-0.8, -0.735)},
        {'name': "Ares", 'value': (-0.97, -0.8)},
        {'name': "Artemis", 'value': (-1.226, -0.97)},
        {'name': "Hephaestus", 'value': (-1.29, -1.226)},
        {'name': "Hermes", 'value': (-1.43, -1.29)},
        {'name': "Hestia", 'value': (-9, -1.43)}
    ]
    locationNames = [
        {'name': "Surface", 'value': (-1, 200)},
        {'name': "Shallow", 'value': (200, 2000)},
        {'name': "Profound", 'value': (2000, 20000)},
        {'name': "Deep", 'value': (20000, float('inf'))},
    ]

    if(datums['mode'] == 'auto'):
        x1 = random.uniform(xmin, xmax)
        x2 = random.uniform(xmin, xmax)
        y1 = random.uniform(ymin, ymax)
        y2 = (1 / 1) * (x2 - x1) + y1
        r = round(random.uniform(0, 1), 2)
        g = round(random.uniform(0, 1), 2)
        b = round(random.uniform(0, 1), 2)
        maxiter = int(datums['maxiter'])
        stripe_s = random.randint(0, 10)
        ncycle = random.randint(1, 64)
        step_s = random.randint(0, 10)
        xpixels = 1280 if datums['imgResolution'] == '' else int(
            datums['imgResolution'])

        start = timeit.default_timer()
        mand = Mandelbrot(maxiter=maxiter, coord=[x1, x2, y1, y2], rgb_thetas=[
                          r, g, b], stripe_s=stripe_s, ncycle=ncycle, step_s=step_s, xpixels=xpixels)
        mand.draw('./results/' + str(value) + '.png')
        stop = timeit.default_timer()

        color_thief = ColorThief('./results/' + str(value) + '.png')
        dominant_color = color_thief.get_color(quality=1)
        dominant_color_name = convert_rgb_to_names(dominant_color).capitalize()

        centerPointX = (x2 + x1) / 2
        pointName = ''
        for point in pointNames:
            if point['value'][0] <= centerPointX and point['value'][1] >= centerPointX:
                pointName = point['name']

        locationName = ''
        zoom = int(round((xmax - xmin) * (ymax - ymin)) /
                   ((x2 - x1) * (y2 - y1)))
        for location in locationNames:
            if location['value'][0] <= zoom and location['value'][1] >= zoom:
                locationName = location['name']

        x = (x1 + x2) / 2
        y = (y1 + y2) / 2

        imgg = Image.open('./results/' + str(value) + '.png')

        complexity = image_complexity(imgg)
        splendor = image_splendor(imgg)
        energy = stop-start

        token = {
            "image": datums['uploadURL'] + '/' + str(value) + '.png',
            "tokenId": str(value),
            "name": "#" + str(value) + " " + locationName + " " + dominant_color_name + " " + pointName,
            "description": dominant_color_name + " " + pointName + " that consumed " + str(energy) + " of energy in a neighbourhood of the point (" + str(x) + ", " + str(y) + "), on the " + locationName + " of the Mandelbrot set",
            "attributes": [
                {
                    "trait_type": "Stripe",
                    "value": stripe_s,
                },
                {
                    "trait_type": "Cycle",
                    "value": ncycle,
                },
                {
                    "trait_type": "Step",
                    "value": step_s,
                },
                {
                    "trait_type": "Zoom",
                    "value": zoom,
                },
                {
                    "trait_type": "Color",
                    "value": dominant_color_name,
                },
                {
                    "trait_type": "Point",
                    "value": pointName,
                },
                {
                    "trait_type": "Location",
                    "value": locationName,
                },
                {
                    "trait_type": "x",
                    "value": x,
                },
                {
                    "trait_type": "y",
                    "value": y,
                },
                {
                    "trait_type": "Copmlexity",
                    "value": round(complexity, 2),
                },
                {
                    "trait_type": "Splendor",
                    "value": splendor,
                },
                {
                    "trait_type": "Energy",
                    "value": round(energy),
                },
            ]
        }
        with open('./metadata/' + str(value), 'w') as outfile:
            json.dump(token, outfile, indent=4)

    if(datums['mode'] == 'semi'):
        x1 = float(datums['coord']['x1'])
        x2 = float(datums['coord']['x2'])
        y1 = float(datums['coord']['y1'])
        y2 = float(datums['coord']['y2'])
        x1 = random.uniform(x1, x2)
        x2 = random.uniform(x1, x2)
        y1 = random.uniform(y1, y2)
        y2 = (1 / 1) * (x2 - x1) + y1
        xpixels = 1280 if datums['imgResolution'] == '' else int(
            datums['imgResolution'])
        r = round(random.uniform(0, 1), 2) if datums['color']['r'] == '' else float(
            datums['color']['r'])
        g = round(random.uniform(0, 1), 2) if datums['color']['g'] == '' else float(
            datums['color']['g'])
        b = round(random.uniform(0, 1), 2) if datums['color']['b'] == '' else float(
            datums['color']['b'])
        stripe_s = random.randint(
            0, 10) if datums['stripeS'] == '' else int(datums['stripeS'])
        ncycle = random.randint(
            1, 64) if datums['ncycle'] == '' else int(datums['ncycle'])
        step_s = random.randint(
            0, 10) if datums['stepS'] == '' else int(datums['stepS'])

        start = timeit.default_timer()
        mand = Mandelbrot(maxiter=int(datums['maxiter']), coord=[x1, x2, y1, y2], rgb_thetas=[
                          r, g, b], stripe_s=step_s, ncycle=ncycle, step_s=step_s, xpixels=xpixels)
        mand.draw('./results/' + str(value) + '.png')
        stop = timeit.default_timer()

        color_thief = ColorThief('./results/' + str(value) + '.png')
        dominant_color = color_thief.get_color(quality=1)
        dominant_color_name = convert_rgb_to_names(dominant_color).capitalize()

        centerPointX = (x2 + x1) / 2
        pointName = ''
        for point in pointNames:
            if point['value'][0] <= centerPointX and point['value'][1] >= centerPointX:
                pointName = point['name']

        locationName = ''
        zoom = int(round((xmax - xmin) * (ymax - ymin)) /
                   ((x2 - x1) * (y2 - y1)))
        for location in locationNames:
            if location['value'][0] <= zoom and location['value'][1] >= zoom:
                locationName = location['name']

        x = (x1 + x2) / 2
        y = (y1 + y2) / 2

        imgg = Image.open('./results/' + str(value) + '.png')

        complexity = image_complexity(imgg)
        splendor = image_splendor(imgg)
        energy = stop-start

        token = {
            "image": datums['uploadURL'] + '/' + str(value) + '.png',
            "tokenId": str(value),
            "name": "#" + str(value) + " " + locationName + " " + dominant_color_name + " " + pointName,
            "description": dominant_color_name + " " + pointName + " in a neighbourhood of the point (" + str(x) + ", " + str(y) + "), on the " + locationName + " of the Mandelbrot set",
            "attributes": [
                {
                    "trait_type": "Stripe",
                    "value": stripe_s,
                },
                {
                    "trait_type": "Cycle",
                    "value": ncycle,
                },
                {
                    "trait_type": "Step",
                    "value": step_s,
                },
                {
                    "trait_type": "Zoom",
                    "value": zoom,
                },
                {
                    "trait_type": "Color",
                    "value": dominant_color_name,
                },
                {
                    "trait_type": "Point",
                    "value": pointName,
                },
                {
                    "trait_type": "Location",
                    "value": locationName,
                },
                {
                    "trait_type": "x",
                    "value": x,
                },
                {
                    "trait_type": "y",
                    "value": y,
                },
                {
                    "trait_type": "Copmlexity",
                    "value": round(complexity, 2),
                },
                {
                    "trait_type": "Splendor",
                    "value": splendor,
                },
                {
                    "trait_type": "Energy",
                    "value": round(energy),
                },
            ]
        }
        with open('./metadata/' + str(value), 'w') as outfile:
            json.dump(token, outfile, indent=4)

    if(datums['mode'] == 'range'):
        x1 = float(datums['coord']['x1'])
        x2 = float(datums['coord']['x2'])
        y1 = float(datums['coord']['y1'])
        y2 = float(datums['coord']['y2'])
        x1 = random.uniform(x1, x2)
        x2 = random.uniform(x1, x2)
        y1 = random.uniform(y1, y2)
        y2 = (1 / 1) * (x2 - x1) + y1

        r = round(random.uniform(0, 1), 2) if datums['color']['r'] == '' else float(
            datums['color']['r'])
        g = round(random.uniform(0, 1), 2) if datums['color']['g'] == '' else float(
            datums['color']['g'])
        b = round(random.uniform(0, 1), 2) if datums['color']['b'] == '' else float(
            datums['color']['b'])
        stripe_s = random.randint(
            0, 10) if datums['stripeS'] == '' else int(datums['stripeS'])
        ncycle = random.randint(
            1, 64) if datums['ncycle'] == '' else int(datums['ncycle'])
        step_s = random.randint(
            0, 10) if datums['stepS'] == '' else int(datums['stepS'])
        xpixels = 1280 if datums['imgResolution'] == '' else int(
            datums['imgResolution'])

        start = timeit.default_timer()
        mand = Mandelbrot(maxiter=int(datums['maxiter']), coord=[x1, x2, y1, y2], rgb_thetas=[
                          r, g, b], stripe_s=step_s, ncycle=ncycle, step_s=step_s, xpixels=xpixels)
        mand.draw('./results/' + str(value) + '.png')
        stop = timeit.default_timer()

        color_thief = ColorThief('./results/' + str(value) + '.png')
        dominant_color = color_thief.get_color(quality=1)
        dominant_color_name = convert_rgb_to_names(dominant_color).capitalize()

        centerPointX = (x2 + x1) / 2
        pointName = ''
        for point in pointNames:
            if point['value'][0] <= centerPointX and point['value'][1] >= centerPointX:
                pointName = point['name']

        locationName = ''
        zoom = int(round((xmax - xmin) * (ymax - ymin)) /
                   ((x2 - x1) * (y2 - y1)))
        for location in locationNames:
            if location['value'][0] <= zoom and location['value'][1] >= zoom:
                locationName = location['name']

        x = (x1 + x2) / 2
        y = (y1 + y2) / 2

        imgg = Image.open('./results/' + str(value) + '.png')

        complexity = image_complexity(imgg)
        splendor = image_splendor(imgg)
        energy = stop-start

        token = {
            "image": datums['uploadURL'] + '/' + str(value) + '.png',
            "tokenId": str(value),
            "name": "#" + str(value) + " " + locationName + " " + dominant_color_name + " " + pointName,
            "description": dominant_color_name + " " + pointName + " in a neighbourhood of the point (" + str(x) + ", " + str(y) + "), on the " + locationName + " of the Mandelbrot set",
            "attributes": [
                {
                    "trait_type": "Stripe",
                    "value": stripe_s,
                },
                {
                    "trait_type": "Cycle",
                    "value": ncycle,
                },
                {
                    "trait_type": "Step",
                    "value": step_s,
                },
                {
                    "trait_type": "Zoom",
                    "value": zoom,
                },
                {
                    "trait_type": "Color",
                    "value": dominant_color_name,
                },
                {
                    "trait_type": "Point",
                    "value": pointName,
                },
                {
                    "trait_type": "Location",
                    "value": locationName,
                },
                {
                    "trait_type": "x",
                    "value": x,
                },
                {
                    "trait_type": "y",
                    "value": y,
                },
                {
                    "trait_type": "Copmlexity",
                    "value": round(complexity, 2),
                },
                {
                    "trait_type": "Splendor",
                    "value": splendor,
                },
                {
                    "trait_type": "Energy",
                    "value": round(energy),
                },
            ]
        }
        with open('./metadata/' + str(value), 'w') as outfile:
            json.dump(token, outfile, indent=4)


@eel.expose
def getRange():
    mand = Mandelbrot()
    mand.explore()
    return json.dumps(mand.range)


def convert_rgb_to_names(rgb_tuple):
    css3_db = CSS3_HEX_TO_NAMES
    names = []
    rgb_values = []

    for color_hex, color_name in css3_db.items():
        names.append(color_name)
        rgb_values.append(hex_to_rgb(color_hex))

    kdt_db = KDTree(rgb_values)

    distance, index = kdt_db.query(rgb_tuple)
    return names[index]


def image_complexity(img):
    histogram = img.histogram()
    histogram_length = sum(histogram)

    samples_probability = [float(h) / histogram_length for h in histogram]

    return -sum([p * math.log(p, 2) for p in samples_probability if p != 0])


def image_splendor(img):
    uniqueColors = set()
    w, h = img.size
    for x in range(w):
        for y in range(h):
            pixel = img.getpixel((x, y))
            uniqueColors.add(pixel)
    totalUniqueColors = len(uniqueColors)
    return totalUniqueColors


eel.start('index.html', port=0)
