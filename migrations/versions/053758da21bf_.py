"""empty message

Revision ID: 053758da21bf
Revises: b162c3c10243
Create Date: 2019-12-18 21:29:58.482898

"""
from alembic import op
import sqlalchemy as sa
import ormtypes
from sqlalchemy.dialects import mysql
from sqlalchemy.engine import Connection
# revision identifiers, used by Alembic.
revision = '053758da21bf'
down_revision = 'b162c3c10243'
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
    op.add_column('users', sa.Column(
        'force_logout_before', sa.Float(), nullable=False))
    conn: Connection = op.get_bind()
    # 设置
    conn.execute(
        """UPDATE users set force_logout_before = 0 where 1 = 1"""
    )
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
    op.drop_column('users', 'force_logout_before')
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
    # ### end Alembic commands ###