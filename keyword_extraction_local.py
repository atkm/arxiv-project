import pickle
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans, MiniBatchKMeans
import heapq
from nltk.corpus import stopwords

'''
Prototype of keyword extraction procedure
Load data in in-memory pd.DataFrame
'''

# using a stream for text and HashingVectorizer instead of TfidfVectorizer is more memory-efficient,
# though that would mean giving up tfidf. 
def rank_phrases(text, n):
    tfidf_vect = TfidfVectorizer(ngram_range=(2,4))
    text_vect = tfidf_vect.fit_transform(text)
    text_vect = np.asarray(text_vect.sum(axis=0)).ravel()
    tfidf_dict = dict()
    idf = tfidf_vect.idf_
    for k, v in tfidf_vect.vocabulary_.items():
        tfidf_dict[k] = text_vect[v]
    return heapq.nlargest(n, tfidf_dict, key=tfidf_dict.get)

def cluster_docs(abstracts, K):
    tfidf_vect = TfidfVectorizer()
    abs_tfidf = tfidf_vect.fit_transform(abstracts)
    print('Running kmeans')
    kmeans = MiniBatchKMeans(n_clusters=K, batch_size=1000, reassignment_ratio=0).fit(abs_tfidf)
    print('Kmeans finished')
    cluster = kmeans.predict(abs_tfidf)
    return cluster

def load_data(category):
    print('Loading data')
    with open('metha-all-math.pkl','rb') as f:
        df = pickle.load(f)
    
    df['abstract'] = df['abstract'].apply(lambda t: t.replace('\n',' '))\
            .apply(remove_stopwords)
    df['title'] = df['title'].apply(lambda t: t.replace('\n',' '))\
            .apply(remove_stopwords)
    
    mask = df['categories'].apply(lambda cs: True if category in cs else False)
    df_c = df[mask]
    abs_c = df_c.apply(lambda row: 
            '. '.join([row['title'], row['abstract']]), axis=1)
    print('Data loaded')
    return abs_c[:100] # use a small dataset for testing

def remove_stopwords(text):
    stopWords = set(stopwords.words('english'))
    return ' '.join([w for w in text.split() if w not in stopWords])

def extract_keywords(category):
    K = 10
    abs_c = load_data(category)
    cluster = cluster_docs(abs_c, K) # use small K for testing
    abs_clusters = pd.DataFrame({
        'cluster': cluster,
        'text': abs_c
    })
    
    keywords = []
    for j in range(K):
        c = abs_clusters[abs_clusters['cluster']==j]
        for phrase in rank_phrases(c['text'], 2):
            keywords.append(phrase)

    print(keywords)
    return keywords

if __name__=='__main__':
    category_keywords('math.AT')
