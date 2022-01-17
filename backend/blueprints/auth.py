import flask
import pymysql

from backend.auth import jwt
from flask import Blueprint, request, make_response, jsonify
from models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
from models import db
from models.user import User
from backend.helper.error import derived_error, ErrorCode as E
from flask_jwt_extended import create_access_token

bp = Blueprint('auth', __name__, url_prefix='/auth/api')


# Register a callback function that takes whatever object is passed in as the
# identity when creating JWTs and converts it to a JSON serializable format.
@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.username if user.username else user.id


# Register a callback function that loads a user from your database whenever
# a protected route is accessed. This should return any python object on a
# successful lookup, or None if the lookup failed for any reason (for example
# if the user has been deleted from the database).
@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    # query db for every request, kand of waste time
    return User.query.filter_by(username=identity).one_or_none()


@bp.route('/register', methods=['POST'])
def register():
    username = request.json['username']
    password = request.json['password']
    try:
        user = User(username, generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        resp = make_response(jsonify(derived_error(E.table_insert_error, extra=e.__str__())))
        resp.status_code = 200
        return resp
    # user object pass to generate token
    token = create_access_token(user)
    return make_response(jsonify(**derived_error(E.ok), access_token=token))


@bp.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']
    try:
        user = db.session.query(User).filter_by(username=username).one_or_none()
    except Exception as e:
        return make_response(jsonify(derived_error(E.table_insert_error, extra=e.__str__()))), 200
    if check_password_hash(generate_password_hash(password), password) and user is not None:
        token = create_access_token(user)
        return make_response(jsonify(**derived_error(E.ok), access_token=token)), 200
    else:
        return make_response(jsonify(**derived_error(E.user_not_exist_or_password_wrong))), 200


@bp.route('/logout', methods=['POST'])
def logout():
    return 'tbd'
