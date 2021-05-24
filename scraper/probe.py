import praw
import datetime 
import pickle 
import os
import pymssql 
import json 
import re 
import pandas
from datetime import datetime

configfile = open("dbconfig.json", "r")
data = json.load(configfile)
conn = pymssql.connect("localhost", data['db_reddit']['username'], data['db_reddit']['password'], "redditdata")

def probe_and_write():


    r = praw.Reddit(user_agent="nooooo", client_id=data['redditlogin']['client_id'], client_secret=data['redditlogin']['client_secret'])
    #with open("reddit_info.csv","a") as log:

    for rank, i in enumerate(r.front.hot(limit=25)):
        cursor = conn.cursor()

        postinfo = {"subreddit": str(i.subreddit), 
                    "ups": i.ups,
                    "downs": i.downs,
                    "title": re.sub('[^0-9a-zA-Z ]', '', i.title), #i.title, #i.title.encode("UTF-8"),
                    "over_18": int(i.over_18),
                    "num_comments": i.num_comments,
                    "score": i.score,
                    "id_art": i.id, 
                    "ranking": rank+1,
                    "created_ts": datetime.fromtimestamp(i.created).strftime('%Y-%m-%d %H:%M:%S'),
                    "collection_ts": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
        #print(i.title)
        query = ''' insert into [raw].topposts_all (subreddit, ups, downs, title, over_18, num_comments, score, id_art, ranking, created_ts, collection_ts)
        values ('{subreddit}' , {ups}, {downs}, '{title}', {over_18}, {num_comments}, {score}, '{id_art}', {ranking}, '{created_ts}', '{collection_ts}')
        '''.format(**postinfo)


        #print(query)
        try:
            cursor.execute(query)
            conn.commit()
        except pymssql.IntegrityError: 
            ## In case the post id with the same rank exists in the data base, then we 
            ## don't add anything 
            pass


probe_and_write()

#x = pandas.read_sql("SELECT * from [raw].topposts_all", conn)
#print(x)
conn.close()
