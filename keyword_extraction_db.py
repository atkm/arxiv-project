import pickle
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import MiniBatchKMeans
import heapq
from nltk.corpus import stopwords

from app import db
from models import *

import functools

def compose(*functions):
    return functools.reduce(lambda f, g: lambda x: f(g(x)), functions, lambda x: x)

# do LaTeX-specific pre-processing, then removes stopwords.
# Combines titles and abstracts, and returns processed text in the lower case.
def pre_process(df):
    remove_newline = lambda t: t.replace('\n',' ')
    process_umlaut = lambda t: re.sub("\"([auo])", r"\1", t)
    ignore_backslash = lambda t: t.replace('\\','')
    ignore_dollar = lambda t: t.replace('$','')
    pre_processor = compose(
            remove_stopwords, ignore_dollar, ignore_backslash, process_umlaut, remove_newline)
    df['abstract'] = df['abstract'].apply(pre_processor)
    df['title'] = df['title'].apply(pre_processor)
    abstracts = df.apply(lambda row: 
            '. '.join([row['title'], row['abstract']]), axis=1)
    return abstracts

# loads abstracts from a pickle file.
def load_pkl(category):
    print('Loading data')
    with open('metha-all-math.pkl','rb') as f:
        df = pickle.load(f)
        mask = df['categories'].apply(lambda cs: category in cs)
        df = df[mask]
        abstracts = pre_process(df)
        print('Data loaded')
        return abstracts

def remove_stopwords(text):
    stopWords = set(stopwords.words('english'))
    math_stopwords = ['we', 'prove', 'show', 'paper', 'study']
    for w in math_stopwords:
        stopWords.add(w)
    return ' '.join([w.lower() for w in text.split() if w.lower() not in stopWords])

# loads abstracts from Postgres and pre-processes them.
def load_data(category):
    print('Pulling data from Postgres.')
    df = pull_abstracts(category)
    abstracts = pre_process(df)
    print('Data loaded.')
    return abstracts
    
# joins tables to obtain abstracts of the given category.
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

def rank_phrases(text, n, ngram_range):
    tfidf_vect = TfidfVectorizer(ngram_range=ngram_range)
    text_vect = tfidf_vect.fit_transform(text)
    text_vect = np.asarray(text_vect.sum(axis=0)).ravel()
    tfidf_dict = dict()
    idf = tfidf_vect.idf_
    for k, v in tfidf_vect.vocabulary_.items():
        tfidf_dict[k] = text_vect[v]
    return heapq.nlargest(n, tfidf_dict, key=tfidf_dict.get)

# clustering is done with 1-grams
def cluster_docs(abstracts, K):
    tfidf_vect = TfidfVectorizer()
    abs_tfidf = tfidf_vect.fit_transform(abstracts)
    #print('Running kmeans.')
    # reassignment_ratio is set to zero, since unbalanced clusters are not harmful to our application.
    kmeans = MiniBatchKMeans(n_clusters=K, batch_size=1000, reassignment_ratio=0).fit(abs_tfidf)
    #print('Kmeans finished.')
    cluster_idx = kmeans.predict(abs_tfidf)
    return cluster_idx

# input: abstracts is a pd.Series.
def extract_keywords(abstracts, K, topN, ngram_range=(2,3)):
    cluster_idx = cluster_docs(abs_c, K)
    abs_clusters = pd.DataFrame({
        'cluster': cluster_idx,
        'text': abstracts
    })
    
    keywords = []
    for j in range(K):
        # get the j^th cluster
        c = abs_clusters[abs_clusters['cluster']==j]
        for phrase in rank_phrases(c['text'], topN, ngram_range):
            keywords.append(phrase)

    return keywords
