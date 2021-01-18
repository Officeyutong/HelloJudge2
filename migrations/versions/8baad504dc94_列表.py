"""列表

Revision ID: 8baad504dc94
Revises: 97ea3a6c014d
Create Date: 2020-08-25 21:47:21.456801

"""
import ormtypes
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8baad504dc94'
down_revision = '97ea3a6c014d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('problem_todo',
    sa.Column('uid', sa.Integer(), nullable=False),
    sa.Column('problem_id', sa.Integer(), nullable=False),
    sa.Column('join_time', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['problem_id'], ['problem.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['uid'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('uid', 'problem_id')
    )
    op.create_index(op.f('ix_problem_todo_join_time'), 'problem_todo', ['join_time'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_problem_todo_join_time'), table_name='problem_todo')
    op.drop_table('problem_todo')
    # ### end Alembic commands ###
