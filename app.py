from flask import Flask, render_template, url_for, request, redirect, session
import db as db
from flask_session import Session
import json
import random


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


@app.route('/staff', methods=['GET', 'POST'])
def staff():
    bank_id = request.form.get('bank_id')
    email = request.form.get('email')
    password = request.form.get('password')

    if request.method == 'POST':
        if(db.StaffLogin(bank_id, email, password)):
            session['bank_id'] = bank_id
            session['email'] = email

            return redirect(url_for('dashboard_staff'))
        else:
            pass

    return render_template("staff_login.html")


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    bank_id = request.form.get('bank_id')
    email = request.form.get('email')
    password = request.form.get('password')
    fname = request.form.get('fname')
    lname = request.form.get('lname')

    if request.method == 'POST':
        num = str(random.randint(10000000, 99999999))
        account_no = bank_id + num
        print("yay")
        if(db.CreateUser(email,password,fname,lname,bank_id,account_no,0)):
            print("foo")
            session['bank_id'] = bank_id
            session['email'] = email
            session['account_no'] = account_no

            db.CreditScore(bank_id, account_no, 850.00, 8.0)

            return redirect(url_for('dashboard_user'))

        

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

    if 'send' in request.form:
        account = request.form.get('account')
        amount = float(request.form.get('amount'))

        db.CreateTransaction(bank_id,account_no, -1 * amount)
        db.CreateTransaction(bank_id,account,amount)

    return render_template("user_dashboard.html", balance=balance, credit_score=credit_score, transactions=transactions, loans=loans, account_no=account_no)

@app.route('/staffonline', methods=['GET', 'POST'])
def dashboard_staff():
    depositacc = request.form.get('deposit-acc')
    depositamount = request.form.get('deposit-amount')
    accfrom = request.form.get('acc-from')
    accto = request.form.get('acc-to')
    transferamount = request.form.get('transfer-amount')
    benaccount = request.form.get('ben-account')
    reason = request.form.get('reason')
    benamount = request.form.get('ben-amount')

    if 'deposit-button' in request.form:
        db.CreateTransaction(session['bank_id'], depositacc, float(depositamount))

    if 'transfer-button' in request.form:
        transferamount = float(transferamount)
        db.CreateTransaction(session['bank_id'], accfrom, -1 * transferamount)
        db.CreateTransaction(session['bank_id'], accto, transferamount)
    
    if 'grant-button' in request.form:
        benamount = float(benamount)
        db.CreditReport(session['bank_id'],benaccount, benamount)

    return render_template("staff_dashboard.html")

@app.route('/bank', methods=['GET', 'POST'])
def bank():
    bank_name = request.form.get('bank_name')
    address = request.form.get('address')
    email = request.form.get('email')
    password = request.form.get('password')
    fname = request.form.get('fname')
    lname = request.form.get('lname')

    if request.method == 'POST':
        session['bank_id'] = db.CreateBank(bank_name, address)
        bank_id = session['bank_id']
        if(db.CreateBankEntity(bank_id,email,password,fname,lname,'readwrite','readwrite','readwrite')):
            session['transaction'] = 'readwrite'
            session['users'] = 'readwrite'
            session['executive_access'] = 'readwrite'

            return redirect(url_for('dashboard_staff'))

    return render_template("bank.html")

if __name__ == "__main__":
    app.run(debug = True)