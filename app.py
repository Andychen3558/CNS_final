#!flask/bin/python3
from flask import Flask
from flask import url_for, redirect
from flask import render_template
from flask import request
from flask import flash

app = Flask(__name__)

# class number():
# 	def __init__(self):
# 		self.a = 1

# 	def addone(self):
# 		self.a += 1

# test = number()


"""@app.route('/user/<username>/<int:age>')
def user(username, age):
	return "I'm " + username + ", " + str(age) + " years old"

@app.route('/a')
def url_for_a():
	return "this is a"
@app.route('/b')
def b():
	return redirect(url_for('url_for_a'))"""

@app.route('/')
def index():
	return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		if checkUser(request.form['username']):
			flash('Login success!')
			flash('done well!')
			return redirect(url_for('valid_user', username=request.form['username']))
	return render_template('login.html')
def checkUser(username):
	if username == 'andy':
		return True
	else:
		return False

@app.route('/<username>')
def valid_user(username):
	return render_template('home.html', username=username)

@app.route('/logOut')
def logOut():
	return render_template('base.html')

if __name__ == '__main__':
	app.secret_key = '12345'
	app.run(host='127.0.0.1', port=8000, debug=True)

