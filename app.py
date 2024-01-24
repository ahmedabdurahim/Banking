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


@app.route('/user/login', methods=['GET', 'POST'])
def login():
    return render_template("user_login.html")


@app.route('/user/staff', methods=['GET', 'POST'])
def staff():
    return render_template("staff_login.html")


@app.route('/user/signup', methods=['GET', 'POST'])
def signup():
    return render_template("signup.html")


@app.route('/user/dashboard', methods=['GET', 'POST'])
def dashboard_user():
    return render_template("user_dashboard.html")

@app.route('/staff/dashboard', methods=['GET', 'POST'])
def dashboard_staff():
    return render_template("staff_dashboard.html")



if __name__ == "__main__":
    app.run(debug = True)