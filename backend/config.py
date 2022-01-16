class Common(object):
    URL_PREFIX = '/api/v1'

class Development(Common):
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///./app.db'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@localhost:3306/joycast'
    # SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://root:root@localhost:3306/joycast'
    # SQLALCHEMY_DATABASE_URI = 'postgres://default:secret@localhost:5432/default'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_ECHO = False
    FLASK_DEBUG = True

    # jwt
    JWT_SECRET_KEY = 'super'
