from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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
		return cls.query.filter_by(name=name).first()