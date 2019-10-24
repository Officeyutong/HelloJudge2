"""empty message

Revision ID: 4fb154859865
Revises: 58fae4d1a268
Create Date: 2019-10-24 21:56:03.453010

"""
from alembic import op
import sqlalchemy as sa
import ormtypes


# revision identifiers, used by Alembic.
revision = '4fb154859865'
down_revision = '58fae4d1a268'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('problems', sa.Column('can_see_results', sa.Boolean(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('problems', 'can_see_results')
    # ### end Alembic commands ###
