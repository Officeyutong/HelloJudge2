from datetime import datetime
from main import db

from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, String, BigInteger
# from sqlalchemy.dialects.mysql import


class FileStorage(db.Model):
    __tablename__ = "file_storage"
    # 唯一ID
    uuid = Column(String(128), primary_key=True)
    # 文件名
    filename = Column(String(256), nullable=False, default="", index=True)
    # 文件大小
    filesize = Column(BigInteger, nullable=False)
    # 上传时间
    upload_time = Column(DateTime, nullable=False, default=datetime.now)
