from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SECRET_KEY"] = "597a03341bd35ff16eeebbd42872a8be"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nmc.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

from nmcvisits import routes
