import color_handler
import threading 
import asyncio

from database import db
from redis_conn import redis_conn

import time

class ImageClassifier:


    def __init__(self, threads):

        self.r = redis_conn()
        self.db = db()
        self.threads = threads

    def run_threads(self):

        for thread in range(0, self.threads):
            threading.Thread(target=self.process_images).start()


    def process_images(self):

        # to avoid blocking caused by adding to the database,
        # prepare_image is run asynchronously and creates new
        # coroutines whenever adding a database entry

        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
        asyncio.ensure_future(self.prepare_image())
        loop.run_forever()


    async def prepare_image(self):

        
        img_url = self.r.get_image()

        while img_url == 0:

            time.sleep(10)
            img_url = self.r.get_image()

        self.r.write_image(img_url)

        while img_url != 0:
            
            img_url = self.r.get_image()
            
            if img_url != 0:
                print(len(img_url))
                img_file = color_handler.load(img_url)
                colors = color_handler.get_colors_hex(img_file)
            
                #self.db.add_entry(colors, img_url)

                loop = asyncio.get_event_loop()
                asyncio.ensure_future(self.db.add_entry(colors, img_url))






