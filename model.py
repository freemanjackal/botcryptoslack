from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://postgresql-cubed-34952"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.String, unique=True, nullable=False)
    token = db.Column(db.String, unique=True, nullable=False)


def init_db():
	db.create_all()
	print("database created succesfully")

def insert_token(team_id, token):
	try:
		db.session.add(Token(team_id=team_id, token=token))
		db.session.commit()
	except Exception as e:
		db.session.rollback()
		print(e)


def get_token(team_id):
	tokens = db.session.query(Token).filter(Token.team_id==team_id)
	token = tokens.first()
	return token.token





if __name__ == "__main__":
	init_db()


#token = get_token('Flaskddsd')
#print(token)

