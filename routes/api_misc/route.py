from common.permission import require_permission
from typing import List
from common.utils import make_json_response, require_schema
from flask import Blueprint
from .schema import homepage_swiper_schema, HomepageSwiperEntry
from main import db, permission_manager
from models import HomepageSwiper
router = Blueprint("api_misc", "api_misc")


@router.route("/homepage_swiper/list", methods=["POST"])
# @require_schema(homepage_swiper_schema)
# @require_permission(permission_manager,"backend.manage")
def swiper_list():
    """
    返回主页轮播图列表
    """
    data = db.session.query(HomepageSwiper.link_url,
                            HomepageSwiper.image_url).all()
    return make_json_response(0, data=[{"link_url": item.link_url, "image_url": item.image_url} for item in data])


@router.route("/homepage_swiper/update", methods=["POST"])
@require_schema(homepage_swiper_schema)
@require_permission(permission_manager, "backend.manage")
def swiper_update(data: List[HomepageSwiperEntry]):
    """
    更新主页轮播图列表
    """
    db.session.query(HomepageSwiper).delete()
    db.session.add_all([HomepageSwiper(
        link_url=item.link_url, image_url=item.image_url) for item in data])
    db.session.commit()
    return make_json_response(0, message="操作完成")
