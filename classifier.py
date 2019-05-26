import sklearn, pandas, pdb, datetime, numpy 
import matplotlib.pyplot as plt 
from collections import Counter
import nltk
from nltk.corpus import stopwords
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from reddit_geo_worldnews import look_for_country_names

nltk.data.path.append("/data/corpora/")
nltk.download("stopwords")

data = pandas.read_csv("data/reddit_info_all.csv", 
        delimiter="\t", header=None, names=['rank', 
        'download_time', 'timestamp', 'subreddit', 
        'id_art', 'ups', 'downs', 'title', 
        'num_comments', 'score', 'over_18'],
        error_bad_lines=False)
data = pandas.DataFrame(data)
data = data.drop_duplicates('title')

data = data.groupby("subreddit").filter(lambda x: 
                len(x) > 500)


def all_dictionary(sub):
    all_words = []
    #text = text.split()
    for text in sub:
        words = text.split()
        text = [word.lower() for word in text.split() 
                if word.lower() not in stopwords.words('english')]
        #pdb.set_trace()
        all_words += text
    dictionary = Counter(all_words)
    list_to_remove = list(dictionary)

    for item in list_to_remove:
        if item.isalpha() == False:
            del dictionary[item]
        elif len(item) == 1:
            del dictionary[item]
    
    return dictionary.most_common(3000)



d = all_dictionary(data.title)
""" for title, subreddit in zip(data.title, data.subreddit):
    dict = all_dictionary(title) """
subs = data.subreddit.unique()
sub_maps = {}
for name, id_ in zip(pandas.Series(subs), pandas.Series(subs).astype('category').cat.codes.values):
    sub_maps.update({name:id_})


def features(data):
    features_matrix = numpy.zeros((len(data.title), 3000))
    train_labels = numpy.zeros(len(data.title))
    count = 0
    docid = 0 
    d = all_dictionary(data.title)
    for titles, subreddit in zip(data.title, data.subreddit):
        words = titles.split()
        for word in set(words): 
            wordid = 0 
            for i, dictw in enumerate(d):
                if dictw[0] == word:
                    wordid = i 
                    features_matrix[docid, wordid] = words.count(word)
        #pdb.set_trace()
        train_labels[docid] = sub_maps[subreddit]
        docid += 1
    return features_matrix, train_labels


feats, labels = features(data)
feat_train, feat_test, labels_train, labels_test = train_test_split(feats, labels, test_size=0.3, random_state=42)

model = RandomForestClassifier(n_estimators=20)
model.fit(feat_train, labels_train)
pred = model.predict(feat_test)

accuracy_score(labels_test, pred)
print(classification_report(labels_test, pred))


## Adding features
data['nwords'] = data.title.apply(lambda x: len(x.split()))
data['nchar'] = data.title.apply(lambda x: len(x))
data['ncoutries'] = data.title.apply(lambda x: len(look_for_country_names(x)))
data['usmentions'] = data.title.apply(lambda x: Counter(look_for_country_names(x))['United States'])
