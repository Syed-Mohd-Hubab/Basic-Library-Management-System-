import requests

from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class booksDB(db.Model):
    __tablename__ = 'books'
    bookID = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    authors = db.Column(db.String(50))
    pages = db.Column(db.Integer) 
    rating = db.Column(db.String(5))

def getBooks(title = '', authors = '', isbn = '', publisher ='', numBooks=20):
    URL = 'https://frappe.io/api/method/frappe-library'
    pages = []
    PARAMS = {
        'title'    : title,
        'authors'  : authors,
        'isbn'     : isbn,
        'publisher': publisher,
        'page'     : page
    }


    

@app.route('/', methods=['GET'])
def initialPopulation():
    URL = 'https://frappe.io/api/method/frappe-library'

    results = requests.get(url=URL)
    data = results.json()

    i = 0
    for book in data['message']:
        i += 1
        add_book = booksDB(
            bookID = book['bookID'], 
            title = book['title'],
            authors = book['authors'],
            pages = book['  num_pages'],
            rating = book['average_rating']   
        )

        try:
            db.session.add(add_book)
            db.session.commit()

        except Exception as e:
            return 'Couldnt add book ' + str(i) +' to db:'+str(e)
    
    return '20 Books have been added'

if __name__ == "__main__":
    app.run(debug = True)


