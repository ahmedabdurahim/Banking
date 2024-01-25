from flask import Flask, render_template, url_for, request, redirect, session
import db as db
from flask_session import Session
import json


app = Flask(__name__)

app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template("home.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    bank_id = request.form.get('bank_id')
    email = request.form.get('email')
    password = request.form.get('password')

    if request.method == 'POST':
        if(db.Login(bank_id, email, password)):
            session['bank_id'] = bank_id
            session['email'] = email
            session['account_no'] = db.FetchAccountNumber(bank_id, email)

            return redirect(url_for('dashboard_user'))
        else:
            pass
        
    return render_template("user_login.html")


@app.route('/user/staff', methods=['GET', 'POST'])
def staff():
    return render_template("staff_login.html")


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    return render_template("signup.html")


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard_user():
    bank_id = session['bank_id']
    account_no = session['account_no']
    email = session['email']

    balance = db.FetchBalance(bank_id, account_no)
    credit_score = db.FetchCreditScore(bank_id, account_no)
    transactions = db.GetTransactions(bank_id, account_no)
    loans = db.GetLoans(bank_id, account_no)

    return render_template("user_dashboard.html", balance=balance, credit_score=credit_score, transactions=transactions, loans=loans)

@app.route('/staff/dashboard', methods=['GET', 'POST'])
def dashboard_staff():
    return render_template("staff_dashboard.html")



if __name__ == "__main__":
    app.run(debug = True)