from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from nmcvisits.config import Config



bcrypt = Bcrypt()
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
login_manager.login_view = "users.login"
login_manager.login_message_category = "info"




def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    bcrypt.init_app(app) 
    db.init_app(app) 
    login_manager.init_app(app) 
    mail.init_app(app) 

    from nmcvisits.Users.routes import usersBP
    from nmcvisits.Appointments.routes import appointmentsBP
    from nmcvisits.Hospitals.routes import hospitals
    from nmcvisits.Main.routes import main
    from nmcvisits.errors.handlers import errors

    app.register_blueprint(usersBP)
    app.register_blueprint(appointmentsBP)
    app.register_blueprint(hospitals)
    app.register_blueprint(main)
    app.register_blueprint(errors)

    return app