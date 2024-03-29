"""列重命名

Revision ID: 6d2916806f22
Revises: 663e2f408a65
Create Date: 2021-07-02 11:19:45.524509

"""
import ormtypes
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '6d2916806f22'
down_revision = '663e2f408a65'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('problem_solution', sa.Column('verify_comment', mysql.LONGTEXT(), nullable=True))
    op.drop_column('problem_solution', 'verify_comments')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('problem_solution', sa.Column('verify_comments', mysql.LONGTEXT(), nullable=True))
    op.drop_column('problem_solution', 'verify_comment')
    # ### end Alembic commands ###
