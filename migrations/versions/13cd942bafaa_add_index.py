"""add_index

Revision ID: 13cd942bafaa
Revises: db7d86c6092d
Create Date: 2022-01-23 23:13:29.225745

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '13cd942bafaa'
down_revision = 'db7d86c6092d'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(op.f('ix_track_source_id_title'), 'track', ['source_id', 'album_id'], unique=False)
    pass


def downgrade():
    op.drop_index(op.f('ix_track_source_id_title'), table_name='track')
    pass
