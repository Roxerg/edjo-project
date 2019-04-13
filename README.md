# Pinterest Color API

a RESTful API for finding Pinterest images based on hex color codes that goes fast.

---



## Setup

This application runs on Python 3 with Sanic web server and requires Redis, PostgreSQL, and Selenium. Additional dependencies can be installed by running

```bash
pip3 install -r requirements.txt
```

Connection details for PostgreSQL and Redis, as well as parameters such as amount of threads used for scraper and classifier, default amount of items displayed per page, and expiry time can be specified in the `config.ini` file. 

## Running

Web Server, along with helper processes can be started with

`python3 main.py`

## API

All URLs can be accessed via a GET or POST request. Results are returned in `JSON`. 

In case of an issue, a response of this form will be returned:

```json
{
    "error" : "error description"
}
```

Along with an appropriate HTTP Code. 



Available URLs:

<!--ts-->

* [/find](#/find)
* [/page](#/page)
* [/page/next](#/page/next)
* [/dispose](#/dispose)
* [/colors](#/colors)

<!--te-->

## /find

Performs the main task of the API, returning a collection of URLs for images containing specified colors.

##### Example request:

```json
{	
    "colors": ["#303f59", "#20b523", "#140c23"],
    "perpage": 3
} 
```

**colors** - a list of 6 character hex color codes as strings. 

**perpage** - amount of entries to display per request. 

If **colors** argument is not provided, or is incorrectly formatted, a 400 status code will be returned. If the request failed for an internal reason, 500 status code will be returned.

##### Example response:

```json
{
    "images": [
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
    "p": 7
} 
```

**id** - initially received from **/find**. 

**p** - choice of a page. 

if **p** exceeds the pagecount, an error is thrown.

##### Example response:

```json
{
    "images": [
        		"https://i.pinimg.com/236x/19/f6/ed/19f6ed06c3e36f682ac74df84c806c91.jpg"
    		  ],
    "total" : 19,
    "p" : 7,
    "pages": 7,
    "id" : "4b558b47d6724f0fa820b6f7e08779a1p7"
}

```

the format and the meaning of variables is the same as in **/find**.

## /page/next

Instead of returning a specified page, returns the page that follows the current one. Returns 404 if called with the **id** of the last page.

##### Example request:

```json
{
    "id": "4b558b47d6724f0fa820b6f7e08779a1p4"
}

```

**id** - initially received from **/find**.

##### Example response:

Same as in **/find** and **/page**

## /dispose

Deletes the stored information for the search results with a given  **id**.

##### Example request:

```json

{   
    "id": "4b558b47d6724f0fa820b6f7e08779a1p4"
}
```

**id** - initially received from **/find**

This method returns a status code 200 if it successfully cleared the search data. 

## /colors

Returns the hex color codes stored in the database. Only colors that were found in stored images are included in the database. 

No arguments are needed for this URL.

##### Example response:

```json
{   
    "count": "5",
    "colors": ["#303f59", "#20b523", "#140c23", "#47a133", "#100113"]
}
```

**count**  - number of colors stored in the database.

**colors** - hex color codes as list of strings. 