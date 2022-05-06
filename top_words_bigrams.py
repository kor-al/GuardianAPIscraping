import json
import re
# remove punctuation
import string 
import nltk
from nltk.stem.porter import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import matplotlib.pyplot as plt
# from wordcloud import WordCloud
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import pandas as pd

# nltk.download("stopwords")
# nltk.download('wordnet')
# nltk.download('omw-1.4')

stop_words = set(stopwords.words("english") + ["the"])
punct = set(string.punctuation + "'")
stemmer = PorterStemmer()
lemmatizer = WordNetLemmatizer()

MAXWORDS=1000
filename = "ukraine_data"
with open(filename + '.json', 'r') as f:
  data = json.load(f)

remove_words= ["russian", "russias","uk", "us", "the", "ukrainian", "boris", "johnson", "biden", "cup",
 "putins", "ukraines", "ukrainians", "vladimir", "sunak", "face", "russians", "amid", "bn", "it", "go",
 "rishi", "like", "way", "british", "right", "far", "away", "way", "make", "australia","its" , "guardian", "can", "may", "mps", "could",
 "know", "they", "he", "she", "it", "will", "ll"
]

skip_count=0
corpus = []
for article in data['articles']:
    title = article['title']
    if 'Russia-Ukraine war: what we know on day' in title or 'Corrections and clarifications' in title:
      print(title)
      skip_count+=1
      continue
    # body = article['body']

    # removing stopwords
    text = " ".join([word for word in title.split() if word not in stop_words])

    # encoding the text to ASCII format
    text_encode = text.encode(encoding="ascii", errors="ignore")
    # decoding the text
    text_decode = text_encode.decode()
    # cleaning the text to remove extra whitespace 
    pattern = r'[0-9]'
    text = " ".join([re.sub(pattern, '', word) for word in text_decode.split()])
    #remove authors, editorials etc
    text = text.split("|")[0]

    # Change any white space to one space
    stripped = re.sub('\s+', ' ', text)
      
    # Remove start and end white spaces
    stripped = stripped.strip().lower()

    #remove authors, editorials etc
    clean_text = " ".join([ch for ch in stripped.split() if ch not in punct])
    lemmas = " ".join([lemmatizer.lemmatize(word) for word in clean_text.split(" ")])
    filtered = " ".join([w for w in clean_text.split(" ") if w not in remove_words])
    corpus.append(filtered)

print('skip_count', skip_count)



      
# Getting grams 
vectorizer = CountVectorizer(ngram_range = (1,3))
X1 = vectorizer.fit_transform(corpus) 
features = (vectorizer.get_feature_names())
# print("\n\nFeatures : \n", features)
print("\n\nX1 : \n", X1.toarray())
  
# Applying TFIDF
vectorizer = TfidfVectorizer(ngram_range = (1,3))
X2 = vectorizer.fit_transform(corpus)
feature_names = vectorizer.get_feature_names()
scores = (X2.toarray())
print("\n\nScores : \n", scores)


dense = X2.todense()
lst1 = dense.tolist()
df = pd.DataFrame(lst1, columns=feature_names)
ranking = df.T.sum(axis=1).sort_values(ascending=False)#.to_csv('top_words_bigrams.csv')
print("...Sorting completed")

max = MAXWORDS
if len(ranking) < MAXWORDS:
  max = len(ranking)
  

dics = ranking[0:max].to_frame().reset_index().rename({'index': 'word',0: 'size'}, axis = 'columns').to_dict('records')

print("Writing to the file...")
with open(filename + '_top_words_bigrams.json', 'w') as f: 
    for d in dics:
      f.write(json.dumps(d) + ",\n")
print("...Writing to the file completed")
  
# Getting top ranking features
sums = X1.sum(axis = 0)
data1 = []
for col, term in enumerate(features):
    data1.append( (term, sums[0,col] ))
ranking = pd.DataFrame(data1, columns = ['term','rank'])
words = (ranking.sort_values('rank', ascending = False))
print ("\n\nWords head : \n", words.head(15))