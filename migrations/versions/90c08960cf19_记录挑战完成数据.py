"""记录挑战完成数据

Revision ID: 90c08960cf19
Revises: 67e87203d4e4
Create Date: 2021-11-01 22:14:23.719605

"""
import ormtypes
from alembic import op
import sqlalchemy as sa
from sqlalchemy import orm
import models

# revision identifiers, used by Alembic.
revision = '90c08960cf19'
down_revision = '67e87203d4e4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('challenge_record',
                    sa.Column('uid', sa.Integer(), nullable=False),
                    sa.Column('challenge_id', sa.Integer(), nullable=False),
                    sa.Column('problemset_id', sa.Integer(), nullable=False),
                    sa.Column('finished', sa.Boolean(), nullable=True),
                    sa.ForeignKeyConstraint(
                        ['challenge_id'], ['challenge.id'], ondelete='CASCADE'),
                    sa.ForeignKeyConstraint(
                        ['problemset_id'], ['problem_set.id'], ondelete='CASCADE'),
                    sa.ForeignKeyConstraint(
                        ['uid'], ['user.id'], ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint(
                        'uid', 'challenge_id', 'problemset_id')
                    )
    op.create_index(op.f('ix_challenge_record_finished'),
                    'challenge_record', ['finished'], unique=False)
    # import json
    session = orm.Session(bind=op.get_bind())
    default_perm_group = session.query(models.PermissionGroup).filter(
        models.PermissionGroup.id == "default").one()
    q = "[provider:all-challenge]"
    default_perm_group.permissions = [
        t for t in default_perm_group.permissions if t != q]+[q]
    
    for user in session.query(models.User):
        user.permissions = [
            t for t in user.permissions if not t.startswith("challenge.")]
    session.commit()
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_challenge_record_finished'),
                  table_name='challenge_record')
    op.drop_table('challenge_record')
    # ### end Alembic commands ###
