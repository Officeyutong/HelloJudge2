from flask import Blueprint
from common.utils import make_json_response, unpack_argument
from main import permission_manager
router = Blueprint("permission", "permission")


@router.route("/get_all_permissions", methods=["POST"])
@unpack_argument
def get_all_permissions(uid: int):
    return make_json_response(0, data=permission_manager.get_all_permissions(uid))
