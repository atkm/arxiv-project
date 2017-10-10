import pickle
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans, MiniBatchKMeans
import heapq
from nltk.corpus import stopwords

from app import db
from models import *

# Using a stream for text and HashingVectorizer instead of TfidfVectorizer is more memory-efficient,
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
    print('Running kmeans.')
    kmeans = MiniBatchKMeans(n_clusters=K, batch_size=1000, reassignment_ratio=0).fit(abs_tfidf)
    print('Kmeans finished.')
    cluster = kmeans.predict(abs_tfidf)
    return cluster


def load_data(category):
    print('Pulling data from Postgres.')
    df = pull_abstracts(category)
    df['abstract'] = df['abstract'].apply(lambda t: t.replace('\n',' '))\
            .apply(remove_stopwords)
    df['title'] = df['title'].apply(lambda t: t.replace('\n',' '))\
            .apply(remove_stopwords)
    abs_c = df.apply(lambda row: 
            '. '.join([row['title'], row['abstract']]), axis=1)
    print('Data loaded.')
    return abs_c
    

def pull_abstracts(category):
    articles = db.session.query(Article)\
            .filter(Article.id == article_category.c.article_id)\
            .filter(Category.id == article_category.c.category_id)\
            .filter(Category.name == category)
    
    identifier, title, authors, abstract, categories, submitted = ([] for i in range(6))
    for row in articles:
        title.append(row.title)
        abstract.append(row.abstract)
        #categories.append( [c.name for c in row.categories] )

    df = pd.DataFrame({
        'title': title,
        'abstract': abstract,
        })
    return df


def remove_stopwords(text):
    stopWords = set(stopwords.words('english'))
    return ' '.join([w for w in text.split() if w not in stopWords])

def extract_keywords(category):
    K = 100
    abs_c = load_data(category)
    cluster = cluster_docs(abs_c, K)
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
