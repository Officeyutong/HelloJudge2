"""置顶增加索引

Revision ID: d1252c9c618a
Revises: bb92b366d72b
Create Date: 2020-08-19 15:10:21.132420

"""
import ormtypes
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'd1252c9c618a'
down_revision = 'bb92b366d72b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_discussion_top'), 'discussion', ['top'], unique=False)
    op.add_column('feed', sa.Column('top', mysql.TINYINT(display_width=1), nullable=True))
    op.create_index(op.f('ix_feed_top'), 'feed', ['top'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_feed_top'), table_name='feed')
    op.drop_column('feed', 'top')
    op.drop_index(op.f('ix_discussion_top'), table_name='discussion')
    # ### end Alembic commands ###
