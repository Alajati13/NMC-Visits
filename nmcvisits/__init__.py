from distutils.log import Log
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config["SECRET_KEY"] = "597a03341bd35ff16eeebbd42872a8be"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nmc.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
login_manager = LoginManager(app)


from nmcvisits import routes
