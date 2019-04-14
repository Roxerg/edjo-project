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


# primary functionality. finds images based on their color,
# returns paginated results
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
        page = int(request.args["p"][0])
        if page <= 0: 
            page = 1
    except:
        return json({"error":"page error"}, status=400)
    
    try:
        req_id = request.args["id"][0]
    except:
        return json({"error":"id error"}, status=400)

    ### PROCESSING REQUEST ### 
    
    try:
        update = int(request.args["update"][0])
    except:
        update = 0

    total, pages, p = db.fetch_stats(req_id)

    if update == 1:
        db.update_page(req_id, page)

    return get_page(req_id, total, pages, page)





# retrieve next page of a given search
@app.route("/page/next", methods=['GET', 'POST'])
async def page_next(request):

    req_id, total, pages, p = move_page(request)

    if p != pages:
        p += 1

    db.update_page(req_id, p)

    return get_page(req_id, total, pages, p)





# retrieve previous page of a given search
@app.route("/page/previous", methods=['GET', 'POST'])
async def page_prev(request):

    req_id, total, pages, p = move_page(request)

    if p != 1:
        p -= 1

    db.update_page(req_id, p)

    return get_page(req_id, total, pages, p)





def move_page(req):

    req_id = None

    ### INPUT VALIDATION ###

    try:
        req_id = req.args["id"][0]
    except Exception as e:
        return json({"error":"id error"}, status=400)

    ### PROCESSING REQUEST ### 

    total, pages, p = db.fetch_stats(req_id)

    return req_id, total, pages, p





# code shared by /page, /page/next, /page/previous
def get_page(req_id, total, pages, p):

    res = db.fetch_page(req_id, p)

    urls = list(res)

    if len(urls) == 0:
        return json({
            "error":"no results found"
        }, status=404)

    return json({
        "images" : urls,
        "total" : total,
        "p": p,
        "pages": pages,
        "id" : req_id
    }, status=200)






# get the colors from the images
@app.route("/colors", methods=['GET', 'POST'])
async def colors(request):

    try:
        offset = int(request.args["offset"][0])
    except:
        offset = 0
    
    try:
        num = int(request.args["num"][0])
    except:
        num = -1

    colors = db.fetch_colors(offset, num)

    return json({
        "count" : len(colors),
        "colors" : colors
    }, status=200)





@app.route("/stats", methods=['GET', 'POST'])
async def stats(request):

    imgs, colors, search = db.fetch_general_stats()
    return json({
        "stored_images"   : imgs,
        "stored_colors"   : colors,
        "active_searches" : search
        }, status=200)





# an awful joke
@app.route("/memes", methods=['GET', 'POST'])
async def memes(request):
    return json({"error": """due to the new EU copyright directive released under 
                             Article 13, this feature is temporarily suspended"""}, 
                status=451)




if __name__ == "__main__":
    app.run(host=HOST, port=PORT)
