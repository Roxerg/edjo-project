# Pinterest Color API

a RESTful API for finding Pinterest images based on hex color codes that goes fast 



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

