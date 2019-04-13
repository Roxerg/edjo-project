import asyncio
import threading

from database import db
from pinterest import SiteScraper
from redis_conn import redis_conn

import time

class Scraper:

    def __init__(self):

        self.drivers = []
        
        self.r = redis_conn()

        self.imgs = set()
        self.used_words = set()
        
    def init_scraper(self, drivernum=1):
        

        for i in range(0, drivernum):
            dr = SiteScraper()
        
            dr.run_scrape()

            for word in dr.return_search_words():
                self.r.write_word(word)

            for img in dr.return_sources():
                self.r.write_image(img)
            
            self.drivers.append(dr)
    
        print("no. of drivers initiated: " + str(len(self.drivers)))

    def run_searches(self, driver, limit=5):

        
        search_word = self.r.get_word()
        
        while search_word != 0 and search_word != None and len(self.used_words) < limit:


            self.used_words.add(search_word)
            

            driver.load_search(search_word)
            driver.run_scrape()

            words = driver.return_search_words()
            for word in words:
                if word not in self.used_words:
                    self.r.write_word(word)

            for img in driver.return_sources():
                self.r.write_image(img)

            search_word = self.r.get_word()

        
        print("used: " + str(len(self.used_words)))
        driver.close()
        return 1
        

    def run_threads(self):
        self.init_scraper()
        for driver in self.drivers:
            threading.Thread(target=self.run_searches, args=[driver]).start()
    
    #async def Run(self):
      
    #    loop = asyncio.get_event_loop()   
        #loop.run_until_complete(asyncio.ensure_future(self.InitScraper()))
    #    self.InitScraper(1)

    #    tasks = []
    #    for driver in self.drivers:
    #        tasks.append(asyncio.ensure_future(self.RunSearches(driver)))

    #    loop.run_until_complete(asyncio.gather(*tasks))




