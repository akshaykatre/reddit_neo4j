"""


TO DO:
1. Two worded nation names: Figure out how to deal 
    with country names with two words
2. Possessive words: Words like Indian, Korean, 
    American - all still reflect country
4. How often are two countries referred in the same 
    title? Build a module that helps identify all 
    countries in a title
3. Find the subjects (essence) of the title, and 
    link it to the country
"""


import pandas 
import datetime
import matplotlib.pyplot as plt
import pdb 
import nltk
import pycountry
from collections import OrderedDict

#x = pandas.read_csv("data/reddit_info_all.csv", delimiter="\t", header=None, names=['rank', 'download_time', 'timestamp', 'subreddit', 'id_art', 'ups', 'downs', 'title', 'num_comments', 'score', 'over_18'],error_bad_lines=False)
#x = pandas.DataFrame(x)
#x = x.drop_duplicates('title')

#x = x[x.subreddit==' worldnews']
x = pandas.read_csv("data/reddit_info_worldnews.csv")
titles = x.title.unique()

country_nums = {}

long_country_names = []
common_names = {}
for country in list(pycountry.countries):
    if len(country.name.split()) > 1: 
        long_country_names.append(country.name)
        
    try: 
        if len(country.common_name.split()) > 1:
            common_names.update({country.common_name: country.name})
    except:
        pass



def look_for_country_names(words):
    places = []
    for txt in nltk.word_tokenize(words):
        ## Search for country names - these are single word countries
        try:
            cname = pycountry.countries.get(name=txt).name
            places.append(cname)
        except LookupError:
            pass
        ## Search for common names 
        """
        Added a small hack here for countries like North and South 
        Korea. I had to edit the database of pycountries to add these
        as common names
        """

        try:
            cname = pycountry.countries.get(common_name=txt).common_name
            places.append(cname)
        except LookupError:
            pass
    
        ## Search for country names based on 2 letter codes; US/ UK
        try:
            cname = pycountry.countries.get(alpha_2=txt).name
            places.append(cname)
        except LookupError:
            pass
        
    for lnames in long_country_names:
        if lnames in words:
            places.append(lnames)
    for cnames in common_names:
        if cnames in words:
            places.append(cnames)

    return set(places)

for title in titles:
    names = look_for_country_names(title)
    print(names)
    if names != []:
        for name in names:
            if name not in country_nums.keys():
                country_nums.update({name:1})
            else:   
                country_nums.update({name:country_nums[name]+1})
        
sorted_country_names = OrderedDict(sorted(country_nums.items(), key=lambda kv: kv[1], reverse=True))
plt.bar(range(len(sorted_country_names)), list(sorted_country_names.values()), align='center')
plt.xticks(range(len(sorted_country_names)), list(sorted_country_names.keys()), rotation=90) 
