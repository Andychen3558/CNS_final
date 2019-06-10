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
vecfile = 'embedding/wiki.en.vec.small'
caahe = 'embedding/wiki.en.vec.small.urlcache.json'
userAPIs = API(vecfile, use_url=True, init_thres=0.6)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5) 

db = SQLAlchemy()
db.init_app(app)

user_session={}
success_user=[]

class UserModel(db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(30), unique=True, nullable=False)
	password = db.Column(db.String(30))
	choices = db.Column(db.String(100))

	def __init__(self, username, password):
		self.username = username
		self.password = password
		self.choices = ""

	def add_user(self):
		db.session.add(self)
		db.session.commit()
	def add_choice(self, choice):
		self.choices += (choice+';')
		db.session.commit()
	def init_choices(self):
		self.choices = ""
		db.session.commit()

	@classmethod
	def get_user(cls, username):
		return cls.query.filter_by(username=username).first()
	@classmethod
	def delete_user(cls, username):
		db.session.delete(username)
		db.session.commit()
	@classmethod
	def delete_all_users(cls):
		db.session.query(UserModel).delete()
		db.session.commit()

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
			user.init_choices()
			return redirect(url_for('authenticate', username=user.username))
	return render_template('login.html')

@app.route('/<username>/authenticate', methods=['GET', 'POST'])
def authenticate(username):
	user = find_user(username)
	# print(user.choices)
	if user_session.get(username)==None:
		user_session[username] = random.randint(0,100000)
	sessionid = user_session[username]

	good , next_question_words, next_question_urls = userAPIs.try_to_login(user.username, user.password, sessionid)
	# print(next_question_urls)
	if request.method == 'POST':
		#user choose an answer from next_question
		if request.form:
			print(request.form)
			index = next_question_urls.index(request.form['choice'])
			# print(index)
			answer = next_question_words[index]
			user.add_choice(answer)
			userAPIs.update_by_choice(user.username, user.password, sessionid, answer)
		return redirect(url_for('authenticate', username=user.username))
	else:
		if not good:
			flash('Login failed!')
			return render_template('home.html')
		elif next_question_words is None:
			success_user.append(user.username)
			del user_session[username]
			return redirect(url_for('valid_user', username=user.username))
		else:
			return render_template('authenticate1.html', next_question=next_question_urls)

@app.route('/<username>')
def valid_user(username):
	if username not in success_user:
		return render_template('home.html')
	flash('Login success!')
	flash('done well!')
	### set session
	session['username'] = username
	session.permanent = True
	return render_template('home.html', username=username)

@app.route('/logout/')
def logout(username):
	session.pop('username', None)
	# success_user.remove(username)
	return render_template('home.html')

@app.route('/<username>/delete')
def delete(username):
	user = find_user(username)
	UserModel.delete_user(user)
	return redirect(url_for('index'))

@app.route('/delete')
def delete_all():
	UserModel.delete_all_users()
	return redirect(url_for('index'))

# ------ #

def find_user(username):
	user = UserModel.get_user(username)
	return user
	
def check_password(password):
	return userAPIs.register(password)


if __name__ == '__main__':
	app.secret_key = '12345'
	app.run(host='localhost', port=8000, debug=True)

