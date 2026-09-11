##############################################################################
# Nombre del archivo:
# Fecha última modificación:
# Autor/es:
#   Gustavo Hernandez
###############################################################################
# Descripción:
# Guarda una variable con el codigo y nobre de los directorios de los aeropuertos
###############################################################################


class Config:
    SECRET_KEY = 'TidopWebGisAvila'

    DATABASE_FILE = 'database.db'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_FILE
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Security config
    SECURITY_URL_PREFIX = "/admin"
    SECURITY_PASSWORD_HASH = "pbkdf2_sha512"
    SECURITY_PASSWORD_SALT = "$2a$12$kPifOQHjrFsLGJeD9u9D4O4SqkBCnoA1aA3X2lHDD7OlpLOJNgXym"
    SECURITY_LOGIN_USER_TEMPLATE = "security/login_user.html"




