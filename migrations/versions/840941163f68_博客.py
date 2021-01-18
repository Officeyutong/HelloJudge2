"""博客

Revision ID: 840941163f68
Revises: 9f6db39075c7
Create Date: 2020-09-01 15:44:10.161848

"""
import ormtypes
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '840941163f68'
down_revision = '9f6db39075c7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('discussion', sa.Column('private', mysql.TINYINT(display_width=1), nullable=True))
    op.drop_column('discussion', 'blog_private')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('discussion', sa.Column('blog_private', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True))
    op.drop_column('discussion', 'private')
    # ### end Alembic commands ###
