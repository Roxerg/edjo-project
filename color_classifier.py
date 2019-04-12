import color_handler
import threading 

from database import db
from redis_conn import redis_conn

import time


class ImageClassifier:


    def __init__(self):
        
        self.r = redis_conn()
        self.db = db()
        self.db.connect()    



    def RunThreads(self, threads=2):   
   
        img_url = r.getImage()
        while img_url == 0:
            time.sleep(10)
            img_url = r.getImage()

        r.writeImage(self, img_url)

        for thread in range(0, threads):
            threading.Thread(target=ProcessImages).start()



    def ProcessImages(self):
    
        while img_url != 0:
            img_url = r.getImage()

            img_file = color_handler.load(img_url)
        
            colors = color_handler.GetColorsHex(img_file)
            
            self.db.AddEntry(colors, img_url)







