import os
from typing import Tuple
import flask
from flask_sqlalchemy import SQLAlchemy

import pathlib
import uuid
BASE_DIR = pathlib.Path(".")/"file_storage"


class FileStorage:
    def __init__(self, db: SQLAlchemy) -> None:
        self.db = db

    def get_filepath(self, name):
        return BASE_DIR/name

    def ensure_datadir(self):
        if not os.path.exists(BASE_DIR):
            os.mkdir(BASE_DIR)

    def get_flask_sendfile(self, file_id: str, as_attach: bool = False):
        self.ensure_datadir()
        from models.file_storage import FileStorage as model_FileStorage
        target_file = BASE_DIR/file_id
        entry: model_FileStorage = self.db.session.query(
            model_FileStorage).filter(model_FileStorage.uuid == file_id).one_or_none()
        if not entry:
            flask.abort(404)
        return flask.send_file(target_file, as_attachment=as_attach, attachment_filename=entry.filename, conditional=True)

    def store_file_into_db(self, file_id: str, filename: str, filesize: int):
        self.ensure_datadir()
        from models.file_storage import FileStorage as model_FileStorage
        self.db.session.add(model_FileStorage(
            uuid=file_id,
            filename=filename,
            filesize=filesize
        ))
        self.db.session.commit()

    def remove_file(self, file_id: str):
        self.ensure_datadir()
        from models.file_storage import FileStorage as model_FileStorage
        self.db.session.query(model_FileStorage).filter(
            model_FileStorage.uuid == file_id).delete()
        self.db.session.commit()
        filename = BASE_DIR/file_id
        if os.path.exists(filename):
            os.remove(filename)
