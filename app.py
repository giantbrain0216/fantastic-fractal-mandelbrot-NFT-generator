import eel
import os
import json
import random
import shutil
from mandelbrot import Mandelbrot
import joblib
from joblib import Parallel, delayed

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

        mand = Mandelbrot(maxiter=maxiter, coord=[x1, x2, y1, y2], rgb_thetas=[
                          r, g, b], stripe_s=stripe_s, ncycle=ncycle, step_s=step_s)
        mand.draw('./results/' + str(value) + '.png')
        zoom = int(round((xmax - xmin) * (ymax - ymin)) /
                   ((x2 - x1) * (y2 - y1)))
        token = {
            "image": datums['uploadURL'] + '/' + str(value) + '.png',
            "tokenId": str(value),
            "name": datums['projectName'] + '#' + str(value),
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
            ]
        }
        with open('./metadata/' + str(value), 'w') as outfile:
            json.dump(token, outfile, indent=4)

    if(datums['mode'] == 'semi'):
        x1 = float(datums['coord']['x1'])
        x2 = float(datums['coord']['x2'])
        y1 = float(datums['coord']['y1'])
        y2 = float(datums['coord']['y2'])
        xrange = (x2-x1)/2
        yrange = (y2-y1)/2
        x1 = random.uniform(x1-xrange, x1+xrange)
        x2 = random.uniform(x2-xrange, x2+xrange)
        y1 = random.uniform(y1-yrange, y1+yrange)
        y2 = (9 / 16) * (x2 - x1) + y1
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

        mand = Mandelbrot(maxiter=int(datums['maxiter']), coord=[x1, x2, y1, y2], rgb_thetas=[
                          r, g, b], stripe_s=step_s, ncycle=ncycle, step_s=step_s)
        mand.draw('./results/' + str(value) + '.png')
        zoom = int(round((xmax - xmin) * (ymax - ymin)) /
                   ((x2 - x1) * (y2 - y1)))
        token = {
            "image": datums['uploadURL'] + '/' + str(value) + '.png',
            "tokenId": str(value),
            "name": datums['projectName'] + '#' + str(value),
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
            ]
        }
        with open('./metadata/' + str(value), 'w') as outfile:
            json.dump(token, outfile, indent=4)
    if(datums['mode'] == 'range'):
        x1 = float(datums['coord']['x1'])
        x2 = float(datums['coord']['x2'])
        y1 = float(datums['coord']['y1'])
        y2 = float(datums['coord']['y2'])
        xrange = (x2-x1)/2
        yrange = (y2-y1)/2
        x1 = random.uniform(x1-xrange, x1+xrange)
        x2 = random.uniform(x2-xrange, x2+xrange)
        y1 = random.uniform(y1-yrange, y1+yrange)
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

        mand = Mandelbrot(maxiter=int(datums['maxiter']), coord=[x1, x2, y1, y2], rgb_thetas=[
                          r, g, b], stripe_s=step_s, ncycle=ncycle, step_s=step_s)
        mand.draw('./results/' + str(value) + '.png')
        zoom = int(round((xmax - xmin) * (ymax - ymin)) /
                   ((x2 - x1) * (y2 - y1)))
        token = {
            "image": datums['uploadURL'] + '/' + str(value) + '.png',
            "tokenId": str(value),
            "name": datums['projectName'] + '#' + str(value),
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
            ]
        }
        with open('./metadata/' + str(value), 'w') as outfile:
            json.dump(token, outfile, indent=4)


@eel.expose
def getRange():
    mand = Mandelbrot()
    mand.explore()
    return json.dumps(mand.range)


eel.start('index.html', port=0)
