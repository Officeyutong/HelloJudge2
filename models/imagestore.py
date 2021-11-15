from main import db

from sqlalchemy import Integer, ForeignKey, Column, String


class ImageStoreFile(db.Model):
    __tablename__ = "image_store_file"
    file_id = Column(String(128), ForeignKey(
        "file_storage.uuid", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, primary_key=True)
    thumbnail_id = Column(String(128), ForeignKey(
        "file_storage.uuid", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, index=True)
    uid = Column(Integer, ForeignKey(
        "user.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, index=True)
