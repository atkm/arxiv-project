from app import db
from models import Article, Author, Category, article_author, article_category

import os, gzip, glob
from datetime import datetime
import xml.etree.ElementTree as ET

def get_title(record):
    arXiv_prefix = '{http://arxiv.org/OAI/arXiv/}'
    metadata = record.find('metadata').find(arXiv_prefix + "arXiv")
    title = metadata.find(arXiv_prefix + "title").text
    return title

def get_authors(record):
    arXiv_prefix = '{http://arxiv.org/OAI/arXiv/}'
    metadata = record.find('metadata').find(arXiv_prefix + "arXiv")
    authors = metadata.find(arXiv_prefix + 'authors')
    ls = []
    for a in authors.getchildren():
        keyname = a.find(arXiv_prefix + "keyname").text
        forenames = a.find(arXiv_prefix + "forenames").text
        ls.append( ' '.join( (forenames, keyname) ) )
    return ls

def get_categories(record):
    arXiv_prefix = '{http://arxiv.org/OAI/arXiv/}'
    metadata = record.find('metadata').find(arXiv_prefix + "arXiv")
    categories = metadata.find(arXiv_prefix + 'categories').text
    return categories.split()

def insert_record(record):
    arXiv_prefix = '{http://arxiv.org/OAI/arXiv/}'
    
    article = Article()
    
    metadata = record.find('metadata').find(arXiv_prefix + "arXiv")
    if metadata is None:
        return 'deleted'
    
    identifier = metadata.find(arXiv_prefix + "id").text
    exists = db.session.query(Article).filter(
            Article.identifier == identifier
            ).exists()
    if db.session.query(exists).scalar():
        return 'exists'
    
    submitted = metadata.find(arXiv_prefix + "created").text
    submitted = datetime.strptime(submitted, "%Y-%m-%d")
    title = metadata.find(arXiv_prefix + "title").text
    abstract = metadata.find(arXiv_prefix + "abstract").text.strip()
    article.submitted = submitted
    article.title = title
    article.identifier = identifier
    article.abstract = abstract

    authors = metadata.find(arXiv_prefix + 'authors')
    added_authors = []

    for a in authors.getchildren():
        keyname = a.find(arXiv_prefix + "keyname")
        forenames = a.find(arXiv_prefix + "forenames")
        if keyname is None or forenames is None:
            continue #bad entry
        fullname = ' '.join( (forenames.text, keyname.text) )
        # authors added in this record. Fix error from ['Wende Liu', 'Wende Liu']
        if fullname in added_authors:
            continue
        else:
            added_authors.append(fullname)
        search = db.session.query(Author).filter_by(name=fullname)
        if db.session.query(search.exists()).scalar():
            article.authors.append(search.one())
        else:
            article.authors.append(Author(fullname))

    categories = metadata.find(arXiv_prefix + "categories").text
    for c in categories.split():
        search = db.session.query(Category).filter_by(name=c)
        if db.session.query(search.exists()).scalar():
            article.categories.append(search.one())
        else:
            article.categories.append(Category(c))

    db.session.add(article)
    return 'inserted'

def insert_xml(xml):
    """
    xml: ElementTree such that xml.getroot() returns an Element
    """
    root = xml.getroot()

    for record in root.find('ListRecords').findall("record"):
        result = insert_record(record)
        if result == 'exists':
            print('Skipping file as content already exist.')
            return
    db.session.commit() #commit after each file -> a logical unit of work
    print('Added. Commit.')

if __name__=='__main__':
    # if starting from scratch
    #db.metadata.drop_all(db.engine)
    #db.metadata.create_all(db.engine)

    files = glob.glob('/home/atkm/.metha/20170923/*.xml.gz')
    #files = glob.glob('/home/atkm/.metha/20170923/2017-08-31-*.xml.gz') # test.

    try:
        for xmlgz in files:
            print(os.path.basename(xmlgz), end=' ')
            with gzip.open(xmlgz, 'rb') as f:
                xml = ET.parse(f)
                insert_xml(xml)
        print('Population succeeded.')
        print('%s articles in db.' %
                db.session.query(Article).count())
    except Exception as e:
        print('Error in %s.' % xmlgz)
        print('Rolling back...')
        db.session.rollback()
        raise e
