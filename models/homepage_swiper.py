from main import db

from sqlalchemy import String, Column, Integer


class HomepageSwiper(db.Model):
    __tablename__ = "homepage_swiper"
    id = Column(Integer, primary_key=True)
    image_url = Column(String(length=200), nullable=False, default="")
    link_url = Column(String(length=200), nullable=False, default="")