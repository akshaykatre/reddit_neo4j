import sklearn, pandas, pdb, datetime, numpy 
import matplotlib.pyplot as plt 
from collections import Counter
import nltk
from nltk.corpus import stopwords
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from reddit_geo_worldnews import look_for_country_names
import re 
from nltk.stem import WordNetLemmatizer, PorterStemmer, LancasterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
import scipy
from sklearn import naive_bayes, svm
import xgboost

params = {'stemmer': 'lancaster',
          'rf_n_estimators': 1000,
          'tf_max_estimators': 2000,
          }

print("Using ", params['stemmer'], ' for lemmatizer')

nltk.data.path.append("/data/corpora/")
nltk.download("stopwords")

data = pandas.read_csv("data/reddit_info_all.csv", 
        delimiter="\t", header=None, names=['rank', 
        'download_time', 'timestamp', 'subreddit', 
        'id_art', 'ups', 'downs', 'title', 
        'num_comments', 'score', 'over_18'],
        error_bad_lines=False)
data = pandas.DataFrame(data)
data = data.drop_duplicates(subset='title', keep='first')

data = data.groupby("subreddit").filter(lambda x: 
                len(x) > 1800)
data = data.reset_index()
stemmers = {'porter': PorterStemmer(), 
            'lancaster': LancasterStemmer(),
            'wordnet': WordNetLemmatizer()}

def preprocess(text, stemmer_choice=None):
	if stemmer_choice == None:
			print("Using porter by default!")
			stemmer_choice = 'porter'
	## Remove all special characters
	text = re.sub(r'\W', ' ', text)

	## Remove all single characters
	text = re.sub(r'\s+[a-zA-Z]\s+', ' ', text)

	## Remove single characters from the start
	text = re.sub(r'\^[a-zA-Z]\s+', ' ', text)

	##Substituting multiple spaces with single space
	text = re.sub(r'\s+', ' ', text, flags=re.I)

	#      # Removing prefixed 'b'
	#      text = re.sub(r'^b\s+', '', text)

	## Lower cases
	text = text.lower()

	## Lemmatization

	text = text.split()
	stemmer = stemmers[stemmer_choice]  
	if stemmer_choice != 'wordnet':
		text = [stemmer.stem(word) for word in text]
	else:
		text = [stemmer.lemmatize(word) for word in text]
	text = ' '.join(text)

	return text


data['subreddit'] = data.subreddit.apply(lambda x: x.lstrip())
data['process_title'.format(params['stemmer'])] = data.title.apply(lambda x: preprocess(x, params['stemmer']))
data['nwords'] = data['process_title'].apply(lambda x: len(x.split()))
data['nchar'] = data['process_title'].apply(lambda x: len(x))
data['ncountries'] = data['process_title'].apply(lambda x: len(look_for_country_names(x)))
data['usmentions'] = data['process_title'].apply(lambda x: Counter(look_for_country_names(x))['United States'])



y = data.subreddit.values
encoder = sklearn.preprocessing.LabelEncoder()
y = encoder.fit_transform(y)

## Make the features, it is a combination of the text and 
## text characteristics, length, country mentions etc
tfidf = TfidfVectorizer(max_features=2000, min_df=5,max_df=0.7, stop_words=stopwords.words('english'))
xtmp = tfidf.fit_transform(data.process_title)
vocab = tfidf.get_feature_names()

tempdf = pandas.DataFrame(xtmp.toarray(), columns = vocab)
tempdf['ncountries'] = data['ncountries']
tempdf['nwords'] = data['nwords']
tempdf['nchar'] = data['nchar']
tempdf['usmentions'] = data['usmentions']

xsparse = scipy.sparse.csr_matrix(tempdf.values)



x_train, x_test, y_train, y_test = train_test_split(xtmp, y, test_size=0.2, random_state=42)
xadd_train, xadd_test, y_train, y_test = train_test_split(xsparse, y, test_size=0.2, random_state=42)

def trainclassifier(classifier, trainset, label, testset):
	print(trainset.shape, label.shape, testset.shape, y_test.shape)
	## Fit the classifier
	classifier.fit(trainset, label)

	## Make predictions on the test set
	predictions = classifier.predict(testset)

	print(classification_report(y_test, predictions))
	print(confusion_matrix(y_test, predictions))

print("Random forest, normal features")
rf = RandomForestClassifier(n_estimators=1000, random_state=42, max_depth=100, min_samples_leaf=3)
trainclassifier(rf, x_train, y_train, x_test)

print("Random forest, With additional features added")
trainclassifier(rf, xadd_train, y_train, xadd_test)

print("XGboost, normal features")
trainclassifier(xgboost.XGBClassifier(), x_train.tocsc(), y_train, x_test.tocsc())

print("XGboost, additional features")
trainclassifier(xgboost.XGBClassifier(), xadd_train.tocsc(), y_train, xadd_test.tocsc())

print("NB, normal features")
trainclassifier(naive_bayes.MultinomialNB(), x_train, y_train, x_test)

print("NB, additional features")
trainclassifier(naive_bayes.MultinomialNB(), xadd_train, y_train, xadd_test)


""" predict = rf.predict(x_test)

##Print report
print(classification_report(y_test,predict))
print(confusion_matrix(y_test, predict))
 """

## Adding features
