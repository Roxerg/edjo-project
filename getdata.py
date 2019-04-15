from scraper import Scraper
from color_classifier import ImageClassifier
from redis_conn import redis_conn
import configparser
import time


if __name__ == "__main__":

    # runs classifier and scraper tasks.
    # 

    conf = configparser.ConfigParser()
    conf.read("config.ini")

    sc_threads = conf.getint("app","scraper")
    cl_threads = conf.getint("app","classifier")
    limit = conf.getint("app", "limit")
    
    scraper = Scraper(sc_threads)
    classifier = ImageClassifier(cl_threads)

    scraper.run_threads(limit=limit)
    classifier.run_threads()

    
    




