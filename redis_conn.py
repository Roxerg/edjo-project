import redis
import configparser 


class redis_conn:

    def __init__(self):
        conf = configparser.ConfigParser()
        conf.read("config.ini")

        host = conf["redis"]["host"]
        port = conf["redis"]["port"]
        pwd  = conf["redis"]["password"]

        self.imagekey = conf["redis"]["imagekey"]
        self.wordkey = conf["redis"]["wordskey"]
        del conf

        self.r = redis.Redis(
                    host=host,
                    port=port,
                    password=pwd)


    # only two sets are used:
    # for storing unclassified image urls
    # for storing unsearched keywords
    # 0 used to identify a failed addition or pop.

    def write_image(self, img):
        try:
            self.r.sadd(self.imagekey, img)
            return 1
        except:
            return 0

    def write_word(self, word):
        
        
        try: 
            self.r.sadd(self.wordkey, word)
            return 1
        except:
            return 0

    def get_image(self):
        try:
            return self.r.spop(self.imagekey).decode("utf-8")
        except: 
            return 0

    
    def get_word(self):
        try:
            return self.r.spop(self.wordkey).decode("utf-8")
        except:
            return 0
            

