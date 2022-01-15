from backend.auth import jwt
from flask import Blueprint, request, make_response, jsonify
from models.user import User

bp = Blueprint('auth', __name__)


@bp.route('/login')
def login():
    user = User()
    return {
        "nice": "you saw me"
    }


def logout():
    user = User()
    return {
        "nice": "you saw me"
    }
