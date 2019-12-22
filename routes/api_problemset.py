from main import db, permission_manager
from main import web_app as app
from common.permission import require_permission
from common.utils import unpack_argument
from models import User, ProblemSet, Problem


@app.route("/api/problemset/list", methods=["POST"])
@require_permission(permission_manager, "problemset.use.public")
def api_problem_set_list(page: int = 1):
    pass
