from PIL import Image
from requests import get
from collections import Counter
import time


def load(path):

    # if path is URL, GET request it first
    if path[0:4] == "http":
        path = get(path)

    img = Image.open(path)
    return img 

# returns colors along with their frequencies in RGB
def get_colors_freq_rgb(img):
    img = img.convert("RGB")
    # img = img.resize((16,16))
    
    w, h = img.size
    return img.getcolors(maxcolors=w*h)

# returns colors along with their frequencies in hex codes
def get_colors_freq_hex(img):
    colors = get_colors_freq_rgb(img)
    for i in range(0, len(colors)):
        colors[i] = (colors[i][0], rgb_to_hex(*colors[i][1]))
    return colors

# returns just the unique hex codes of colors
def get_colors_hex(img):
    colors = get_colors_freq_hex(img)
    return [tpl[1] for tpl in colors]


def rgb_to_hex(r, g, b):
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)

