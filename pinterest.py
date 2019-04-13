import configparser
import requests
import re


from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class SiteScraper:

    def __init__(
        self, 
        search_word="car"
            ):

        conf = configparser.ConfigParser()
        conf.read("config.ini")

        self.url = conf["selenium"]["url"] 
        self.sources = []
        self.searchwords = []
        
        args = conf["selenium"]["args"].split(",")
        path = conf["selenium"]["path"]
        wait = conf.getint("selenium", "wait")
        

        options = self.set_options(args)
        self.driver = webdriver.Chrome(path, chrome_options=options)
        self.driver.implicitly_wait(wait)

        self.driver.get(self.url+search_word)


    def set_options(self, 
                   args=["headless","--ignore-certificate-errors","--test-type"]):
        
        #binary_location="/usr/bin/chromium"
        options = webdriver.ChromeOptions()
        #options.binary_location=binary_location

        for arg in args:
            options.add_argument(arg)
            
        return options
    
    def run_scrape(self):

        self.get_search_words()
        self.get_sources()
        
    
    # gets the html img elements whole
    def get_images(self):
        return self.driver.find_elements_by_tag_name('img')


    def load_search(self, search_word):
        try:
            self.driver.get(self.url+search_word)
        except Exception as e:
            print(str(e))

    def get_search_words(self):
        
        # gets recommended words for given search.
        # which appear on top of the page on some searches
        try:
            elems = self.driver.find_elements_by_css_selector('a[title^="Search for"]') 
        except Exception as e:
            elems = []
            
        
        for elem in elems:
            # gets the part of the title of element that contains the recommended word
            word = re.findall(r'\"(.+?)\"', elem.get_attribute("title"))[0]
            word = word.split(' ')[1]
            # don't add duplicates
            if word not in self.searchwords: 
                self.searchwords.append(word)
        
    # gets the urls to the images from the html elements
    def get_sources(self):
        
        images = self.get_images()

        for img in images:
            src = img.get_attribute('src')
            self.sources.append(src)

    def close(self):
        del self.sources
        del self.searchwords
        self.driver.quit()


    def return_search_words(self):
        return self.searchwords

    def return_sources(self):
        return self.sources

    def return_img_elements(self):
        return self.images


if __name__ == "__main__":
    scraper = SiteScraper()
    print (scraper.return_sources())
    print (scraper.return_search_words())

# SELENIUM
# MANY-TO-MANY
# https://www.pinterest.co.uk/search/pins/?q=car


# THE PLAN:
# 1 . BACKGROUND PROCESSES:
#   (1.1) Process for getting images and writing them into db with color vals
#        (1.1.1) Use SELENIUM to simulate Chrome
#        (1.1.2) Use https://www.pinterest.co.uk/search/pins/?q=car
#   (1.2) Process for getting entries from there and entering them into db with
#       Many-to-Many relationsip
# 2 . ACTUAL API:
#   just make queries to the database
