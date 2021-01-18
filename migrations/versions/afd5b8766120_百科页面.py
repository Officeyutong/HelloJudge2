"""百科页面

Revision ID: afd5b8766120
Revises: 933014989333
Create Date: 2020-09-02 22:17:35.702971

"""
import ormtypes
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'afd5b8766120'
down_revision = '933014989333'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('wikipage_ibfk_1', 'wikipage', type_='foreignkey')
    op.drop_column('wikipage', 'cached_last_modified_time')
    op.drop_column('wikipage', 'cached_last_modified_user')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('wikipage', sa.Column('cached_last_modified_user', mysql.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('wikipage', sa.Column('cached_last_modified_time', mysql.DATETIME(), nullable=True))
    op.create_foreign_key('wikipage_ibfk_1', 'wikipage', 'user', ['cached_last_modified_user'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###
