from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = "597a03341bd35ff16eeebbd42872a8be"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nmc.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = os.environ.get("GMAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.environ.get("GMAIL_PASSWORD")
app.config["MAIL_ASCII_ATTACHMENTS"] = False

mail = Mail(app)


from nmcvisits import routes
