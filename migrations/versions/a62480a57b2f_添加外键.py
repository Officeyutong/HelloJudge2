"""添加外键

Revision ID: a62480a57b2f
Revises: 4c3a6d07cc13
Create Date: 2020-12-20 18:36:21.393776

"""
import ormtypes
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a62480a57b2f'
down_revision = '4c3a6d07cc13'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, 'submission', 'problem', ['problem_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'submission', type_='foreignkey')
    # ### end Alembic commands ###
