"""empty message

Revision ID: f003393a123f
Revises: add347b3d6b3
Create Date: 2020-08-09 15:21:35.716430

"""
from alembic import op
import sqlalchemy as sa
import ormtypes
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'f003393a123f'
down_revision = 'add347b3d6b3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('contest', 'invite_code',
               existing_type=mysql.VARCHAR(length=10),
               type_=sa.String(length=20),
               existing_nullable=False)
    op.alter_column('contest', 'judge_result_visible',
               existing_type=mysql.TINYINT(display_width=1),
               type_=sa.Boolean(),
               existing_nullable=False)
    op.alter_column('contest', 'private_contest',
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
               existing_type=mysql.TINYTEXT(),
               type_=sa.Text(length=20),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'permission_group',
               existing_type=sa.Text(length=20),
               type_=mysql.TINYTEXT(),
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
    op.alter_column('contest', 'private_contest',
               existing_type=sa.Boolean(),
               type_=mysql.TINYINT(display_width=1),
               existing_nullable=False)
    op.alter_column('contest', 'judge_result_visible',
               existing_type=sa.Boolean(),
               type_=mysql.TINYINT(display_width=1),
               existing_nullable=False)
    op.alter_column('contest', 'invite_code',
               existing_type=sa.String(length=20),
               type_=mysql.VARCHAR(length=10),
               existing_nullable=False)
    # ### end Alembic commands ###
