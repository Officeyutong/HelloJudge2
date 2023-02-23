from sqlalchemy.sql.expression import join
from sqlalchemy.sql.operators import exists
from models.team import TeamMember
from flask_sqlalchemy import SQLAlchemy
from typing import Iterable, Optional, Set

from models import Team, ProblemSet, PermissionPack, Challenge, ChallengeRecord


class DefaultPermissionProvider:
    def __init__(self, db: SQLAlchemy) -> None:
        self.db = db

    def get_challenge_finish(self, uid: int, challenge_id: Optional[str]) -> Set[str]:
        return {f"challenge.finish.{challenge_id}.all"}

    def get_all_challenge_access(self, uid: int, data: Optional[str]) -> Set[str]:
        access: Iterable[ChallengeRecord] = self.db.session.query(
            ChallengeRecord.challenge_id, ChallengeRecord.problemset_id, ChallengeRecord.finished).filter(ChallengeRecord.uid == uid).all()
        ret: Set[str] = set()
        all_challenges: Set[int] = set()
        exists_unfinished: Set[int] = set()
        for item in access:
            all_challenges.add(item.challenge_id)
            if item.finished:
                # 习题集完成了的，加完成标记
                ret.add(
                    f"challenge.finish.{item.challenge_id}.{item.problemset_id}")
            else:
                exists_unfinished.add(item.challenge_id)

        for item in all_challenges:
            ret.add(f"[provider:challenge-access.{item}]")
            # 习题集都完成了的，加挑战完成标记
            if item not in exists_unfinished:
                ret.add(f"challenge.finish.{item}.all")
        # ret = {f"[provider:challenge-access.{x.challenge_id}]" for x in access}
        # ret |= {
        #     f"[provider:challenge-finish.{x.challenge_id}]" for x in access if x.finished}
        return ret

    def get_challenge_access(self, uid: int, challenge_id: Optional[str]) -> Set[str]:
        problem_sets: Challenge = self.db.session.query(
            Challenge.problemset_list).filter(Challenge.id == challenge_id).one_or_none()
        if problem_sets:
            return {f"[provider:problemset.{x}]" for x in problem_sets.problemset_list} | {f"challenge.access.{challenge_id}"}
        return set()

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
        # print(team)
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

    def get_public_problemset(self, uid: int, data: Optional[str]) -> Set[str]:
        problem_sets = self.db.session.query(
            ProblemSet.id).filter(ProblemSet.private == False).all()
        return {f"[provider:problemset.{s.id}]" for s in problem_sets}
