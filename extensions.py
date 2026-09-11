from datetime import timedelta

from flask import Flask, request, session
from flask_sqlalchemy import SQLAlchemy

from flask_babel import Babel
from flask_migrate import Migrate
from flask_security import Security, SQLAlchemyUserDatastore


from config import Config

# Inicializa las extensiones
db = SQLAlchemy()
babel = Babel()
migrate = Migrate()
app = None
user_datastore = None

# Crea la aplicación
def create_app():
    global app, user_datastore

    app = Flask(__name__, static_folder='static', template_folder='templates')
    #app = Flask(__name__)
    app.secret_key = "TdUsal#2025?"
    # Configura la aplicación
    app.config.from_object(Config)
    app.config['BABEL_DEFAULT_LOCALE'] = 'es'
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=130)
    app.config['SECURITY_LOGIN_USER_TEMPLATE'] = 'security/login_user.html'


    # Inicializa las extensiones con la aplicación
    db.init_app(app)
    babel.init_app(app)
    migrate.init_app(app, db)

    from admin.modelUser import User, Role, CustomLoginForm
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(app, user_datastore, login_form=CustomLoginForm)
    security.login_manager.login_view = 'login'
    security.login_manager.login_message_category = 'error'

    return app


