"""习题集记录扩充

Revision ID: 5328b82a3943
Revises: 6d2916806f22
Create Date: 2021-08-07 21:07:08.176501

"""
import ormtypes
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5328b82a3943'
down_revision = '6d2916806f22'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('comment_ibfk_2', 'comment', type_='foreignkey')
    op.drop_constraint('comment_ibfk_1', 'comment', type_='foreignkey')
    op.create_foreign_key(None, 'comment', 'user', ['uid'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'comment', 'discussion', ['discussion_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('contest_ibfk_1', 'contest', type_='foreignkey')
    op.create_foreign_key(None, 'contest', 'user', ['owner_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('discussion_ibfk_1', 'discussion', type_='foreignkey')
    op.create_foreign_key(None, 'discussion', 'user', ['uid'], ['id'], ondelete='CASCADE')
    op.drop_constraint('feed_ibfk_1', 'feed', type_='foreignkey')
    op.create_foreign_key(None, 'feed', 'user', ['uid'], ['id'], ondelete='CASCADE')
    op.drop_constraint('follower_ibfk_1', 'follower', type_='foreignkey')
    op.drop_constraint('follower_ibfk_2', 'follower', type_='foreignkey')
    op.create_foreign_key(None, 'follower', 'user', ['target'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'follower', 'user', ['source'], ['id'], ondelete='CASCADE')
    op.drop_constraint('mail_ibfk_2', 'mail', type_='foreignkey')
    op.drop_constraint('mail_ibfk_1', 'mail', type_='foreignkey')
    op.create_foreign_key(None, 'mail', 'user', ['from_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'mail', 'user', ['to_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('permission_pack_user_ibfk_1', 'permission_pack_user', type_='foreignkey')
    op.create_foreign_key(None, 'permission_pack_user', 'permission_pack', ['pack_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('problem_ibfk_2', 'problem', type_='foreignkey')
    op.drop_constraint('problem_ibfk_1', 'problem', type_='foreignkey')
    op.create_foreign_key(None, 'problem', 'team', ['team_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'problem', 'user', ['uploader_id'], ['id'], ondelete='CASCADE')
    op.add_column('problem_set', sa.Column('foreign_problems', ormtypes.json_pickle.JsonPickle(), nullable=False))
    op.drop_constraint('problem_set_ibfk_1', 'problem_set', type_='foreignkey')
    op.create_foreign_key(None, 'problem_set', 'user', ['owner_uid'], ['id'], ondelete='CASCADE')
    op.drop_constraint('problem_todo_ibfk_1', 'problem_todo', type_='foreignkey')
    op.drop_constraint('problem_todo_ibfk_2', 'problem_todo', type_='foreignkey')
    op.create_foreign_key(None, 'problem_todo', 'user', ['uid'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'problem_todo', 'problem', ['problem_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('problemtag_ibfk_2', 'problemtag', type_='foreignkey')
    op.drop_constraint('problemtag_ibfk_1', 'problemtag', type_='foreignkey')
    op.create_foreign_key(None, 'problemtag', 'problem', ['problem_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'problemtag', 'tag', ['tag_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('submission_ibfk_1', 'submission', type_='foreignkey')
    op.drop_constraint('submission_ibfk_2', 'submission', type_='foreignkey')
    op.create_foreign_key(None, 'submission', 'user', ['uid'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'submission', 'virtual_contest', ['virtual_contest_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('team_ibfk_1', 'team', type_='foreignkey')
    op.create_foreign_key(None, 'team', 'user', ['owner_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('virtual_contest_ibfk_2', 'virtual_contest', type_='foreignkey')
    op.drop_constraint('virtual_contest_ibfk_1', 'virtual_contest', type_='foreignkey')
    op.create_foreign_key(None, 'virtual_contest', 'user', ['owner_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'virtual_contest', 'contest', ['contest_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('wikipage_version_ibfk_1', 'wikipage_version', type_='foreignkey')
    op.drop_constraint('wikipage_version_ibfk_2', 'wikipage_version', type_='foreignkey')
    op.drop_constraint('wikipage_version_ibfk_3', 'wikipage_version', type_='foreignkey')
    op.create_foreign_key(None, 'wikipage_version', 'wikipage', ['wikipage_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'wikipage_version', 'user', ['uid'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'wikipage_version', 'wiki_navigation_item', ['navigation_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###
    op.execute("""UPDATE problem_set SET foreign_problems='[]'""")

def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'wikipage_version', type_='foreignkey')
    op.drop_constraint(None, 'wikipage_version', type_='foreignkey')
    op.drop_constraint(None, 'wikipage_version', type_='foreignkey')
    op.create_foreign_key('wikipage_version_ibfk_3', 'wikipage_version', 'wiki_navigation_item', ['navigation_id'], ['id'], onupdate='RESTRICT', ondelete='CASCADE')
    op.create_foreign_key('wikipage_version_ibfk_2', 'wikipage_version', 'wikipage', ['wikipage_id'], ['id'], onupdate='RESTRICT', ondelete='CASCADE')
    op.create_foreign_key('wikipage_version_ibfk_1', 'wikipage_version', 'user', ['uid'], ['id'], onupdate='RESTRICT', ondelete='CASCADE')
    op.drop_constraint(None, 'virtual_contest', type_='foreignkey')
    op.drop_constraint(None, 'virtual_contest', type_='foreignkey')
    op.create_foreign_key('virtual_contest_ibfk_1', 'virtual_contest', 'contest', ['contest_id'], ['id'], onupdate='RESTRICT', ondelete='CASCADE')
    op.create_foreign_key('virtual_contest_ibfk_2', 'virtual_contest', 'user', ['owner_id'], ['id'], onupdate='RESTRICT', ondelete='CASCADE')
    op.drop_constraint(None, 'team', type_='foreignkey')
    op.create_foreign_key('team_ibfk_1', 'team', 'user', ['owner_id'], ['id'], onupdate='RESTRICT', ondelete='CASCADE')
    op.drop_constraint(None, 'submission', type_='foreignkey')
    op.drop_constraint(None, 'submission', type_='foreignkey')
    op.create_foreign_key('submission_ibfk_2', 'submission', 'virtual_contest', ['virtual_contest_id'], ['id'], onupdate='RESTRICT', ondelete='CASCADE')
    op.create_foreign_key('submission_ibfk_1', 'submission', 'user', ['uid'], ['id'], onupdate='RESTRICT', ondelete='CASCADE')
    op.drop_constraint(None, 'problemtag', type_='foreignkey')
    op.drop_constraint(None, 'problemtag', type_='foreignkey')
    op.create_foreign_key('problemtag_ibfk_1', 'problemtag', 'problem', ['problem_id'], ['id'], onupdate='RESTRICT', ondelete='CASCADE')
    op.create_foreign_key('problemtag_ibfk_2', 'problemtag', 'tag', ['tag_id'], ['id'], onupdate='RESTRICT', ondelete='CASCADE')
    op.drop_constraint(None, 'problem_todo', type_='foreignkey')
    op.drop_constraint(None, 'problem_todo', type_='foreignkey')
    op.create_foreign_key('problem_todo_ibfk_2', 'problem_todo', 'user', ['uid'], ['id'], onupdate='RESTRICT', ondelete='CASCADE')
    op.create_foreign_key('problem_todo_ibfk_1', 'problem_todo', 'problem', ['problem_id'], ['id'], onupdate='RESTRICT', ondelete='CASCADE')
    op.drop_constraint(None, 'problem_set', type_='foreignkey')
    op.create_foreign_key('problem_set_ibfk_1', 'problem_set', 'user', ['owner_uid'], ['id'], onupdate='RESTRICT', ondelete='CASCADE')
    op.drop_column('problem_set', 'foreign_problems')
    op.drop_constraint(None, 'problem', type_='foreignkey')
    op.drop_constraint(None, 'problem', type_='foreignkey')
    op.create_foreign_key('problem_ibfk_1', 'problem', 'user', ['uploader_id'], ['id'], onupdate='RESTRICT', ondelete='CASCADE')
    op.create_foreign_key('problem_ibfk_2', 'problem', 'team', ['team_id'], ['id'], onupdate='RESTRICT', ondelete='CASCADE')
    op.drop_constraint(None, 'permission_pack_user', type_='foreignkey')
    op.create_foreign_key('permission_pack_user_ibfk_1', 'permission_pack_user', 'permission_pack', ['pack_id'], ['id'], onupdate='RESTRICT', ondelete='CASCADE')
    op.drop_constraint(None, 'mail', type_='foreignkey')
    op.drop_constraint(None, 'mail', type_='foreignkey')
    op.create_foreign_key('mail_ibfk_1', 'mail', 'user', ['from_id'], ['id'], onupdate='RESTRICT', ondelete='CASCADE')
    op.create_foreign_key('mail_ibfk_2', 'mail', 'user', ['to_id'], ['id'], onupdate='RESTRICT', ondelete='CASCADE')
    op.drop_constraint(None, 'follower', type_='foreignkey')
    op.drop_constraint(None, 'follower', type_='foreignkey')
    op.create_foreign_key('follower_ibfk_2', 'follower', 'user', ['target'], ['id'], onupdate='RESTRICT', ondelete='CASCADE')
    op.create_foreign_key('follower_ibfk_1', 'follower', 'user', ['source'], ['id'], onupdate='RESTRICT', ondelete='CASCADE')
    op.drop_constraint(None, 'feed', type_='foreignkey')
    op.create_foreign_key('feed_ibfk_1', 'feed', 'user', ['uid'], ['id'], onupdate='RESTRICT', ondelete='CASCADE')
    op.drop_constraint(None, 'discussion', type_='foreignkey')
    op.create_foreign_key('discussion_ibfk_1', 'discussion', 'user', ['uid'], ['id'], onupdate='RESTRICT', ondelete='CASCADE')
    op.drop_constraint(None, 'contest', type_='foreignkey')
    op.create_foreign_key('contest_ibfk_1', 'contest', 'user', ['owner_id'], ['id'], onupdate='RESTRICT', ondelete='CASCADE')
    op.drop_constraint(None, 'comment', type_='foreignkey')
    op.drop_constraint(None, 'comment', type_='foreignkey')
    op.create_foreign_key('comment_ibfk_1', 'comment', 'discussion', ['discussion_id'], ['id'], onupdate='RESTRICT', ondelete='CASCADE')
    op.create_foreign_key('comment_ibfk_2', 'comment', 'user', ['uid'], ['id'], onupdate='RESTRICT', ondelete='CASCADE')
    # ### end Alembic commands ###
