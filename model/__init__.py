from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

db = SQLAlchemy()
ma = Marshmallow()

from datetime import datetime


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