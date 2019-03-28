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

def get_colors(img):
    img = img.convert("RGB")
    # Image gets resized to reduce the amount of colors to
    # sift through and due to compression low-frequency colors
    # are removed
    img = img.resize((16,16))
    
    # w, h = img.size
    cols = img.getcolors(maxcolors=16*16)
    c = Counter(cols)
    return len(cols)



if __name__ == "__main__":
    start = time.time()
    f = load("test_img/test1.jpg")
  
    print(get_colors(f))
    end = time.time()
    print(end-start)
