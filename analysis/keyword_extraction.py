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

if __name__=='__main__':

    ### Setup
    with open('../metha-all-math.pkl','rb') as f:
        df = pickle.load(f)
    
    df['abstract'] = df['abstract'].apply(lambda t: t.replace('\n',' '))\
            .apply(remove_stopwords)
    df['title'] = df['title'].apply(lambda t: t.replace('\n',' '))\
            .apply(remove_stopwords)
    
    ### Get category
    categories = open('math_categories.txt','r').read().splitlines()
    math_c = categories[10] # user should pick a category
    
    mask = df['categories'].apply(lambda cs: True if math_c in cs else False)
    df_c = df[mask]
    abs_c = df_c.apply(lambda row: 
            '. '.join([row['title'], row['abstract']]), axis=1)
    
    ### Clustering
    tfidf_vect = TfidfVectorizer()
    abs_tfidf = tfidf_vect.fit_transform(abs_c)
    K = 100
    kmeans = MiniBatchKMeans(n_clusters=K, batch_size=1000, reassignment_ratio=0).fit(abs_tfidf)
    cluster = kmeans.predict(abs_tfidf)
    abs_cluster = pd.DataFrame({
        'cluster': cluster,
        'text': abs_DS
    })
    
    ### Result
    for j in range(K):
        c = abs_clusters[abs_clusters['cluster']==j]
        print(rank_phrases(c['text'], 2))
