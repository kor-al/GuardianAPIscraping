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
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd

# nltk.download("stopwords")
# nltk.download('wordnet')
# nltk.download('omw-1.4')

stop_words = set(stopwords.words("english"))
punct = set(string.punctuation + "'")
stemmer = PorterStemmer()
lemmatizer = WordNetLemmatizer()

filename = "war AND ukraine AND NOT UK"
with open(filename + '.json', 'r') as f:
  data = json.load(f)

# Output: {'name': 'Bob', 'languages': ['English', 'French']}
# print(data['articles'])


corpus = []
for article in data['articles']:
    title = article['title']
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
    cut_text = text.split("|")[0]
    clean_text = " ".join([ch for ch in cut_text.split() if ch not in punct])
    lemmas = " ".join([lemmatizer.lemmatize(word) for word in clean_text.split(" ")])
    corpus.append(lemmas)

print(corpus)



vectorizer = TfidfVectorizer(stop_words='english')
X = vectorizer.fit_transform(corpus)
print(X.shape)

feature_names = vectorizer.get_feature_names()
dense = X.todense()
lst1 = dense.tolist()
df = pd.DataFrame(lst1, columns=feature_names)
df.T.sum(axis=1).sort_values(ascending=False).to_csv(filename+'top_words.csv')