from app import db
from sqlalchemy.dialects.postgresql import JSON

article_category = db.Table('article_category',
        db.Column('category_id', db.Integer, db.ForeignKey('categories.id')),
        db.Column('article_id', db.Integer, db.ForeignKey('articles.id'))
        )

article_author = db.Table('article_author',
        db.Column('author_id', db.Integer, db.ForeignKey('authors.id')),
        db.Column('article_id', db.Integer, db.ForeignKey('articles.id'))
        )

class Article(db.Model):
    __tablename__='articles'
    id = db.Column(db.Integer, primary_key=True)
    identifier = db.Column(db.String, unique=True, nullable=False)
    title = db.Column(db.String, nullable=False)
    authors = db.relationship('Author', secondary=article_author,\
            backref='articles', lazy='dynamic') # backref furnishes Author with .articles
    abstract = db.Column(db.Text, nullable=False)
    categories = db.relationship('Category', secondary=article_category,\
            backref='articles', lazy='dynamic')
    submitted = db.Column(db.Date, nullable=False)

    def __init__(self, **entries):
        self.__dict__.update(entries)

    def __repr__(self):
        return '<article {}>'.format(self.identifier)

class Author(db.Model):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    # not needed when using backref.
    #articles = db.relationship('Article', secondary=article_author,\
    #        back_populates='authors')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<author {}>'.format(self.name)

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    #articles = db.relationship('Article', secondary=article_category,\
    #        back_populates='categories')

    def __init__(self, category):
        self.name = category
    
    def __repr__(self):
        return '<category {}>'.format(self.name)


# Stores keyword extraction results
class Result(db.Model):
    __tablename__ = 'results'

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String())
    result_all = db.Column(JSON)
    result_no_stop_words = db.Column(JSON)

    def __init__(self, url, result_all, result_no_stop_words):
        self.url = url
        self.result_all = result_all
        self.result_no_stop_words = result_no_stop_words

    def __repr__(self):
        return '<id {}>'.format(self.id)
