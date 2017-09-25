import feedparser
import requests

query_string = 'all:electron&start=0&max_results=1'

def arxiv_query():
    baseurl = 'http://export.arxiv.org/api/query?search_query='
    response = requests.get(baseurl + query_string)
    response = feedparser.parse(response.text)
    summary = 
    return 

def parse_arxiv_atom():
    pass
