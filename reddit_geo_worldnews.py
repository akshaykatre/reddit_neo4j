import pandas 
import datetime
import matplotlib.pyplot as plt
import pdb 
import nltk
import pycountry
from collections import OrderedDict

x = pandas.read_csv("data/reddit_info_all.csv", delimiter="\t", header=None, names=['rank', 'download_time', 'timestamp', 'subreddit', 'id_art', 'ups', 'downs', 'title', 'num_comments', 'score', 'over_18'],error_bad_lines=False)
x = pandas.DataFrame(x)
x = x.drop_duplicates('title')

x = x[x.subreddit==' worldnews']

titles = x.title.unique()

country_nums = {}
def look_for_country_names(txt):
    try:
        cname = pycountry.countries.get(name=txt).name
        return cname
    except LookupError:
        pass

    try:
        cname = pycountry.countries.get(alpha_2=txt).name
        return cname
    except LookupError:
        return False


for title in titles:
    for words in nltk.word_tokenize(title):
        names = look_for_country_names(words)
        if names != False:
            if names not in country_nums.keys():
                    country_nums.update({names:1})
            else:   
                country_nums.update({names:country_nums[names]+1})
        
sorted_country_names = OrderedDict(sorted(country_nums.items(), key=lambda kv: kv[1], reverse=True))
plt.bar(range(len(sorted_country_names)), list(sorted_country_names.values()), align='center')
plt.xticks(range(len(sorted_country_names)), list(sorted_country_names.keys()), rotation=90) 
