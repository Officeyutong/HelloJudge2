"""虚拟比赛

Revision ID: f0795e8d4f6f
Revises: 5bca0c90b54e
Create Date: 2020-08-23 13:31:41.304997

"""
import ormtypes
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f0795e8d4f6f'
down_revision = '5bca0c90b54e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('virtual_contest',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('owner_id', sa.Integer(), nullable=False),
    sa.Column('contest_id', sa.Integer(), nullable=False),
    sa.Column('start_time', sa.DateTime(), nullable=False),
    sa.Column('end_time', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['contest_id'], ['contest.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['owner_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('submission', sa.Column('virtual_contest_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_submission_virtual_contest_id'), 'submission', ['virtual_contest_id'], unique=False)
    op.create_foreign_key(None, 'submission', 'virtual_contest', ['virtual_contest_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'submission', type_='foreignkey')
    op.drop_index(op.f('ix_submission_virtual_contest_id'), table_name='submission')
    op.drop_column('submission', 'virtual_contest_id')
    op.drop_table('virtual_contest')
    # ### end Alembic commands ###
