from sqlalchemy.sql.expression import join
from models.team import TeamMember
from flask_sqlalchemy import SQLAlchemy
from typing import Optional, Set

from models import Team, ProblemSet, PermissionPack


class DefaultPermissionProvider:
    def __init__(self, db: SQLAlchemy) -> None:
        self.db = db

    def get_allteams_permissions(self, uid: int, arg: Optional[str]) -> Set[str]:
        joined = self.db.session.query(TeamMember.team_id).filter_by(
            uid=uid).all()
        return {f"[provider:team.{x.team_id}]" for x in joined}

    def get_contest_permissions(self, uid: int, contest_id: Optional[str]) -> Set[str]:
        return {f"contest.use.{contest_id}"}

    def get_team_permissions(self, uid: int, team_id: Optional[str]) -> Set[str]:
        joined = self.db.session.query(TeamMember).filter_by(
            uid=uid, team_id=team_id).count() != 0
        team: Team = self.db.session.query(
            Team.team_contests, Team.team_problems, Team.team_problemsets, Team.id).filter(Team.id == team_id).one_or_none()
        if not team:
            return set()
        print(team)
        if joined:
            return {f"team.use.{team_id}"} | {f"[provider:contest.{x}]" for x in team.team_contests} | {f"problem.use.{x}" for x in team.team_problems} | {f"[provider:problemset.{x}]" for x in team.team_problemsets}
        else:
            return {f"team.use.{team_id}"}

    def get_problemset_permissions(self, uid: int, problemset: Optional[str]) -> Set[str]:
        ps: ProblemSet = self.db.session.query(
            ProblemSet.problems).filter_by(id=problemset).one_or_none()
        if not ps:
            return set()
        return {f"problem.use.{x}" for x in ps.problems} | {f"problemset.use.{problemset}"}

    def get_permissionpack_permissions(self, uid: int, permpack_id: Optional[str]) -> Set[str]:
        permpack: PermissionPack = self.db.session.query(
            PermissionPack.permissions).filter(PermissionPack.id == permpack_id).one_or_none()
        if not permpack:
            return set()
        return {f"permissionpack.claimed.{permpack_id}"} | {x for x in permpack.permissions}
