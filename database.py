from asyncpg import create_pool
import config
import asyncio
import psycopg2

import sqlalchemy.sql
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql.sqltypes import DateTime, NullType, String

from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

class db:


    def __init__(self):

        ## TODO: READ CONFIG FOR CAPS LOCK VALS

        self.DB_NAME = 'pinimg'
        self.DB_HOST = ''
        
        self.user_name = 'pin'
        self.password = 'pinterest'

        self.con, self.cur = None, None
        

        
        
    def connect(self):

        # tries to connect to the database that the API uses.
        # if it is not found, it is initialized and the connection is reattempted.      
        self.db_conn(dbname='postgres')
        self.db_init()
            

    def db_conn(self, dbname, host=''):
        self.con = psycopg2.connect(dbname = dbname,
                                    user = self.user_name,
                                    password = self.password,
                                    host = host)
        self.con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        self.cur = self.con.cursor()
        print("Connected to database {}.".format(dbname))
    
    def db_init(self):

        exists_query = "SELECT exists(SELECT 1 from pg_catalog.pg_database where datname = %s);"
        self.cur.execute(exists_query, (self.DB_NAME,))


        if not self.cur.fetchone()[0]:
            print("Database not found, attempting to create...")
            dbcreate_query = "CREATE DATABASE {}".format(self.DB_NAME) 
            try:
                self.cur.execute(dbcreate_query, (self.DB_NAME,))
            except Exception:
                if Exception == psycopg2.errors.DuplicateDatabase:
                    pass
                print("Failed to create database. Check user permissions.")
            
            self.db_disconnect()

            self.db_conn(dbname=self.DB_NAME)

            colortable_query = "CREATE TABLE colors( color_id serial PRIMARY KEY, hex VARCHAR (7) UNIQUE NOT NULL);"
            self.cur.execute(colortable_query)
            
            urltable_query = "CREATE TABLE urls( url_id serial PRIMARY KEY, url VARCHAR (200) UNIQUE NOT NULL);"
            self.cur.execute(urltable_query)

            idreltable_query = """CREATE TABLE url_color_lookup 
            (color_id int REFERENCES colors (color_id), 
            url_id int REFERENCES urls (url_id), 
            CONSTRAINT url_color_pkey PRIMARY KEY (color_id, url_id)); """
            self.cur.execute(idreltable_query)
        else:
            self.db_conn(dbname=self.DB_NAME)
    
    def AddEntry(self, colors, img_url):
        insert_url_query = "INSERT INTO urls (url_id, url) VALUES (DEFAULT, %s) ON CONFLICT (url) DO NOTHING RETURNING url_id;"
        insert_clr_query = """
                            INSERT INTO colors (color_id, hex) VALUES (DEFAULT, %s) 
                            ON CONFLICT (hex) DO NOTHING RETURNING color_id;"""
        find_clr_query = "SELECT color_id FROM colors WHERE hex = %s; " 
        
        insert_lookup_query = "INSERT INTO url_color_lookup VALUES (%s, %s) ;"

        self.cur.execute(insert_url_query, (img_url,))
        try:
            url_idx = self.cur.fetchone()[0]
        except:
            colors = []

        for col in colors:
            self.cur.execute(insert_clr_query, (col,))
            
            try:
                clr_idx = self.cur.fetchone()[0]
            except:
                clr_idx = -1
            # if entry already exists, look up it's index
            if clr_idx < 0:
                self.cur.execute(find_clr_query, (col,))
                clr_idx = self.cur.fetchone()[0]

            self.cur.execute(insert_lookup_query, (clr_idx, url_idx,))
        
        print("new entry added")



    def fetch_imgs(self, colors):
        colors = tuple(colors)
        get_urls_query = """
    SELECT url_id, url FROM 
    (SELECT url_id, url FROM urls) u
    INNER JOIN
    (SELECT url_id from url_color_lookup WHERE color_id in (SELECT color_id FROM colors WHERE colors.hex in (%s)) 
    GROUP BY url_id HAVING COUNT(url_id) = %s ORDER BY url_id DESC) b
    ON u.url_id = b.url_id;
"""
        self.cur.execute(get_urls_query, (colors, len(colors)))
        
        return self.cur.fetchall()


    def db_disconnect(self):
        self.cur.close()
        self.con.close()

if __name__ == "__main__":
    db = db()
    db.connect()
    print(db.fetch_imgs(["green"]))
