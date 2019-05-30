"""


TO DO:
1. DONE: Two worded nation names: Figure out how to deal 
    with country names with two words 
2. DONE: Possessive words: Words like Indian, Korean, 
    American - all still reflect country
3. DONE: How often are two countries referred in the same 
    title? Build a module that helps identify all 
    countries in a title
4. Find the subjects (essence) of the title, and 
    link it to the country
5. DONE: Upload data to neo4j database 

Minor fixes: 
1. To be able to track abbreviations like "UK" 
2. DONE: Full names of countries may not be identified 
    in sentences. Eg.: Korea, Democratic People's Republic of.
    Need to be able to identify these as well. 
3. Plurals are not working for possessive words. 
"""


import pandas 
import datetime
import matplotlib.pyplot as plt
import pdb 
import nltk
import pycountry
from collections import OrderedDict, Counter
import json 
from neo4j.v1 import GraphDatabase, basic_auth

#x = pandas.read_csv("data/reddit_info_all.csv", delimiter="\t", header=None, names=['rank', 'download_time', 'timestamp', 'subreddit', 'id_art', 'ups', 'downs', 'title', 'num_comments', 'score', 'over_18'],error_bad_lines=False)
#x = pandas.DataFrame(x)
#x = x.drop_duplicates('title')
nn_df = pandas.read_csv('data/demonyms.csv')
nationalities_nation = {}
for nationality, nation in nn_df.values:
    nationalities_nation.update({nationality:nation}) ## To be case insensitive

#x = x[x.subreddit==' worldnews']
x = pandas.read_csv("data/reddit_info_worldnews.csv")
titles = x.title

country_nums = {}



long_country_names = []
common_names = {}
for country in list(pycountry.countries):
    if len(country.name.split()) > 1: 
        try:
            long_country_names.append(country.official_name)
        except AttributeError:
            long_country_names.append(country.name)

    try: 
        if len(country.common_name.split()) > 1:
            common_names.update({country.common_name: country.name})
    except:
        pass



def look_for_country_names(words):
    """
    Input: str 
    Output: Return of set of country names in text

    The fuction looks for words that indicate names of countries in the 
    text. It can handle sentences as well as words. 

    Each word in the sentence is looked up via the pycountry library to 
    match a country name. For countries with multiple words, we use 
    predefined lists and check for its inclusions in text. 

    Added a small hack here for countries like North and South 
    Korea. I had to edit the database of pycountries to add these
    as common names

    """ 
    if len(words.split()) > 1:
        tokens = nltk.word_tokenize(words)
    else: 
        tokens = [words]
    places = []
    for txt in tokens:
        ## If the text refers to a nationality, switch it with the nation
        ## Indian -> India, American -> America; is now also case insensitive
        if txt in nationalities_nation.keys() or txt in set(k.lower() for k in nationalities_nation.keys()): ## To be case insensitive
            try:
                txt = nationalities_nation[txt.capitalize()]
            except KeyError:
                txt = nationalities_nation[txt.upper()]
        ## Search for country names - these are single word countries
        try:
            cname = pycountry.countries.get(name=txt).name
            places.append(cname)
        except LookupError:
            pass
        ## Search for common names 
        try:
            cname = pycountry.countries.get(common_name=txt).name
            places.append(cname)
        except LookupError:
            pass
    
        ## Search for country names based on 2 letter codes; US/ UK
        try:
            cname = pycountry.countries.get(alpha_2=txt).name
            places.append(cname)
        except LookupError:
            pass

        
            
        ## Search for country names based on 3 letter codes; GBR 
    

    ### This is now for two worded countries, with name and common 
    ### names that can be found in the text
    for lnames in long_country_names:
        if lnames in words:
            places.append(lnames)
    for cnames in common_names:
        if cnames in words:
            places.append(cnames)

    return set(places)

db_config = json.load(open('db-config.json', 'r'))
print(db_config['port'])
#driver = GraphDatabase.driver('bolt://{0}:{1}'.format(db_config['host'], db_config['port']), auth=basic_auth(db_config['user'], db_config['pass']))

#session = driver.session()
print("Gathering data..")
#    x = pandas.read_csv("data/reddit_info.csv", delimiter="\t", header=None, names=['rank', 'download_time', 'timestamp', 'subreddit', 'id_art', 'ups', 'downs', 'title', 'num_comments', 'score', 'over_18'],error_bad_lines=False)
#    x_df = pandas.DataFrame(x)
#    print("Grouping..")
#    xj = x.groupby(['subreddit', 'id_art'])


#writeto = open('queries.txt', 'w')
all_countries = []
for title in titles:
    names = look_for_country_names(title)
    #print(names)
    if len(names) >1 :
        for name in names:
            all_countries.append(name)
            query = '''
                MERGE (primary: Country {name:{Country}})
                MERGE (secondary: Article {desr:{Article}})
                MERGE (secondary)-[:is_about]->(primary)
            '''

 #           qtop = 'MERGE (primary: Country {{name:"{0}"}}) \n'.format(name) + 'MERGE (secondary: Article {{desr:"{0}"}}) \n'.format(title.lstrip(" ").replace('"', "'"))+'MERGE (secondary)-[:is_about]->(primary)\n'
 #           print(query)
            #writeto.write(qtop)
            #pdb.set_trace()
            #session.run(query, {'Country': name, 'Article':title})
#session.close()
#writeto.close()
country_nums = Counter(all_countries)

sorted_country_names = OrderedDict(sorted(country_nums.items(), key=lambda kv: kv[1], reverse=True))
plt.bar(range(len(sorted_country_names)), list(sorted_country_names.values()), align='center')
plt.xticks(range(len(sorted_country_names)), list(sorted_country_names.keys()), rotation=90) 
