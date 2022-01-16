from flask import Blueprint, request, make_response, jsonify
import datetime
from models import db
from models.user import *
from backend.helper.utils import get_short_code
from backend.helper.error import derived_error
from flask_restful import Resource, Api
from flask_jwt_extended import  jwt_required

bp = Blueprint('v1', __name__,url_prefix='/api/v1')
api = Api(bp, catch_all_404s=True)

from flask_jwt_extended import current_user

@bp.route('/')
def index():
    return {
        "nice": "you saw me"
    }

@bp.route('/protect')
@jwt_required()
def protect():
    user = current_user
    return {
        'username' : user.username
    }
    pass


@api.resource('/activity/<int:id>')
class ActivityView(Resource):
    def get(self, id):
        # Query db, usb schema dump into json , then make it a http response
        pass
    def put(self, id):
        # Load json from request, use schema load into db instance , then updated it into db
        pass

