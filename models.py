from app import db
from sqlalchemy.dialects.postgresql import JSON


class Result(db.Model):
    __tablename__='arxiv_project'
    id = db.Column(db.Integer, primary_key=True)

    def __init__(self):
        pass

    def __repr__(self):
        pass
