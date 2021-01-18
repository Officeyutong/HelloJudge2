"""增加索引

Revision ID: 77dd6caa9e91
Revises: 40632a2cc3f8
Create Date: 2020-12-16 17:00:42.293175

"""
import ormtypes
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '77dd6caa9e91'
down_revision = '40632a2cc3f8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('mail', 'from_id',
               existing_type=mysql.INTEGER(),
               nullable=False)
    op.alter_column('mail', 'time',
               existing_type=mysql.DATETIME(),
               nullable=False)
    op.alter_column('mail', 'to_id',
               existing_type=mysql.INTEGER(),
               nullable=False)
    op.create_index(op.f('ix_mail_time'), 'mail', ['time'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_mail_time'), table_name='mail')
    op.alter_column('mail', 'to_id',
               existing_type=mysql.INTEGER(),
               nullable=True)
    op.alter_column('mail', 'time',
               existing_type=mysql.DATETIME(),
               nullable=True)
    op.alter_column('mail', 'from_id',
               existing_type=mysql.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###
