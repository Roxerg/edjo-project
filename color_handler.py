from PIL import Image
from requests import get
from collections import Counter
import time


def Load(path):

    # if path is URL, GET request it first
    if path[0:4] == "http":
        path = get(path)

    img = Image.open(path)
    return img 

def GetColorsWithFreq(img):
    img = img.convert("RGB")
    # img = img.resize((16,16))
    
    w, h = img.size
    return img.getcolors(maxcolors=w*h)

def GetColorsWithFreqHex(img):
    colors = GetColorsWithFreq(img)
    for i in range(0, len(colors)):
        colors[i] = (colors[i][0], RgbToHex(*colors[i][1]))
    return colors


def GetColorsHex(img):
    colors = GetColorsWithFreqHex(img)
    return [tpl[1] for tpl in colors]


def RgbToHex(r, g, b):
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)


if __name__ == "__main__":
    f = Load("test_img/test1.png")
  
    print(GetColorsHex(f))
    
    
