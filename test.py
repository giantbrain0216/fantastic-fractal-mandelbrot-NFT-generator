from PIL import Image


# calculate splendor
imgPath = './mandelbrotNFT/90.png'

img = Image.open(imgPath)
uniqueColors = set()

w, h = img.size
for x in range(w):
    for y in range(h):
        pixel = img.getpixel((x, y))
        uniqueColors.add(pixel)

totalUniqueColors = len(uniqueColors)

print(totalUniqueColors)