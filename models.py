from app import db
from sqlalchemy.dialects.postgresql import JSON


class Article(db.Model):
    __tablename__='arxiv_project'
    id = db.Column(db.Integer, primary_key=True)
    identifier = db.Column(db.String, unique=True)
    title = db.Column(db.String)
    authors = db.Column(db.String) # article has-many authors
    abstract = db.Column(db.String)
    categories = db.Column(db.String) # article has-many categories
    submitted = db.Column(db.Date)

    def __init__(self, identifier, title,
            authors, abstract, categories, submitted):
        self.identifier = identifier
        self.title = title
        self.authors = authors
        self.abstract = abstract
        self.categories = categories
        self.submitted = submitted

    def __repr__(self):
        return '<id {}>'.format(self.id)
