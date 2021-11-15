from flask import Blueprint
from sqlalchemy.sql import expression
from common.utils import make_json_response, unpack_argument
from main import db, permission_manager, user_operation, file_storage, config
from common.permission import require_permission
from flask import request, abort
from models.imagestore import ImageStoreFile
from models.file_storage import FileStorage as model_FileStorage
import math
import uuid
import werkzeug
import os
import cv2
import shutil
router = Blueprint("api_imagestore", "api_imagestore")

# 长225 高170
TARGET_SIZE = (225, 170)


def scale_image(infile: str, filename: str) -> str:
    img = cv2.imread(str(file_storage.get_filepath(infile)))
    height, width, _ = img.shape
    dwidth, dheight = TARGET_SIZE
    if width <= dwidth and height <= dheight:
        return infile
    ratio = max(width/dwidth, height/dheight)
    target = cv2.resize(img, (int(width/ratio), int(height/ratio)))
    currid = str(uuid.uuid4())
    import tempfile
    temp_file = tempfile.mktemp(".png")
    cv2.imwrite(temp_file, target)
    shutil.copy(temp_file, file_storage.get_filepath(currid))
    os.remove(temp_file)
    file_storage.store_file_into_db(
        currid, filename, os.path.getsize(file_storage.get_filepath(currid))
    )
    return currid


@router.route("/upload", methods=["POST"])
@require_permission(permission_manager, "imagestore.use")
def image_upload():
    uid = user_operation.ensure_login()
    to_save = []
    for filename, file in request.files.items():
        file: werkzeug.FileStorage
        curr_id = str(uuid.uuid4())
        file.save(str(file_storage.get_filepath(curr_id)))
        thumbnail_id = scale_image(curr_id, filename)
        size = os.path.getsize(file_storage.get_filepath(curr_id))
        to_save.append({
            "file_id": curr_id,
            "filename": filename,
            "filesize": size,
            "thumbnail_id": thumbnail_id
        })
    for t in to_save:
        file_storage.store_file_into_db(
            filename=t["filename"], file_id=t["file_id"], filesize=t["filesize"])
    db.session.add_all([ImageStoreFile(
        file_id=t["file_id"],
        uid=uid,
        thumbnail_id=t["thumbnail_id"]
    ) for t in to_save])
    db.session.commit()
    return make_json_response(0, data=[{t["filename"]:t["file_id"] for t in to_save}])


@router.route("/get", methods=["GET", "POST"])
def image_get():
    args = request.args
    if "file_id" not in args:
        abort(403)
    file_id = args["file_id"]
    if not db.session.query(ImageStoreFile.file_id).filter(expression.or_(
        ImageStoreFile.file_id == file_id,
        ImageStoreFile.thumbnail_id == file_id
    )).one_or_none():
        abort(404)
    return file_storage.get_flask_sendfile(file_id, False)


@router.route("/remove", methods=["POST"])
@unpack_argument
@require_permission(permission_manager, "imagestore.use")
def image_remove(file_id: str):
    inst = db.session.query(ImageStoreFile.file_id, ImageStoreFile.thumbnail_id).filter_by(
        file_id=file_id).one_or_none()
    if not inst:
        return make_json_response(-1, message="图片不存在!")
    file_id = inst.file_id
    thumbnail_id = inst.thumbnail_id
    file_storage.remove_file(file_id)
    if thumbnail_id != file_id:
        file_storage.remove_file(thumbnail_id)
    return make_json_response(0)


@router.route("/list", methods=["POST"])
@unpack_argument
@require_permission(permission_manager, "imagestore.use")
def image_getall(page: int = 1):
    uid = user_operation.ensure_login()
    query = db.session.query(
        model_FileStorage.filename,
        model_FileStorage.filesize,
        model_FileStorage.upload_time,
        ImageStoreFile.file_id,
        ImageStoreFile.thumbnail_id
    ).filter(ImageStoreFile.uid == uid).order_by(model_FileStorage.upload_time.desc()).join(model_FileStorage, model_FileStorage.uuid == ImageStoreFile.file_id)
    page_count = math.ceil(query.count()/config.IMAGES_PER_PAGE)
    resp = {
        "images": [{
            "filename": t.filename,
            "filesize": t.filesize,
            "upload_time": t.upload_time.timestamp(),
            "file_id": t.file_id,
            "thumbnail_id": t.thumbnail_id
        }for t in query.slice((page-1)*config.IMAGES_PER_PAGE, page*config.IMAGES_PER_PAGE)],
        "pageCount": page_count
    }
    return make_json_response(0, data=resp)
