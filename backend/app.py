from flask import Flask
from backend.config import Development
from flask_migrate import Migrate
from flask_script import Manager
from backend.blueprints.api.v1 import bp as api
from backend.blueprints.web.page import bp as web
from models import db,ma
from flask_cors import CORS
from auth import jwt


app = Flask(__name__)
app.config.from_object(Development)
prefix = app.config['URL_PREFIX']
# create blueprint
app.register_blueprint(api, url_prefix=prefix)
app.register_blueprint(web)

db.init_app(app)
ma.init_app(app)
jwt.init_app(app)

manager = Manager(app)
migrate = Migrate(app, db)

CORS(app)

if __name__ == '__main__':
    app.run(debug=True)
