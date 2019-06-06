#!flask/bin/python3
from flask import Flask
from flask import url_for, redirect
from flask import render_template
from flask import request
from flask import flash
from flask import session
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import random

from server_core import API
userAPIs = API()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5) # 配置7天有效 

db = SQLAlchemy()
db.init_app(app)

class UserModel(db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(30), unique=True, nullable=False)
	password = db.Column(db.String(30))

	def __init__(self, username, password):
		self.username = username
		self.password = password
	def add_user(self):
		db.session.add(self)
		db.session.commit()
	@classmethod
	def get_user(cls, username):
		return cls.query.filter_by(username=username).first()

migrate = Migrate(app, db)



@app.route('/')
def index():
	if 'username' in session:
		username = session['username']
		return redirect(url_for('valid_user', username=username))
	return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == 'POST':
		if find_user(request.form['username']):
			return render_template('register.html', error_msg="User exists!")
		elif check_password(request.form['password']) is False:
			return render_template('register.html', error_msg="Password out of vocabulary!")
		else:
			user = UserModel(request.form['username'], request.form['password'])
			user.add_user()
			return redirect(url_for('valid_user', username=request.form['username']))
	if 'username' in session:
		username = session['username']
		return render_template('register.html', username=username)
	return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		user = find_user(request.form['username'])
		if user:
			return redirect(url_for('authenticate', username=user.username))
			#return redirect(url_for('authenticate', user=user.username))
	return render_template('login.html')

@app.route('/<username>/authenticate', methods=['GET', 'POST'])
def authenticate(username):
	user = find_user(username)
	sessionid = random.randint(0, 100000)
	good , next_question = userAPIs.try_to_login(user.username, user.password, sessionid)
	if request.method == 'POST':
		#user choose an answer from next_question
		userAPIs.update_by_choice(user.username, user.password, sessionid, user_ans)
		return redirect(url_for('authenticate', user=user))
	else:
		if not good:
			flash('Login failed!')
			return render_template('home.html')
		elif next_question is None:
			return redirect(url_for('valid_user', username=user.username))
		else:
			return render_template('authenticate.html', next_question=next_question)

@app.route('/<username>')
def valid_user(username):
	flash('Login success!')
	flash('done well!')
	### set session
	session['username'] = username
	session.permanent = True
	return render_template('home.html', username=username)

@app.route('/logout')
def logout():
	session.pop('username', None)
	return render_template('home.html')

# ------ #

def find_user(username):
	user = UserModel.get_user(username)
	return user
	
def check_password(password):
	return userAPIs.register(password)


if __name__ == '__main__':
	app.secret_key = '12345'
	app.run(host='127.0.0.1', port=8000, debug=True)

