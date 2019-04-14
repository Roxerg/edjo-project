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
    limit = conf.getint("app", "limit")

    classifier = ImageClassifier()
    scraper = Scraper(limit=limit)
    
    scraper.run_threads()
    classifier.run_threads()

    
    




