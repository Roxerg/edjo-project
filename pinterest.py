import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import re






class SiteScraper:

    def __init__(
        self, 
        search_word="car"
            ):

        self.url="https://www.pinterest.co.uk/search/pins/?q="
        options = self.setOptions()
        self.driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver", chrome_options=options)
        self.driver.implicitly_wait(10)
        self.driver.get(self.url+search_word)

        #self.images = self.getImages()
        

        self.sources = []

        self.searchwords = []

        #self.getSources() 
        #self.getSearchWords()

    def setOptions(self, 
                   args=["headless","--ignore-certificate-errors","--test-type"]):
        
        #binary_location="/usr/bin/chromium"
        options = webdriver.ChromeOptions()
        #options.binary_location=binary_location

        for arg in args:
            options.add_argument(arg)
            
        return options
    
    def runScrape(self):
        
        self.getSearchWords()
        self.getSources()
        
    
    def getImages(self):
        return self.driver.find_elements_by_tag_name('img')


    def loadSearch(self, search_word):
        print("attempting to close and reopen new page")
        
        try:
            self.driver.get(self.url+search_word)
        except Exception as e:
            print(str(e))

    def getSearchWords(self):
        
        # gets recommended words for given search.
        # data-test-id
        # "search-guide"
        try:
            #parent = self.driver.find_element_by_class_name("SearchImprovementsBar-InnerScrollContainer")
            elems = self.driver.find_elements_by_css_selector('a[title^="Search for"]') 
        except Exception as e:
            print(e)
            print("no suggested searches found!")
            elems = []
            
        
        for elem in elems:
            #print(elem)
            # gets the part of the title of div that contains the recommended word
            word = re.findall(r'\"(.+?)\"', elem.get_attribute("title"))[0]
            word = word.split(' ')[1]
            # don't add duplicates
            if word not in self.searchwords: 
                self.searchwords.append(word)
        
    def getSources(self):
        
        images = self.getImages()

        # throw out the pinterest logo 
        # all other images are useful.
        for img in images:
            src = img.get_attribute('src')
            self.sources.append(src)

    def Close(self):
        del self.sources
        del self.searchwords
        self.driver.quit()


    def returnSearchWords(self):
        return self.searchwords

    def returnSources(self):
        return self.sources

    def returnImgElements(self):
        return self.images


if __name__ == "__main__":
    scraper = SiteScraper()
    print (scraper.returnSources())
    print (scraper.returnSearchWords())

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
