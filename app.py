from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_BINDS'] = {  
                                    'two':'sqlite:///users.db',
                                    'three':'sqlite:///transactions.db'
                            }

db = SQLAlchemy(app)

class booksDB(db.Model):
    __tablename__ = 'books'
    bookID = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    authors = db.Column(db.String(50))
    pages = db.Column(db.Integer) 
    rating = db.Column(db.String(5))

class usersDB(db.Model):
    __bind_key__ = 'two'
    __tablename__ = 'users'
    userID = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable=False)
    book_assigned = db.Column(db.Integer, default=0)
    book_assigned_date = db.Column(db.DateTime, default=None) 

class transactionsDB(db.Model):
    __bind_key__ = 'three'
    transactionID = db.Column(db.Integer, primary_key = True)
    userID = db.Column(db.Integer)
    bookID = db.Column(db.Integer)
    paid = db.Column(db.Float)
    debt = db.Column(db.Float)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/books', methods=['GET'])
def books():
    books = booksDB.query.all()
    return render_template('books.html', books=books)

@app.route('/members', methods=['GET'])
def members():
    users = usersDB.query.all()
    return render_template('users.html', users=users, date_now=datetime.utcnow())

@app.route('/searchbooks', methods=['GET', 'POST'])
def searchbooks():
    if request.method == 'POST':
        search = request.form['search']
        results = db.engine.execute(
            "SELECT * from books where title LIKE :search or authors LIKE :search",
            {"search": "%" + search + "%"}
        )
        try:
            db.session.commit()
            return render_template('searchresults.html', books=results)
        except Exception as e:
            return 'Couldnt commit search results:'+str(e)
    else:
        return render_template('searchbooks.html')

@app.route('/deletebook/<int:bookid>')
def deletebook(bookid):
    book_to_delete = booksDB.query.get_or_404(bookid)
    try:
        db.session.delete(book_to_delete)
        db.session.commit()
        return redirect('/books')
    except Exception as err:
        return 'Couldnt delete the book:'+str(err)

@app.route('/updatebook/<int:bookid>', methods=['GET', 'POST'])
def updatebook(bookid):
    book = booksDB.query.get_or_404(bookid)
    if request.method == 'POST':
        book.quantity = request.form['qty']
        book.rating = request.form['rating']
        try:
            db.session.commit()
            return redirect('/books')
        except Exception as e:
           return 'Couldnt update book:'+str(e)
    else:
        return render_template('updatebook.html', book=book)        

@app.route('/updateuser/<int:userid>', methods=['GET', 'POST'])
def updateuser(userid):
    user = usersDB.query.get_or_404(userid)
    if request.method == 'POST':
        user.name = request.form['name']
        try:
            db.session.commit()
            return redirect('/members')
        except Exception as e:
           return 'Couldnt update user:'+str(e)
    else:
        return render_template('updateuser.html', user=user)

@app.route('/deleteuser/<int:userid>')
def deleteuser(userid):
    user_to_delete = usersDB.query.get_or_404(userid)
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        return redirect('/members')
    except Exception as err:
        return 'Couldnt delete the user:'+str(err)

@app.route('/addmember', methods=['GET','POST'])
def addmembers():
    if request.method == 'POST':
        user_name = request.form['username']
        new_user = usersDB(name=user_name)
        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect('/members')
        
        except Exception as e:
            return 'Couldnt add a New User:'+str(e)
    
    else:
        return render_template('addmember.html')

@app.route('/assignbook/<int:bookid>', methods=['GET', 'POST'])
def assignbook(bookid):
    if request.method == 'POST':
        book = booksDB.query.get_or_404(bookid)
        book.quantity -= 1
        user_id = request.form['userid']
        user = usersDB.query.get_or_404(user_id)
        user.book_assigned = bookid
        user.book_assigned_date = datetime.utcnow()
        try:
            db.session.commit()    
            return redirect('/members')
        except Exception as e:
            return 'Couldnt assign book to user:'+str(e)

    else:
        users = usersDB.query.all()
        return render_template('assignbook.html', users=users, bookid=bookid)

@app.route('/return/<int:bookid>', methods=['POST'])
def returnbook(bookid):
    if request.method == 'POST':
        book = booksDB.query.get_or_404(bookid)
        book.quantity += 1
        user_id = request.form['userid']
        user = usersDB.query.get_or_404(user_id)
        user.book_assigned = 0
        user.book_assigned_date = None
        payment = request.form['payment']
        amount_due = request.form['amount_due']
        bal = float(payment) - float(amount_due)
        new_transaction = transactionsDB(userID=user_id, bookID=bookid, paid=payment, debt=bal)
        try:
            db.session.add(new_transaction)
            db.session.commit()    
            return redirect('/members')
        except Exception as e:
            return 'Couldnt return book from user:'+str(e)

@app.route('/debts', methods=['GET'])
def debts():
    transactions = transactionsDB.query.all()
    total_debts = {}
    # try:
    for t in transactions:
        user_obj = {}
        if t.userID in total_debts:
            total_debts[t.userID]['debt'] += float(t.debt)
            total_debts[t.userID]['paid'] += float(t.paid)
        else:
            user_obj['debt'] = float(t.debt)
            user_obj['paid'] = float(t.paid)
            total_debts[t.userID] = user_obj
    
    for userid in total_debts.keys():
        user = usersDB.query.get_or_404(userid)
        total_debts[userid]['name'] = user.name
    print('HERERE:')
    print(total_debts)
    # except Exception as e:
    #     return 'err in debt:'+str(e)

    return render_template('debts.html', total_debts=total_debts)

if __name__ == "__main__":
    app.run(debug = True)
