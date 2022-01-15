from PIL import Image


# calculate splendor
# imgPath = './mandelbrotNFT/0.png'

# img = Image.open(imgPath)
# uniqueColors = set()

# w, h = img.size
# for x in range(w):
#     for y in range(h):
#         pixel = img.getpixel((x, y))
#         uniqueColors.add(pixel)

# totalUniqueColors = len(uniqueColors)

# print(totalUniqueColors)


# calcualte complexity (entropy)

import math


def image_entropy(img):
    """calculate the entropy of an image"""
    histogram = img.histogram()
    histogram_length = sum(histogram)

    samples_probability = [float(h) / histogram_length for h in histogram]

    return -sum([p * math.log(p, 2) for p in samples_probability if p != 0])


img = Image.open('./mandelbrotNFT/6.png')

print(image_entropy(img))
