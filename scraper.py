import asyncio
import threading

from database import db
from pinterest import SiteScraper
from redis_conn import redis_conn


class Scraper:

    def __init__(self):

        self.drivers = []
        
        self.r = redis_conn()

        self.imgs = set()
        self.used_words = set()
        
    def init_scraper(self, drivernum=2):
        
        for i in range(0, drivernum):
            dr = SiteScraper()
        
            dr.runScrape()

            for word in dr.returnSearchWords():
                if word not in self.used_words:
                    self.words.add(word)

            for img in dr.returnSources():
                self.imgs.add(img)
            
            self.drivers.append(dr)
    
        print("no. of drivers initiated: " + str(len(self.drivers)))

    def run_searches(self, driver, limit=2):

        search_word = self.r.get_word()

        while search_word != 0 and len(self.used_words) < limit:

            self.used_words.add(search_word)
            
            driver.loadSearch(search_word)
            driver.runScrape()

            for word in driver.returnSearchWords():
                if word not in self.used_words:
                    self.words.add(word)

            for img in driver.returnSources():
                # self.imgs.add(img)
                self.r.write_image(img)

            search_word = self.r.get_word()

        driver.Close()
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




