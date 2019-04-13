from sanic import Sanic
from sanic.response import json
from json import loads

from database import db
from redis_conn import redis_conn

import configparser

import hashlib
import re
import uuid

app = Sanic()
db = db()
r = redis_conn()

conf = configparser.ConfigParser()
conf.read("config.ini")


# sanic parameters 
HOST = conf["sanic"]["host"]
PORT = conf["sanic"]["port"]

# load config
DEFAULT_PERPAGE = conf.getint("app", "perpage")
DEFAULT_EXPIRY = conf.getint("app", "expiry")


@app.route("/find", methods=['GET', 'POST']) 
async def find(request):
    
    args = request.args 
    colors = []
    urls = []

    ### INPUT VALIDATION ###
    try:
        colors = loads(args["colors"][0])
        
        colors = [clr.lower() for clr in colors]
    except KeyError:
        return json({"error": "no 'colors' argument found"}, 
                    status=400)

    for color in colors:
        print(color)
        if not re.match(r"#([a-f0-9]){6}\b", color):
            return json({"error": "incorrect color format"}, 
                        status=400)

    try: 
        perpage = int(args["perpage"][0])
        print(perpage)
    except:
        perpage = DEFAULT_PERPAGE
    
    try:
        expire = int(args["expire"][0])
    except:
        expire = DEFAULT_EXPIRY

    if not (isinstance(perpage, int) or isinstance(expire, int)):
        return json({"error": "invalid arguments"},
                    status=400)
    elif (expire < 0 or perpage < 0):
        return json({"error": "invalid arguments"},
                    status=400)


    ### PROCESSING REQUEST ### 

    try:
        data = db.fetch_imgs(colors)
    except Exception as e:
        print(str(e))
        return json({"error": "database failure"}, status=500)

    # urls for current response, ids for saving session 
    if len(data) > 0:
        ids, urls = zip(*data)
    else:
        ids = []
        urls = []
    urls = list(urls)[0:perpage]

    identifier = uuid.uuid4().hex

    pages = db.save_search(identifier, list(ids), expire, perpage)

    # pages are simply attached to the end of the search ID
    identifier += "P1"

    print(urls)

    return json({
        "images" : urls,
        "total": len(ids),
        "p": 1,
        "pages": pages,
        "id": identifier
    }, status=200)

    

# deletes the search information created by making a /find request.
@app.route("/dispose", methods=['GET', 'POST'])
async def dispose(request):
    try:
        req_id = request.args["id"].split("P")[0]
        db.delete(req_id)
    except:
        return json({"error":"failed to dispose"}, 
                    status=500)

    return json(status=200)
    

# retrieve a specific page of a given search
@app.route("/page", methods=['GET', 'POST'])
async def page(request):

    page = 1
    req_id = None

    ### INPUT VALIDATION ###

    try:
        page = request.args["p"]
        if page <= 0: 
            page = 1
    except:
        return json({"error":"page error"}, status=400)
    
    try:
        req_id = request.args["id"].split("P")[0]
    except:
        return json({"error":"id error"}, status=400)

    ### PROCESSING REQUEST ### 

    return getpage(req_id, page)

# retrieve next page of a given search
@app.route("/page/next", methods=['GET', 'POST'])
async def page_next(request):

    req_id = None
    page = 1

    ### INPUT VALIDATION ###

    try:
        args = request.args["id"][0].split("P")
        req_id = args[0]
        page = int(args[1])
        if page <= 0: 
            page = 1
    except Exception as e:
        print(e)
        return json({"error":"id error"}, status=400)

    ### PROCESSING REQUEST ### 

    return getpage(req_id, page+1)


# code shared by /page and /page/next
def getpage(req_id, page):

    res = db.fetch_page(req_id, page)

    urls = list(res)
    req_id = req_id + "P" + str(page)

    return json({
        "images" : urls,
        "p": page,
        "id" : req_id
    }, status=200)


@app.route("/memes", methods=['GET', 'POST'])
async def memes(request):
    return json({"error": """due to the new EU copyright directive released under 
                             Article 13, this feature is temporarily suspended"""}, 
                status=451)


if __name__ == "__main__":
    app.run(host=HOST, port=PORT)
