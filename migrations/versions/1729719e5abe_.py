"""empty message

Revision ID: 1729719e5abe
Revises: e09726b41f8e
Create Date: 2019-12-20 21:52:20.144674

"""
from alembic import op
import sqlalchemy as sa
import ormtypes
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '1729719e5abe'
down_revision = 'e09726b41f8e'
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
    op.add_column('permission_groups', sa.Column(
        'inherit', sa.String(length=20), nullable=False))
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
    from sqlalchemy.engine import Connection
    conn: Connection = op.get_bind()
    conn.execute(
        """update permission_groups set inherit = "" where 1=1"""
    )
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
    op.drop_column('permission_groups', 'inherit')
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
