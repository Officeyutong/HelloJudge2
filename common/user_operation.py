from flask_sqlalchemy import SQLAlchemy
import datetime
import sqlalchemy.sql.expression as expr
import sqlalchemy.sql.functions as func
import flask

from common.exceptions import APIException
from common.permission import PermissionManager


class UserOperation:
    def __init__(self, db: SQLAlchemy, permission_manager: PermissionManager) -> None:
        self.db = db
        self.permission_manager = permission_manager

    def ensure_accepted_problems_for_user(self, uid: int) -> None:
        from models.user import User, CachedAcceptedProblems
        from models.contest import Contest
        from models.problem import Problem
        from models.submission import Submission
        from main import config
        last_refreshed: User = self.db.session.query(
            User.last_refreshed_cached_accepted_problems).filter(User.id == uid).one_or_none()
        now = datetime.datetime.now()
        if not last_refreshed:
            return
        should_refresh = False
        if last_refreshed.last_refreshed_cached_accepted_problems is None:
            should_refresh = True
        elif (now - last_refreshed.last_refreshed_cached_accepted_problems).total_seconds() > config.ACCEPTED_PROBLEMS_REFRESH_INTERVAL:
            should_refresh = True
        if not should_refresh:
            return
        print("Refreshing accepted problems for", uid)
        self.db.session.query(CachedAcceptedProblems).filter(
            CachedAcceptedProblems.uid == uid).delete()
        self.db.session.commit()
        closed_contests_subq = expr.select(Contest.id).where(
            Contest.closed == True).scalar_subquery()
        problems = self.db.session.query(Problem.id).filter(
            expr.or_(
                # 要么有AC的非比赛提交
                expr.select(func.count(Submission.id)).where(
                    expr.and_(
                        Submission.problem_id == Problem.id,
                        Submission.status == "accepted",
                        Submission.contest_id == -1,
                        Submission.uid == uid
                    )
                ).limit(1).scalar_subquery() > 0,
                # 要么有AC的比赛提交，并且该比赛已关闭
                expr.select(func.count(Submission.id)).where(
                    expr.and_(
                        Submission.contest_id.in_(closed_contests_subq),
                        Submission.problem_id == Problem.id,
                        Submission.uid == uid,
                        Submission.status == "accepted"
                    )
                ).limit(1).scalar_subquery() > 0
            )
        )
        self.db.session.add_all(CachedAcceptedProblems(
            uid=uid,
            problem_id=item.id
        ) for item in problems)
        self.db.session.execute(expr.update(User).where(User.id == uid).values(
            last_refreshed_cached_accepted_problems=now))
        self.db.session.commit()

    def ensure_login(self) -> int:
        uid = flask.session.get("uid", -1)
        if uid == -1:
            raise APIException("请先登录", -1)
        return uid

    def ensure_in_team(self, uid: int, team_id: int, allow_public: bool = True, allow_permission: bool = True, throw_when_not_in: bool = False) -> bool:
        from models.team import TeamMember, Team
        in_team = bool(self.db.session.query(TeamMember).filter_by(
            uid=uid, team_id=team_id).count())
        public = not bool(self.db.session.query(
            Team.private).filter(Team.id == team_id).one().private)
        ok = in_team or (
            allow_permission and self.permission_manager.has_permission(
                uid, f"team.use.{team_id}")
        ) or (
            allow_public and public
        )
        if throw_when_not_in:
            raise APIException("你没有权限进行此操作", -1)
        else:
            return ok

    def ensure_team_admin(self, uid: int, team_id: int, allow_permission: bool, throw_when_not: bool = False) -> bool:
        from models.team import TeamMember
        member = self.db.session.query(TeamMember).filter_by(
            uid=uid, team_id=team_id).one_or_none()
        ok = (member is not None and bool(member.is_admin)) or (
            allow_permission and self.permission_manager.has_permission(uid, "team.manage"))
        if throw_when_not:
            raise APIException("你没有权限进行此操作", -1)
        else:
            return ok
