"""empty message

Revision ID: 8bf4313c0b80
Revises: a9f66b2ef3d8
Create Date: 2019-12-28 21:53:16.188163

"""
from alembic import op
import sqlalchemy as sa
import ormtypes
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '8bf4313c0b80'
down_revision = 'a9f66b2ef3d8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
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
    op.alter_column('problem_set', 'private',
               existing_type=mysql.TINYINT(display_width=1),
               type_=sa.Boolean(),
               existing_nullable=False)
    op.alter_column('problem_set', 'show_ranklist',
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
    op.drop_column('users', 'reset_token')
    op.drop_column('users', 'auth_token')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('auth_token', mysql.VARCHAR(collation='utf8mb4_bin', length=128), nullable=False))
    op.add_column('users', sa.Column('reset_token', mysql.VARCHAR(collation='utf8mb4_bin', length=128), nullable=True))
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
    op.alter_column('problem_set', 'show_ranklist',
               existing_type=sa.Boolean(),
               type_=mysql.TINYINT(display_width=1),
               existing_nullable=False)
    op.alter_column('problem_set', 'private',
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
    # ### end Alembic commands ###