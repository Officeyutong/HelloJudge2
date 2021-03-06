"""恢复远程评测的表

Revision ID: 9bb664cd6149
Revises: a62480a57b2f
Create Date: 2021-01-13 13:17:27.724529

"""
import ormtypes
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9bb664cd6149'
down_revision = 'a62480a57b2f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('remote_accounts',
    sa.Column('account_id', sa.String(length=128), nullable=False),
    sa.Column('username', sa.String(length=100), nullable=False),
    sa.Column('password', sa.String(length=100), nullable=False),
    sa.Column('oj', sa.String(length=20), nullable=False),
    sa.Column('uid', sa.Integer(), nullable=False),
    sa.Column('session', sa.String(length=1024), nullable=False),
    sa.PrimaryKeyConstraint('account_id'),
    sa.UniqueConstraint('account_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('remote_accounts')
    # ### end Alembic commands ###
