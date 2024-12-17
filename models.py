from app import db
from datetime import datetime
from flask_login import UserMixin
class User( UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    name = db.Column(db.String(60), nullable=False)
    history = db.relationship('History', backref='user', lazy=True)
    book = db.relationship('Book', backref='user', lazy=True)
    search_history = db.relationship('SearchHistory', backref='user', lazy=True)



    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()    


class History(db.Model):
    __tablename__ = 'history'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    book_url = db.Column(db.String(200), nullable=False)
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    book = db.relationship('Book', backref='history', lazy=True)
    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()



class SearchHistory(db.Model):
    __tablename__ = 'search_history'
    id = db.Column(db.Integer, primary_key=True)
    query = db.Column(db.String(200), nullable=False)
    search_type = db.Column(db.String(50), nullable=False)  # e.g., 'name', 'author', 'genre', etc.
    date_searched = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def save(self):
        db.session.add(self)
        db.session.commit()
        
class Book(db.Model):
    __tablename__ = 'book'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    book_url = db.Column(db.String(200), nullable=False)
    genre =  db.Column(db.String(200), nullable=False)
    author =  db.Column(db.String(200), nullable=False)
    publication =  db.Column(db.String(200), nullable=False)
    keywords =  db.Column(db.String(200), nullable=False)
    description =  db.Column(db.String(200), nullable=False)
    word_counts =  db.Column(db.String(200), nullable=False)
    pen_name =  db.Column(db.String(200), nullable=False)
    ratings =  db.Column(db.String(200), nullable=False)
    book_cover = db.Column(db.String(200), nullable=False)

    date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


from app import login_manager

@login_manager.user_loader
def load_user(email):
    return User.query.get(email)     

