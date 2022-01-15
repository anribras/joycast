from flask import Blueprint, request, make_response, jsonify
import datetime
from model import db
from model.user import User
from backend.helper.utils import get_short_code
from backend.helper.error import derived_error
from flask_restful import Resource, Api
from backend.helper.error import ErrorCode as E

bp = Blueprint('api/v1', __name__)
api = Api(bp, catch_all_404s=True)


@bp.route('/')
def index():
    return {
        "nice": "you saw me"
    }


@api.resource('/activity/<int:id>')
class ActivityView(Resource):
    def get(self, id):
        # Query db, usb schema dump into json , then make it a http response
        pass
    def put(self, id):
        # Load json from request, use schema load into db instance , then updated it into db
        pass

