import pandas
import datetime
import matplotlib.pyplot as plt
import pdb 
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction import FeatureHasher

data = pandas.read_csv("reddit_info_all.csv", delimiter="\t", names=["position", "probe_time", "created_time", "subreddit", "id", "ups", "downs", "title", "num_comments", "score", "over_18"])

x_df = pandas.DataFrame(data)
titles = x_df.drop_duplicates('title')

data_short = titles[titles.groupby("subreddit")["subreddit"].transform('size')>90]
x = data_short['title']
y = data_short['subreddit']

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.33, random_state=42)

fh = FeatureHasher(n_features=2**13, input_type='string')
