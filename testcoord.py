import json

a = []
with open('coords.json', 'r') as f:
    text = f.read()
    a = json.loads(text)

i = 0
for b in a:
    if(float(b['xmax'])-float(b['xmin']) == 0 or float(b['ymax'])-float(b['ymin']) == 0):
        print(i)
        print(b['xmax'])
    
    i = i + 1