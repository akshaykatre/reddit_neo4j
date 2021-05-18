import praw
import datetime 
import pickle 
import os
import pymssql 
import json 
import re 
import pandas

configfile = open("dbconfig.json", "r")
data = json.load(configfile)
conn = pymssql.connect("localhost", data['db_reddit']['username'], data['db_reddit']['password'], "redditdata")

def probe_and_write():


    r = praw.Reddit(user_agent="nooooo", client_id=data['redditlogin']['client_id'], client_secret=data['redditlogin']['client_secret'])
    #with open("reddit_info.csv","a") as log:

    for i in r.front.hot(limit=25):
        cursor = conn.cursor()

        postinfo = {"subreddit": str(i.subreddit), 
                    "ups": i.ups,
                    "downs": i.downs,
                    "title": re.sub('[^0-9a-zA-Z ]', '', i.title), #i.title, #i.title.encode("UTF-8"),
                    "over_18": int(i.over_18),
                    "num_comments": i.num_comments,
                    "score": i.score,
                    "id_art": i.id}
        print(i.title)
        query = ''' insert into topposts_all (subreddit, ups, downs, title, over_18, num_comments, score, id_art)
        values ('{subreddit}' , {ups}, {downs}, '{title}', {over_18}, {num_comments}, {score}, '{id_art}')
        '''.format(**postinfo)


        print(query)
        cursor.execute(query)


x = pandas.read_sql("SELECT * from topposts_all", conn)