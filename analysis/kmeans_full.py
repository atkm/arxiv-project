import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

import pickle
with open('../metha-all-math.pkl','rb') as f:
    df = pickle.load(f)

tfidf_vect = TfidfVectorizer()
abstracts = df['abstract']
abs_vect = tfidf_vect.fit_transform(abstracts)

k_per_category = 1 # see if categories correspond to clusters
n_categories = 150 # 163 for full df; 143 for df_17
kmeans = KMeans(n_clusters=k_per_category * n_categories,\
                      n_init=1,\
                     n_jobs=1).fit(abs_vect)
print('Result saved in `kmeans`.')
print('Run pickle.save!')
# Result saved in kmeans_full.pkl with df and abs_vect
# >> pickle.dump([kmeans, df, abs_vect], f)
