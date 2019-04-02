import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import re






class SiteScraper:

    def __init__(
        self, 
        url="https://www.pinterest.co.uk/search/pins/?q=car"
            ):


        options = self.setOptions()
        self.driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver", chrome_options=options)
        self.driver.implicitly_wait(20)
        self.driver.get(url)

        self.images = self.getImages()
        
        self.sources = []
        self.searchwords = []
        
        self.getSources() 
        self.getSearchWords()

    def setOptions(self, args=["headless","--ignore-certificate-errors","--test-type"]):
        #binary_location="/usr/bin/chromium"
        options = webdriver.ChromeOptions()
        #options.binary_location=binary_location

        for arg in args:
            options.add_argument(arg)
            
        return options

    def getImages(self):
        return self.driver.find_elements_by_tag_name('img')


    def getSearchWords(self):
        
        # gets recommended words for given search.

        try:
            parent = self.driver.find_element_by_class_name("Jea gjz zI7 iyn Hsu")
            elems = parent.find_elements_by_tag_name("div")
        except:
            elems = []
            
        for elem in elems:
            # gets the part of the title of div that contains the recommended word
            word = re.findall(r'\"(.+?)\"', elem.get_attribute("title"))[0]
            word = word.split(' ')[1]
            # don't add duplicates
            if word not in self.searchwords: 
                self.searchwords.append(word)
        

    def getSources(self):
        
        # throw out the pinterest logo 
        for img in self.images:
            src = img.get_attribute('src')
            self.sources.append(src)



if __name__ == "__main__":
    sitescrap = SiteScraper()                                                                                                                                                       
    print(sitescrap.sources)




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
#   apparently pagination is ok