from scraper import Scraper
from color_classifier import ImageClassifier
from redis_conn import redis_conn
import configparser
import time


if __name__ == "__main__":

    conf = configparser.ConfigParser()
    conf.read("config.ini")

    sc_threads = conf.getint("app","scraper")
    cl_threads = conf.getint("app","classifier")

    classifier = ImageClassifier()
    scraper = Scraper()
    
    scraper.run_threads()
    classifier.run_threads()

    
    




