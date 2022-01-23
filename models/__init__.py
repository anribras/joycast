from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime

db = SQLAlchemy()
ma = Marshmallow()


class TimeStampMixin(object):
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, default=datetime.utcnow)
    delete_at = db.Column(db.DateTime, nullable=True)


# 1.
# modify this in migration/env.py:
# with connectable.connect() as connection:
#     context.configure(
#         connection=connection,
#         target_metadata=target_metadata,
#         process_revision_directives=process_revision_directives,
#         render_as_batch=True, # this line
#         **current_app.extensions['migrate'].configure_args
#     )

# 2.
# # op.drop_table('spatial_ref_sys')

# 3.
# # add import geoalchemy2

import sqlalchemy.exc as e


def get_one_or_create(session,
                      model,
                      create_method='',
                      create_method_kwargs=None,
                      **kwargs):
    try:
        return session.query(model).filter_by(**kwargs).one(), False
    except e.NoResultFound:
        kwargs.update(create_method_kwargs or {})
        created = getattr(model, create_method, model)(**kwargs)
        try:
            session.add(created)
            session.flush()
            return created, True
        except e.IntegrityError:
            session.rollback()
            return session.query(model).filter_by(**kwargs).one(), False


def update_or_create(session, model, is_existed_keys: list = [], **kwargs):
    query = None
    old = None
    obj = None
    new_kwargs = kwargs if len(is_existed_keys) == 0 else {}
    created_by_key = is_existed_keys or []
    for key in created_by_key:
        new_kwargs[key] = kwargs[key]
    try:
        query = session.query(model).filter_by(**new_kwargs)
        old = query.one()
    except e.NoResultFound:
        obj = model(**kwargs)
        try:
            session.add(obj)
            session.flush()
        except e.IntegrityError:
            session.rollback()
            return session.query(model).filter_by(**kwargs).one(), False
        return obj, True
    try:
        # need update
        query.update(kwargs)
        session.flush()
    except e.IntegrityError:
        session.rollback()
    return old, False
