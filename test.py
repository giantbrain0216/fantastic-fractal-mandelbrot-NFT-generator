from PIL import Image
import imageio
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans
import cv2
from skimage.color import rgb2lab, deltaE_cie76
from collections import Counter
import os

imgPath = './mandelbrotNFT/0.png'

img = Image.open(imgPath)
uniqueColors = set()

w, h = img.size
for x in range(w):
    for y in range(h):
        pixel = img.getpixel((x, y))
        uniqueColors.add(pixel)

totalUniqueColors = len(uniqueColors)

print(uniqueColors)

pic = imageio.imread(
    '/content/drive/MyDrive/Yugesh/Image Color Analyzer in Python/image.JPG')
plt.figure(figsize=(10, 10))
plt.imshow(pic)
image = cv2.imread(
    '/content/drive/MyDrive/Yugesh/Image Color Analyzer in Python/photo.JPG')
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
plt.imshow(image)
