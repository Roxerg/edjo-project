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



    def writeImage(self, img):
        try:
            self.r.sadd(self.imagekey, img)
            return 1
        except:
            return 0

    def writeWord(self, word):
        try: 
            self.r.sadd(self.wordkey, word)
            return 1
        except:
            return 0

    def getImage(self):
        try:
            return self.r.spop(self.imagekey)
        except: 
            return 0

    
    def GetWord(self):
        try:
            self.r.spop(self.wordkey)
        except:
            return 0
            
    def 

