from sanic import Sanic
from sanic.response import json
from database import db
from redis_conn import redis_conn

import hashlib
import re
import uuid

app = Sanic()
db = db()
db.connect()
r = redis_conn()


# load config
DEFAULT_PERPAGE = 10
DEFAULT_EXPIRY = 1000

@app.route("/")
async def test(request):
    return json({"hello": "world"})


@app.route("/echo", methods=['GET', 'POST'])
async def Echo(request):
    return json({"received": True, "args": request.args,
                "url": request.url, "req": request.query_string},
                status=200)



@app.route("/find", methods=['GET', 'POST']) 
async def Find(request):
    
    args = request.args 
    colors = []
    urls = []

    try:
        colors = args["colors"]
    except KeyError:
        return json({"error": "no 'colors' argument found"}, status=400)

    for color in colors:
        if not re.match(r"#([a-f0-9]{6})\b", color):
            return json({"error": "incorrect color format"}, status=400)

    try:
        data = db.fetch_imgs(colors)
    except:
        return json({"error": "database failure"}, status=500)

    # urls for current response, ids for saving session 
    ids, urls = zip(*data)

    # have a field for page number in the database and calculate them initially
    # when this request is called.

    identifier = uuid.uuid4().hex

# deletes the search information created by making a /find request.
@app.route("/dispose", methods=['GET', 'POST'])
async def Dispose(request):
    pass


@app.route("/page", methods=['GET', 'POST'])
async def Page(request):



@app.route("/memes", methods=['GET', 'POST'])
async def Memes(request):
    return json({"error": "due to the new EU copyright directive released under Article 13, this feature is temporarily suspended"}, status=451)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000)
