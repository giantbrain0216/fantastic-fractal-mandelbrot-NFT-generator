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

# import cv2
# import matplotlib.pyplot as plt
# import numpy as np
# import math


# originalImage = cv2.imread('./mandelbrotNFT/0.png')
# grayImage = cv2.cvtColor(originalImage, cv2.COLOR_BGR2GRAY)

# #Calculation of histogram (number of pixels of each color)
# histgram = [0]*256
# for i in range(256):
#     for j in range(256):
#         histgram[grayImage[i, j, 0]] += 1

# #Calculation of entropy
# size = grayImage.shape[0] * grayImage.shape[1]
# entropy = 0

# for i in range(256):
#     #Probability of appearance of level i p
#     p = histgram[i]/size
#     if p == 0:
#         continue
#     entropy -= p*math.log2(p)

# plt.imshow(grayImage)
# print('Entropy:{}'.format(entropy))

# import Image
import math

def image_entropy(img):
    """calculate the entropy of an image"""
    histogram = img.histogram()
    histogram_length = sum(histogram)

    samples_probability = [float(h) / histogram_length for h in histogram]

    return -sum([p * math.log(p, 2) for p in samples_probability if p != 0])

img = Image.open('./mandelbrotNFT/6.png')

print(image_entropy(img))