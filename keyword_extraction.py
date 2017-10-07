import pickle
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans, MiniBatchKMeans
import heapq
from nltk.corpus import stopwords

def remove_stopwords(text):
    stopwords = set(stopwords.words('english'))
    return ' '.join([w for w in text.split() if w not in stopwords])

# TODO: implement text stream
def rank_phrases(text, n):
    tfidf_vect = TfidfVectorizer(ngram_range=(2,4))
    text_vect = tfidf_vect.fit_transform(text)
    text_vect = np.asarray(text_vect.sum(axis=0)).ravel()
    tfidf_dict = dict()
    idf = tfidf_vect.idf_
    for k, v in tfidf_vect.vocabulary_.items():
        tfidf_dict[k] = text_vect[v]
    return heapq.nlargest(n, tfidf_dict, key=tfidf_dict.get)

def cluster_docs(abstracts):
    tfidf_vect = TfidfVectorizer()
    abs_tfidf = tfidf_vect.fit_transform(abstracts)
    K = 100
    kmeans = MiniBatchKMeans(n_clusters=K, batch_size=1000, reassignment_ratio=0).fit(abs_tfidf)
    cluster = kmeans.predict(abs_tfidf)
    return cluster

def category_keywords(category):
    ### Setup. Modify to read from database 
    with open('../metha-all-math.pkl','rb') as f:
        df = pickle.load(f)
    
    df['abstract'] = df['abstract'].apply(lambda t: t.replace('\n',' '))\
            .apply(remove_stopwords)
    df['title'] = df['title'].apply(lambda t: t.replace('\n',' '))\
            .apply(remove_stopwords)
    
    categories = open('math_categories.txt','r').read().splitlines()
    
    mask = df['categories'].apply(lambda cs: True if category in cs else False)
    df_c = df[mask]
    abs_c = df_c.apply(lambda row: 
            '. '.join([row['title'], row['abstract']]), axis=1)
    
    ### Clustering
    cluster = cluster_docs(abs_c)
    abs_cluster = pd.DataFrame({
        'cluster': cluster,
        'text': abs_DS
    })
    
    ### Result
    for j in range(K):
        c = abs_clusters[abs_clusters['cluster']==j]
        print(rank_phrases(c['text'], 2))



