"""empty message

Revision ID: c4c107c0821b
Revises: 1729719e5abe
Create Date: 2019-12-20 22:27:49.174052

"""
from alembic import op
import sqlalchemy as sa
import ormtypes
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'c4c107c0821b'
down_revision = '1729719e5abe'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('problem_set',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('private', sa.Boolean(), nullable=False),
    sa.Column('invitation_code', sa.String(length=100), nullable=True),
    sa.Column('show_ranklist', sa.Boolean(), nullable=False),
    sa.Column('problems', ormtypes.json_pickle.JsonPickle(), nullable=False),
    sa.Column('create_time', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.alter_column('contest', 'judge_result_visible',
               existing_type=mysql.TINYINT(display_width=1),
               type_=sa.Boolean(),
               existing_nullable=False)
    op.alter_column('contest', 'ranklist_visible',
               existing_type=mysql.TINYINT(display_width=1),
               type_=sa.Boolean(),
               existing_nullable=False)
    op.alter_column('contest', 'rated',
               existing_type=mysql.TINYINT(display_width=1),
               type_=sa.Boolean(),
               existing_nullable=False)
    op.alter_column('discussions', 'top',
               existing_type=mysql.TINYINT(display_width=1),
               type_=sa.Boolean(),
               existing_nullable=False)
    op.alter_column('problems', 'can_see_results',
               existing_type=mysql.TINYINT(display_width=1),
               type_=sa.Boolean(),
               existing_nullable=False)
    op.alter_column('problems', 'public',
               existing_type=mysql.TINYINT(display_width=1),
               type_=sa.Boolean(),
               existing_nullable=True)
    op.alter_column('problems', 'using_file_io',
               existing_type=mysql.TINYINT(display_width=1),
               type_=sa.Boolean(),
               existing_nullable=True)
    op.alter_column('submissions', 'public',
               existing_type=mysql.TINYINT(display_width=1),
               type_=sa.Boolean(),
               existing_nullable=True)
    op.alter_column('users', 'banned',
               existing_type=mysql.TINYINT(display_width=1),
               type_=sa.Boolean(),
               existing_nullable=False)
    op.alter_column('users', 'permission_group',
               existing_type=mysql.TINYTEXT(collation='utf8mb4_bin'),
               type_=sa.Text(length=20),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'permission_group',
               existing_type=sa.Text(length=20),
               type_=mysql.TINYTEXT(collation='utf8mb4_bin'),
               existing_nullable=False)
    op.alter_column('users', 'banned',
               existing_type=sa.Boolean(),
               type_=mysql.TINYINT(display_width=1),
               existing_nullable=False)
    op.alter_column('submissions', 'public',
               existing_type=sa.Boolean(),
               type_=mysql.TINYINT(display_width=1),
               existing_nullable=True)
    op.alter_column('problems', 'using_file_io',
               existing_type=sa.Boolean(),
               type_=mysql.TINYINT(display_width=1),
               existing_nullable=True)
    op.alter_column('problems', 'public',
               existing_type=sa.Boolean(),
               type_=mysql.TINYINT(display_width=1),
               existing_nullable=True)
    op.alter_column('problems', 'can_see_results',
               existing_type=sa.Boolean(),
               type_=mysql.TINYINT(display_width=1),
               existing_nullable=False)
    op.alter_column('discussions', 'top',
               existing_type=sa.Boolean(),
               type_=mysql.TINYINT(display_width=1),
               existing_nullable=False)
    op.alter_column('contest', 'rated',
               existing_type=sa.Boolean(),
               type_=mysql.TINYINT(display_width=1),
               existing_nullable=False)
    op.alter_column('contest', 'ranklist_visible',
               existing_type=sa.Boolean(),
               type_=mysql.TINYINT(display_width=1),
               existing_nullable=False)
    op.alter_column('contest', 'judge_result_visible',
               existing_type=sa.Boolean(),
               type_=mysql.TINYINT(display_width=1),
               existing_nullable=False)
    op.drop_table('problem_set')
    # ### end Alembic commands ###