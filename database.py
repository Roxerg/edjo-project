import psycopg2
import configparser
import asyncio

from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT





class db:


    def __init__(self):

        conf = configparser.ConfigParser()
        conf.read("config.ini")

        self.db_name = conf["postgresql"]["database"]
        self.db_host = conf["postgresql"]["host"]
        initialized = conf.getint("postgresql", "initialized")

        self.user_name = conf["postgresql"]["user"]
        self.password = conf["postgresql"]["password"]

        self.con, self.cur = None, None

        if initialized == 0:
            self.db_conn(dbname='postgres')
            self.db_init()
        else:
            self.db_conn(dbname=self.db_name)


    def db_conn(self, dbname, host=''):
        self.con = psycopg2.connect(dbname = dbname,
                                    user = self.user_name,
                                    password = self.password,
                                    host = host)
        self.con.autocommit = True
        self.con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        self.cur = self.con.cursor()
        print("Connected to database {}.".format(dbname))



    
    def db_init(self):

        # tries to connect to the database that the API uses.
        # if it is not found, it is initialized and the connection is reattempted.

        exists_query = "SELECT exists(SELECT 1 from pg_catalog.pg_database where datname = %s);"
        self.cur.execute(exists_query, (self.db_name,))


        if not self.cur.fetchone()[0]:
            print("Database not found, attempting to create...")
            dbcreate_query = "CREATE DATABASE {}".format(self.db_name) 
            try:
                self.cur.execute(dbcreate_query, (self.db_name,))
            except Exception as e:
                if e == psycopg2.errors.DuplicateDatabase:
                    pass
                else:
                    print("Failed to create database. Check user permissions.")
            
            self.db_disconnect()

            self.db_conn(dbname=self.db_name)

            colortable_query = """CREATE TABLE colors 
                                  (color_id serial PRIMARY KEY, 
                                  hex VARCHAR (7) UNIQUE NOT NULL);"""
            self.cur.execute(colortable_query)
            
            urltable_query = """CREATE TABLE urls( 
                                url_id serial PRIMARY KEY, 
                                url VARCHAR (200) UNIQUE NOT NULL);"""
            self.cur.execute(urltable_query)

            idreltable_query = """CREATE TABLE url_color_lookup 
                                  (color_id int REFERENCES colors (color_id), 
                                  url_id int REFERENCES urls (url_id), 
                                  CONSTRAINT url_color_pkey PRIMARY KEY (color_id, url_id)); """
            self.cur.execute(idreltable_query)

            searchestable_query = """CREATE TABLE searches 
                                     (id serial PRIMARY KEY,
                                     search_id VARCHAR (36) NOT NULL,
                                     page integer NOT NULL, 
                                     url_id integer REFERENCES urls(url_id));"""
            self.cur.execute(searchestable_query)

            searhstatstable_query = """CREATE TABLE search_stats
                                       (search_id VARCHAR (36) PRIMARY KEY,
                                       totalurls integer,
                                       totalpages integer,
                                       currpage integer);"""
            self.cur.execute(searhstatstable_query)

            expiretable_query = """CREATE TABLE expire(
                                   id serial PRIMARY KEY,
                                   search_id VARCHAR (36) REFERENCES searches(search_id),
                                   expire timestamp without time zone);"""
            self.cur.execute(expiretable_query)

        else:
            self.db_conn(dbname=self.db_name)





    
    def add_entry(self, colors, img_url):

        img_url = img_url[:67] + ".jpg"

        insert_url_query = """INSERT INTO urls (url) VALUES (%s) 
                              ON CONFLICT (url) 
                              DO NOTHING RETURNING url_id;"""

        entries_template = ','.join(['%s'] * len(colors))

        insert_clr_query = """INSERT INTO colors (hex) VALUES {} 
                              ON CONFLICT (hex) 
                              DO NOTHING;""".format(entries_template)

        get_clr_idxs_query = """SELECT color_id FROM colors 
                                WHERE hex in ({})""".format(entries_template)

        
        insert_lookup_query = """INSERT INTO url_color_lookup (color_id, url_id) VALUES {} 
                                 ON CONFLICT ON CONSTRAINT url_color_pkey DO NOTHING;"""

        self.cur.execute(insert_url_query, (img_url,))

        # no url_idx will be returned if the url already exists in the database
        try:
            url_idx = self.cur.fetchone()[0]
        except:
            colors = []
         

        if len(colors) == 0:
            return

        self.cur.execute(insert_clr_query, [(x,) for x in colors])
        
        self.cur.execute(get_clr_idxs_query, colors)

        color_idxs = [x[0] for x in self.cur.fetchall()]
        if len(color_idxs) == 0:
            return

        lookupdata = list(zip(color_idxs, [url_idx]*len(color_idxs)))

        entries_template = ','.join(['%s'] * len(lookupdata))
        insert_lookup_query = insert_lookup_query.format(entries_template)

        
        self.cur.execute(insert_lookup_query, lookupdata)
        
        print("new entry added")





    def save_search(self, key, ids, expire, perpage):
        # key - unique identifier of a search
        # ids - ids of images
        # expire - time (in minutes) after which entry can expire
        # perpage - results per page

        # prepare an array of page indices to zip with other variables
        pages = len(ids)//perpage + (len(ids)%perpage>0)
        page_idxs = []
        for p in range(1, pages+1):
            page_idxs += [p]*perpage

        # prepare data for query
        data = list(zip([key]*len(ids), page_idxs, ids))

        entries_template = ','.join(['%s'] * len(ids))

        save_search_query = "INSERT INTO searches (search_id, page, url_id) VALUES {}".format(entries_template)
        self.cur.execute(save_search_query, data)

        save_expiry_query = """INSERT INTO expire (search_id, expire) 
                               VALUES (%s, NOW() + (%s * interval '1 minute'));"""
        self.cur.execute(save_expiry_query, (key, expire,))
        
        save_search_stats_query = """INSERT INTO search_stats 
                                     (search_id, totalurls, totalpages, currpage)
                                     VALUES (%s, %s, %s, %s);"""
        self.cur.execute(save_search_stats_query, (key, len(ids), pages, 1))

        self.delete_expired()

        return pages
        




    def fetch_page(self, key, page):

        page_query = """SELECT url FROM
                        (SELECT url_id FROM searches WHERE search_id = %s AND page = %s) b
                        JOIN urls
                        ON urls.url_id = b.url_id;"""
        self.cur.execute(page_query, (key, page,))

        # flatten an array of one dimensional arrays
        pages = [j for i in self.cur.fetchall() for j in i]

        return pages



    def fetch_stats(self, key):

        stats_query = """SELECT (totalurls, totalpages, currpage)
                         FROM search_stats WHERE search_id = %s;"""
        self.cur.execute(stats_query, (key,))
        res = self.cur.fetchone()
        return eval(res[0])



    def update_page(self, key, page):

        update_page_query = """UPDATE search_stats SET currpage = %s WHERE search_id = %s;"""
        self.cur.execute(update_page_query, (page, key,))



    # to run whenever a new search is saved.
    def delete_expired(self):

        delete_search_query = """DELETE FROM searches WHERE search_id in 
                                 (SELECT search_id FROM expire 
                                 WHERE expire < NOW());"""
        self.cur.execute(delete_search_query)

        delete_expire_query = "DELETE FROM expire WHERE expire < NOW());"
        self.cur.execute(delete_search_query)





    def delete(self, key):
        # If have time, edit tables to cascade on delete

        delete_search_query = "DELETE FROM searches WHERE search_id = %s;"
        self.cur.execute(delete_search_query, (key,))

        delete_expire_query = "DELETE FROM expire WHERE search_id = %s;"
        self.cur.execute(delete_expire_query, (key,))

        delete_stats_query = "DELETE FROM search_stats WHERE search_id = %s;"
        self.cur.execute(delete_stats_query, (key,))





    def fetch_imgs(self, colors):
        params = tuple(colors) + (len(colors), )

        entries_template = ','.join(['%s'] * len(colors))
        
        get_urls_query = """SELECT u.url_id, url FROM 
                            (SELECT url_id, url FROM urls) u
                            INNER JOIN
                            (SELECT url_id from url_color_lookup WHERE color_id in 
                            (SELECT color_id FROM colors WHERE colors.hex in ({})) 
                            GROUP BY url_id HAVING COUNT(url_id) = %s 
                            ORDER BY url_id DESC) b
                            ON u.url_id = b.url_id;""".format(entries_template)

        self.cur.execute(get_urls_query, params)
        
        return self.cur.fetchall()





    def fetch_colors(self, offset=0, num=-1):

        if num == -1:
            get_colors_query = """SELECT hex FROM colors 
                                  ORDER BY color_id ASC
                                  OFFSET %s""";
            self.cur.execute(get_colors_query, (offset,))
        else:
            get_colors_query = """SELECT hex FROM colors 
                                  ORDER BY color_id ASC
                                  OFFSET %s LIMIT %s""";
            self.cur.execute(get_colors_query, (offset, num))

        return [x[0] for x in self.cur.fetchall()]
        
    
    def fetch_general_stats(self):

        imgcount_query = "SELECT COUNT(url) FROM urls;"

        colorcount_query = "SELECT COUNT(hex) FROM colors;"

        searchcount_query = "SELECT COUNT(search_id) FROM search_stats;"

        self.cur.execute(imgcount_query)
        imgs = self.cur.fetchone()

        self.cur.execute(colorcount_query)
        colors = self.cur.fetchone()

        self.cur.execute(searchcount_query)
        search = self.cur.fetchone()

        return imgs[0], colors[0], search[0]




    def db_disconnect(self):
        self.cur.close()
        self.con.close()




if __name__ == "__main__":
    db = db()
    db.connect()
    print(db.fetch_colors())