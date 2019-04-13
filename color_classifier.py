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

    def run_threads(self, threads=2):

        for thread in range(0, threads):
            threading.Thread(target=process_images).start()


    def process_images(self):

        img_url = self.r.get_image()

        while img_url == 0:

            time.sleep(10)
            img_url = self.r.get_image()

        r.write_image(self, img_url)

        while img_url != 0:

            img_url = self.r.get_image()

            img_file = color_handler.load(img_url)
            colors = color_handler.get_colors_hex(img_file)
            
            self.db.add_entry(colors, img_url)







