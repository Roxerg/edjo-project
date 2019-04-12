from scraper import Scraper
from color_classifier import ImageClassifier
from redis_conn import redis_conn
import time


if __name__ == "__main__":


    classifier = ImageClassifier()
    scraper = Scraper()
    
    
    scraper.RunThreads()
    classifier.RunThreads()

    
    




