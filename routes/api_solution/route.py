from common.permission import require_permission
from typing import List
from flask import Blueprint
from common.utils import make_json_response, require_schema, get_uid
from common.schema import GeneralUserEntry
from .schema import RouteAdminSubmitSolutionSchema, RouteSolutionListEntrySchema, route_solution_entry_schema
from main import db, permission_manager, config, model_api
from models import Problem, ProblemSolution, User
import math
import datetime
router = Blueprint("solution", "solution")


"""
维护一张题解总表。

用户提交题解后，等待审核。每次提交视为一篇题解。题目的题解会显示每个用户提交的最新的通过审核的题解。

审核通过后更改verified。

管理通过其他方式发送的题解直接审核通过。
"""


@router.route("/submit", methods=["POST"])
@require_schema(route_solution_entry_schema)
def submit_solution(content: str, problem_id: int):
    """
    发布题解
    """
    problem: Problem = db.session.query(
        Problem.id, Problem.public).filter_by(id=problem_id).one_or_none()
    if not problem:
        return make_json_response(-1, message="题目ID错误")
    uid = get_uid()
    if not problem.public and not permission_manager.has_permission(uid, f"problem.use.{problem_id}"):
        return make_json_response(-1, message="你没有权限发布题解")
    sol = ProblemSolution(
        uid=uid,
        problem_id=problem_id,
        content=content
    )
    db.session.add(sol)
    db.session.commit()
    return make_json_response(0, data={"solutionID": sol.id})


@router.route("/problem/list", methods=["POST"])
def problem_list_solution(problem_id: int, page: int = 1):
    """
    题目列表题解
    """
    problem: Problem = db.session.query(
        Problem.id, Problem.public).filter_by(id=problem_id).one_or_none()
    if not problem:
        return make_json_response(-1, message="题目ID错误")
    uid = get_uid()
    if not problem.public and not permission_manager.has_permission(uid, f"problem.use.{problem_id}"):
        return make_json_response(-1, message="你没有权限查看该题题解")
    query = db.session.query(
        ProblemSolution.id,
        ProblemSolution.uid,
        User.username,
        User.email,
        ProblemSolution.content,
        ProblemSolution.top,
        ProblemSolution.verified,
        ProblemSolution.upload_time,
        ProblemSolution.verifier,
        ProblemSolution.verify_time
    ).join(User, User.id == ProblemSolution.uid).order_by(ProblemSolution.top.desc()).order_by(ProblemSolution.upload_time.desc())
    page_count = int(math.ceil(query.count()/config.SOLUTIONS_PER_PAGE))
    result: List[RouteSolutionListEntrySchema] = []
    for item in query.slice((page-1)*config.SOLUTIONS_PER_PAGE, page*config.SOLUTIONS_PER_PAGE).all():
        item: ProblemSolution
        verifier = db.session.query(
            User.username, User.email).filter_by(uid=item.verifier).one()
        result.append(RouteSolutionListEntrySchema(
            id=item.id,
            uploader=GeneralUserEntry(
                uid=item.uid,
                email=item.email,
                username=item.username
            ),
            content=item.content,
            top=item.top,
            verified=item.verified,
            upload_timestamp=int(item.upload_time.timestamp()),
            verifier=GeneralUserEntry(
                uid=item.verifier,
                username=verifier.username,
                email=verifier.email
            ),
            verify_timestamp=int(item.verify_time.timestamp())
        ))
    return make_json_response(0, data=RouteSolutionListEntrySchema.Schema(many=True).dump(result), pageCount=page_count)


@router.route("/admin/submit", methods=["POST"])
@require_schema(RouteAdminSubmitSolutionSchema.Schema())
@require_permission(permission_manager, "solution.manage")
def admin_submit(content: str, top: bool, problem_id: int):
    model_api.ensure_problem_id(problem_id)
    inst = ProblemSolution(
        uid=get_uid(),
        problem_id=problem_id,
        content=content,
        top=top,
        verified=True,
        verifier=get_uid(),
        verify_time=datetime.datetime.now(),
        verify_comments=""
    )
    db.session.add(inst)
    db.session.commit()
    return make_json_response(0, message="ok")


@router.route("/admin/verify", methods=["POST"])
@require_permission(permission_manager, "solution.manage")
def admin_verify(solution_id: int, comment: str = ""):
    """
    审核一条题解

    comments: 审核评语
    """
    solution: ProblemSolution = db.session.query(
        ProblemSolution).filter_by(id=solution_id).one_or_none()
    if not solution:
        return make_json_response(-1, message="题解不存在")
    if solution.verified:
        return make_json_response(-1, message="题解已经审核")
    solution.verified = True
    solution.verifier = get_uid()
    solution.verify_comment = comment
    solution.verify_time = datetime.datetime.now()
    db.session.commit()
    return make_json_response(0)


@router.route("/admin/toggle_top_status", methods=["POST"])
@require_permission(permission_manager, "solution.manage")
def admin_toggle_top_status(solution_id: int):
    solution: ProblemSolution = db.session.query(
        ProblemSolution).filter_by(id=solution_id).one_or_none()
    if not solution:
        return make_json_response(-1, message="题解不存在")
    solution.top = not solution.top
    db.session.commit()
    return make_json_response(0)
