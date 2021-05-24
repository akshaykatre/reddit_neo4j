import pandas
import datetime
import matplotlib.pyplot as plt
import pdb 

x = pandas.read_csv("reddit_info_all.csv", delimiter="\t", names=["position", "probe_time", "created_time", "subreddit", "id", "ups", "downs", "title", "num_comments", "score", "over_18"])

def set_hours(hour_map, time):
    ## 
    if time.hour in hour_map.keys() == False:
        hour_map.update({time.hour:0})
    if time.hour in hour_map.keys() == True:
        hour_map[time.hour]+=1 


def first_position(csvfile, inposition = 0, weekdaystyle='r', weekendstyle='b'):
    ## The idea of this function is to check how long one particular article has been in the first 
    ## or any given position
    ## initialise variables 
    ## thisid is initialised to '' so that the first instance is recorded 
    ## hours_* are maps that hold the number of changes experienced in a particular hour for the 
    ## probe time
    thisid = ''
    hours_weekdays = {}
    hours_weekends = {}
    hours = {}

    ## Loop over different rows of the csv
    for i, ids, times, created_time, sub, o18 in zip(csvfile.position, csvfile.id, csvfile.probe_time, csvfile.created_time, csvfile.subreddit, csvfile.over_18):

        ## If the relevant position is not in the first column, lets forget about the entry
        if i != inposition :
            continue

        ## For the first instance, need to store the 'ids' value in thisid and record its 
        ## corresponding times; 
        ## thisid_ft : first time the sub with the ID was created
        ## thisid_ct : creation time of sub with ID 
        if thisid == '':
            thisid = ids
            thisid_ft = times
            thisid_ct = created_time
            thissub = sub


        if ids != thisid:
            lasttime = datetime.datetime.strptime(times, ' %d/%m/%y %H:%M:%S')
            initial_time = datetime.datetime.strptime(thisid_ft, ' %d/%m/%y %H:%M:%S')
            thisid_ft = times

            ## 
            if 0 <= initial_time.weekday() <= 5:
                set_hours(hours_weekdays, initial_time)
            if initial_time.weekday() > 5:
                set_hours(hours_weekends, initial_time)
      
            print(thisid, "has time", (lasttime-initial_time).total_seconds()/60., initial_time.hour, thissub, o18)
            thisid = ids
            thisid_ct = created_time
            thissub = sub

    plt.plot(hours_weekdays.keys(), hours_weekdays.values(), weekdaystyle,label=str(inposition+1)+' Weekday')
    plt.plot(hours_weekends.keys(), [(x*5)/2. for x in hours_weekends.values()], weekendstyle,label=str(inposition+1)+' Weekend')
    plt.legend(fancybox=True)

first_position(x, 0, weekdaystyle='r-', weekendstyle='b--')
first_position(x, 1, weekdaystyle='y', weekendstyle='g:')
