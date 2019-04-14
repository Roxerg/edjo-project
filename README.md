# Pinterest Color API

a RESTful API for finding Pinterest images based on hex color codes that GOES FAST.

---



## Setup

This application runs on Python 3 with Sanic web server and requires Redis, PostgreSQL, and Selenium (with Chromium). Additional dependencies can be installed by running:

```bash
pip3 install -r requirements.txt
```

If there are issues installing `psycopg2`, run this and retry:

```bash
sudo apt install python3-dev postgresql postgresql-contrib python3-psycopg2 libpq-dev
```

Connection details for PostgreSQL and Redis, as well as parameters such as amount of threads used for scraper and classifier, default amount of items displayed per page, and expiry time can be specified in the `config.ini` file. 

## Running

Scrapers and classifiers that populate the database can be started with:

`python3 getdata.py`

Web Server can be started with:

`python3 main.py`

## API

All endpoints can be accessed via a GET or POST request. Results are returned in `JSON`. 

In case of an issue, a response of this form will be returned:

```json
{
    "error" : "error description"
}
```

Along with an appropriate HTTP Code. 



Available endpoints:

<!--ts-->

* [/find](#/find)
* [/page](#/page)
* [/page/next](#/page/next)
* [/page/previous](#/page/previous)
* [/dispose](#/dispose)
* [/colors](#/colors)

<!--te-->

## /find

Performs the main task of the API, returning a collection of URLs for images containing specified colors.

##### Example request:

```json
{	
    "colors": ["#303f59", "#20b523", "#140c23"],
    "perpage": 3,
    "expire": 120 
} 
```

###### REQUIRED PARAMETERS:

**colors** - a list of 6 character hex color codes as strings. 

###### OPTIONAL PARAMETERS:

**perpage** - amount of entries to display per request. uses a default value if unspecified.

**expire** - time after which a request can expire **(in minutes)**. uses a default value if unspecified.

If **colors** argument is not provided, or is incorrectly formatted, a `400` status code will be returned. If the request failed for an internal reason, `500` status code will be returned.

##### Example response:

```json
{
    "images": 
                [
                    "https://i.pinimg.com/236x/19/f6/ed/19f6ed06c3e36f682ac74df84c806c91.jpg",
                    "https://i.pinimg.com/236x/70/98/7a/70987acba05e1bbd3877e4d2f05573fb.jpg",
                    "https://i.pinimg.com/236x/75/03/33/750333fcd5352a237fa7b6b77fb938ef.jpg"	   
                ],
    "total" : 19,
    "p" : 1,
    "pages": 7,
    "id" : "4b558b47d6724f0fa820b6f7e08779a1p1"
}
```

**images** - Pinterest URLs of images that contain all the requested colors.

**total** - total amount of entries that were found with the colors requested.

**p** - current page of results.

**pages** - total amount of pages of results for this request.

**id** - unique id of the search



## /page 

goes to a specified page of results 

##### Example request:

```json
{	
    "id": "4b558b47d6724f0fa820b6f7e08779a1p2",
    "p": 7,
    "update" : 1
} 
```

###### REQUIRED PARAMETERS:

**id** - initially received from **/find**. 

**p** - choice of a page. 

###### OPTIONAL PARAMETERS:

**update**  - if set to 1, page requests will update the page position for **/page/next**. By default, only **page/next** updates the position for itself. 

##### Example response:

```json
{
    "images": 
                [
                    "https://i.pinimg.com/236x/19/f6/ed/19f6ed06c3e36f682ac74df84c806c91.jpg"
                ],
    "p" : 7,
    "id" : "4b558b47d6724f0fa820b6f7e08779a1P7"
}

```

the format and the meaning of variables is the same as in **/find**.

## /page/next

Instead of returning a specified page, returns the page that follows the current one. Returns `404` if called with the **id** of the last page.

**if /page/next is called on the final page, it will just return the last page again.**

##### Example request:

```json
{
    "id": "4b558b47d6724f0fa820b6f7e08779a1P4"
}
```

###### REQUIRED PARAMETERS:

**id** - initially received from **/find**. 

##### Example response:

Same as **/page**

## page/previous

Identical in all aspects to **page/next**, except it will go backwards instead of forwards.

**if /page/next is called on the first page, it will just return the first page again.**

##### Example request:

same as for **/page/next**

##### Example response:

same as for **/page/next**

this method was mostly made for double-redirection in example responses in this documentation.

## /dispose

Deletes the stored information for the search results with a given  **id**.

##### Example request:

```json

{   
    "id": "4b558b47d6724f0fa820b6f7e08779a1P4"
}
```

###### REQUIRED PARAMETERS:

**id** - initially received from **/find**

This method returns a status code `200` if it successfully cleared the search data. 

## /colors

Returns the hex color codes stored in the database. Only colors that were found in stored images are included in the database. 

No arguments are required for this endpoint, but there are optional **offset** and **num** arguments, that specify which part of the color list to return and how many colors to return, respectively. (colors are sorted by their id in the database, in other words, the order they were added). 

If parameters are not set **offset** is 0 and all colors in the database are returned.

##### Example request:

```json
{
    "offset" : 100,
    "num" : 2500
}
```

###### OPTIONAL PARAMETERS:

**offset** - offset from the start of the list (sorted by their ids) of colors.

**num**  - number of colors to be returned. 

##### Example response:

```json
{   
    "count": 5,
    "colors": ["#303f59", "#20b523", "#140c23", "#47a133", "#100113"]
}
```

**count**  - number of colors returned.

**colors** - hex color codes as list of strings.

If the response returns less colors than requested, there are no more colors after the specified offset.

## /stats

returns statistics in the form of number of things kept in the database. No parameters needed.

##### Example response:

```json
{
    "stored_images": 465,
    "stored_colors": 1476903,
    "active_searches": 2
}
```

# FAQ

**Q:** Why am I getting errors on Selenium?

**A:**  



**Q:** How to install PostgreSQL?

**A:** For PostgreSQL to work with Python, some extra packages need to be installed besides the server and the Python library. To do this, simply run this line:

```bash
sudo apt install python3-dev postgresql postgresql-contrib python3-psycopg2 libpq-dev
```

**Q:** Why are there PostgreSQL authentication erros with "peer" in the description?

**A:** Make sure the postgres user provided in `config.ini` has the password authentication. to do this:

run `locate pg_hba.conf` and open this file with a text editor.

if there is a line like this:

`local   all             postgres                                peer`

replace `peer` with `md5`

after this

**Q:** are there more endpoints?

**A:** Yes. There's one undocumented one and it's terrible.





## Improvements

* Thread management! Ideally, more threads would automatically get dedicated to the task that is more "needed".   E.g. if the scraper builds up a high amount of URLs it can be temporarily stopped and the thread can be reassigned to classifying. 

* An additional database table could be implemented for keeping track of data initially calculated or required for **/find** (total amount of pages, entries per page, expire time) Biggest argument in favour of this is that currently **page/next** is trivial since the page number is not-so-subtly appended to the end of the id, thus requiring id to be switched out for each next.
* **/colors** should take an argument to return an interval rather than entire massive list at once.

* The performance would most likely benefit from calling database actions, especially updates, asynchronously.
* Write the FAQ 

