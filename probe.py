import praw
import datetime 
import pickle 
import os

def probe_and_write():
    r = praw.Reddit(user_agent="nooooo", client_id='BiRRpASwJlqWsg', client_secret='onZ-5b3X2XdY-5v68ZvhJJK8Whg')
    with open("reddit_info.csv","a") as log:
        for i in r.front.hot(limit=25):
            subreddit = str(i.subreddit)
            ups = i.ups
            downs = i.downs
            title = i.title.encode("UTF-8")
            over_18 = str(i.over_18)
            num_comments = i.num_comments
            score = i.score
            id_art = i.id
            timestamp_created = datetime.datetime.fromtimestamp(i.created).strftime('%d/%m/%y %H:%M:%S')
            timenow = datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S")
            print subreddit, ups, downs, title, over_18, num_comments, score, id_art
            log.write("{0}\t {1}\t {2}\t {3}\t {4}\t {5}\t {6}\t {7} \t {8}\t {9}\n".format(timenow, timestamp_created, subreddit, id_art, ups, downs, title, num_comments, score, over_18))


## Need to check if the list already exists first. Then I need to call 
## probe_and_write()            
def probe_and_test():
    ## Create the pickle file if it doesn't exist already and dump a dummy list
    if os.path.exists('last_ordering') == False: 
        randomlist = []
        fopen = open('last_ordering', 'wb')
        pickle.dump(randomlist, fopen)
        fopen.close()
    r = praw.Reddit(user_agent="nooooo", client_id='BiRRpASwJlqWsg', client_secret='onZ-5b3X2XdY-5v68ZvhJJK8Whg')
    curr_list = []
    for i in r.front.hot(limit=25):
        curr_list.append(i.id)
    last_order = pickle.load(open('last_ordering', 'r'))
    if last_order != curr_list:
        pickle.dump(curr_list, open('last_ordering', 'wb'))
        return True
    
    else:
        return False

if probe_and_test():
    probe_and_write()
