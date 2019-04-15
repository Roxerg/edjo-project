import asyncio
import threading

from database import db
from pinterest import SiteScraper
from redis_conn import redis_conn

import time

class Scraper:

    def __init__(self, drivernum):

        self.drivers = []
        
        self.r = redis_conn()

        self.imgs = set()
        self.used_words = set()

        self.drivernum = drivernum


        
    def init_scraper(self):
        

        for i in range(0, self.drivernum):
            dr = SiteScraper()
        
            dr.run_scrape()

            for word in dr.return_search_words():
                self.r.write_word(word)

            for img in dr.return_sources():
                self.r.write_image(img)
            
            self.drivers.append(dr)
    
        print("no. of drivers initiated: " + str(len(self.drivers)))



    def run_searches(self, driver, limit):

        # pops search word from the redis table,
        # loads up that page, gets images and search words from it
        # deposits both to appropriate redis tables
        # repeats until runs out of search words or reaches a set limit
        
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
        



    def run_threads(self, limit=100):
        self.init_scraper()
        for driver in self.drivers:
            threading.Thread(target=self.run_searches, args=[driver, limit]).start()
    
    #async def Run(self):
      
    #    loop = asyncio.get_event_loop()   
        #loop.run_until_complete(asyncio.ensure_future(self.InitScraper()))
    #    self.InitScraper(1)

    #    tasks = []
    #    for driver in self.drivers:
    #        tasks.append(asyncio.ensure_future(self.RunSearches(driver)))

    #    loop.run_until_complete(asyncio.gather(*tasks))




